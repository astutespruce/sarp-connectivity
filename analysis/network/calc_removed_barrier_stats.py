from pathlib import Path
from time import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from pyarrow.dataset import dataset

from analysis.constants import NETWORK_TYPES
from analysis.lib.graph.speedups import DirectedGraph
from analysis.lib.io import read_arrow_tables
from analysis.lib.util import append
from analysis.network.lib.networks import create_barrier_networks
from analysis.network.lib.stats import update_downstream_subnetwork_stats

BARRIER_COUNT_KINDS = [
    "waterfalls",
    "dams",
    "small_barriers",
    "road_crossings",
    "headwaters",
]

# NOTE: downstream stats are only valid to the root of the network
# containing the removed barrier, and must be summed to the downstream
# stats of that network
# Likewise, total upstream barrier stats (tot_) are only valid up to the
# top of the network containing the barrier
# For now, drop them all
DROP_COLS = [f"tot_{kind}" for kind in BARRIER_COUNT_KINDS] + [f"fn_{kind}" for kind in BARRIER_COUNT_KINDS]

DOWNSTREAM_COLS = [f"totd_{kind}" for kind in BARRIER_COUNT_KINDS[:4]] + [
    "miles_to_outlet",
    "flows_to_ocean",
    "flows_to_great_lakes",
    "exits_region",
]


data_dir = Path("data")
network_dir = data_dir / "networks"
src_dir = network_dir / "raw"
out_dir = network_dir / "clean"

network_types = list(NETWORK_TYPES.keys())

start = time()

huc2_group_df = pd.read_feather(network_dir / "connected_huc2s.feather").sort_values(by=["group", "HUC2"])
huc2_groups = huc2_group_df.groupby("group").HUC2.apply(list).tolist()
all_huc2s = huc2_group_df.HUC2.values

# read all flowline joins (limited to subnetworks later)
all_joins = read_arrow_tables(
    [src_dir / huc2 / "flowline_joins.feather" for huc2 in all_huc2s],
    columns=["downstream_id", "upstream_id", "type", "marine", "great_lakes", "junction"],
    new_fields={"HUC2": all_huc2s},
).to_pandas()

all_barriers = (
    dataset(src_dir / "all_barriers.feather", format="feather")
    .to_table(
        columns=[
            "id",
            "kind",
            "HUC2",
            "primary_network",
            "largefish_network",
            "smallfish_network",
            "removed",
            "YearRemoved",
        ],
    )
    .to_pandas()
)

# FIXME: remove after re-running prep_dams.py
all_barriers.loc[(all_barriers.YearRemoved > 0) & (all_barriers.YearRemoved < 1900), "YearRemoved"] = np.uint16(0)

# 1 represents everything < 2000 so that sorting works
all_barriers.loc[(all_barriers.YearRemoved > 0) & (all_barriers.YearRemoved < 2000), "YearRemoved"] = 1

# 9999 represents everything not removed
all_barriers.loc[~all_barriers.removed, "YearRemoved"] = 9999

removed_barriers = all_barriers.loc[all_barriers.removed]
nonremoved_barriers = all_barriers.loc[~all_barriers.removed]

# Read all barrier joins because we need non-removed barriers that overlap
# subnetworks containing removed barriers
all_barrier_joins = (
    read_arrow_tables(
        [src_dir / huc2 / "barrier_joins.feather" for huc2 in all_huc2s],
        columns=["id", "downstream_id", "upstream_id", "type", "marine", "great_lakes", "kind"],
        new_fields={"HUC2": all_huc2s},
    )
    .to_pandas()
    .set_index("id")
).join(
    all_barriers.set_index("id")[
        [
            "primary_network",
            "largefish_network",
            "smallfish_network",
            "YearRemoved",
        ]
    ]
)


