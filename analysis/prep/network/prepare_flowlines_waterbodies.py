"""Transforms raw (minimally processed) NHD data into formats and structures
for use in the rest of this data pipeline.

This depends on data created in `extract_flowlines_waterbodies.py` and `extract_nhd_lines.py`:
- data/nhd/raw/<region>/flowlines.feather
- data/nhd/raw/<region>/flowline_joins.feather
- data/nhd/raw/<region>/waterbodies.feather
- data/nhd/raw/<region>/waterbody_flowline_joins.feather
- data/nhd/extra/nhd_lines.feather

It removes flowlines that are specifically excluded, are loops, or longer pipelines.

It dissolves waterbodies except where they are divided by NHD lines (these are typically dams between parts of reservoirs).

It then intersects the flowlines with the waterbodies and builds the final mapping of flowlines to waterbodies.

It calculates waterbody drain points from the lowest downstream intersection point of flowlines and their respective waterbodies.

It produces data in `data/nhd/clean/<region>`
- flowlines.feather
- flowline_joins.feather
- waterbodies.feather
- waterbody_flowline_joins.feather
"""


from pathlib import Path
import os
from time import time

import geopandas as gp
import pandas as pd
import pygeos as pg
from pyogrio import read_dataframe, write_dataframe
from nhdnet.nhd.joins import remove_joins

from analysis.constants import (
    CRS,
    EXCLUDE_IDS,
    CONVERT_TO_NONLOOP,
    MAX_PIPELINE_LENGTH,
    WATERBODY_MIN_SIZE,
)

from analysis.prep.network.lib.dissolve import (
    cut_waterbodies_by_dams,
    dissolve_waterbodies,
)
from analysis.prep.network.lib.cut import cut_lines_by_waterbodies
from analysis.prep.network.lib.lines import remove_pipelines, remove_flowlines
from analysis.prep.network.lib.drains import create_drain_points


data_dir = Path("data")
nhd_dir = data_dir / "nhd"
src_dir = nhd_dir / "raw"
out_dir = nhd_dir / "clean"

huc4_df = pd.read_feather(
    data_dir / "boundaries/huc4.feather", columns=["HUC2", "HUC4"]
)
# Convert to dict of sorted HUC4s per HUC2
units = huc4_df.groupby("HUC2").HUC4.unique().apply(sorted).to_dict()

# manually subset keys from above for processing
# huc2s = ['02', '03', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '21']
huc2s = ["02"]


