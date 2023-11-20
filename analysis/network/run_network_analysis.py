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

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc

from analysis.constants import NETWORK_TYPES
from analysis.lib.io import read_arrow_tables
from analysis.network.lib.networks import (
    create_barrier_networks,
)

warnings.simplefilter("always")  # show geometry related warnings every time

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


data_dir = Path("data")
nhd_dir = data_dir / "nhd/clean"
networks_dir = data_dir / "networks"
src_dir = networks_dir / "raw"
out_dir = networks_dir / "clean"
out_dir.mkdir(exist_ok=True, parents=True)


start = time()

huc2_group_df = pd.read_feather(networks_dir / "connected_huc2s.feather").sort_values(by=["group", "HUC2"])
huc2s = huc2_group_df.HUC2.values
groups = huc2_group_df.groupby("group").HUC2.apply(list).tolist()

all_barriers = (
    pa.dataset.dataset(src_dir / "all_barriers.feather", format="feather")
    .to_table(
        columns=[
            "id",
            "kind",
            "HUC2",
            "primary_network",
            "largefish_network",
            "smallfish_network",
        ],
        # exclude all removed barriers from this analysis; they are handled in a separate step
        filter=pc.field("removed") == False,  # noqa
    )
    .to_pandas()
)

all_joins = read_arrow_tables(
    [src_dir / huc2 / "flowline_joins.feather" for huc2 in huc2s],
    columns=[
        "upstream",
        "downstream",
        "type",
        "marine",
        "great_lakes",
        "upstream_id",
        "downstream_id",
        "junction",
    ],
    new_fields={"HUC2": huc2s},
).to_pandas()

# WARNING: set_index alters dtype of "id" column
all_barrier_joins = (
    read_arrow_tables(
        [src_dir / huc2 / "barrier_joins.feather" for huc2 in huc2s],
        columns=[
            "id",
            "upstream_id",
            "downstream_id",
            "kind",
            "marine",
            "great_lakes",
            "type",
        ],
        new_fields={"HUC2": huc2s},
    )
    .to_pandas()
    .set_index("id")
    .join(
        all_barriers.set_index("id")[["primary_network", "largefish_network", "smallfish_network"]],
        # only keep barrier joins that are in the set of barriers above
        how="inner",
    )
)


for group_huc2s in groups:
    print(f"\n===========================\nCreating networks for {', '.join(group_huc2s)}")
    group_start = time()

    # create output directories
    for huc2 in group_huc2s:
        huc2_dir = out_dir / huc2
        huc2_dir.mkdir(exist_ok=True, parents=True)

    # select records in HUC2s
    barriers = all_barriers.loc[all_barriers.HUC2.isin(group_huc2s)]
    joins = all_joins.loc[
        all_joins.HUC2.isin(group_huc2s),
        ["downstream_id", "upstream_id", "type", "marine", "great_lakes", "junction"],
    ]
    barrier_joins = all_barrier_joins.loc[all_barrier_joins.HUC2.isin(group_huc2s)]

    flowlines = (
        read_arrow_tables(
            [src_dir / huc2 / "flowlines.feather" for huc2 in group_huc2s],
            columns=[
                "lineID",
            ]
            + FLOWLINE_COLS,
            new_fields={"HUC2": group_huc2s},
        )
        .to_pandas()
        .set_index("lineID")
    )

    for network_type in NETWORK_TYPES:
        print(f"-------------------------\nCreating networks for {network_type}")
        network_start = time()

        breaking_kinds = NETWORK_TYPES[network_type]["kinds"]
        col = NETWORK_TYPES[network_type]["column"]

        focal_barrier_joins = barrier_joins.loc[barrier_joins.kind.isin(breaking_kinds) & barrier_joins[col]]

        barrier_networks, network_stats, flowlines = create_barrier_networks(
            barriers,
            barrier_joins,
            focal_barrier_joins,
            joins,
            flowlines,
            network_type,
        )

        # save network stats to the HUC2 where the network originates
        for huc2 in sorted(network_stats.origin_HUC2.unique()):
            network_stats.loc[network_stats.origin_HUC2 == huc2].reset_index().to_feather(
                out_dir / huc2 / f"{network_type}_network_stats.feather"
            )

        # save barriers by the HUC2 where they are located
        for huc2 in group_huc2s:
            tmp = (
                barrier_networks.loc[barrier_networks.HUC2 == huc2]
                .reset_index()
                .to_feather(out_dir / huc2 / f"{network_type}_network.feather")
            )

    print("-------------------------\n")

    s = flowlines.groupby(level=0).size()
    if (s > 1).sum():
        print("dups", s[s > 1])

    # all flowlines without networks marked -1
    for network_type in NETWORK_TYPES:
        flowlines[network_type] = flowlines[network_type].fillna(-1).astype("int64")

    # save network segments in the HUC2 where they are located
    print("Serializing network segments")
    for huc2 in group_huc2s:
        flowlines.loc[flowlines.HUC2 == huc2].reset_index().to_feather(out_dir / huc2 / "network_segments.feather")

    print(f"group done in {time() - group_start:.2f}s\n\n")

print(f"All done in {time() - start:.2f}s")