# extract a non-zero lineID to join to segments in order to resolve the
# networkID of each type that contains this removed barrier
removed_barrier_joins = all_barrier_joins.loc[all_barrier_joins.index.isin(removed_barriers.id.values)].copy()
removed_barrier_joins["lineID"] = removed_barrier_joins[["downstream_id", "upstream_id"]].max(axis=1)
subnetwork_lookup = (
    read_arrow_tables(
        [out_dir / huc2 / "network_segments.feather" for huc2 in all_huc2s],
        columns=["lineID"] + network_types,
        filter=pc.is_in(pc.field("lineID"), pa.array(removed_barrier_joins.lineID.unique())),
    )
    .to_pandas()
    .set_index("lineID")
)
removed_barrier_joins = removed_barrier_joins.join(subnetwork_lookup, on="lineID").drop(columns=["lineID"])


############ IN PROGRESS: rework outer loop to be network type

for network_type in network_types:
    print(f"\n===========================\nCreating networks for {network_type}")
    network_start = time()

    breaking_kinds = NETWORK_TYPES[network_type]["kinds"]
    col = NETWORK_TYPES[network_type]["column"]
    removed_focal_barriers = removed_barriers.loc[removed_barriers.kind.isin(breaking_kinds) & removed_barriers[col]]

    if len(removed_focal_barriers) == 0:
        print(f"skipping {network_type}, no removed barriers of this type present")
        continue

    # find all subnetworks that contain removed barriers and read in associated
    # network segments
    subnetworks = (
        removed_barrier_joins.loc[removed_barrier_joins.index.isin(removed_focal_barriers.id.values)]
        .rename(columns={network_type: "subnetworkID"})
        .subnetworkID.unique()
    )

    # read in previously created networks that contain these removed barriers
    subnetwork_segments = (
        read_arrow_tables(
            [out_dir / huc2 / "network_segments.feather" for huc2 in all_huc2s],
            columns=[
                "lineID",
                "NHDPlusID",
                "intermittent",
                "altered",
                "waterbody",
                "sizeclass",
                "length",
                "AreaSqKm",
                "HUC2",
                network_type,
            ],
            filter=pc.is_in(pc.field(network_type), pa.array(subnetworks)),
        )
        .to_pandas()
        .set_index("lineID")
        .rename(columns={network_type: "subnetworkID"})
    )

    # read in previous downstream stats
    prev_stats = (
        read_arrow_tables(
            [out_dir / huc2 / f"{network_type}_network_stats.feather" for huc2 in all_huc2s],
            columns=["networkID", "barrier"] + DOWNSTREAM_COLS,
            filter=pc.is_in(pc.field("networkID"), pa.array(subnetworks)),
        )
        .to_pandas()
        .set_index("networkID")
    )

    # include only joins where upstream_id is in subnetworks or downstream is
    # within subnetwork and terminates at top of network
    subnetwork_joins = all_joins.loc[
        all_joins.upstream_id.isin(subnetwork_segments.index.values)
        | (all_joins.downstream_id.isin(subnetwork_segments.index.values) & (all_joins.upstream_id == 0))
    ]

    # FIXME: make loop
    years_removed = sorted(removed_barriers.YearRemoved.unique())
    year = years_removed[0]

    # Select any not-yet-removed barriers (YearRemoved >= year) and any non-removed
    # barriers that either join adjacent subnetworks or if they terminate on upstream
    # or downstream side
    active_removed_barriers = removed_barriers.loc[removed_barriers.YearRemoved >= year]
    active_focal_removed_barriers = active_removed_barriers.loc[
        active_removed_barriers.kind.isin(breaking_kinds) & active_removed_barriers[col]
    ]

    active_barrier_joins = all_barrier_joins.loc[
        # keep any active removed barriers regardless of position on subnetworks
        all_barrier_joins.index.isin(active_removed_barriers.id.values)
        | (
            all_barrier_joins.index.isin(nonremoved_barriers.id.values)
            & (
                # barrier joins adjacent subnetworks
                (
                    all_barrier_joins.downstream_id.isin(subnetwork_segments.index.values)
                    & all_barrier_joins.upstream_id.isin(subnetwork_segments.index.values)
                )
                # terminate on downstream side
                | (
                    (all_barrier_joins.downstream_id == 0)
                    & all_barrier_joins.upstream_id.isin(subnetwork_segments.index.values)
                )
                # terminate on upstream side
                | (
                    all_barrier_joins.downstream_id.isin(subnetwork_segments.index.values)
                    & (all_barrier_joins.upstream_id == 0)
                )
            )
        )
    ]
    active_focal_barrier_joins = active_barrier_joins.loc[
        active_barrier_joins.kind.isin(breaking_kinds) & active_barrier_joins[col]
    ]

    # FIXME: need to adjust for focal_barrier_joins including non-removed?
    # FIXME: re-enable
    # within_subnetwork_stats = (
    #     focal_barrier_joins.join(prev_stats, on="subnetworkID")[prev_stats.columns]
    #     .reset_index()
    #     .drop_duplicates(subset="id")
    #     .set_index("id")
    # )
    # # increment the count based on the type at the root of the subnetwork
    # for kind in BARRIER_COUNT_KINDS[:4]:
    #     within_subnetwork_stats.loc[within_subnetwork_stats.barrier == kind[:-1], f"totd_{kind}"] += 1

    # prev_stats = prev_stats.drop(columns=["barrier"])
    # within_subnetwork_stats = within_subnetwork_stats.drop(columns=["barrier"])

    ################
    (
        tmp_networks,
        tmp_stats,
        tmp_segments,
    ) = create_barrier_networks(
        active_focal_removed_barriers,
        active_barrier_joins,
        active_focal_barrier_joins,  # needs to include non-removed barriers that
        subnetwork_joins,
        subnetwork_segments,
        network_type,
    )
    ###########

    # ### Extract networks for barriers on isolated subnetworks
    # # these only have one barrier per subnetwork and can be calculated once
    # # up front
    # num_barriers_per_subnetwork = focal_barrier_joins.groupby("subnetworkID").size()
    # isolated_subnetworks = num_barriers_per_subnetwork[num_barriers_per_subnetwork == 1].index.values
    # isolated_barrier_ids = focal_barrier_joins.loc[
    #     focal_barrier_joins.subnetworkID.isin(isolated_subnetworks)
    # ].index.unique()

    # # TODO: accumulate results of isolated subnetworks
    # merged_networks = None
    # merged_network_stats = None
    # merged_network_segments = None

    # if len(isolated_barrier_ids) > 0:
    #     print(f"Extracting networks for {len(isolated_barrier_ids):,} barriers in isolated subnetworks")

    #     isolated_barriers = focal_barriers.loc[focal_barriers.id.isin(isolated_barrier_ids)]
    #     isolated_subnetwork_flowlines = subnetwork_segments.loc[
    #         subnetwork_segments.subnetworkID.isin(isolated_subnetworks)
    #     ]
    #     isolated_subnetwork_joins = subnetwork_joins.loc[
    #         subnetwork_joins.upstream_id.isin(isolated_subnetwork_flowlines.index.values)
    #         | subnetwork_joins.downstream_id.isin(isolated_subnetwork_flowlines.index.values)
    #     ]

    #     # FIXME: still not fusing origin networks properly
    #     (
    #         isolated_subnetwork_networks,
    #         isolated_subnetwork_stats,
    #         isolated_subnetwork_segments,
    #     ) = create_barrier_networks(
    #         isolated_barriers,
    #         all_barrier_joins_without_networks,
    #         focal_barrier_joins.loc[focal_barrier_joins.index.isin(isolated_barrier_ids)],
    #         isolated_subnetwork_joins,
    #         isolated_subnetwork_flowlines,
    #         network_type,
    #     )

    #     # join year removed
    #     isolated_subnetwork_networks = isolated_subnetwork_networks.drop(columns=DROP_COLS, errors="ignore").join(
    #         isolated_barriers.set_index("id").YearRemoved
    #     )
    #     network_by_year = pd.concat(
    #         [
    #             isolated_subnetwork_networks[["upNetID", "YearRemoved"]]
    #             .reset_index(drop=True)
    #             .rename(columns={"upNetID": "networkID"}),
    #             isolated_subnetwork_networks[["downNetID", "YearRemoved"]]
    #             .reset_index(drop=True)
    #             .rename(columns={"downNetID": "networkID"}),
    #         ]
    #     )
    #     network_by_year = network_by_year.loc[network_by_year.networkID > 0]
    #     # FIXME: this isn't working seem to be multiple barriers of different years that share the same downstream

    #     # update network stats based on previous downstream network stats
    #     isolated_subnetwork_networks, isolated_subnetwork_stats = update_downstream_subnetwork_stats(
    #         isolated_subnetwork_networks,
    #         isolated_subnetwork_stats.drop(columns=DROP_COLS, errors="ignore"),
    #         prev_stats,
    #         within_subnetwork_stats,
    #     )

    #     # TODO: accumalate these toward final results

    # ### Extract networks for subnetworks with multiple barriers
    # # these require special handling to first slice out a subset by year,
    # # then do extra accounting on barriers removed within the same year on the same subnetwork
    # # remaining_barrier_ids = np.setdiff1d(focal_barrier_joins.index.unique(), isolated_barrier_ids)

    # remaining_subnetworks = num_barriers_per_subnetwork[num_barriers_per_subnetwork > 1].index.values
    # remaining_barrier_ids = focal_barrier_joins.loc[
    #     focal_barrier_joins.subnetworkID.isin(remaining_subnetworks)
    # ].index.unique()

    # # TODO: accumulate these toward final
    # if len(remaining_barrier_ids) > 0:
    #     remaining_barriers = focal_barriers.loc[focal_barriers.id.isin(remaining_barrier_ids)]

    #     remaining_subnetwork_flowlines = subnetwork_segments.loc[
    #         subnetwork_segments.subnetworkID.isin(remaining_subnetworks)
    #     ]
    #     remaining_subnetwork_joins = subnetwork_joins.loc[
    #         subnetwork_joins.upstream_id.isin(remaining_subnetwork_flowlines.index.values)
    #         | subnetwork_joins.downstream_id.isin(remaining_subnetwork_flowlines.index.values)
    #     ]

    #     years_removed = remaining_barriers.YearRemoved.sort_values().unique()

    #     for year in years_removed:
    #         print(f"\n---------------------------\nProcessing {network_type} removed in {year}")

    #         # TODO: possible optimization, only run on subnetworks that have a barrier removed within that year

    #         # select all remaining barriers >= year
    #         active_barriers = remaining_barriers.loc[remaining_barriers.YearRemoved >= year]
    #         active_barrier_joins = focal_barrier_joins.loc[active_barriers.id.values]
    #         active_subnetworks = active_barrier_joins.subnetworkID.unique()
    #         active_flowlines = remaining_subnetwork_flowlines.loc[
    #             remaining_subnetwork_flowlines.subnetworkID.isin(active_subnetworks)
    #         ]
    #         active_joins = remaining_subnetwork_joins.loc[
    #             remaining_subnetwork_joins.upstream_id.isin(active_flowlines.index.values)
    #             | remaining_subnetwork_joins.downstream_id.isin(active_flowlines.index.values)
    #         ]

    #         # for each year, break the network at each barrier with YearRemoved >= year
    #         # but only keep those where YearRemoved == year
    #         tmp_networks, tmp_stats, tmp_segments = create_barrier_networks(
    #             active_barriers,
    #             all_barrier_joins_without_networks,
    #             active_barrier_joins,
    #             active_joins,
    #             active_flowlines,
    #             network_type,
    #         )

    #         # update network stats based on previous downstream network stats
    #         tmp_networks, tmp_stats = update_downstream_subnetwork_stats(
    #             tmp_networks.drop(columns=DROP_COLS, errors="ignore"),
    #             tmp_stats.drop(columns=DROP_COLS, errors="ignore"),
    #             prev_stats,
    #             within_subnetwork_stats,
    #         )

    #         # WARNING: there will be multiple entries for the origin networks
    #         # across different years because of varying removed barriers

    #         current_year_barriers = active_barriers.loc[active_barriers.YearRemoved == year]
    #         current_year_networks = tmp_networks.loc[current_year_barriers.id]
    #         current_year_network_ids = current_year_networks.upNetID.unique()
    #         current_year_stats = tmp_stats.loc[current_year_network_ids].drop(columns=DROP_COLS, errors="ignore")
    #         current_year_segments = tmp_segments.loc[tmp_segments[network_type].isin(current_year_network_ids)]

    #         # TODO: use upstream graph to connect current year networks


