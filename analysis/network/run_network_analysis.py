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
from pyarrow.dataset import dataset
import pyarrow.compute as pc
from pyarrow.feather import write_feather

from analysis.constants import NETWORK_TYPES
from analysis.lib.io import read_arrow_tables
from analysis.network.lib.networks import load_flowlines, create_barrier_networks

warnings.simplefilter("always")  # show geometry related warnings every time


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
    dataset(src_dir / "all_barriers.feather", format="feather")
    .to_table(
        columns=[
            "id",
            "SARPID",
            "kind",
            "HUC2",
            "primary_network",
            "largefish_network",
            "smallfish_network",
            "invasive",
        ],
        # exclude all removed barriers from this analysis; they are handled in a separate step
        filter=pc.field("removed") == False,  # noqa
    )
    .combine_chunks()
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
    dict_fields={"HUC2"},
)


all_barrier_joins = (
    all_barriers.select(
        [
            "id",
            "primary_network",
            "largefish_network",
            "smallfish_network",
            "invasive",
        ]
    )
    .join(
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
            dict_fields={"HUC2"},
        ),
        "id",
        join_type="inner",
    )
    .combine_chunks()
)


for group_huc2s in groups:
    print(f"\n===========================\nCreating networks for {', '.join(group_huc2s)}")
    group_start = time()

    # create output directories
    for huc2 in group_huc2s:
        huc2_dir = out_dir / huc2
        huc2_dir.mkdir(exist_ok=True, parents=True)

    # select records in HUC2s
    group_huc2_array = pa.array(group_huc2s)
    barriers = all_barriers.filter(pc.is_in(all_barriers["HUC2"], group_huc2_array))
    joins = all_joins.filter(pc.is_in(all_joins["HUC2"], group_huc2_array)).select(
        ["downstream_id", "upstream_id", "type", "marine", "great_lakes", "junction"]
    )
    barrier_joins = all_barrier_joins.filter(pc.is_in(all_barrier_joins["HUC2"], group_huc2_array))

    flowlines = load_flowlines(group_huc2s)

    # collate all upstream functional and mainstem network assignments into
    # a single table
    upstream_network_segments = flowlines.select(["lineID", "HUC2"])

    for network_type in NETWORK_TYPES:
        print(f"-------------------------\nCreating networks for {network_type}")
        network_start = time()

        breaking_kinds = pa.array(NETWORK_TYPES[network_type]["kinds"])
        col = NETWORK_TYPES[network_type].get("column")

        filter = pc.is_in(pc.field("kind"), breaking_kinds)

        if col:
            # Select barriers marked as participating in this network
            filter = filter & pc.equal(pc.field(col), True)
        # otherwise: all barriers otherwise included here are used for the analysis,
        # including road crossings

        focal_barriers = barriers.filter(filter).combine_chunks()
        focal_barrier_joins = barrier_joins.filter(filter).combine_chunks()

        (
            barrier_networks,
            network_stats,
            upstream_functional_networks,
            upstream_mainstem_networks,
            downstream_mainstem_networks,
            downstream_linear_networks,
        ) = create_barrier_networks(
            focal_barriers,
            barrier_joins,
            focal_barrier_joins,
            joins,
            flowlines,
            network_type,
        )

        upstream_network_segments = upstream_network_segments.join(
            upstream_functional_networks.select(["lineID", "networkID"]).rename_columns({"networkID": network_type}),
            "lineID",
        ).join(
            upstream_mainstem_networks.select(["lineID", "networkID"]).rename_columns(
                {"networkID": f"{network_type}_mainstem"}
            ),
            "lineID",
        )

        # save network stats to the HUC2 where the network originates
        for huc2 in sorted(pc.unique(network_stats["origin_HUC2"]).to_pylist()):
            write_feather(
                network_stats.filter(pc.equal(network_stats["origin_HUC2"], huc2)),
                out_dir / huc2 / f"{network_type}_network_stats.feather",
            )

        # tag downstream networks to HUC2 based on the HUC2 of the barrier at top of downstream network
        # tmp = barriers.set_index("id").HUC2
        barrier_huc2 = focal_barriers.select(["id", "HUC2"])
        downstream_mainstem_networks = downstream_mainstem_networks.join(barrier_huc2, "id")
        downstream_linear_networks = downstream_linear_networks.join(barrier_huc2, "id")

        # save barriers by the HUC2 where they are located and downstream linear networks
        # based on the HUC2 where the barrier is located
        for huc2 in group_huc2s:
            write_feather(
                barrier_networks.filter(pc.equal(barrier_networks["HUC2"], huc2)),
                out_dir / huc2 / f"{network_type}_network.feather",
            )

            write_feather(
                downstream_mainstem_networks.filter(pc.equal(downstream_mainstem_networks["HUC2"], huc2)).select(
                    ["id", "lineID"]
                ),
                out_dir / huc2 / f"{network_type}_downstream_mainstem_segments.feather",
            )

            write_feather(
                downstream_linear_networks.filter(pc.equal(downstream_linear_networks["HUC2"], huc2)).select(
                    ["id", "lineID"]
                ),
                out_dir / huc2 / f"{network_type}_downstream_linear_segments.feather",
            )

    print("-------------------------\n")

    # all network segments without networks marked -1
    upstream_network_segments = pa.Table.from_pydict(
        {
            "lineID": upstream_network_segments["lineID"],
            "HUC2": upstream_network_segments["HUC2"],
            **{
                c: pc.fill_null(pc.cast(upstream_network_segments[c], pa.int64()), -1)
                for c in upstream_network_segments.column_names
                if c not in {"lineID", "HUC2"}
            },
        }
    )

    # save network segments in the HUC2 where they are located
    print("Serializing network segments")
    for huc2 in group_huc2s:
        write_feather(
            upstream_network_segments.filter(pc.equal(upstream_network_segments["HUC2"], huc2)),
            out_dir / huc2 / "network_segments.feather",
        )

    print(f"group done in {time() - group_start:.2f}s\n\n")

print(f"All done in {time() - start:.2f}s")
