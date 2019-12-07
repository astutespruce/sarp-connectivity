from pathlib import Path
import os
from time import time

import pandas as pd
import geopandas as gp
import numpy as np
import networkx as nx
from shapely.geometry import Point
from geofeather import to_geofeather, from_geofeather
from nhdnet.io import serialize_df, deserialize_df, serialize_sindex, to_shp
from nhdnet.nhd.joins import (
    index_joins,
    find_joins,
    find_join,
    create_upstream_index,
    remove_joins,
)

from analysis.constants import REGION_GROUPS, EXCLUDE_IDS, CONVERT_TO_NONLOOP
from analysis.util import flatten_series
from analysis.prep.network.lib.dissolve import dissolve_waterbodies
from analysis.prep.network.lib.cut import cut_lines_by_waterbodies

# Threshold for dropping pipelines
# above this drop any pipelines from the network (some in region 2 at ~ 200m are pipelines we want to drop)
# Also will drop any loops
MAX_PIPELINE_LENGTH = 150  # meters

nhd_dir = Path("data/nhd")
src_dir = nhd_dir / "raw"


# load NHDlines - these indicate dam lines that need to remain cut across adjacent waterbodies
nhd_lines = from_geofeather(
    nhd_dir / "extra" / "nhd_lines.feather", columns=["geometry"]
)
nhd_lines.sindex


