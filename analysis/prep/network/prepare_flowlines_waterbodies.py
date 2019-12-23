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

import pygeos as pg
from geofeather.pygeos import to_geofeather, from_geofeather
from pgpkg import to_gpkg
from nhdnet.io import serialize_df, deserialize_df
from nhdnet.nhd.joins import remove_joins

from analysis.constants import (
    CRS,
    REGION_GROUPS,
    EXCLUDE_IDS,
    CONVERT_TO_NONLOOP,
    MAX_PIPELINE_LENGTH,
    WATERBODY_MIN_SIZE,
)

from analysis.prep.network.lib.dissolve import dissolve_waterbodies
from analysis.prep.network.lib.cut import cut_lines_by_waterbodies
from analysis.prep.network.lib.lines import remove_pipelines, remove_flowlines
from analysis.prep.network.lib.drains import create_drain_points


nhd_dir = Path("data/nhd")
src_dir = nhd_dir / "raw"


start = time()
for region, HUC2s in list(REGION_GROUPS.items())[4:]:
    region_start = time()

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

    ### Drop underground conduits
    ix = flowlines.loc[flowlines.FType == 420].index
    print("Removing {:,} underground conduits".format(len(ix)))
    flowlines = flowlines.loc[~flowlines.index.isin(ix)].copy()
    joins = remove_joins(
        joins, ix, downstream_col="downstream_id", upstream_col="upstream_id"
    )

    ### Manual fixes for flowlines
    exclude_ids = EXCLUDE_IDS.get(region, [])
    if exclude_ids:
        flowlines, joins = remove_flowlines(flowlines, joins, exclude_ids)
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

    print("------------------")

    ### Drop pipelines that are > PIPELINE_MAX_LENGTH or are otherwise isolated from the network
    print("Evaluating pipelines")
    flowlines, joins = remove_pipelines(flowlines, joins, MAX_PIPELINE_LENGTH)
    print("{:,} flowlines after dropping pipelines".format(len(flowlines)))

    print("------------------")

    ### Aggregate waterbodies that are in contact / overlapping each other
    waterbodies = from_geofeather(src_dir / region / "waterbodies.feather").set_index(
        "wbID"
    )
    wb_joins = deserialize_df(src_dir / region / "waterbody_flowline_joins.feather")
    print(
        "Read {:,} waterbodies and {:,} flowine / waterbody joins".format(
            len(waterbodies), len(wb_joins)
        )
    )

    # TODO: remove this on next full rerun of extract_flowlines...
    waterbodies = waterbodies.drop(columns=["hash"], errors="ignore")
    # Convert multipolygons to single part poylgons
    idx = (
        pg.get_type_id(waterbodies.geometry) == 6
    )  # idx = waterbodies.loc[waterbodies.geometry.type == "MultiPolygon"].index
    waterbodies.loc[idx, "geometry"] = waterbodies.loc[idx].geometry.apply(
        lambda g: pg.get_geometry(g, 0)
    )

    # raise min size
    waterbodies = waterbodies.loc[waterbodies.AreaSqKm >= WATERBODY_MIN_SIZE].copy()
    wb_joins = wb_joins.loc[wb_joins.wbID.isin(waterbodies.index)].copy()

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

    waterbodies, wb_joins = dissolve_waterbodies(waterbodies, wb_joins)
    print("{:,} waterbodies after dissolve".format(len(waterbodies)))

    # Make sure that all empty joins are dropped
    wb_joins = wb_joins.loc[
        wb_joins.lineID.isin(flowlines.index) & wb_joins.wbID.isin(waterbodies.index)
    ].copy()

    ### If needed, output intermediates for troubleshooting
    # print("Serializing flowlines before later processing")
    # to_geofeather(flowlines.reset_index(), out_dir / "temp_flowlines.feather")
    # serialize_df(joins.reset_index(), out_dir / "temp_flowline_joins.feather")
    # print("Serializing {:,} dissolved waterbodies".format(len(waterbodies)))
    # to_geofeather(waterbodies.reset_index(), out_dir / "dissolved_waterbodies.feather")
    # serialize_df(
    #     wb_joins.reset_index(drop=True), out_dir / "dissolved_waterbody_joins.feather"
    # )

    print("------------------")

    ### Cut flowlines by waterbodies

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
    to_gpkg(flowlines.reset_index(), "flowlines", crs=CRS)
    to_gpkg(waterbodies.reset_index(), "waterbodies", crs=CRS)
    to_gpkg(drains, "waterbody_drain_points", crs=CRS)

    print("Region done in {:.2f}s".format(time() - region_start))

print("==============\nAll done in {:.2f}s".format(time() - start))