###############################################################################

# ###############
# for huc2s in huc2_groups:
#     print(f"\n===========================\nCreating networks for removed barriers in {', '.join(huc2s)}")
#     group_start = time()

#     group_barriers = barriers.loc[barriers.HUC2.isin(huc2s)]
#     if len(group_barriers) == 0:
#         print("Skipping, no removed barriers present")
#         continue

#     group_joins = joins.loc[joins.HUC2.isin(huc2s)]

# TODO: avoid adding network IDs fields to barriers
# group_barriers = group_barriers.join(group_barrier_joins[NETWORK_TYPES.keys()], on="id")

# for network_type in NETWORK_TYPES:
#     print(f"-------------------------\nCreating networks for {network_type}")
#     network_start = time()

#     breaking_kinds = NETWORK_TYPES[network_type]["kinds"]
#     col = NETWORK_TYPES[network_type]["column"]

#     focal_barrier_joins = group_barrier_joins.loc[
#         group_barrier_joins.kind.isin(breaking_kinds) & group_barrier_joins[col]
#     ]
#     if len(focal_barrier_joins) == 0:
#         print(f"skipping {network_type}, no removed barriers of this type present")
#         continue

#     # only keep the joins and segments for the subnetworks containing removed barriers
#     subnetworks = focal_barrier_joins[network_type].unique()
#     subnetwork_prev_segments = prev_segments.loc[prev_segments[network_type].isin(subnetworks)]
#     subnetwork_joins = group_joins.loc[
#         group_joins.upstream_id.isin(subnetwork_prev_segments.index.values)
#         | group_joins.downstream_id.isin(subnetwork_prev_segments.index.values)
#     ]

