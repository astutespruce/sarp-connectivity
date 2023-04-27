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
from time import time

import geopandas as gp
import numpy as np
import pandas as pd
import shapely
from pyogrio import write_dataframe


from analysis.constants import (
    CONVERT_TO_LOOP,
    CONVERT_TO_NONLOOP,
    CONVERT_TO_MARINE,
    REMOVE_IDS,
    MAX_PIPELINE_LENGTH,
    KEEP_PIPELINES,
    JOIN_FIXES,
    REMOVE_JOINS,
)

from analysis.lib.flowlines import (
    remove_flowlines,
    remove_pipelines,
    remove_great_lakes_flowlines,
    remove_marine_flowlines,
    cut_lines_by_waterbodies,
    mark_altered_flowlines,
    repair_disconnected_subnetworks,
)
from analysis.prep.network.lib.drains import create_drain_points


data_dir = Path("data")
nhd_dir = data_dir / "nhd"
src_dir = nhd_dir / "raw"
nwi_dir = data_dir / "nwi/raw"
waterbodies_dir = data_dir / "waterbodies"
out_dir = nhd_dir / "clean"

huc2s = sorted(
    pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"]).HUC2.values
)
# manually subset keys from above for processing
huc2s = [
    # "01",
    # "02",
    # "03",
    # "04",
    # "05",
    # "06",
    # "07",
    # "08",
    # "09",
    # "10",
    # "11",
    # "12",
    # "13",
    # "14",
    # "15",
    # "16",
    # "17",
    "18",
    # "19",
    # "21",
]


