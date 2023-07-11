from pathlib import Path
from time import time

import numpy as np
import pandas as pd

from analysis.constants import NETWORK_TYPES
from analysis.lib.io import read_feathers
from analysis.lib.util import append
from analysis.network.lib.networks import create_barrier_networks

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
DROP_COLS = (
    [f"tot_{kind}" for kind in BARRIER_COUNT_KINDS]
    + [f"fn_{kind}" for kind in BARRIER_COUNT_KINDS]
    + [
        # FIXME: temporary until run_network_analysis.py completely rerun; then can
        # be removed since the cat_* stats will no longer be present
        f"cat_{kind}"
        for kind in BARRIER_COUNT_KINDS
    ]
)


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


start = time()

huc2_groups = (
    pd.read_feather(network_dir / "connected_huc2s.feather")
    .groupby("group")
    .HUC2.apply(set)
    .values
)

barriers = pd.read_feather(
    src_dir / "all_barriers.feather",
    columns=["id", "kind", "intermittent", "HUC2", "loop", "removed", "YearRemoved"],
)
# extract removed barriers, dropping any on loops (will be off-network)
barriers = barriers.loc[barriers.removed & (~barriers.loop)]

# Lump together YearRemoved < 2000 with baseline
barriers.loc[barriers.YearRemoved < 2000, "YearRemoved"] = 0