#     # read in previous downstream stats
#     prev_stats = (
#         read_arrow_tables(
#             [out_dir / huc2 / f"{network_type}_network_stats.feather" for huc2 in huc2s],
#             columns=["networkID", "barrier"] + DOWNSTREAM_COLS,
#             filter=pc.is_in(pc.field("networkID"), pa.array(subnetworks)),
#         )
#         .to_pandas()
#         .set_index("networkID")
#     )

#     within_subnetwork_stats = (
#         focal_barrier_joins.join(prev_stats, on=network_type)[prev_stats.columns]
#         .reset_index()
#         .drop_duplicates(subset="id")
#         .set_index("id")
#     )
#     # increment the count based on the type at the root of the subnetwork
#     for kind in BARRIER_COUNT_KINDS[:4]:
#         within_subnetwork_stats.loc[within_subnetwork_stats.barrier == kind[:-1], f"totd_{kind}"] += 1

#     prev_stats = prev_stats.drop(columns=["barrier"])
#     within_subnetwork_stats = within_subnetwork_stats.drop(columns=["barrier"])

#######################################
# for barriers on the same subnetwork in the same year, ordinate them from upstream to downstream
# calculate network for furthest upstream, then remove it
# next downstream claims that same network (as if the one upstream had already been removed)
# furthest dowstream claims all the networks upstream in subnetwork
# this means that there will be multiple network IDs per segment
# this enables each barrier in the series to get a better miles gained metric
# simplification: one we have starting line IDs in joins, can remove all
# other barrier joins in same year since we are moving in the upstream direction

