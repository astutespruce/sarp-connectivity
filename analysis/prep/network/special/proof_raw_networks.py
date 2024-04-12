"""
This script builds networks from the raw flowline joins after dropping loops
to verify that flowlines do not end up in duplicate networks.

This runs on a per-region basis because that is the level where loops are recoded
to loop / nonloop manually.
"""


from pathlib import Path

import pyarrow as pa
from pyarrow.dataset import dataset
import pyarrow.compute as pc
import pandas as pd
import geopandas as gp
import numpy as np
from pyogrio import write_dataframe
import shapely

from analysis.lib.graph.speedups import DirectedGraph
from analysis.lib.geometry.lines import merge_lines
from analysis.lib.joins import find_joins
from analysis.constants import (
    CRS,
    CONVERT_TO_LOOP,
    CONVERT_TO_NONLOOP,
    REMOVE_IDS,
    MAX_PIPELINE_LENGTH,
    KEEP_PIPELINES,
    JOIN_FIXES,
    REMOVE_JOINS,
)
from analysis.lib.flowlines import (
    remove_flowlines,
    remove_pipelines,
    repair_disconnected_subnetworks,
)


data_dir = Path("data")
nhd_dir = data_dir / "nhd"
src_dir = nhd_dir / "raw"

huc2 = "18"

################################################################################
### Apply join fixes from the top of prepare_flowlines_waterbodies
################################################################################

flowlines = gp.read_feather(src_dir / huc2 / "flowlines.feather").set_index("lineID")
joins = pd.read_feather(src_dir / huc2 / "flowline_joins.feather")

# update loop status of joins, if needed
loop_ix = flowlines.loc[flowlines.loop].NHDPlusID.unique()
joins["loop"] = joins.upstream.isin(loop_ix) | joins.downstream.isin(loop_ix)

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


################################################################################
### Now proof that raw networks do not overlap
################################################################################

joins = joins.loc[~joins.loop]
flowlines = flowlines.loc[~flowlines.loop]

# find junctions (downstream_id with multiple upstream_id valeus)
num_upstreams = joins.loc[joins.downstream_id != 0].groupby("downstream_id").size()
multiple_upstreams = num_upstreams[num_upstreams > 1].index.values
joins["junction"] = joins.downstream_id.isin(multiple_upstreams)

# create a directed graph facing upstream
upstream_joins = joins.loc[(joins.downstream_id != 0) & (joins.upstream_id != 0)]
graph = DirectedGraph(
    upstream_joins["downstream_id"].values.astype("int64"),
    upstream_joins["upstream_id"].values.astype("int64"),
)

# find joins that are not marked as terminated, but do not have upstreams in the region
unterminated = joins.loc[(joins.downstream_id != 0) & ~joins.downstream_id.isin(joins.upstream_id)]

origin_idx = np.unique(
    np.concatenate(
        [
            # anything that has no downstream is an origin
            joins.loc[joins.downstream_id == 0].upstream_id.unique(),
            # if downstream_id is not in upstream_id for region, and is in flowlines, add downstream id as origin
            unterminated.loc[unterminated.downstream_id.isin(flowlines.index.values)].downstream_id.unique(),
            # otherwise add upstream id
            unterminated.loc[~unterminated.downstream_id.isin(flowlines.index.values)].upstream_id.unique(),
        ]
    )
)

print(f"Generating networks for {len(origin_idx):,} origin points")
networks = pd.DataFrame(
    graph.network_pairs(origin_idx.astype("int64")),
    columns=["networkID", "lineID"],
)


networks_at_junctions = np.intersect1d(networks.networkID.unique(), joins.loc[joins.junction].upstream_id.unique())
if len(networks_at_junctions):
    print(f"Merging multiple upstream networks at network junctions, affects {len(networks_at_junctions):,} networks")

    downstreams = joins.loc[joins.upstream_id.isin(networks_at_junctions)].downstream_id.unique()
    for downstream_id in downstreams:
        # find all the networks that have the same downstream and fuse them
        networkIDs = (
            networks.loc[networks.networkID.isin(joins.loc[joins.downstream_id == downstream_id].upstream_id)]
            .groupby("networkID")
            .size()
            .sort_values()
            .index.values
        )
        # use the networkID with longest number of segments as out networkID
        networkID = networkIDs[0]
        networks.loc[networks.networkID.isin(networkIDs), "networkID"] = networkID


### Export networks
joins["marine"] = joins.marine.fillna(False)
joins["great_lakes"] = joins.great_lakes.fillna(False)
networks["flows_to_ocean"] = networks.networkID.isin(joins.loc[joins.marine].upstream_id.unique())
networks["flows_to_great_lakes"] = networks.networkID.isin(joins.loc[joins.great_lakes].upstream_id.unique())

tmp = merge_lines(
    flowlines[["geometry"]].join(networks.reset_index().set_index("lineID"), how="inner"), by="networkID"
).join(networks.groupby("networkID")[["flows_to_ocean", "flows_to_great_lakes"]].max(), on="networkID")
write_dataframe(tmp, "/tmp/raw_networks.fgb")


### Check for duplicates
network_counts = networks.groupby("lineID").size().rename("num_networks")
dup_lineIDs = network_counts.loc[network_counts > 1]

if len(dup_lineIDs):
    print("ERROR: overlapping networks!")
    # DEBUG
    # network_counts.reset_index().to_feather("/tmp/dup_networks.feather")

    # export the flowlines that occur in multiple networks
    write_dataframe(flowlines.loc[flowlines.index.isin(dup_lineIDs.index.values)], "/tmp/dup_network_flowlines.fgb")