for region, HUC2s in REGION_GROUPS.items():
    print("\n----- {} ------\n".format(region))

    out_dir = nhd_dir / "clean" / region
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    print("Reading flowlines...")
    flowlines = from_geofeather(src_dir / region / "flowlines.feather").set_index(
        "lineID"
    )
    joins = deserialize_df(src_dir / region / "flowline_joins.feather")
    print("Read {:,} flowlines".format(len(flowlines)))

    ### Manual fixes for flowlines
    exclude_ids = EXCLUDE_IDS.get(region, [])
    if exclude_ids:
        # drop from flowlines
        flowlines = flowlines.loc[~flowlines.NHDPlusID.isin(exclude_ids)].copy()

        # IDs are based on NHDPlusID, make sure to use correct columns for joins
        joins = remove_joins(
            joins, exclude_ids, downstream_col="downstream", upstream_col="upstream"
        )

        # update our ids to match zeroed out ids
        joins.loc[joins.downstream == 0, "downstream_id"] = 0
        joins.loc[joins.downstream == 0, "type"] = "terminal"
        joins.loc[joins.upstream == 0, "upstream_id"] = 0

        print(
            "Removed {:,} excluded flowlines, now have {:,}".format(
                len(exclude_ids), len(flowlines)
            )
        )

    ### Fix segments that should not have been coded as loops
    convert_ids = CONVERT_TO_NONLOOP.get(region, [])
    if convert_ids:
        print("Converting {:,} loops to non-loops".format(len(convert_ids)))
        flowlines.loc[flowlines.NHDPlusID.isin(convert_ids), "loop"] = False
        joins.loc[joins.upstream.isin(convert_ids), "loop"] = False
        joins.loc[joins.downstream.isin(convert_ids), "loop"] = False

    ### Drop remaining loops
    loop_ids = flowlines.loc[flowlines.loop].index
    print("Dropping remaining {:,} loops".format(len(loop_ids)))
    flowlines = flowlines.loc[~flowlines.index.isin(loop_ids)].drop(columns=["loop"])
    joins = joins.loc[~joins.loop].drop(columns=["loop"])

    print("{:,} flowlines after dropping loops".format(len(flowlines)))

    ### Drop pipelines that are > PIPELINE_MAX_LENGTH or are otherwise isolated from the network
    print("Evaluating pipelines")
    pids = flowlines.loc[flowlines.FType == 428].index
    pjoins = find_joins(
        joins, pids, downstream_col="downstream_id", upstream_col="upstream_id"
    )[["downstream_id", "upstream_id"]]
    print(
        "Found {:,} pipelines and {:,} pipeline-related joins".format(
            len(pids), len(pjoins)
        )
    )

    # drop any terminal joins before traversing network
    # otherwise the 0's close the loop
    pjoins = pjoins.loc[
        ~((pjoins.upstream_id == 0) | (pjoins.downstream_id == 0))
    ].copy()

    # create a network of pipelines to group them together
    network = nx.from_pandas_edgelist(pjoins, "downstream_id", "upstream_id")
    components = pd.Series(nx.connected_components(network)).apply(list)

    groups = (
        pd.DataFrame(flatten_series(components))
        .reset_index()
        .rename(columns={0: "lineID", "index": "group"})
    )
    groups = groups.join(flowlines[["length"]], on="lineID")
    stats = groups.groupby("group").agg({"length": "sum"})
    drop_groups = stats.loc[stats.length >= MAX_PIPELINE_LENGTH].index
    drop_ids = groups.loc[groups.group.isin(drop_groups)].lineID

    print(
        "Dropping {:,} pipelines that are greater than the max allowed length".format(
            len(drop_ids)
        )
    )
    flowlines = flowlines.loc[~flowlines.index.isin(drop_ids)].copy()
    joins = remove_joins(
        joins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )

    # update NHDPlusIDs to match zeroed out ids
    joins.loc[joins.downstream_id == 0, "downstream"] = 0
    joins.loc[joins.downstream_id == 0, "type"] = "terminal"
    joins.loc[joins.upstream_id == 0, "upstream"] = 0

    # TODO: watch for pipelines that intersect with non-pipelines at other places than their terminals
    # we want to drop these too

    ### Aggregate waterbodies that are in contact / overlapping each other
    waterbodies = from_geofeather(src_dir / region / "waterbodies.feather").set_index(
        "wbID"
    )
    wb_joins = deserialize_df(src_dir / region / "waterbody_flowline_joins.feather")
    print("Read {:,} waterbodies".format(len(waterbodies)))

    # TODO: remove this on next full rerun of extract_flowlines...
    idx = waterbodies.loc[waterbodies.geometry.type == "MultiPolygon"].index
    waterbodies.loc[idx, "geometry"] = waterbodies.loc[idx].geometry.apply(
        lambda g: g[0]
    )
    # End TODO:

    # Drop any waterbodies and waterbody joins to flowlines that are no longer present
    # based on above processing of flowlines
    wb_joins = wb_joins.loc[wb_joins.lineID.isin(flowlines.index)].copy()
    to_drop = ~waterbodies.index.isin(wb_joins.wbID)
    print(
        "Dropping {:,} waterbodies that no longer intersect with the flowlines retained above".format(
            to_drop.sum()
        )
    )
    waterbodies = waterbodies.loc[~to_drop].copy()

    # Overlay and dissolve
    print("Dissolving adjacent waterbodies (where appropriate)")
    waterbodies, wb_joins = dissolve_waterbodies(waterbodies, wb_joins, nhd_lines)
    print("{:,} waterbodies after dissolve".format(len(waterbodies)))

    ### Refine overlaps between remaining waterbodies and flowlines
    print("Processing intersections between waterbodies and flowlines")
    flowlines, joins, waterbodies, wb_joins = cut_lines_by_waterbodies(
        flowlines, joins, waterbodies, wb_joins
    )

    # intersect the new flowlines back to the waterbody geometry to identify those that are inside or not
    # intersection = new_lines.intersection(gp.GeoSeries(new_lines.waterbody))
    # temp = gp.GeoDataFrame(
    #     new_lines[["level_1", "lineID", "wbID"]]
    #     .join(intersection.rename("geometry"))
    #     .join(flowlines["length"].rename("origLength"), on="lineID"),
    #     crs=flowlines.crs,
    # )

    # need to remove from flowlines and add new ones

    # TODO: watch for places where there is a difference between total length of cut parts and original line
    # these indicate shared edges and need a different method

    # NOTE: all that are not inside touch, but only some of those that touch cross

    # any that don't cross and are not inside can now be dropped from joins and wb_lines

    # TODO: IMPORTANT: cut flowlines by waterbodies

    print("Serializing {:,} flowlines".format(len(flowlines)))
    to_geofeather(flowlines.reset_index(), out_dir / "flowlines.feather")
    serialize_sindex(joins, out_dir / "flowline_joins.feather")

    print("Serializing {:,} waterbodies".format(len(waterbodies)))
    to_geofeather(waterbodies.reset_index(), out_dir / "waterbodies.feather")
    serialize_df(wb_joins, out_dir / "waterbody_flowline_joins.feather")

    # Serialize to shapefiles
    print("Serializing to shapefile")
    flowlines.reset_index().to_file(out_dir / "flowlines.shp")
    waterbodies.reset_index().to_file(out_dir / "waterbodies.shp")