#######################################

############### rework below

# ### Extract networks for barriers on isolated subnetworks
# # these only have one barrier per subnetwork and can be calculated once
# # up front
# num_barriers_per_subnetwork = focal_barrier_joins.groupby(network_type).size()

# isolated_barrier_ids = focal_barrier_joins.loc[
#     focal_barrier_joins[network_type].isin(
#         num_barriers_per_subnetwork[num_barriers_per_subnetwork == 1].index.values
#     )
# ].index.unique()

# if len(isolated_barrier_ids) > 0:
#     isolated_barriers = group_barriers.loc[group_barriers.id.isin(isolated_barrier_ids)]
#     isolated_subnetworks = isolated_barriers[network_type].unique()

#     isolated_subnetwork_flowlines = subnetwork_prev_segments.loc[
#         subnetwork_prev_segments[network_type].isin(isolated_subnetworks)
#     ].drop(columns=NETWORK_TYPES.keys(), errors="ignore")
#     isolated_subnetwork_joins = group_joins.loc[
#         group_joins.upstream_id.isin(isolated_subnetwork_flowlines.index.values)
#         | group_joins.downstream_id.isin(isolated_subnetwork_flowlines.index.values)
#     ].copy()

#     print("Extracting networks for barriers in isolated subnetworks")
#     (
#         isolated_barrier_networks,
#         isolated_subnetwork_stats,
#         isolated_subnetwork_segments,
#     ) = create_barrier_networks(
#         isolated_barriers,
#         barrier_joins.drop(columns=NETWORK_TYPES.keys()),
#         focal_barrier_joins.loc[focal_barrier_joins.index.isin(isolated_barrier_ids)].drop(
#             columns=NETWORK_TYPES.keys()
#         ),
#         isolated_subnetwork_joins,
#         isolated_subnetwork_flowlines,
#         network_type,
#     )

