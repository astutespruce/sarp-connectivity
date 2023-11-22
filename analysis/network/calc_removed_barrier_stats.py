from pathlib import Path
from time import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from pyarrow.dataset import dataset

from analysis.constants import NETWORK_TYPES
from analysis.lib.io import read_arrow_tables
from analysis.lib.util import append
from analysis.network.lib.networks import create_barrier_networks

BARRIER_COUNT_KINDS = [
    "waterfalls",
    "dams",
    "small_barriers",
    "road_crossings",
    "headwaters",
]

# We can't calculate accurate upstream or downstream counts without doing the
# full network analysis and also accounting for removed barriers active at the
# time a given barrier is removed
DROP_COLS = (
    [f"totd_{kind}" for kind in BARRIER_COUNT_KINDS]
    + [f"tot_{kind}" for kind in BARRIER_COUNT_KINDS]
    + [f"fn_{kind}" for kind in BARRIER_COUNT_KINDS]
)
DOWNSTREAM_COLS = [
    "miles_to_outlet",
    "flows_to_ocean",
    "flows_to_great_lakes",
    "exits_region",
]


data_dir = Path("data")
network_dir = data_dir / "networks"
raw_dir = network_dir / "raw"
clean_dir = network_dir / "clean"
out_dir = clean_dir / "removed"
out_dir.mkdir(exist_ok=True)

network_types = list(NETWORK_TYPES.keys())

start = time()

huc2_group_df = pd.read_feather(network_dir / "connected_huc2s.feather").sort_values(by=["group", "HUC2"])
huc2_groups = huc2_group_df.groupby("group").HUC2.apply(list).tolist()
all_huc2s = huc2_group_df.HUC2.values

# read all flowline joins (limited to subnetworks later)
all_joins = read_arrow_tables(
    [raw_dir / huc2 / "flowline_joins.feather" for huc2 in all_huc2s],
    columns=["downstream_id", "upstream_id", "type", "marine", "great_lakes", "junction"],
    new_fields={"HUC2": all_huc2s},
).to_pandas()

all_barriers = (
    dataset(raw_dir / "all_barriers.feather", format="feather")
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
        [raw_dir / huc2 / "barrier_joins.feather" for huc2 in all_huc2s],
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
        [clean_dir / huc2 / "network_segments.feather" for huc2 in all_huc2s],
        columns=["lineID"] + network_types,
        filter=pc.is_in(pc.field("lineID"), pa.array(removed_barrier_joins.lineID.unique())),
    )
    .to_pandas()
    .set_index("lineID")
)
removed_barrier_joins = removed_barrier_joins.join(subnetwork_lookup, on="lineID").drop(columns=["lineID"])
removed_barriers = removed_barriers.join(removed_barrier_joins[network_types].groupby(level=0).first(), on="id")

############ IN PROGRESS: rework outer loop to be network type

