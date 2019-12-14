import os
from pathlib import Path
from time import time

import numpy as np
import pandas as pd
import pygeos as pg
import networkx as nx
from geofeather import to_geofeather, from_geofeather
import geopandas as gp

from nhdnet.io import (
    serialize_sindex,
    to_shp,
    deserialize_gdfs,
    deserialize_dfs,
    deserialize_df,
)
from nhdnet.nhd.joins import find_joins, index_joins, find_downstream_terminals

from analysis.pygeos_compat import (
    to_pygeos,
    from_pygeos,
    from_geofeather_as_pygeos,
    split_multi_geoms,
    sjoin,
    dissolve,
)

from analysis.constants import REGION_GROUPS

nhd_dir = Path("data/nhd")

print("Reading NHD lines")


nhd_lines = from_geofeather(nhd_dir / "extra" / "nhd_lines.feather")
nhd_lines = nhd_lines.loc[
    (nhd_lines.FType.isin([343, 369, 398])) & nhd_lines.geometry.notnull()
].copy()
# create buffers (5m) to merge with NHD areas
nhd_lines["geometry"] = pg.buffer(to_pygeos(nhd_lines.geometry), 5, quadsegs=1)

# All NHD areas indicate a dam-related feature
nhd_areas = from_geofeather(nhd_dir / "extra" / "nhd_areas.feather")
nhd_areas = nhd_areas.loc[nhd_areas.geometry.notnull()].copy()
nhd_areas["geometry"] = to_pygeos(nhd_areas.geometry)

# Dissolve adjacent nhd lines and waterbodies together
nhd_dams = nhd_lines.append(nhd_areas, ignore_index=True, sort=False)
nearby = sjoin(nhd_dams.g, nhd_dams.g)
network = nx.from_pandas_edgelist(nearby.reset_index(), "index", "index_right")
components = pd.Series(nx.connected_components(network)).apply(list)
groups = (
    pd.DataFrame(components.explode().rename("index_right"))
    .reset_index()
    .rename(columns={"index": "group", "index_right": "index"})
    .set_index("index")
)

nhd_dams = nhd_dams.join(groups)
# Extract composite names
name = (
    nhd_dams.groupby("group")
    .GNIS_Name.unique()
    .apply(lambda n: ", ".join([s for s in n if s]))
)

nhd_dams = (
    dissolve(nhd_dams[["HUC2", "group", "geometry"]], by="group")
    .join(name)
    .reset_index(drop=True)
    .rename(columns={"group": "id"})
    .set_index("id")
)


start = time()
for region, HUC2s in list(REGION_GROUPS.items())[0:1]:
    region_start = time()

    print("\n----- {} ------\n".format(region))

    # TODO: read into pygeos directly instead
    print("Reading flowlines...")
    flowlines = from_geofeather_as_pygeos(
        nhd_dir / "clean" / region / "flowlines.feather"
    ).set_index("lineID")
    joins = deserialize_df(src_dir / region / "flowline_joins.feather")

    dams = nhd_dams.loc[nhd_dams.HUC2.isin(HUC2s)]

    print("Joining {:,} NHD dams to {:,} flowlines".format(len(dams), len(flowlines)))
    join_start = time()
    dams = (
        pd.DataFrame(sjoin(dams.geometry, flowlines.geometry).rename("lineID"))
        .join(dams.geometry)
        .join(flowlines.geometry.rename("line"), on="lineID")
    ).reset_index()
    print("Join elapsed {:.2f}s".format(time() - join_start))

    print("Extracting intersecting flowlines...")
    # Only keep the joins for lines that signficantly cross
    intersection = pg.intersection(dams.geometry, dams.line)
    ix = pg.get_type_id(intersection).isin([1, 5])
    dams = dams.loc[ix].copy()

    print("Deduplicating joins...")
    # Some joins will have multiple flowlines
    # aggregate these to their lowest common flowline
    counts = dams.groupby("id").size()
    lineIDs = dams.loc[dams.id.isin(counts.loc[counts > 1].index)].lineID

    # extract overlapping nodes and build subnetworks
    j = find_joins(
        joins, lineIDs, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    # downstream-most segments are those that terminate in a segment not in our set here
    downstreams = find_downstream_terminals(
        j, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    nodes = j.loc[
        (j.upstream_id != 0) & (j.downstream_id != 0), ["downstream_id", "upstream_id"]
    ]
    # use undirected graph for finding neighbors
    network = nx.from_pandas_edgelist(nodes, "upstream_id", "downstream_id")
    components = pd.Series(nx.connected_components(network)).apply(list)

    # WARNING: this might blow up if there are true terminals (downstream == 0)
    downstream_for_group = components.apply(lambda c: np.intersect1d(c, downstreams)[0])
    nets = (
        pd.DataFrame(components.explode().rename("lineID"))
        .reset_index()
        .rename(columns={"index": "netID"})
        .set_index("lineID")
    )

    # FIXME: id==10171 is not getting a netID, and so is being left as dups
    # these aren't showing up in above

    # logic error - we are assigning further upstream than we should

    # netID == nan are single segment joins, not a problem
    dams = dams.join(nets, on="lineID", how="left").join(
        downstream_for_group.rename("newLineID"), on="netID", how="left"
    )
    ix = dams.netID.notnull()
    dams.loc[ix, "lineID"] = dams.loc[ix].newLineID.astype("uint32")
    dams = dams.drop(columns=["netID", "newLineID"]).drop_duplicates(
        subset=["id", "lineID"]
    )

    print("Found {:,} joins between NHD dams and flowlines".format(len(dams)))

    ### Extract representative point
    # Look at either end of overlapping line and use that as representative point.
    # Otherwise intersect and extract first coordinate of overlapping line
    first = pg.get_point(dams.line, 0)
    intersects_first = pg.intersects(dams.geometry, first)
    ix = intersects_first
    dams.loc[ix, "pt"] = first.loc[ix]

    ix = ~intersects_first
    last = pg.get_point(dams.loc[ix].line, -1)
    intersects_last = pg.intersects(dams.loc[ix].geometry, last)
    last = last.loc[intersects_last]
    dams.loc[last.index, "pt"] = last

    ix = dams.pt.isnull()
    # WARNING: this might fail for odd intersection geoms
    pt = pg.get_point(
        pg.intersection(dams.loc[ix].geometry, dams.loc[ix].line), 0
    ).dropna()
    dams.loc[pt.index, "pt"] = pt

