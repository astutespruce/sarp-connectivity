"""Create networks by first cutting flowlines at barriers, then traversing upstream to
determine upstream networks to upstream-most endpoints or upstream barriers.

After networks are created, summary statistics are calculated.

The final outputs of this process are a set of network-related files for each region
and network type (dams or small barriers):

data/networks/<region>/<network type>/*
"""

from pathlib import Path
from time import time
import warnings

import numpy as np
import pandas as pd


from analysis.lib.io import read_feathers
from analysis.network.lib.stats import (
    calculate_upstream_network_stats,
    calculate_downstream_stats,
)
from analysis.network.lib.networks import create_networks, connect_huc2s

warnings.simplefilter("always")  # show geometry related warnings every time
warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

# Note: only includes columns used later for network stats
FLOWLINE_COLS = [
    "NHDPlusID",
    "intermittent",
    "altered",
    "waterbody",
    "sizeclass",
    "length",
    "AreaSqKm",
]


barrier_types = ["dams", "small_barriers"]  # , "road_crossings"]

data_dir = Path("data")
nhd_dir = data_dir / "nhd/clean"
src_dir = data_dir / "networks/raw"
out_dir = data_dir / "networks/clean"
out_dir.mkdir(exist_ok=True, parents=True)


start = time()

barriers = pd.read_feather(
    src_dir / "all_barriers.feather",
    columns=["id", "barrierID", "loop", "intermittent", "kind", "HUC2"],
)

huc2s = sorted([huc2 for huc2 in barriers.HUC2.unique() if huc2])

# manually subset keys from above for processing
# huc2s = [
#     "02",
#     "03",
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
#     "21",
# ]


print("Finding connected HUC2s")
joins = read_feathers(
    [src_dir / huc2 / "flowline_joins.feather" for huc2 in huc2s],
    columns=[
        "upstream",
        "downstream",
        "type",
        "marine",
        "upstream_id",
        "downstream_id",
    ],
    new_fields={"HUC2": huc2s},
)

# TODO: remove once all flowlines have been re-extracted
joins.loc[(joins.upstream == 0) & (joins.type == "internal"), "type"] = "origin"

groups, joins = connect_huc2s(joins)
print(f"Found {len(groups)} HUC2 groups in {time() - start:,.2f}s")

# persist table of connected HUC2s
connected_huc2s = pd.DataFrame({"HUC2": groups}).explode(column="HUC2")
connected_huc2s["group"] = connected_huc2s.index.astype("uint8")
connected_huc2s.reset_index(drop=True).to_feather(
    data_dir / "networks/connected_huc2s.feather"
)