start = time()
# for region, HUC2s in list(REGION_GROUPS.items())[4:]:
for huc2 in huc2s:
    region_start = time()

    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2
    if not os.path.exists(huc2_dir):
        os.makedirs(huc2_dir)

    print("Reading flowlines...")
    flowlines = gp.read_feather(src_dir / huc2 / "flowlines.feather").set_index(
        "lineID"
    )
    joins = pd.read_feather(src_dir / huc2 / "flowline_joins.feather")
    print("Read {:,} flowlines".format(len(flowlines)))

    ### Drop underground conduits
    ix = flowlines.loc[flowlines.FType == 420].index
    print("Removing {:,} underground conduits".format(len(ix)))
    flowlines = flowlines.loc[~flowlines.index.isin(ix)].copy()
    joins = remove_joins(
        joins, ix, downstream_col="downstream_id", upstream_col="upstream_id"
    )

    ### Manual fixes for flowlines
    exclude_ids = EXCLUDE_IDS.get(huc2, [])
    if exclude_ids:
        flowlines, joins = remove_flowlines(flowlines, joins, exclude_ids)
        print(
            "Removed {:,} excluded flowlines, now have {:,}".format(
                len(exclude_ids), len(flowlines)
            )
        )

    ### Fix segments that should not have been coded as loops
    convert_ids = CONVERT_TO_NONLOOP.get(huc2, [])
    if convert_ids:
        print("Converting {:,} loops to non-loops".format(len(convert_ids)))
        flowlines.loc[flowlines.NHDPlusID.isin(convert_ids), "loop"] = False
        joins.loc[joins.upstream.isin(convert_ids), "loop"] = False
        joins.loc[joins.downstream.isin(convert_ids), "loop"] = False

    print("------------------")

    ### Drop pipelines that are > PIPELINE_MAX_LENGTH or are otherwise isolated from the network
    print("Evaluating pipelines")
    flowlines, joins = remove_pipelines(flowlines, joins, MAX_PIPELINE_LENGTH)
    print("{:,} flowlines after dropping pipelines".format(len(flowlines)))

    print("------------------")

    ### Aggregate waterbodies that are in contact / overlapping each other
    waterbodies = gp.read_feather(src_dir / huc2 / "waterbodies.feather").set_index(
        "wbID"
    )
    print(f"Read {len(waterbodies):,} waterbodies")
    # wb_joins = pd.read_feather(src_dir / huc2 / "waterbody_flowline_joins.feather")
    # print(
    #     "Read {:,} waterbodies and {:,} flowine / waterbody joins".format(
    #         len(waterbodies), len(wb_joins)
    #     )
    # )

    # Drop any waterbodies and waterbody joins to flowlines that are no longer present
    # based on above processing of flowlines
    # wb_joins = wb_joins.loc[wb_joins.lineID.isin(flowlines.index)].copy()
    # to_drop = ~waterbodies.index.isin(wb_joins.wbID)
    # print(
    #     "Dropping {:,} waterbodies that no longer intersect with the flowlines retained above".format(
    #         to_drop.sum()
    #     )
    # )
    # waterbodies = waterbodies.loc[~to_drop].copy()

    # Overlay and dissolve
    print(
        "Processing adjacent waterbodies to clip shared edges that must be preserved..."
    )
    nhd_lines = gp.read_feather(src_dir / huc2 / "nhd_lines.feather")
    waterbodies = cut_waterbodies_by_dams(waterbodies, nhd_lines)

    print("Dissolving adjacent waterbodies (where appropriate)")
    waterbodies = dissolve_waterbodies(waterbodies, nhd_lines)
    print("{:,} waterbodies after dissolve".format(len(waterbodies)))

    # Make sure that all empty joins are dropped
    # wb_joins = wb_joins.loc[
    #     wb_joins.lineID.isin(flowlines.index) & wb_joins.wbID.isin(waterbodies.index)
    # ].copy()

    ### If needed, output intermediates for troubleshooting
    write_dataframe(waterbodies, "/tmp/waterbodies.gpkg")

    raise Foo

    print("------------------")

    ### Cut flowlines by waterbodies

    # TODO: load up wbJoins and select flowlines from that

    print("Processing intersections between waterbodies and flowlines")
    flowlines, joins, waterbodies, wb_joins = cut_lines_by_waterbodies(
        flowlines, joins, waterbodies, wb_joins, out_dir
    )

    # Update dtypes
    joins.upstream = joins.upstream.astype("uint64")
    joins.downstream = joins.downstream.astype("uint64")
    joins.upstream_id = joins.upstream_id.astype("uint32")
    joins.downstream_id = joins.downstream_id.astype("uint32")

    # TODO: fix joins that are getting assigned null for loop
    # these appear to be coming from segments cut by waterbodies
    # ix = flowlines.loc[flowlines.loop].index
    # joins.loc[joins.upstream_id.isin(ix) | joins.downstream_id.isin(ix), "loop"] = True
    # joins.loop = joins.loop.fillna(False)

    print(
        "Now have {:,} flowlines, {:,} waterbodies, {:,} waterbody-flowline joins".format(
            len(flowlines), len(waterbodies), len(wb_joins)
        )
    )

    print("------------------")

    print("Identifying waterbody drain points")
    drains = create_drain_points(flowlines, joins, waterbodies, wb_joins)

    # fix index data type issues
    waterbodies.index = waterbodies.index.astype("uint32")

    print("------------------")

    print("Serializing {:,} flowlines".format(len(flowlines)))
    flowlines = flowlines.reset_index()
    to_geofeather(flowlines, out_dir / "flowlines.feather", crs=CRS)
    serialize_df(joins.reset_index(drop=True), out_dir / "flowline_joins.feather")

    print("Serializing {:,} waterbodies".format(len(waterbodies)))
    to_geofeather(waterbodies.reset_index(), out_dir / "waterbodies.feather", crs=CRS)
    serialize_df(
        wb_joins.reset_index(drop=True), out_dir / "waterbody_flowline_joins.feather"
    )

    print("Serializing {:,} drain points".format(len(drains)))
    to_geofeather(drains, out_dir / "waterbody_drain_points.feather", crs=CRS)

    # Serialize to GIS files
    print("Serializing to GIS files")
    to_gpkg(flowlines.reset_index(), out_dir / "flowlines", crs=CRS)
    to_gpkg(waterbodies.reset_index(), out_dir / "waterbodies", crs=CRS)
    to_gpkg(drains, out_dir / "waterbody_drain_points", crs=CRS)

    print("Region done in {:.2f}s".format(time() - region_start))

print("==============\nAll done in {:.2f}s".format(time() - start))