for group in huc2_groups:
    group_start = time()

    group_huc2s = sorted(group)
    group_barriers = barriers.loc[barriers.HUC2.isin(group)]

    print(
        f"\n===========================\nCreating networks for removed barriers in {', '.join(group_huc2s)}"
    )

    if len(group_barriers) == 0:
        print("Skipping, no removed barriers present")
        continue

    # reuse previous network segments
    prev_segments = read_feathers(
        [out_dir / huc2 / "network_segments.feather" for huc2 in group_huc2s],
    ).set_index("lineID")

    group_joins = read_feathers(
        [src_dir / huc2 / "flowline_joins.feather" for huc2 in group],
        columns=["downstream_id", "upstream_id", "type", "marine", "great_lakes"],
    )

    # only keep barrier joins for removed barriers
    barrier_joins = (
        read_feathers(
            [src_dir / huc2 / "barrier_joins.feather" for huc2 in group_huc2s],
            new_fields={"HUC2": group_huc2s},
        )
        .set_index("id")
        .join(barriers.set_index("id").YearRemoved, how="inner")
    )

    # extract a non-zero lineID to join to segments in order to resolve the
    # networkID of a given type that contains this removed barrier
    barrier_joins["lineID"] = barrier_joins[["downstream_id", "upstream_id"]].max(
        axis=1
    )

    # add networkID columns for each network type
    barrier_joins = barrier_joins.join(
        prev_segments[NETWORK_TYPES.keys()],
        on="lineID",
    ).drop(columns=["lineID"])

    # extract flowlines that are present in any of the network types
    ids = []
    for network_type in NETWORK_TYPES:
        ids = np.append(
            ids,
            prev_segments.loc[
                prev_segments[network_type].isin(barrier_joins[network_type].unique())
            ].index.values,
        )

    flowlines = prev_segments.loc[prev_segments.index.isin(np.unique(ids))].drop(
        columns=NETWORK_TYPES
    )

    for network_type, breaking_kinds in NETWORK_TYPES.items():
        print(f"-------------------------\nCreating networks for {network_type}")
        network_start = time()

        focal_barrier_joins = barrier_joins.loc[barrier_joins.kind.isin(breaking_kinds)]

        if len(focal_barrier_joins) == 0:
            print(f"skipping {network_type}, no removed barriers of this type present")
            flowlines[network_type] = np.nan
            continue

        # read in previous downstream stats
        prev_stats = read_feathers(
            [
                out_dir / huc2 / f"{network_type}_network_stats.feather"
                for huc2 in group_huc2s
            ],
            columns=["networkID", "barrier"] + DOWNSTREAM_COLS,
        ).set_index("networkID")

        prev_stats = prev_stats.loc[
            prev_stats.index.isin(barrier_joins[network_type].unique())
        ]

        within_subnetwork_stats = (
            focal_barrier_joins.join(prev_stats, on=network_type)[prev_stats.columns]
            .reset_index()
            .drop_duplicates(subset="id")
            .set_index("id")
        )
        # increment the count based on the type at the root of the subnetwork
        for kind in BARRIER_COUNT_KINDS[:4]:
            within_subnetwork_stats.loc[
                within_subnetwork_stats.barrier == kind[:-1], f"totd_{kind}"
            ] += 1

        prev_stats = prev_stats.drop(columns=["barrier"])
        within_subnetwork_stats = within_subnetwork_stats.drop(columns=["barrier"])

        # only keep the joins and segments for the subnetworks containing removed barriers
        subnetwork_flowlines = prev_segments.loc[
            prev_segments[network_type].isin(focal_barrier_joins[network_type].unique())
        ].drop(columns=NETWORK_TYPES)
        lineIDs = subnetwork_flowlines.index.values
        subnetwork_joins = group_joins.loc[
            group_joins.upstream_id.isin(lineIDs)
            | group_joins.downstream_id.isin(lineIDs)
        ].copy()

        barrier_networks, network_stats, network_segments = create_barrier_networks(
            group_barriers,
            barrier_joins.drop(columns=NETWORK_TYPES.keys()),
            focal_barrier_joins.drop(columns=NETWORK_TYPES.keys()),
            subnetwork_joins,
            subnetwork_flowlines,
            network_type,
        )

        # save networkID to flowlines
        flowlines = flowlines.join(network_segments[network_type])

        barrier_networks = barrier_networks.drop(
            columns=DROP_COLS, errors="ignore"
        ).join(group_barriers.set_index("id").YearRemoved)

        # update network stats based on previous downstream network stats
        network_stats = network_stats.drop(columns=DROP_COLS, errors="ignore")

        # bring in previous downstream stats on the bottom networks in this
        # subnetwork
        origin_network_stats = network_stats.drop(columns=prev_stats.columns).join(
            prev_stats, how="inner"
        )

        # update network stats for barriers in this subnetwork based on within
        # network stats
        barrier_network_stats = network_stats.join(
            within_subnetwork_stats.join(
                barrier_networks.upNetID.rename("networkID")
            ).set_index("networkID"),
            how="inner",
            rsuffix="_prev",
        )

        for col in within_subnetwork_stats.columns:
            if barrier_network_stats[col].dtype == "bool":
                barrier_network_stats[col] = barrier_network_stats[f"{col}_prev"]
            else:
                # increment based on the type of barrier at the root of the subnetwork
                barrier_network_stats[col] += barrier_network_stats[f"{col}_prev"]

        barrier_network_stats = barrier_network_stats.drop(
            columns=[c for c in barrier_network_stats.columns if c.endswith("_prev")]
        )

        network_stats = pd.concat(
            [
                origin_network_stats.reset_index(),
                barrier_network_stats.reset_index(),
            ],
            ignore_index=True,
        ).set_index("networkID")

        # save network stats to the HUC2 where the network originates
        # NOTE: these stats only apply to networks cut by all removed barriers
        for huc2 in sorted(network_stats.origin_HUC2.unique()):
            network_stats.loc[
                network_stats.origin_HUC2 == huc2
            ].reset_index().to_feather(
                out_dir / huc2 / f"removed_{network_type}_network_stats.feather"
            )

        # save a version cut by all barriers at the same time
        effective_gains = barrier_networks[["GainMiles", "PerennialGainMiles"]].rename(
            columns={
                "GainMiles": "EffectiveGainMiles",
                "PerennialGainMiles": "EffectivePerennialGainMiles",
            }
        )

        years_removed = barrier_networks.YearRemoved.sort_values().unique()

        # can start from any that are in year 1 or are not on the same original network
        s = focal_barrier_joins.groupby(network_type).size()
        isolated_ids = focal_barrier_joins.loc[
            focal_barrier_joins[network_type].isin(s[s == 1].index.values)
        ].index
        barrier_networks_by_year = barrier_networks.loc[
            (barrier_networks.YearRemoved == years_removed[0])
            | barrier_networks.index.isin(isolated_ids)
        ].reset_index()

        # calculate remaining years to remove after removing first year and
        # isolated removed barriers
        years_removed = (
            barrier_networks.loc[
                ~barrier_networks.index.isin(barrier_networks_by_year.id.values)
            ]
            .YearRemoved.sort_values()
            .unique()
        )

        for year in years_removed:
            print(
                f"\n---------------------------\nProcessing {network_type} removed in {year}"
            )

            # exclude any focal_barrier_joins that have already been evaluated
            # NOTE: this intentionally reuses the subnetwork joins / flowlines
            # from above
            barrier_networks = (
                create_barrier_networks(
                    group_barriers.loc[
                        ~group_barriers.id.isin(barrier_networks_by_year.id.values)
                    ],
                    barrier_joins.loc[
                        ~barrier_joins.index.isin(barrier_networks_by_year.id.values)
                    ].drop(columns=NETWORK_TYPES.keys()),
                    focal_barrier_joins.loc[
                        ~focal_barrier_joins.index.isin(
                            barrier_networks_by_year.id.values
                        )
                    ].drop(columns=NETWORK_TYPES.keys()),
                    subnetwork_joins,
                    subnetwork_flowlines,
                    network_type,
                )[0]
                .drop(columns=DROP_COLS, errors="ignore")
                .join(group_barriers.set_index("id").YearRemoved)
            )

            # add in barriers removed in this year; their stats reflect that any
            # previously-removed barriers have been removed
            barrier_networks_by_year = append(
                barrier_networks_by_year,
                barrier_networks.loc[
                    barrier_networks.YearRemoved == year
                ].reset_index(),
            )

        barrier_networks = barrier_networks_by_year

        # join back in effective gain miles
        barrier_networks = barrier_networks.join(
            effective_gains,
            on="id",
        )

        # update barrier networks based on previous downstream network stats
        barrier_networks = barrier_networks.join(
            within_subnetwork_stats,
            on="id",
            rsuffix="_prev",
        )
        for col in within_subnetwork_stats.columns:
            if barrier_networks[col].dtype == "bool":
                barrier_networks[col] = barrier_networks[f"{col}_prev"]
            else:
                # increment based on the type of barrier at the root of the subnetwork
                barrier_networks[col] += barrier_networks[f"{col}_prev"]

        barrier_networks = barrier_networks.drop(
            columns=[c for c in barrier_networks.columns if c.endswith("_prev")]
        )

        # save barriers by the HUC2 where they are located
        for huc2 in group_huc2s:
            tmp = (
                barrier_networks.loc[barrier_networks.HUC2 == huc2]
                .reset_index(drop=True)
                .to_feather(out_dir / huc2 / f"removed_{network_type}_network.feather")
            )

    print("-------------------------\n")

    s = flowlines.groupby(level=0).size()
    if (s > 1).sum():
        print("dups", s[s > 1])

    # all flowlines without networks marked -1
    for network_type in NETWORK_TYPES:
        flowlines[network_type] = flowlines[network_type].fillna(-1).astype("int64")

    # drop any that weren't assigned any networks; these were selected because
    # they were part of a network that contained a given barrier but network
    # was for a different type (e.g., large dams network, but only evaluted
    # small part of it for a removed small_barrier)

    flowlines = flowlines.loc[flowlines[list(NETWORK_TYPES)].max(axis=1) > -1]

    # save network segments in the HUC2 where they are located
    print("Serializing network segments")
    for huc2 in group_huc2s:
        flowlines.loc[flowlines.HUC2 == huc2].reset_index().to_feather(
            out_dir / huc2 / "removed_barriers_network_segments.feather"
        )

    print(f"group done in {time() - group_start:.2f}s\n\n")


print(f"All done in {time() - start:.2f}s")