for network_type in network_types:
    print(f"\n===========================\nCreating networks for {network_type}")
    network_start = time()

    breaking_kinds = NETWORK_TYPES[network_type]["kinds"]
    network_col = NETWORK_TYPES[network_type]["column"]
    removed_focal_barriers = removed_barriers.loc[
        removed_barriers.kind.isin(breaking_kinds) & removed_barriers[network_col]
    ]

    if len(removed_focal_barriers) == 0:
        print(f"skipping {network_type}, no removed barriers of this type present")
        continue

    # find all subnetworks that contain removed barriers and read in associated
    # network segments
    subnetworks = removed_focal_barriers[network_type].unique()

    # read in previously created networks that contain these removed barriers
    subnetwork_segments = (
        read_arrow_tables(
            [clean_dir / huc2 / "network_segments.feather" for huc2 in all_huc2s],
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

    # read in previous downstream stats; these can be used directly for networks
    # that are (not really) origins within these subnetworks
    prev_subnetwork_stats = (
        read_arrow_tables(
            [clean_dir / huc2 / f"{network_type}_network_stats.feather" for huc2 in all_huc2s],
            columns=["networkID"] + DOWNSTREAM_COLS,
            filter=pc.is_in(pc.field("networkID"), pa.array(subnetworks)),
        )
        .to_pandas()
        .set_index("networkID")
    )
    # assign these to removed barriers so we can update their stats later
    prev_stats = (
        removed_focal_barriers[["id", network_type]]
        .set_index("id")
        .join(prev_subnetwork_stats, on=network_type)
        .rename(columns={network_type: "subnetworkID"})
    )

    # include only joins where upstream_id is in subnetworks or downstream is
    # within subnetwork and terminates at top of network
    subnetwork_joins = all_joins.loc[
        all_joins.upstream_id.isin(subnetwork_segments.index.values)
        | (all_joins.downstream_id.isin(subnetwork_segments.index.values) & (all_joins.upstream_id == 0))
    ]

    ########## LOOP GOES HERE ##########
    merged_networks = None
    merged_segments = None

    # FIXME: make loop
    years_removed = sorted(removed_barriers.YearRemoved.unique())
    for year in years_removed:
        print(f"\n----------------- Processing barriers removed in year {year} -----------------")

        # Select any not-yet-removed barriers (YearRemoved >= year) and any non-removed
        # barriers that either join adjacent subnetworks or if they terminate on upstream
        # or downstream side
        active_removed_barriers = removed_barriers.loc[removed_barriers.YearRemoved >= year]
        active_focal_removed_barriers = active_removed_barriers.loc[
            active_removed_barriers.kind.isin(breaking_kinds) & active_removed_barriers[network_col]
        ]
        cur_removed_barriers = active_focal_removed_barriers.loc[active_focal_removed_barriers.YearRemoved == year]

        # only select subnetworks that have barriers removed in this year
        active_subnetworks = removed_barrier_joins.loc[
            removed_barrier_joins.index.isin(cur_removed_barriers.id), network_type
        ].unique()
        active_segments = subnetwork_segments.loc[subnetwork_segments.subnetworkID.isin(active_subnetworks)]

        active_joins = subnetwork_joins.loc[
            subnetwork_joins.upstream_id.isin(active_segments.index.values)
            | (subnetwork_joins.downstream_id.isin(active_segments.index.values) & (subnetwork_joins.upstream_id == 0))
        ]

        active_barrier_joins = all_barrier_joins.loc[
            # keep any current removed barriers regardless of position on subnetworks
            all_barrier_joins.index.isin(cur_removed_barriers.id.values)
            # keep any barriers that are still active (removed or non-removed) on
            # these subnetworks
            | (
                (
                    all_barrier_joins.index.isin(nonremoved_barriers.id.values)
                    | all_barrier_joins.index.isin(active_removed_barriers.id.values)
                )
                & (
                    # barrier joins adjacent subnetworks
                    (
                        all_barrier_joins.downstream_id.isin(active_segments.index.values)
                        & all_barrier_joins.upstream_id.isin(active_segments.index.values)
                    )
                    # terminate on downstream side
                    | (
                        (all_barrier_joins.downstream_id == 0)
                        & all_barrier_joins.upstream_id.isin(active_segments.index.values)
                    )
                    # terminate on upstream side
                    | (
                        all_barrier_joins.downstream_id.isin(active_segments.index.values)
                        & (all_barrier_joins.upstream_id == 0)
                    )
                )
            )
        ]
        active_focal_barrier_joins = active_barrier_joins.loc[
            active_barrier_joins.kind.isin(breaking_kinds) & active_barrier_joins[network_col]
        ]

        # Create networks based on all barriers active in this year
        networks, _, network_segments = create_barrier_networks(
            barriers=active_focal_removed_barriers,
            barrier_joins=active_barrier_joins,
            focal_barrier_joins=active_focal_barrier_joins,
            joins=active_joins,
            flowlines=active_segments,
            network_type=network_type,
        )

        # extract networks for currently-removed barriers
        cur_networks = networks.join(cur_removed_barriers.set_index("id").YearRemoved, how="inner").drop(
            columns=DROP_COLS, errors="ignore"
        )

        # for any contiguous subnetworks, we need to deduct the miles_to_outlet
        # calculated for the intermediate non-removed barriers and then deduct
        # this amount from the miles_to_outlet for the previous stats
        updated_prev_stats = prev_stats.join(
            networks.loc[(networks.upNetID != 0) & networks.index.isin(nonremoved_barriers.id)]
            .set_index("upNetID")
            .miles_to_outlet.rename("deduct_miles_to_outlet"),
            on="subnetworkID",
        )
        updated_prev_stats["miles_to_outlet"] -= updated_prev_stats.deduct_miles_to_outlet.fillna(0).astype("float32")

        # bring in stats for the downstream side of the subnetwork the barrier is on
        cur_networks = cur_networks.join(updated_prev_stats, rsuffix="_prev")
        # add in miles_to_outlet based on length downstream of subnetwork this barrier is on
        cur_networks["miles_to_outlet"] += cur_networks.miles_to_outlet_prev
        for col in ["flows_to_ocean", "flows_to_great_lakes", "exits_region"]:
            cur_networks[col] |= cur_networks[f"{col}_prev"]
        cur_networks = cur_networks.drop(columns=[col for col in cur_networks.columns if col.endswith("_prev")])

        # TODO: update upstream stats & gained miles based on barriers removed in same year on same subnetwork

        cur_segments = network_segments.join(
            cur_networks[["upNetID", "YearRemoved"]].reset_index().set_index("upNetID").id.rename("barrier_id"),
            on=network_type,
            how="inner",
        )

        # accumulate networks / network_segments across years
        merged_networks = append(merged_networks, cur_networks.reset_index())
        merged_segments = append(merged_segments, cur_segments.reset_index())

    networks = merged_networks
    network_segments = merged_segments

    networks.to_feather(out_dir / f"removed_{network_type}_networks.feather")
    network_segments.to_feather(out_dir / f"removed_{network_type}_network_segments")


print(f"All done in {time() - start:.2f}s")