for group in groups:
    group_start = time()

    group_huc2s = sorted(group)

    # create output directories
    for huc2 in group_huc2s:
        huc2_dir = out_dir / huc2
        huc2_dir.mkdir(exist_ok=True, parents=True)

    print(f"\n===========================\nCreating networks for {group}")

    group_joins = joins.loc[
        joins.HUC2.isin(group), ["downstream_id", "upstream_id", "type", "marine"]
    ]

    barrier_joins = read_feathers(
        [src_dir / huc2 / "barrier_joins.feather" for huc2 in group_huc2s],
        columns=["barrierID", "upstream_id", "downstream_id", "kind", "marine", "type"],
        new_fields={"HUC2": group_huc2s},
    ).set_index("barrierID")

    flowlines = read_feathers(
        [src_dir / huc2 / "flowlines.feather" for huc2 in group_huc2s],
        columns=[
            "lineID",
        ]
        + FLOWLINE_COLS,
        new_fields={"HUC2": group_huc2s},
    ).set_index("lineID")

    # Build networks for dams and again for small barriers
    for barrier_type in barrier_types:
        print(f"-------------------------\nCreating networks for {barrier_type}")
        network_start = time()

        if barrier_type == "dams":
            focal_barrier_joins = barrier_joins.loc[
                barrier_joins.kind.isin(["waterfall", "dam"])
            ]
        elif barrier_type == "small_barriers":
            focal_barrier_joins = barrier_joins.loc[
                barrier_joins.kind.isin(["waterfall", "dam", "small_barrier"])
            ]
        elif barrier_type == "road_crossings":
            focal_barrier_joins = barrier_joins.loc[
                barrier_joins.kind.isin(
                    ["waterfall", "dam", "small_barrier", "road_crossing"]
                )
            ]
        else:
            raise ValueError("Unsupported barrier type")

        upstream_networks, downstream_linear_networks = create_networks(
            group_joins,
            focal_barrier_joins,
            flowlines.index,
        )

        upstream_networks = upstream_networks.set_index("lineID").networkID
        print(
            f"{len(upstream_networks.unique()):,} networks created in {time() - network_start:.2f}s"
        )

        # join to flowlines
        flowlines = flowlines.join(upstream_networks.rename(barrier_type))
        up_network_df = (
            flowlines[FLOWLINE_COLS + ["HUC2"]]
            .join(upstream_networks, how="inner")
            .reset_index()
            .set_index("networkID")
        )

        # For any barriers that had multiple upstreams, those were coalesced to a single network above
        # So drop any dangling upstream references (those that are not in networks and non-zero)
        # NOTE: these are not persisted because we want the original barrier_joins to reflect multiple upstreams
        focal_barrier_joins = focal_barrier_joins.loc[
            focal_barrier_joins.upstream_id.isin(upstream_networks.unique())
            | (focal_barrier_joins.upstream_id == 0)
        ].copy()

        down_network_df = (
            flowlines[["length", "HUC2"]]
            .join(downstream_linear_networks.set_index("lineID").networkID, how="inner")
            .reset_index()
            .set_index("networkID")
        )

        ### Calculate network statistics
        print("Calculating network stats...")

        stats_start = time()

        # lineIDs that terminate in marine or downstream exits of HUC2
        marine_ids = joins.loc[joins.marine].upstream_id.unique()
        exit_ids = joins.loc[joins.type == "huc2_drain"].upstream_id.unique()

        upstream_stats = calculate_upstream_network_stats(
            up_network_df,
            group_joins,
            focal_barrier_joins,
            barrier_joins,
        )
        # WARNING: because not all flowlines have associated catchments, they are missing
        # natfldpln

        downstream_stats = calculate_downstream_stats(
            down_network_df, focal_barrier_joins, barrier_joins, marine_ids, exit_ids
        )

        ### Join upstream network stats to downstream network stats
        # NOTE: a network will only have downstream stats if it is upstream of a
        # barrier
        network_stats = upstream_stats.join(
            downstream_stats.join(focal_barrier_joins.upstream_id).set_index(
                "upstream_id"
            )
        )
        network_stats.index.name = "networkID"

        # Fill missing data
        for kind in ["waterfalls", "dams", "small_barriers", "road_crossings"]:
            col = f"totd_{kind}"
            network_stats[col] = network_stats[col].fillna(0).astype("uint32")

        for col in ["flows_to_ocean", "exits_region"]:
            network_stats[col] = network_stats[col].fillna(False).astype("bool")

        network_stats.miles_to_outlet = network_stats.miles_to_outlet.fillna(0).astype(
            "float32"
        )
        network_stats.barrier = network_stats.barrier.fillna("")

        # set to_ocean and exits_region for functional networks that terminate
        # in marine or leave region and have no downstream barrier
        network_stats.loc[network_stats.index.isin(marine_ids), "flows_to_ocean"] = True
        # if segments connect to marine they also leave the region
        network_stats.loc[
            network_stats.index.isin(np.unique(np.append(marine_ids, exit_ids))),
            "exits_region",
        ] = True

        print(f"calculated stats in {time() - stats_start:.2f}s")

        # save network stats to the HUC2 where the network originates
        for huc2 in sorted(network_stats.origin_HUC2.unique()):
            network_stats.loc[
                network_stats.origin_HUC2 == huc2
            ].reset_index().to_feather(
                out_dir / huc2 / f"{barrier_type}_network_stats.feather"
            )

        #### Calculate up and downstream network attributes for barriers
        # NOTE: some statistics (totd_*, miles_to_ocean, flows_to_ocean, exits_region)
        # are evaluated from the upstream functional network (i.e., these are statistics)
        # downstream of the barrier associated with that functional network
        # WARNING: some barriers are on the upstream end or downstream end of the
        # total network and are missing either upstream or downstream network
        print("calculating upstream and downstream networks for barriers")

        upstream_networks = (
            focal_barrier_joins[["upstream_id"]]
            .join(
                upstream_stats.drop(
                    columns=[c for c in upstream_stats.columns if c.startswith("free_")]
                ),
                on="upstream_id",
            )
            .rename(
                columns={
                    "upstream_id": "upNetID",
                    "total_miles": "TotalUpstreamMiles",
                    "perennial_miles": "PerennialUpstreamMiles",
                    "intermittent_miles": "IntermittentUpstreamMiles",
                    "altered_miles": "AlteredUpstreamMiles",
                    "unaltered_miles": "UnalteredUpstreamMiles",
                    "perennial_unaltered_miles": "PerennialUnalteredUpstreamMiles",
                    "pct_unaltered": "PercentUnaltered",
                    "pct_perennial_unaltered": "PercentPerennialUnaltered",
                }
            )
        )

        # these are the downstream FUNCTIONAL networks, not linear networks
        downstream_networks = (
            focal_barrier_joins[["downstream_id"]]
            .join(
                up_network_df.reset_index().set_index("lineID").networkID,
                on="downstream_id",
            )
            .join(
                network_stats[
                    [
                        "total_miles",
                        "free_miles",
                        "free_perennial_miles",
                        "free_intermittent_miles",
                        "free_altered_miles",
                        "free_unaltered_miles",
                        "free_perennial_unaltered_miles",
                    ]
                ].rename(
                    columns={
                        "total_miles": "TotalDownstreamMiles",
                        "free_miles": "FreeDownstreamMiles",
                        "free_perennial_miles": "FreePerennialDownstreamMiles",
                        "free_intermittent_miles": "FreeIntermittentDownstreamMiles",
                        "free_altered_miles": "FreeAlteredDownstreamMiles",
                        "free_unaltered_miles": "FreeUnalteredDownstreamMiles",
                        "free_perennial_unaltered_miles": "FreePerennialUnalteredDownstreamMiles",
                    }
                ),
                on="networkID",
            )
            .rename(columns={"networkID": "downNetID"})
            .drop(columns=["downstream_id"])
        )

        # Note: the join creates duplicates if there are multiple upstream or downstream
        # networks for a given barrier, so we drop these duplicates after the join just to be sure.
        barrier_networks = (
            upstream_networks.join(downstream_networks)
            .join(downstream_stats)
            .join(
                barriers.set_index("barrierID")[["id", "kind", "intermittent", "HUC2"]]
            )
        )

        # fill missing data
        # if there is no upstream network, the network of a barrier is in the
        # same HUC2 as the barrier
        ix = barrier_networks.origin_HUC2.isnull()
        barrier_networks.loc[ix, "origin_HUC2"] = barrier_networks.loc[ix].HUC2

        barrier_networks.barrier = barrier_networks.barrier.fillna("")
        barrier_networks.origin_HUC2 = barrier_networks.origin_HUC2.fillna("")
        barrier_networks.flows_to_ocean = barrier_networks.flows_to_ocean.fillna(False)
        barrier_networks.exits_region = barrier_networks.exits_region.fillna(False)
        # if isolated network or connects to marine / exit, there are no further miles downstream from this network
        barrier_networks.miles_to_outlet = barrier_networks.miles_to_outlet.fillna(
            0
        ).astype("float32")
        # total drainage area will be 0 for barriers at top of network
        barrier_networks.fn_dakm2 = barrier_networks.fn_dakm2.fillna(0).astype(
            "float32"
        )

        # Set upstream and downstream count columns to 0 where nan; these are
        # for networks where barrier is at top of total network or bottom
        # of total network
        for stat_type in ["fn", "cat", "tot", "totd"]:
            for t in [
                "waterfalls",
                "dams",
                "small_barriers",
                "road_crossings",
                "headwaters",
            ]:
                col = f"{stat_type}_{t}"
                if col in barrier_networks.columns:
                    barrier_networks[col] = (
                        barrier_networks[col].fillna(0).astype("uint32")
                    )

        barrier_networks = barrier_networks.fillna(0).drop_duplicates()

        # Fix data types after all the joins
        # NOTE: upNetID or downNetID may be 0 if there aren't networks on that side
        for col in ["upNetID", "downNetID"]:
            barrier_networks[col] = barrier_networks[col].astype("uint32")

        length_cols = [c for c in barrier_networks.columns if c.endswith("Miles")]

        for col in length_cols + [
            "natfldpln",
        ]:
            barrier_networks[col] = barrier_networks[col].astype("float32")

        barrier_networks.sizeclasses = barrier_networks.sizeclasses.astype("uint8")

        # save barriers by the HUC2 where they are located
        for huc2 in group_huc2s:
            barrier_networks.loc[
                barrier_networks.HUC2 == huc2
            ].reset_index().to_feather(
                out_dir / huc2 / f"{barrier_type}_network.feather"
            )

    print("-------------------------\n")

    s = flowlines.groupby(level=0).size()
    if (s > 1).sum():
        print("dups", s[s > 1])

    # all flowlines without networks marked -1
    for col in barrier_types:
        flowlines[col] = flowlines[col].fillna(-1).astype("int64")

    # save network segments in the HUC2 where they are located
    print("Serializing network segments")
    for huc2 in group_huc2s:
        flowlines.loc[flowlines.HUC2 == huc2].reset_index().to_feather(
            out_dir / huc2 / "network_segments.feather"
        )

    print(f"group done in {time() - group_start:.2f}s\n\n")

print(f"All done in {time() - start:.2f}s")
