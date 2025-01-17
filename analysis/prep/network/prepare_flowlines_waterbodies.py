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
import pyarrow.compute as pc
import shapely
from pyogrio import write_dataframe


from analysis.constants import (
    CONVERT_TO_LOOP,
    CONVERT_TO_NONLOOP,
    CONVERT_TO_MARINE,
    CONVERT_TO_FLOW_INTO_GREAT_LAKES,
    REMOVE_IDS,
    MAX_PIPELINE_LENGTH,
    KEEP_PIPELINES,
    JOIN_FIXES,
    REMOVE_JOINS,
    COASTAL_HUC2,
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
from analysis.lib.graph.speedups import DirectedGraph
from analysis.lib.io import read_arrow_tables
from analysis.prep.network.lib.drains import create_drain_points


data_dir = Path("data")
nhd_dir = data_dir / "nhd"
src_dir = nhd_dir / "raw"
nwi_dir = data_dir / "nwi/raw"
waterbodies_dir = data_dir / "waterbodies"
wetlands_dir = data_dir / "wetlands"
out_dir = nhd_dir / "clean"

huc2s = sorted(pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"]).HUC2.values)
# manually subset keys from above for processing
# huc2s = [
#     "01",
#     "02",
#     "03",
#     "04",
#     "05",
#     "06",
#     "07",
#     "08",
#     "09",
#     "10",
#     "11",
#     "12",
#     "13",
#     "14",
#     "15",
#     "16",
#     "17",
#     "18",
#     "19",
#     "20",
#     "21",
# ]


start = time()

marine = None
if len(COASTAL_HUC2.intersection(huc2s)):
    marine = gp.read_feather(nhd_dir / "merged/nhd_marine.feather", columns=["geometry"])

for huc2 in huc2s:
    region_start = time()

    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2
    huc2_dir.mkdir(exist_ok=True, parents=True)

    print("Reading flowlines...")
    flowlines = gp.read_feather(src_dir / huc2 / "flowlines.feather").set_index("lineID")
    joins = pd.read_feather(src_dir / huc2 / "flowline_joins.feather")

    # update loop status of joins, if needed
    loop_ix = flowlines.loc[flowlines.loop].NHDPlusID.unique()
    joins["loop"] = joins.upstream.isin(loop_ix) | joins.downstream.isin(loop_ix)

    print(f"Read {len(flowlines):,} flowlines")

    waterbodies = gp.read_feather(waterbodies_dir / huc2 / "waterbodies.feather").set_index("wbID")
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
            ix = (joins.upstream == fix["upstream"]) & (joins.downstream == fix["downstream"])
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
            ix = (joins.upstream == entry["upstream"]) & (joins.downstream == entry["downstream"])
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
        # a join is a loop if either end is a loop
        joins.loc[
            joins.upstream.isin(convert_ids) | joins.downstream.isin(convert_ids),
            "loop",
        ] = True
        print("------------------")

    ### Fix segments that should not have been coded as loops
    convert_ids = CONVERT_TO_NONLOOP.get(huc2, [])
    if convert_ids:
        print(f"Converting {len(convert_ids):,} loops to non-loops")
        flowlines.loc[flowlines.NHDPlusID.isin(convert_ids), "loop"] = False

        # only set loop as False if neither upstream nor downstream are loops
        loop_ix = flowlines.loc[flowlines.loop].NHDPlusID.unique()
        joins.loc[
            (joins.upstream.isin(convert_ids) | joins.downstream.isin(convert_ids))
            & (~(joins.upstream.isin(loop_ix) | (joins.downstream.isin(loop_ix)))),
            "loop",
        ] = False
        print("------------------")

    ### Fix joins that should have been marked as marine
    marine_ids = CONVERT_TO_MARINE.get(huc2, [])
    if marine_ids:
        print(f"Converting {len(marine_ids):,} joins to marine")
        joins.loc[joins.upstream.isin(marine_ids), "marine"] = True
        print("------------------")

    ### Remove any flowlines that start in marine areas
    if huc2 in COASTAL_HUC2:
        flowlines, joins = remove_marine_flowlines(flowlines, joins, marine)
        print("------------------")

    ### Remove any flowlines that fall within or follow coastline of the Great Lakes
    # and mark those that terminate in Great Lakes
    if huc2 == "04":
        # cleanup dangling joins from outside the region; no other regions are
        # connected within this dataset (they come from Canada)
        drop_ix = (joins.type == "huc_in") & (joins.downstream == 0) & (~joins.upstream.isin(flowlines.NHDPlusID))
        joins = joins.loc[~drop_ix].copy()

        flowlines, joins = remove_great_lakes_flowlines(flowlines, joins, waterbodies)
        print("------------------")

    ### Fix joins that should have been marked as great_lakes
    great_lakes_ids = CONVERT_TO_FLOW_INTO_GREAT_LAKES.get(huc2, [])
    if great_lakes_ids:
        print(f"Converting {len(great_lakes_ids):,} joins to marine")
        joins.loc[joins.upstream.isin(great_lakes_ids), "great_lakes"] = True
        print("------------------")

    if "great_lakes" not in joins:
        joins["great_lakes"] = False

    joins["great_lakes"] = joins.great_lakes.fillna(0).astype("bool")

    ### Drop pipelines that are > PIPELINE_MAX_LENGTH or are otherwise isolated from the network
    print("Evaluating pipelines & undeground connectors")
    keep_ids = KEEP_PIPELINES.get(huc2, [])
    flowlines, joins = remove_pipelines(flowlines, joins, MAX_PIPELINE_LENGTH, keep_ids)
    print(f"{len(flowlines):,} flowlines after dropping pipelines & underground connectors")
    print("------------------")

    ### Repair disconnected subnetworks
    if huc2 == "18":
        print("Repairing disconnected subnetworks")
        next_lineID = flowlines.index.max() + np.uint32(1)
        flowlines, joins = repair_disconnected_subnetworks(flowlines, joins, next_lineID)
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

    cut_waterbodies = waterbodies
    if huc2 == "04":
        # exclude Great Lakes since they are evaluated above and they generate
        # a lot of unnecessary intersections and they make the crosses predicate
        # take a very long time
        cut_waterbodies = waterbodies.loc[waterbodies.km2 < 8000]

    next_lineID = flowlines.index.max() + np.uint32(1)
    flowlines, joins, wb_joins = cut_lines_by_waterbodies(flowlines, joins, cut_waterbodies, next_lineID=next_lineID)

    # NOTE: we retain all waterbodies at this point, even if they don't overlap
    # flowlines.  This is because we use headwaters waterbodies to calculate drain points.

    # Fix dtypes
    joins.upstream = joins.upstream.astype("uint64")
    joins.downstream = joins.downstream.astype("uint64")
    joins.upstream_id = joins.upstream_id.astype("uint32")
    joins.downstream_id = joins.downstream_id.astype("uint32")

    # calculate stats for flowlines in waterbodies
    tmp = wb_joins.join(flowlines.geometry, on="lineID")
    tmp["length"] = shapely.length(tmp.geometry.values)
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
    waterbodies.set_crs(flowlines.crs, inplace=True, allow_override=True)
    waterbodies = waterbodies.reset_index()
    waterbodies.to_feather(huc2_dir / "waterbodies.feather")
    write_dataframe(waterbodies, huc2_dir / "waterbodies.fgb")
    wb_joins.reset_index(drop=True).to_feather(huc2_dir / "waterbody_flowline_joins.feather")

    print("Serializing {:,} drain points".format(len(drains)))
    drains.to_feather(huc2_dir / "waterbody_drain_points.feather")
    write_dataframe(drains, huc2_dir / "waterbody_drain_points.fgb")

    print("------------------\nRegion done in {:.2f}s\n------------------\n".format(time() - region_start))

    del flowlines
    del joins
    del waterbodies
    del wb_joins


##########################################################################################
### Identify all flowlines that are part of networks that connect to marine or Great Lakes
### IMPORTANT: this is done after all of the above because joins need to be clean
### and marine / Great Lakes joins need to be correctly identified
###
### NOTE: for now, this excludes all loops because those ultimately break the
### networks when doing network analysis.  However, long term these differences
### should be analyzed because subnetworks that are marine-connected when including
### loops and are not marine-connected when excluding loops (and are not themselves loops)
### likely indicate miscoded loops
##########################################################################################

all_joins = read_arrow_tables(
    [out_dir / huc2 / "flowline_joins.feather" for huc2 in huc2s],
    columns=["upstream", "downstream", "marine", "great_lakes", "type", "loop"],
    new_fields={"HUC2": huc2s},
    filter=(
        (pc.field("upstream") != 0)
        # make sure to break at loops or we get a mismatch in the network analysis
        & (pc.field("loop") == False)  # noqa: E712
        # drop any joins that were added when cutting original flowlines by waterbodies
        & (pc.field("upstream") != pc.field("downstream"))
    ),
).to_pandas()

# for any flowlines that co-occur in adjacent huc2s, make sure they are
# consistently marked for marine and Great Lakes
for col in ["upstream", "downstream"]:
    marine_ids = all_joins.loc[all_joins.marine & (all_joins[col] != 0), col].unique()
    all_joins.loc[all_joins[col].isin(marine_ids) & (~all_joins.marine), "marine"] = True

    great_lake_ids = all_joins.loc[all_joins.great_lakes & (all_joins[col] != 0), col].unique()
    all_joins.loc[all_joins[col].isin(great_lake_ids) & (~all_joins.great_lakes), "great_lakes"] = True

# drop any terminals that are also incoming from the adjacent HUC2
incoming = all_joins.loc[all_joins.type == "huc_in"].upstream.unique()
drop_ix = all_joins.upstream.isin(incoming) & (all_joins.downstream == 0)
all_joins = all_joins.loc[~drop_ix].copy()


# only need to keep joins at level of NHD flowlines
all_joins = all_joins.drop_duplicates(subset=["upstream", "downstream", "marine", "great_lakes"])

# create a directed graph facing upstream; loops are OK because we use a check
# against nodes seen from any starting point
graph = DirectedGraph(all_joins.downstream.values.astype("int64"), all_joins.upstream.values.astype("int64"))

### find any that start from marine areas
marine_huc2 = sorted(all_joins.loc[all_joins.marine].HUC2.unique())

marine_ids = None
for huc2 in marine_huc2:
    print(f"Processing marine networks that start from {huc2}...")

    origins = all_joins.loc[
        (all_joins.HUC2 == huc2) & all_joins.marine & ~all_joins.downstream.isin(all_joins.upstream.unique())
    ].upstream.unique()
    networks = graph.network_pairs_global(origins.astype("int64"))
    networks = pd.DataFrame(networks, columns=["networkID", "NHDPlusID"])

    if marine_ids is None:
        marine_ids = networks.NHDPlusID.values
    else:
        marine_ids = np.concatenate([marine_ids, networks.NHDPlusID.values])

pd.DataFrame({"NHDPlusID": marine_ids}).to_feather(out_dir / "all_marine_flowlines.feather")


# raise a flag if there are any orphaned networks that claim to be marine-connected
# but their downstream terminal is not itself marine
tmp = all_joins.loc[(all_joins.downstream == 0) & (~all_joins.marine) & all_joins.upstream.isin(marine_ids)]
if len(tmp):
    tmp.to_feather("/tmp/problem_marine_joins.feather")
    raise ValueError(
        f"Found {len(tmp):,} downstream terminals of marine-connected networks that are not themselves marine; these indicate orphan subnetworks"
    )


# find any that start from the Great Lakes
great_lakes_huc2 = sorted(all_joins.loc[all_joins.great_lakes].HUC2.unique())

great_lake_ids = None
for huc2 in great_lakes_huc2:
    print(f"Processing Great Lakes networks that start from {huc2}...")

    origins = all_joins.loc[
        (all_joins.HUC2 == huc2) & all_joins.great_lakes & ~all_joins.downstream.isin(all_joins.upstream.unique())
    ].upstream.unique()
    networks = graph.network_pairs_global(origins.astype("int64"))
    networks = pd.DataFrame(networks, columns=["networkID", "NHDPlusID"])

    if great_lake_ids is None:
        great_lake_ids = networks.NHDPlusID.values
    else:
        great_lake_ids = np.concatenate([great_lake_ids, networks.NHDPlusID.values])

pd.DataFrame({"NHDPlusID": great_lake_ids}).to_feather(out_dir / "all_great_lakes_flowlines.feather")


# raise a flag if there are any orphaned networks that claim to be Great-Lakes-connected
# but their downstream terminal is not itself marine or in the Great Lakes
# NOTE: some of the terminals in this region are collected to marine
tmp = all_joins.loc[
    (all_joins.downstream == 0)
    & (~(all_joins.great_lakes | all_joins.marine))
    & all_joins.upstream.isin(great_lake_ids)
]
if len(tmp):
    tmp.to_feather("/tmp/problem_great_lakes_joins.feather")
    raise ValueError(
        f"Found {len(tmp):,} downstream terminals of Great Lakes-connected networks that are not themselves connected directly to the Great Lakes; these indicate orphan subnetworks"
    )


print("==============\nAll done in {:.2f}s".format(time() - start))