#     isolated_barrier_networks = isolated_barrier_networks.drop(columns=DROP_COLS, errors="ignore").join(
#         group_barriers.set_index("id").YearRemoved
#     )

#     # update network stats based on previous downstream network stats
#     isolated_subnetwork_stats = isolated_subnetwork_stats.drop(columns=DROP_COLS, errors="ignore")

#     # bring in previous downstream stats on the bottom networks in this
#     # subnetwork
#     origin_network_stats = isolated_subnetwork_stats.drop(columns=prev_stats.columns).join(
#         prev_stats, how="inner"
#     )

#     # update network stats for barriers in this subnetwork based on within
#     # network stats
#     barrier_network_stats = isolated_subnetwork_stats.join(
#         within_subnetwork_stats.join(isolated_barrier_networks.upNetID.rename("networkID")).set_index(
#             "networkID"
#         ),
#         how="inner",
#         rsuffix="_prev",
#     )

#     for col in within_subnetwork_stats.columns:
#         if barrier_network_stats[col].dtype == "bool":
#             barrier_network_stats[col] = barrier_network_stats[f"{col}_prev"]
#         else:
#             # increment based on the type of barrier at the root of the subnetwork
#             barrier_network_stats[col] += barrier_network_stats[f"{col}_prev"]

#     barrier_network_stats = barrier_network_stats.drop(
#         columns=[c for c in barrier_network_stats.columns if c.endswith("_prev")]
#     )

#     isolated_subnetwork_stats = pd.concat(
#         [
#             origin_network_stats.reset_index(),
#             barrier_network_stats.reset_index(),
#         ],
#         ignore_index=True,
#     ).set_index("networkID")

# ### Extract networks for subnetworks with multiple barriers
# # these require special handling to first slice out a subset by year,
# # then do extra accounting on barriers removed within the same year on the same subnetwork
# remaining_barrier_ids = np.setdiff1d(focal_barrier_joins.index.unique(), isolated_barrier_ids)
# remaining_barriers = group_barriers.join(
#     focal_barrier_joins.loc[focal_barrier_joins.index.isin(remaining_barrier_ids), network_type],
#     on="id",
#     how="inner",
# )
# # TODO: extract subset of prev_segments
# remaining_subnetworks = remaining_barriers[network_type].unique()
# remaining_subnetwork_flowlines = subnetwork_flowlines.loc[
#     prev_segments[network_type].isin(remaining_subnetworks)
# ]
# remaining_subnetwork_joins = group_joins.loc[
#     group_joins.upstream_id.isin(remaining_subnetwork_flowlines.index.values)
#     | group_joins.downstream_id.isin(remaining_subnetwork_flowlines.index.values)
# ].copy()

