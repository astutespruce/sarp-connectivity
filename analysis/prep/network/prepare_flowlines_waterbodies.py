"""Transforms raw (minimally processed) NHD data into formats and structures
for use in the rest of this data pipeline.

This depends on data created in `extract_flowlines_waterbodies.py` and `extract_nhd_lines.py`:
- data/nhd/raw/<region>/flowlines.feather
- data/nhd/raw/<region>/flowline_joins.feather
- data/nhd/raw/<region>/waterbodies.feather
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
- waterbody_drain_points.feather
"""


from pathlib import Path
import os
from time import time
import warnings

import geopandas as gp
import pandas as pd
import pygeos as pg
from pyogrio import write_dataframe


from analysis.constants import (
    CONVERT_TO_NONLOOP,
    REMOVE_IDS,
    MAX_PIPELINE_LENGTH,
)
from analysis.lib.joins import remove_joins
from analysis.lib.flowlines import (
    remove_flowlines,
    remove_pipelines,
    remove_marine_flowlines,
    cut_lines_by_waterbodies,
)
from analysis.prep.network.lib.drains import create_drain_points


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
nhd_dir = data_dir / "nhd"
src_dir = nhd_dir / "raw"
waterbodies_dir = data_dir / "waterbodies"
out_dir = nhd_dir / "clean"

# huc2s = sorted(
#     pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"]).HUC2.values
# )
# manually subset keys from above for processing
huc2s = [
    "02",
    "03",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "21",
]


start = time()
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

    print("------------------")

    ### Drop underground conduits
    # TODO: remove once extract_nhd has been rerun for all areas
    ix = flowlines.loc[flowlines.FType == 420].index
    if len(ix):
        print("Removing {:,} underground conduits".format(len(ix)))
        flowlines = flowlines.loc[~flowlines.index.isin(ix)].copy()
        joins = remove_joins(
            joins, ix, downstream_col="downstream_id", upstream_col="upstream_id"
        )
        print("------------------")

    ### Manual fixes for flowlines
    remove_ids = REMOVE_IDS.get(huc2, [])
    if remove_ids:
        print(f"Removing {len(remove_ids):,} manually specified NHDPlusIDs")
        flowlines, joins = remove_flowlines(flowlines, joins, remove_ids)
        print("------------------")

    ### Fix segments that should not have been coded as loops
    convert_ids = CONVERT_TO_NONLOOP.get(huc2, [])
    if convert_ids:
        print(f"Converting {len(convert_ids):,} loops to non-loops")
        flowlines.loc[flowlines.NHDPlusID.isin(convert_ids), "loop"] = False
        joins.loc[joins.upstream.isin(convert_ids), "loop"] = False
        joins.loc[joins.downstream.isin(convert_ids), "loop"] = False
        print("------------------")

    ### Remove any flowlines that start in marine areas
    marine_filename = src_dir / huc2 / "nhd_marine.feather"
    if marine_filename.exists():
        marine = gp.read_feather(marine_filename)
        flowlines, joins = remove_marine_flowlines(flowlines, joins, marine)
        print("------------------")

    # TODO: temporary shim until marine is attributed everywhere
    elif not "marine" in joins.columns:
        joins["marine"] = False

    ### Drop pipelines that are > PIPELINE_MAX_LENGTH or are otherwise isolated from the network
    print("Evaluating pipelines")
    flowlines, joins = remove_pipelines(flowlines, joins, MAX_PIPELINE_LENGTH)
    print("{:,} flowlines after dropping pipelines".format(len(flowlines)))

    # make sure that updated joins are unique
    joins = joins.drop_duplicates(subset=["upstream_id", "downstream_id"])

    print("------------------")

    waterbodies = gp.read_feather(
        waterbodies_dir / huc2 / "waterbodies.feather"
    ).set_index("wbID")
    print(f"Read {len(waterbodies):,} waterbodies")

    # DEBUG
    # flowlines.reset_index().to_feather("/tmp/flowlines.feather")
    # joins.reset_index(drop=True).to_feather("/tmp/flowline_joins.feather")
    # # flowlines = gp.read_feather("/tmp/flowlines.feather").set_index("lineID")
    # # joins = pd.read_feather(src_dir / huc2 / "flowline_joins.feather")
    # waterbodies = waterbodies.head(1000)
    # end DEBUG

    print("------------------")

    ### Cut flowlines by waterbodies
    print("Processing intersections between waterbodies and flowlines")
    next_lineID = int(flowlines.index.max() + 1)
    flowlines, joins, wb_joins = cut_lines_by_waterbodies(
        flowlines, joins, waterbodies, next_lineID=next_lineID
    )

    # drop any waterbodies that no longer join to flowlines
    waterbodies = waterbodies.loc[wb_joins.wbID.unique()].copy()

    # Fix dtypes
    joins.upstream = joins.upstream.astype("uint64")
    joins.downstream = joins.downstream.astype("uint64")
    joins.upstream_id = joins.upstream_id.astype("uint32")
    joins.downstream_id = joins.downstream_id.astype("uint32")

    # calculate stats for flowlines in waterbodies
    tmp = wb_joins.join(flowlines.geometry, on="lineID")
    tmp["length"] = pg.length(tmp.geometry.values.data)
    tmp = tmp.groupby("wbID")["length"].sum().astype("float32").rename("flowlineLength")
    waterbodies = waterbodies.join(tmp)
    waterbodies.flowlineLength = waterbodies.flowlineLength.fillna(0)

    print(
        "Now have {:,} flowlines, {:,} waterbodies, {:,} waterbody-flowline joins".format(
            len(flowlines), len(waterbodies), len(wb_joins)
        )
    )

    print("------------------")

    print("Identifying waterbody drain points")
    drains = create_drain_points(flowlines, joins, waterbodies, wb_joins)

    print("------------------")

    print("Serializing {:,} flowlines".format(len(flowlines)))
    flowlines = flowlines.reset_index()
    flowlines.to_feather(huc2_dir / "flowlines.feather")
    write_dataframe(flowlines, huc2_dir / "flowlines.gpkg")
    joins.reset_index(drop=True).to_feather(huc2_dir / "flowline_joins.feather")

    print("Serializing {:,} waterbodies".format(len(waterbodies)))
    # waterbodies are losing their CRS somewhere along the way, not sure why it is failing here
    waterbodies.set_crs(flowlines.crs, inplace=True)
    waterbodies = waterbodies.reset_index()
    waterbodies.to_feather(huc2_dir / "waterbodies.feather")
    write_dataframe(waterbodies, huc2_dir / "waterbodies.gpkg")
    wb_joins.reset_index(drop=True).to_feather(
        huc2_dir / "waterbody_flowline_joins.feather"
    )

    print("Serializing {:,} drain points".format(len(drains)))
    drains.to_feather(huc2_dir / "waterbody_drain_points.feather")
    write_dataframe(drains, huc2_dir / "waterbody_drain_points.gpkg")

    print(
        "------------------\nRegion done in {:.2f}s\n------------------\n".format(
            time() - region_start
        )
    )

print("==============\nAll done in {:.2f}s".format(time() - start))
