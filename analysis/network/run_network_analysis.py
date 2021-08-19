"""Create networks by first cutting flowlines at barriers, then traversing upstream to
determine upstream networks to upstream-most endpoints or upstream barriers.

After networks are created, summary statistics are calculated.

The final outputs of this process are a set of network-related files for each region
and network type (dams or small barriers):

data/networks/<region>/<network type>/*
"""

from pathlib import Path
import os
from time import time
import warnings

import pandas as pd


from analysis.constants import NETWORK_TYPES
from analysis.lib.io import read_feathers
from analysis.lib.joins import remove_joins
from analysis.network.lib.stats import calculate_network_stats
from analysis.network.lib.networks import create_networks, connect_huc2s

warnings.simplefilter("always")  # show geometry related warnings every time
warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


barrier_types = NETWORK_TYPES[1:]

data_dir = Path("data")
nhd_dir = data_dir / "nhd/clean"
src_dir = data_dir / "networks/raw"
out_dir = data_dir / "networks/clean"

if not out_dir.exists():
    os.makedirs(out_dir)


start = time()

barriers = pd.read_feather(
    src_dir / "all_barriers.feather",
    columns=["id", "barrierID", "loop", "intermittent", "kind", "HUC2"],
)

huc2s = sorted([huc2 for huc2 in barriers.HUC2.unique() if huc2])

# manually subset keys from above for processing
# huc2s = [
# "02",
# "03",
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
# "21",
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
        if not huc2_dir.exists():
            os.makedirs(huc2_dir)

    print(f"\n===========================\nCreating networks for {group}")

    group_joins = joins.loc[
        joins.HUC2.isin(group), ["downstream_id", "upstream_id", "type", "marine"]
    ]

    barrier_joins = read_feathers(
        [src_dir / huc2 / "barrier_joins.feather" for huc2 in group_huc2s],
        columns=["barrierID", "upstream_id", "downstream_id", "kind"],
        new_fields={"HUC2": group_huc2s},
    ).set_index("barrierID", drop=False)

    # Note: only includes columns used later for network stats
    flowline_cols = [
        "NHDPlusID",
        "intermittent",
        "altered",
        "waterbody",
        "sizeclass",
        "length",
        "sinuosity",
    ]
    flowlines = read_feathers(
        [src_dir / huc2 / "flowlines.feather" for huc2 in group_huc2s],
        columns=["lineID",] + flowline_cols,
        new_fields={"HUC2": group_huc2s},
    ).set_index("lineID")

    # Build networks for dams and again for small barriers
    for barrier_type in barrier_types:
        print(f"-------------------------\nCreating networks for {barrier_type}")
        network_start = time()

        if barrier_type == "dams":
            network_barrier_joins = barrier_joins.loc[
                barrier_joins.kind.isin(["waterfall", "dam"])
            ]
        else:
            network_barrier_joins = barrier_joins

        networks = (
            create_networks(group_joins, network_barrier_joins, flowlines.index,)
            .set_index("lineID")
            .networkID
        )
        print(
            f"{len(networks.index.unique()):,} networks created in {time() - network_start:.2f}s"
        )

        flowlines = flowlines.join(networks.rename(barrier_type))

        network_df = (
            flowlines[flowline_cols + ["HUC2"]]
            .join(networks, how="inner")
            .reset_index()
            .set_index("networkID")
        )

        # For any barriers that had multiple upstreams, those were coalesced to a single network above
        # So drop any dangling upstream references (those that are not in networks and non-zero)
        # NOTE: these are not persisted because we want the original barrier_joins to reflect multiple upstreams
        network_barrier_joins = network_barrier_joins.loc[
            network_barrier_joins.upstream_id.isin(networks.unique())
            | (network_barrier_joins.upstream_id == 0)
        ].copy()

        print("Calculating network stats...")
        network_stats = calculate_network_stats(
            network_df, network_barrier_joins, group_joins
        )
        # WARNING: because not all flowlines have associated catchments, they are missing
        # natfldpln

        # save network stats to the HUC2 where the network originates
        for huc2 in sorted(network_stats.origin_HUC2.unique()):
            network_stats.loc[
                network_stats.origin_HUC2 == huc2
            ].reset_index().to_feather(
                out_dir / huc2 / f"{barrier_type}_network_stats.feather"
            )

        #### Calculate up and downstream network attributes for barriers
        print("calculating upstream and downstream networks for barriers")

        upstream_networks = (
            network_barrier_joins[["upstream_id"]]
            .join(
                network_stats.drop(
                    columns=["flows_to_ocean", "num_downstream", "exits_region"]
                    + [c for c in network_stats.columns if c.startswith("free_")]
                ),
                on="upstream_id",
            )
            .rename(
                columns={
                    "upstream_id": "upNetID",
                    "total_miles": "TotalUpstreamMiles",
                    "perennial_miles": "PerennialUpstreamMiles",
                    "unaltered_miles": "UnalteredUpstreamMiles",
                    "perennial_unaltered_miles": "PerennialUnalteredUpstreamMiles",
                    "pct_altered": "PercentAltered",
                }
            )
        )

        downstream_networks = (
            network_barrier_joins[["downstream_id"]]
            .join(
                network_df.reset_index().set_index("lineID").networkID,
                on="downstream_id",
            )
            .join(
                network_stats[
                    [
                        "total_miles",
                        "free_miles",
                        "free_perennial_miles",
                        "free_unaltered_miles",
                        "free_perennial_unaltered_miles",
                        "num_downstream",
                        "flows_to_ocean",
                        "exits_region",
                    ]
                ].rename(
                    columns={
                        "total_miles": "TotalDownstreamMiles",
                        "free_miles": "FreeDownstreamMiles",
                        "free_perennial_miles": "FreePerennialDownstreamMiles",
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
            .join(
                barriers.set_index("barrierID")[["id", "kind", "intermittent", "HUC2"]]
            )
            .drop(columns=["barrier", "up_ndams", "up_nwfs", "up_sbs"], errors="ignore")
        )

        # fill missing data
        barrier_networks.origin_HUC2 = barrier_networks.origin_HUC2.fillna("")
        barrier_networks.num_downstream = barrier_networks.num_downstream.fillna(
            0
        ).astype("uint16")
        barrier_networks.flows_to_ocean = barrier_networks.flows_to_ocean.fillna(False)
        barrier_networks.exits_region = barrier_networks.exits_region.fillna(False)
        barrier_networks = barrier_networks.fillna(0).drop_duplicates()

        # Fix data types after all the joins
        # NOTE: upNetID or downNetID may be 0 if there aren't networks on that side
        for col in ["upNetID", "downNetID", "segments"]:
            barrier_networks[col] = barrier_networks[col].astype("uint32")

        length_cols = [c for c in barrier_networks.columns if c.endswith("Miles")]

        for col in length_cols + [
            "sinuosity",
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

print("All done in {:.2f}s".format(time() - start))