# years_removed = remaining_barriers.YearRemoved.sort_values().unique()

# for year in years_removed:
#     print(f"\n---------------------------\nProcessing {network_type} removed in {year}")

#     # select all remaining barriers >= year
#     active_barriers = remaining_barriers.loc[remaining_barriers.YearRemoved >= year]
#     active_barrier_joins = focal_barrier_joins.loc[active_barriers.id.values].drop(
#         columns=NETWORK_TYPES.keys(), errors="ignore"
#     )
#     active_subnetworks = active_barriers[network_type].unique()
#     active_flowlines = remaining_subnetwork_flowlines.loc[prev_segments[network_type].isin(active_subnetworks)]
#     remaining_subnetwork_joins = group_joins.loc[
#         group_joins.upstream_id.isin(remaining_subnetwork_flowlines.index.values)
#         | group_joins.downstream_id.isin(remaining_subnetwork_flowlines.index.values)
#     ].copy()

#     # TODO: limit subnetwork joins to those that have barriers still present

#     # for each year, break the network at each barrier with YearRemoved >= year
#     # but only keep those where YearRemoved == year
#     tmp_networks, tmp_stats, tmp_segments = create_barrier_networks(
#         active_barriers,
#         barrier_joins.loc[active_barriers.id.values].drop(columns=NETWORK_TYPES.keys(), errors="ignore"),
#         active_barrier_joins,
#         remaining_subnetwork_joins,
#         remaining_subnetwork_flowlines,
#         network_type,
#     )

#     tmp_networks = tmp_networks.drop(columns=DROP_COLS, errors="ignore").join(
#         active_barriers.set_index("id")[["YearRemoved", network_type]].rename(
#             columns={network_type: "subnetwork"}
#         )
#     )

#     current_year_networks = tmp_networks.loc[tmp_networks.YearRemoved == year]
#     current_year_network_ids = current_year_networks.upNetID.unique()
#     current_year_stats = tmp_stats.loc[current_year_network_ids].drop(columns=DROP_COLS, errors="ignore")
#     current_year_segments = tmp_segments.loc[tmp_segments[network_type].isin(current_year_network_ids)]

#     # TODO: use upstream graph to connect current year networks

#     # create series of networkID indexed by lineID
#     networkID = current_year_segments[network_type].rename("networkID")
#     networkIDs = pd.Series(networkID.unique(), name="networkID")

#     active_network_joins = (
#         active_barrier_joins.loc[
#             (active_barrier_joins.upstream_id != 0) & (active_barrier_joins.downstream_id != 0)
#         ]
#         .join(networkID, on="downstream_id")
#         .rename(
#             columns={
#                 "networkID": "downstream_network",
#                 "upstream_id": "upstream_network",
#             }
#         )[["upstream_network", "downstream_network", "kind"]]
#     ).dropna()

#     upstream_graph = DirectedGraph(
#         active_network_joins.downstream_network.values.astype("int64"),
#         active_network_joins.upstream_network.values.astype("int64"),
#     )
#     upstreams = (
#         pd.Series(
#             upstream_graph.descendants(networkIDs.values.astype("int64")),
#             index=networkIDs,
#             name="upstream_network",
#         )
#         .explode()
#         .dropna()
#     )

# TODO: bring in origin network for downstream end of subnetwork

# TODO: for barriers removed in current year, aggregate networks
# facing upstream and deduct upstream gain miles if using upstream
# side

# TODO: bring back in floodplain KM

############### rework above

# FIXME:
# years_removed = barrier_networks.YearRemoved.sort_values().unique()