start = time()
for huc2 in huc2s:
    region_start = time()

    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2
    huc2_dir.mkdir(exist_ok=True, parents=True)

    print("Reading flowlines...")
    flowlines = gp.read_feather(src_dir / huc2 / "flowlines.feather").set_index(
        "lineID"
    )
    joins = pd.read_feather(src_dir / huc2 / "flowline_joins.feather")
    print(f"Read {len(flowlines):,} flowlines")

    waterbodies = gp.read_feather(
        waterbodies_dir / huc2 / "waterbodies.feather"
    ).set_index("wbID")
    print(f"Read {len(waterbodies):,} waterbodies")

    print("------------------")

    ### Manual fixes to joins

    # TODO: fix this in initial extraction from NHD
    # any marked as internal but with no downstream should be set as terminals
    joins.loc[(joins.downstream == 0) & (joins.type == "internal"), "type"] = "terminal"

    join_fixes = JOIN_FIXES.get(huc2, [])
    if join_fixes:
        print(f"Fixing {len(join_fixes)} joins based on manual updates")
        for fix in join_fixes:
            ix = (joins.upstream == fix["upstream"]) & (
                joins.downstream == fix["downstream"]
            )
            if "new_upstream" in fix:
                joins.loc[ix, "upstream"] = fix["new_upstream"]
                flowline_ix = flowlines.NHDPlusID == fix["new_upstream"]
                # this might be absent from flowlines if at HUC2 join
                if flowline_ix.sum():
                    joins.loc[ix, "upstream_id"] = flowlines.loc[flowline_ix].index[0]

            if "new_downstream" in fix:
                joins.loc[ix, "downstream"] = fix["new_downstream"]
                # this might be absent from flowlines if at HUC2 join
                flowline_ix = flowlines.NHDPlusID == fix["new_downstream"]
                if flowline_ix.sum():
                    joins.loc[ix, "downstream_id"] = flowlines.loc[flowline_ix].index[0]

    ### Manually remove joins
    to_remove = REMOVE_JOINS.get(huc2, [])
    if to_remove:
        print(f"Removing {len(to_remove)} joins based on manual review")
        for entry in to_remove:
            ix = (joins.upstream == entry["upstream"]) & (
                joins.downstream == entry["downstream"]
            )
            joins = joins.loc[~ix].copy()

    ### Manual fixes for flowlines
    remove_ids = REMOVE_IDS.get(huc2, [])
    if remove_ids:
        print(f"Removing {len(remove_ids):,} manually specified NHDPlusIDs")
        flowlines, joins = remove_flowlines(flowlines, joins, remove_ids)
        print("------------------")

    ### Fix segments that should have been coded as loops
    convert_ids = CONVERT_TO_LOOP.get(huc2, [])
    if convert_ids:
        print(f"Converting {len(convert_ids):,} non-loops to loops")
        flowlines.loc[flowlines.NHDPlusID.isin(convert_ids), "loop"] = True
        joins.loc[joins.upstream.isin(convert_ids), "loop"] = True
        joins.loc[joins.downstream.isin(convert_ids), "loop"] = True
        print("------------------")

    ### Fix segments that should not have been coded as loops
    convert_ids = CONVERT_TO_NONLOOP.get(huc2, [])
    if convert_ids:
        print(f"Converting {len(convert_ids):,} loops to non-loops")
        flowlines.loc[flowlines.NHDPlusID.isin(convert_ids), "loop"] = False
        joins.loc[joins.upstream.isin(convert_ids), "loop"] = False
        joins.loc[joins.downstream.isin(convert_ids), "loop"] = False
        print("------------------")

    ### Fix joins that should have been marked as marine
    marine_ids = CONVERT_TO_MARINE.get(huc2, [])
    if marine_ids:
        print(f"Converting {len(marine_ids):,} joins to marine")
        joins.loc[joins.upstream.isin(marine_ids), "marine"] = True
        print("------------------")

    ### Remove any flowlines that start in marine areas
    marine_filename = src_dir / huc2 / "nhd_marine.feather"
    if marine_filename.exists():
        marine = gp.read_feather(marine_filename)
        flowlines, joins = remove_marine_flowlines(flowlines, joins, marine)
        print("------------------")

    ### Remove any flowlines that fall within or follow coastline of the Great Lakes
    if huc2 == "04":
        flowlines, joins = remove_great_lakes_flowlines(flowlines, joins, waterbodies)
        print("------------------")

    ### Drop pipelines that are > PIPELINE_MAX_LENGTH or are otherwise isolated from the network
    print("Evaluating pipelines")
    keep_ids = KEEP_PIPELINES.get(huc2, [])
    flowlines, joins = remove_pipelines(flowlines, joins, MAX_PIPELINE_LENGTH, keep_ids)
    print(f"{len(flowlines):,} flowlines after dropping pipelines")
    print("------------------")

    ### Repair disconnected subnetworks
    if huc2 == "18":
        print("Repairing disconnected subnetworks")
        next_lineID = flowlines.index.max() + np.uint32(1)
        flowlines, joins = repair_disconnected_subnetworks(
            flowlines, joins, next_lineID
        )
        print(f"{len(flowlines):,} flowlines after repairing subnetworks")
        print("------------------")

    # make sure that updated joins are unique
    joins = joins.drop_duplicates()

    ### Set intermittent status
    flowlines["intermittent"] = flowlines.FCode.isin([46003, 46007])

    ### Add altered status
    nwi = gp.read_feather(nwi_dir / huc2 / "altered_rivers.feather")
    flowlines = mark_altered_flowlines(flowlines, nwi)

    print("------------------")

    ### Cut flowlines by waterbodies
    print("Processing intersections between waterbodies and flowlines")
    next_lineID = flowlines.index.max() + np.uint32(1)
    flowlines, joins, wb_joins = cut_lines_by_waterbodies(
        flowlines, joins, waterbodies, next_lineID=next_lineID
    )

    # NOTE: we retain all waterbodies at this point, even if they don't overlap
    # flowlines.  This is because we use headwaters waterbodies to calculate drain points.

    # Fix dtypes
    joins.upstream = joins.upstream.astype("uint64")
    joins.downstream = joins.downstream.astype("uint64")
    joins.upstream_id = joins.upstream_id.astype("uint32")
    joins.downstream_id = joins.downstream_id.astype("uint32")

    # calculate stats for flowlines in waterbodies
    tmp = wb_joins.join(flowlines.geometry, on="lineID")
    tmp["length"] = shapely.length(tmp.geometry.values.data)
    tmp = tmp.groupby("wbID")["length"].sum().astype("float32").rename("flowlineLength")
    waterbodies = waterbodies.join(tmp)
    waterbodies.flowlineLength = waterbodies.flowlineLength.fillna(0)

    print(
        f"Now have {len(flowlines):,} flowlines, {len(waterbodies):,} waterbodies, {len(wb_joins):,} waterbody-flowline joins"
    )

    print("------------------")

    print("Identifying waterbody drain points")
    drains = create_drain_points(flowlines, joins, waterbodies, wb_joins)

    print("------------------")

    print("Serializing {:,} flowlines".format(len(flowlines)))
    flowlines = flowlines.reset_index()
    flowlines.to_feather(huc2_dir / "flowlines.feather")
    write_dataframe(flowlines, huc2_dir / "flowlines.fgb")
    joins.reset_index(drop=True).to_feather(huc2_dir / "flowline_joins.feather")

    print("Serializing {:,} waterbodies".format(len(waterbodies)))
    # waterbodies are losing their CRS somewhere along the way, not sure why it is failing here
    waterbodies.set_crs(flowlines.crs, inplace=True)
    waterbodies = waterbodies.reset_index()
    waterbodies.to_feather(huc2_dir / "waterbodies.feather")
    write_dataframe(waterbodies, huc2_dir / "waterbodies.fgb")
    wb_joins.reset_index(drop=True).to_feather(
        huc2_dir / "waterbody_flowline_joins.feather"
    )

    print("Serializing {:,} drain points".format(len(drains)))
    drains.to_feather(huc2_dir / "waterbody_drain_points.feather")
    write_dataframe(drains, huc2_dir / "waterbody_drain_points.fgb")

    print(
        "------------------\nRegion done in {:.2f}s\n------------------\n".format(
            time() - region_start
        )
    )

    del flowlines
    del joins
    del waterbodies
    del wb_joins

print("==============\nAll done in {:.2f}s".format(time() - start))