# # can start from any that are in year >0 or are not on the same original network
# s = focal_barrier_joins.groupby(network_type).size()
# isolated_ids = focal_barrier_joins.loc[focal_barrier_joins[network_type].isin(s[s == 1].index.values)].index
# barrier_networks_by_year = barrier_networks.loc[
#     (barrier_networks.YearRemoved == years_removed[0]) | barrier_networks.index.isin(isolated_ids)
# ].reset_index()

# # calculate remaining years to remove after removing first year and
# # isolated removed barriers

# years_removed = (
#     barrier_networks.loc[~barrier_networks.index.isin(barrier_networks_by_year.id.values)]
#     .YearRemoved.sort_values()
#     .unique()
# )

#     for year in years_removed:
#         print(f"\n---------------------------\nProcessing {network_type} removed in {year}")

#         # exclude any focal_barrier_joins that have already been evaluated
#         # NOTE: this intentionally reuses the subnetwork joins / flowlines
#         # from above
#         barrier_networks = (
#             create_barrier_networks(
#                 group_barriers.loc[~group_barriers.id.isin(barrier_networks_by_year.id.values)],
#                 barrier_joins.loc[~barrier_joins.index.isin(barrier_networks_by_year.id.values)].drop(
#                     columns=NETWORK_TYPES.keys()
#                 ),
#                 focal_barrier_joins.loc[~focal_barrier_joins.index.isin(barrier_networks_by_year.id.values)].drop(
#                     columns=NETWORK_TYPES.keys()
#                 ),
#                 subnetwork_joins,
#                 subnetwork_flowlines,
#                 network_type,
#             )[0]
#             .drop(columns=DROP_COLS, errors="ignore")
#             .join(group_barriers.set_index("id").YearRemoved)
#         )

#         # add in barriers removed in this year; their stats reflect that any
#         # previously-removed barriers have been removed
#         barrier_networks_by_year = append(
#             barrier_networks_by_year,
#             barrier_networks.loc[barrier_networks.YearRemoved == year].reset_index(),
#         )

#     barrier_networks = barrier_networks_by_year

#     # join back in effective gain miles
#     barrier_networks = barrier_networks.join(
#         effective_gains,
#         on="id",
#     )

#     # update barrier networks based on previous downstream network stats
#     barrier_networks = barrier_networks.join(
#         within_subnetwork_stats,
#         on="id",
#         rsuffix="_prev",
#     )
#     for col in within_subnetwork_stats.columns:
#         if barrier_networks[col].dtype == "bool":
#             barrier_networks[col] = barrier_networks[f"{col}_prev"]
#         else:
#             # increment based on the type of barrier at the root of the subnetwork
#             barrier_networks[col] += barrier_networks[f"{col}_prev"]

#     barrier_networks = barrier_networks.drop(columns=[c for c in barrier_networks.columns if c.endswith("_prev")])

#     # save barriers by the HUC2 where they are located
#     for huc2 in huc2s:
#         tmp = (
#             barrier_networks.loc[barrier_networks.HUC2 == huc2]
#             .reset_index(drop=True)
#             .to_feather(out_dir / huc2 / f"removed_{network_type}_network.feather")
#         )

# print("-------------------------\n")

# s = flowlines.groupby(level=0).size()
# if (s > 1).sum():
#     print("dups", s[s > 1])

# # all flowlines without networks marked -1
# for network_type in NETWORK_TYPES:
#     flowlines[network_type] = flowlines[network_type].fillna(-1).astype("int64")

# # drop any that weren't assigned any networks; these were selected because
# # they were part of a network that contained a given barrier but network
# # was for a different type (e.g., large dams network, but only evaluted
# # small part of it for a removed small_barrier)

# flowlines = flowlines.loc[flowlines[list(NETWORK_TYPES)].max(axis=1) > -1]

# # save network segments in the HUC2 where they are located
# print("Serializing network segments")
# for huc2 in huc2s:
#     flowlines.loc[flowlines.HUC2 == huc2].reset_index().to_feather(
#         out_dir / huc2 / "removed_barriers_network_segments.feather"
#     )

# print(f"group done in {time() - group_start:.2f}s\n\n")


print(f"All done in {time() - start:.2f}s")
