from pathlib import Path
from time import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from pyarrow.dataset import dataset
from pyarrow.feather import write_feather

from analysis.constants import NETWORK_TYPES
from analysis.lib.graph.speedups import DirectedGraph
from analysis.lib.io import read_arrow_tables
from analysis.network.lib.networks import create_barrier_networks, load_flowlines
from analysis.network.lib.stats import percent


# We can't calculate accurate upstream or downstream counts without doing the
# full network analysis and also accounting for removed barriers active at the
# time a given barrier is removed, so we drop these here and they get filled later with -1.
# We also drop the upstream / downstream barrier info because they are more complex
# to manage here.
DROP_COLS = [
    "UpstreamWaterfalls",
    "UpstreamDams",
    "UpstreamSmallBarriers",
    "UpstreamRoadCrossings",
    "UpstreamHeadwaters",
    "TotalUpstreamWaterfalls",
    "TotalUpstreamDams",
    "TotalUpstreamSmallBarriers",
    "TotalUpstreamRoadCrossings",
    "TotalUpstreamHeadwaters",
    "TotalDownstreamWaterfalls",
    "TotalDownstreamDams",
    "TotalDownstreamSmallBarriers",
    "TotalDownstreamRoadCrossings",
    "UpstreamBarrierID",
    "UpstreamBarrierSARPID",
    "UpstreamBarrier",
    "UpstreamBarrierMiles",
    "DownstreamBarrierID",
    "DownstreamBarrierSARPID",
    "DownstreamBarrier",
    "DownstreamBarrierMiles",
]


data_dir = Path("data")
network_dir = data_dir / "networks"
raw_dir = network_dir / "raw"
clean_dir = network_dir / "clean"
out_dir = clean_dir / "removed"
out_dir.mkdir(exist_ok=True)

# NOTE: no need to calculate removed barriers for full, and skip for road_crossings because those aren't published
network_types = [t for t in NETWORK_TYPES.keys() if t not in {"full", "road_crossings"}]
start = time()

huc2_group_df = pd.read_feather(network_dir / "connected_huc2s.feather").sort_values(by=["group", "HUC2"])
groups = huc2_group_df.groupby("group").HUC2.apply(list).tolist()
huc2s = huc2_group_df.HUC2.values

# read all flowline joins (limited to subnetworks later)
all_joins = read_arrow_tables(
    [raw_dir / huc2 / "flowline_joins.feather" for huc2 in huc2s],
    columns=["downstream_id", "upstream_id", "type", "marine", "great_lakes", "junction"],
    new_fields={"HUC2": huc2s},
    dict_fields={"HUC2"},
)

all_barriers = (
    dataset(raw_dir / "all_barriers.feather", format="feather")
    .to_table(
        columns=[
            "id",
            "SARPID",
            "kind",
            "HUC2",
            "primary_network",
            "largefish_network",
            "smallfish_network",
            "removed",
            "invasive",
            "YearRemoved",
        ],
    )
    .combine_chunks()
)

all_barrier_joins = (
    all_barriers.select(
        [
            "id",
            "primary_network",
            "largefish_network",
            "smallfish_network",
            "removed",
            "invasive",
        ]
    )
    .join(
        read_arrow_tables(
            [raw_dir / huc2 / "barrier_joins.feather" for huc2 in huc2s],
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

flowlines = load_flowlines(huc2s)


### update year removed
# 1 represents everything < 2000 so that sorting works
# 0 indicates barriers with unknown year removed; these are removed first in the
# processing and distinct from cases where year is known but < 2000
# 9999 represents anything not removed
year_removed = pc.if_else(
    all_barriers["removed"],
    pc.if_else(
        pc.and_(pc.greater(all_barriers["YearRemoved"], 0), pc.less(all_barriers["YearRemoved"], 2000)),
        # 1 represents everything < 2000 so that sorting works
        1,
        all_barriers["YearRemoved"],
    ),
    9999,
)
all_barriers = all_barriers.drop(["YearRemoved"]).append_column("YearRemoved", year_removed)

removed_barriers = all_barriers.filter(all_barriers["removed"])
nonremoved_barriers = all_barriers.filter(pc.equal(all_barriers["removed"], False))


# extract a representative non-zero lineID to join to segments in order to resolve the
# networkID of each type that contains this removed barrier
# TODO: watch for edge cases where removed barrier is at top or bottom of original network
removed_barrier_joins = all_barrier_joins.filter(all_barrier_joins["removed"])
removed_barrier_joins = removed_barrier_joins.append_column(
    "lineID", pc.max_element_wise(removed_barrier_joins["upstream_id"], removed_barrier_joins["downstream_id"])
)
subnetwork_lookup = read_arrow_tables(
    [clean_dir / huc2 / "network_segments.feather" for huc2 in huc2s],
    columns=["lineID"] + network_types,
    filter=pc.is_in(pc.field("lineID"), pc.unique(removed_barrier_joins["lineID"])),
).rename_columns({c: f"{c}_networkID" for c in network_types})

# NOTE: this will have multiple records for barriers at confluences (multiple upstreams)
removed_barrier_joins = removed_barrier_joins.join(subnetwork_lookup, "lineID").drop(["lineID"])
network_cols = [f"{c}_networkID" for c in network_types]
removed_barriers = removed_barriers.join(
    # keep the first record for each barrier (all network columns will be same for all records for each barrier)
    removed_barrier_joins.select(["id"] + network_cols).group_by(["id"] + network_cols).aggregate([]),
    "id",
)

for network_type in network_types:
    print(f"\n===========================\nCreating removed barrier networks for {network_type}")
    network_start = time()

    prev_network_col = f"{network_type}_networkID"

    breaking_kinds = pa.array(NETWORK_TYPES[network_type]["kinds"])
    col = NETWORK_TYPES[network_type].get("column")

    focal_barrier_filter = pc.is_in(pc.field("kind"), breaking_kinds)
    if col:
        focal_barrier_filter = focal_barrier_filter & pc.equal(pc.field(col), True)

    removed_focal_barriers = removed_barriers.filter(focal_barrier_filter)
    nonremoved_focal_barriers = nonremoved_barriers.filter(focal_barrier_filter)

    if len(removed_focal_barriers) == 0:
        print(f"skipping {network_type}, no removed barriers of this type present")
        continue

    subnetwork_ids = pc.unique(removed_focal_barriers[prev_network_col])

    # read in previously created networks that contain these removed barriers
    # this is small enough, so we read it for all regions
    subnetwork_segments = read_arrow_tables(
        [clean_dir / huc2 / "network_segments.feather" for huc2 in huc2s],
        columns=["lineID", network_type],
        filter=pc.is_in(pc.field(network_type), subnetwork_ids),
    ).rename_columns({network_type: "subnetworkID"})

    subnetwork_flowlines = flowlines.filter(
        pc.is_in(flowlines["lineID"].combine_chunks(), subnetwork_segments["lineID"].combine_chunks())
    )

    # include only joins where upstream_id is in subnetworks or downstream is
    # within subnetwork and terminates at top of network
    subnetwork_joins = all_joins.filter(
        pc.or_(
            pc.is_in(all_joins["upstream_id"], subnetwork_segments["lineID"]),
            pc.and_(
                pc.is_in(
                    all_joins["downstream_id"],
                    subnetwork_segments["lineID"],
                ),
                pc.equal(all_joins["upstream_id"], 0),
            ),
        )
    ).combine_chunks()

    # read in subset of previous linear downstream network stats; these can
    # be added to the downstream stats of the current removed barriers
    prev_downstream_stats = (
        read_arrow_tables(
            [clean_dir / huc2 / f"{network_type}_network_stats.feather" for huc2 in huc2s],
            columns=[
                "networkID",
                "origin_HUC2",
                "flows_to_ocean",
                "flows_to_great_lakes",
                "miles_to_outlet",
                "has_downstream_invasive_barrier",
                "barrier",
            ],
            filter=pc.is_in(pc.field("networkID"), subnetwork_ids),
        )
        .combine_chunks()
        .rename_columns(
            {
                "origin_HUC2": "OriginHUC2_prev",
                "flows_to_ocean": "FlowsToOcean_prev",
                "flows_to_great_lakes": "FlowsToGreatLakes_prev",
                "miles_to_outlet": "MilesToOutlet_prev",
                "has_downstream_invasive_barrier": "HasDownstreamInvasiveBarrier_prev",
            }
        )
    )

    # identify subnetworks that terminate downstream so we can recalc gains below
    prev_downstream_stats = prev_downstream_stats.append_column(
        "TerminatesDownstream_prev",
        pc.and_(
            pc.or_(prev_downstream_stats["FlowsToOcean_prev"], prev_downstream_stats["FlowsToGreatLakes_prev"]),
            pc.is_null(prev_downstream_stats["barrier"]),
        ),
    ).drop(["barrier"])

    # cast to int64 to permit join
    prev_downstream_stats = prev_downstream_stats.drop(["networkID"]).append_column(
        "networkID", pc.cast(prev_downstream_stats["networkID"], pa.int64())
    )
    prev_downstream_stats = (
        removed_focal_barriers.select(["id", prev_network_col])
        .join(prev_downstream_stats, prev_network_col, "networkID", join_type="inner")
        .rename_columns({prev_network_col: "subnetworkID"})
    )
    # cast back for easier joins below
    prev_downstream_stats = prev_downstream_stats.drop(["subnetworkID"]).append_column(
        "subnetworkID", pc.cast(prev_downstream_stats["subnetworkID"], pa.uint32())
    )

    merged_networks = None
    merged_segments = None

    years_removed = sorted(pc.unique(removed_barriers["YearRemoved"]).to_pylist())
    for year in years_removed:
        print(f"\n----------------- Processing barriers removed in year {year} -----------------")

        # Select any not-yet-removed barriers (YearRemoved >= year) and any non-removed
        # barriers that either join adjacent subnetworks or if they terminate on upstream
        # or downstream side
        # NOTE: active means that the dams are still "active" (in place) in the year in this loop
        active_removed_barriers = removed_barriers.filter(pc.greater_equal(removed_barriers["YearRemoved"], year))
        active_focal_removed_barriers = removed_focal_barriers.filter(
            pc.greater_equal(removed_focal_barriers["YearRemoved"], year)
        )

        cur_focal_removed_barriers = active_focal_removed_barriers.filter(
            pc.equal(active_focal_removed_barriers["YearRemoved"], year)
        )

        # only select subnetworks that have barriers removed in this year
        active_subnetwork_ids = pc.unique(
            removed_barrier_joins.select(["id", prev_network_col])
            .rename_columns({prev_network_col: "subnetworkID"})
            .join(cur_focal_removed_barriers.select(["id"]), "id", join_type="inner")["subnetworkID"]
        )
        active_segments = subnetwork_segments.filter(
            pc.is_in(subnetwork_segments["subnetworkID"], active_subnetwork_ids)
        )
        active_lineIDs = active_segments["lineID"].combine_chunks()
        active_flowlines = subnetwork_flowlines.filter(pc.is_in(subnetwork_flowlines["lineID"], active_lineIDs))

        active_joins = subnetwork_joins.filter(
            pc.or_(
                pc.is_in(subnetwork_joins["upstream_id"], active_lineIDs),
                pc.and_(
                    pc.is_in(subnetwork_joins["downstream_id"], active_lineIDs),
                    pc.equal(subnetwork_joins["upstream_id"], 0),
                ),
            )
        )

        # keep any current removed barriers regardless of position on subnetworks
        is_cur_removed_filter = pc.is_in(pc.field("id"), cur_focal_removed_barriers["id"])

        # keep any barriers that are still active (removed or non-removed) on
        # these subnetworks
        is_active_barrier_filter = (
            (pc.field("removed") == False)  # noqa: E712
            | pc.is_in(pc.field("id"), active_removed_barriers["id"])
        )

        # barrier joins adjacent subnetworks
        is_adj_join_filter = pc.is_in(pc.field("upstream_id"), active_lineIDs) & pc.is_in(
            pc.field("downstream_id"), active_lineIDs
        )
        # terminate on upstream side
        is_upstream_join_filter = pc.equal(pc.field("upstream_id"), 0) & pc.is_in(
            pc.field("downstream_id"), active_lineIDs
        )
        # terminate on downstream side
        is_downstream_join_filter = pc.equal(pc.field("downstream_id"), 0) & pc.is_in(
            pc.field("upstream_id"), active_lineIDs
        )
        join_filter = is_cur_removed_filter | (
            is_active_barrier_filter & (is_adj_join_filter | is_upstream_join_filter | is_downstream_join_filter)
        )

        active_barrier_joins = all_barrier_joins.filter(join_filter)
        active_focal_barrier_joins = active_barrier_joins.filter(focal_barrier_filter)

        (
            barrier_networks,
            network_stats,
            upstream_functional_networks,
            _,  # upstream_mainstem_networks: not used
            _,  # downstream_mainstem_networks: not used
            _,  # downstream_linear_networks: not used
        ) = create_barrier_networks(
            focal_barriers=active_focal_removed_barriers,
            barrier_joins=active_barrier_joins,
            focal_barrier_joins=active_focal_barrier_joins,
            joins=active_joins,
            flowlines=active_flowlines,
            network_type=network_type,
        )

        ### find all nonremoved barriers that were included in the above networks
        # because they fall between adjacent subnetworks, and adjust their prior
        # total miles downstream because any downstream total miles calculated for
        # upstream subnetworks above will have passed through them to the bottom-most
        # contiguous subnetwork (i.e., we would double-count miles without this)
        nonremoved_barrier_networks = (
            active_barrier_joins.select(["id", "upstream_id"])
            .rename_columns({"upstream_id": "networkID"})
            .join(nonremoved_focal_barriers.select(["id"]), "id", join_type="inner")
            .drop(["id"])
            .join(
                network_stats.select(["networkID", "miles_to_outlet"]).rename_columns(
                    {"miles_to_outlet": "MilesToOutlet_cur"}
                ),
                "networkID",
                join_type="inner",
            )
            .combine_chunks()
        )
        updated_downstream_stats = prev_downstream_stats.join(nonremoved_barrier_networks, "subnetworkID", "networkID")
        updated_downstream_stats = updated_downstream_stats.drop(
            ["subnetworkID", "MilesToOutlet_prev", "MilesToOutlet_cur"]
        ).append_column(
            "MilesToOutlet_prev",
            pc.if_else(
                pc.is_valid(updated_downstream_stats["MilesToOutlet_cur"]),
                pc.subtract(
                    updated_downstream_stats["MilesToOutlet_prev"], updated_downstream_stats["MilesToOutlet_cur"]
                ),
                updated_downstream_stats["MilesToOutlet_prev"],
            ),
        )

        # extract networks for currently-removed barriers
        cur_barrier_networks = (
            # drop mainstems stats because they are are more complex because
            # removed barriers in series are not necessarily on the same mainstem;
            # also drop EJ fields
            barrier_networks.drop(
                [c for c in barrier_networks.column_names if "Mainstem" in c]
                + [c for c in barrier_networks.column_names if "EJTract" in c or "EJTribal" in c]
            )
            .join(
                cur_focal_removed_barriers.select(["id", "YearRemoved"]),
                "id",
                join_type="inner",
            )
            .join(updated_downstream_stats, "id")
        )

        ### count total number of barriers downstream WITHIN these networks; this tells us if
        # the subnetwork still terminates downstream (may have removed barriers downstream)
        # (we can then drop all the count columns)
        downstream_breaking_barrier_count_cols = [
            f"TotalDownstream{kind.title().replace('_', '')}s" for kind in NETWORK_TYPES[network_type]["kinds"]
        ]
        total_downstream_breaking_barriers = cur_barrier_networks[downstream_breaking_barrier_count_cols[0]]
        for col in downstream_breaking_barrier_count_cols[1:]:
            total_downstream_breaking_barriers = pc.add(total_downstream_breaking_barriers, cur_barrier_networks[col])

        cur_barrier_networks = (
            cur_barrier_networks.append_column(
                "TerminatesDownstream",
                pc.if_else(
                    pc.and_(
                        cur_barrier_networks["TerminatesDownstream_prev"],
                        pc.equal(total_downstream_breaking_barriers, 0),
                    ),
                    True,
                    False,
                ),
            )
            # drop upstream / downstream count fields and all mainstem fields
            # this is because counts require the full network for the analysis rather than subnetworks,
            .drop(DROP_COLS)
        )

        update_cols = ["OriginHUC2", "FlowsToOcean", "FlowsToGreatLakes", "HasDownstreamInvasiveBarrier"]
        updated = {
            c: pc.if_else(
                pc.is_valid(cur_barrier_networks[f"{c}_prev"]),
                cur_barrier_networks[f"{c}_prev"],
                cur_barrier_networks[c],
            )
            for c in update_cols
        }
        # relculate miles to outlet as sum of MilesToOutlet for the removed barrier plus MilesToOutlet at the bottom of its original network
        updated["MilesToOutlet"] = pc.if_else(
            pc.is_valid(cur_barrier_networks["MilesToOutlet_prev"]),
            pc.add(cur_barrier_networks["MilesToOutlet"], cur_barrier_networks["MilesToOutlet_prev"]),
            cur_barrier_networks["MilesToOutlet"],
        )

        cur_barrier_networks = pa.Table.from_pydict(
            {
                c: updated.get(c, cur_barrier_networks[c])
                for c in cur_barrier_networks.column_names
                if not c.endswith("_prev")
            }
        )

        # Set effective gain miles to gain miles since gain miles are recalculated
        # below for sibling barriers, and mark which side a given network is used
        # to derive its gain miles
        other_stats = pa.Table.from_pydict(
            {
                "id": cur_barrier_networks["id"],
                "EffectiveGainMiles": cur_barrier_networks["GainMiles"],
                "GainMilesUpstreamSide": pc.if_else(
                    pc.or_(
                        pc.equal(cur_barrier_networks["upNetID"], 0),
                        np.isclose(cur_barrier_networks["GainMiles"], cur_barrier_networks["TotalUpstreamMiles"]),
                    ),
                    True,
                    False,
                ),
                "EffectivePerennialGainMiles": cur_barrier_networks["PerennialGainMiles"],
                "PerennialGainMilesUpstreamSide": pc.if_else(
                    pc.or_(
                        pc.equal(cur_barrier_networks["upNetID"], 0),
                        np.isclose(
                            cur_barrier_networks["PerennialGainMiles"], cur_barrier_networks["PerennialUpstreamMiles"]
                        ),
                    ),
                    True,
                    False,
                ),
            }
        )
        cur_barrier_networks = cur_barrier_networks.join(other_stats, "id")

        cur_segments = (
            flowlines.select(["lineID", "sizeclass", "intermittent"])
            .join(
                upstream_functional_networks.join(
                    cur_barrier_networks.select(["id", "upNetID", "YearRemoved"]),
                    "networkID",
                    "upNetID",
                    join_type="inner",
                ),
                "lineID",
                join_type="inner",
            )
            .combine_chunks()
        )

        ### Find any cases where there are multiple removed barriers (in the same year)
        # in series within a subnetwork, and aggregate them so that each downstream barrier
        # includes the full upstream network of each upstream removed barrier

        # create pairs between adjacent removed-barrier networks; this automatically
        # exludes non-removed intermediate barriers because their up / down net IDs don't line up
        network_pairs = (
            cur_barrier_networks.select(["id", "upNetID"])
            .filter(pc.not_equal(cur_barrier_networks["upNetID"], 0))
            .rename_columns({"id": "downstream_barrier_id", "upNetID": "downNetID"})
            .join(
                cur_barrier_networks.select(["id", "upNetID", "downNetID"]).rename_columns(
                    {"id": "upstream_barrier_id"}
                ),
                "downNetID",
                join_type="inner",
            )
            .select(["downstream_barrier_id", "upstream_barrier_id"])
        )

        if len(network_pairs):
            other_networks = cur_barrier_networks.filter(
                pc.equal(pc.is_in(cur_barrier_networks["id"], network_pairs["downstream_barrier_id"]), False)
            )

            ids = pc.unique(network_pairs["downstream_barrier_id"])

            # create a network of networks facing upstream
            up_network_graph = DirectedGraph(
                network_pairs["downstream_barrier_id"].to_numpy().astype("int64"),
                network_pairs["upstream_barrier_id"].to_numpy().astype("int64"),
            )
            pairs = pa.Table.from_arrays(
                up_network_graph.network_pairs(ids.to_numpy().astype("int64")).T.astype("uint64"),
                ["downstream_barrier_id", "upstream_barrier_id"],
            )

            ### recalculate upstream fields so that they are based on any sibling
            # barriers in the same subnetwork and removed in the same year having
            # already been removed
            # NOTE: we intentionally keep self-pairs because we are combining together all upstreams
            # update the upstream stats for non-isolated networks
            upstream_cols = [
                c
                for c in cur_barrier_networks.column_names
                if "Upstream" in c and (c.endswith("Acres") or c.endswith("Miles"))
            ] + ["FloodplainAcres", "NatFloodplainAcres"]
            upstream_stats = (
                pairs.join(cur_barrier_networks.select(["id"] + upstream_cols), "upstream_barrier_id", "id")
                .group_by("downstream_barrier_id")
                .aggregate([(c, "sum") for c in upstream_cols])
                .rename_columns({f"{c}_sum": c for c in upstream_cols})
            )

            # NOTE: sibling networks are just the DOWNSTREAM siblings; others are in other_networks above
            sibling_networks = (
                cur_barrier_networks.filter(
                    pc.is_in(cur_barrier_networks["id"], pc.unique(pairs["downstream_barrier_id"]))
                )
                .drop(columns=upstream_cols)
                .join(upstream_stats, "id", "downstream_barrier_id")
            )

            updated = {
                # recalculate gain miles
                "GainMiles": pc.if_else(
                    sibling_networks["TerminatesDownstream"],
                    sibling_networks["TotalUpstreamMiles"],
                    pc.if_else(
                        pc.equal(sibling_networks["upNetID"], 0),
                        0,
                        pc.min_element_wise(
                            sibling_networks["TotalUpstreamMiles"], sibling_networks["FreeDownstreamMiles"]
                        ),
                    ),
                ),
                "FunctionalNetworkMiles": pc.add(
                    sibling_networks["TotalUpstreamMiles"], sibling_networks["FreeDownstreamMiles"]
                ),
                "PerennialGainMiles": pc.if_else(
                    sibling_networks["TerminatesDownstream"],
                    sibling_networks["PerennialUpstreamMiles"],
                    pc.if_else(
                        pc.equal(sibling_networks["upNetID"], 0),
                        0,
                        pc.min_element_wise(
                            sibling_networks["PerennialUpstreamMiles"], sibling_networks["FreePerennialDownstreamMiles"]
                        ),
                    ),
                ),
                "PerennialFunctionalNetworkMiles": pc.add(
                    sibling_networks["PerennialUpstreamMiles"], sibling_networks["FreePerennialDownstreamMiles"]
                ),
                # recalculate percent fields based on updated upstream totals
                "PercentUnaltered": percent(
                    pc.divide(sibling_networks["UnalteredUpstreamMiles"], sibling_networks["TotalUpstreamMiles"])
                ),
                "PercentPerennialUnaltered": percent(
                    pc.if_else(
                        pc.greater(sibling_networks["PerennialUpstreamMiles"], 0),
                        pc.divide(
                            sibling_networks["PerennialUnalteredUpstreamMiles"],
                            sibling_networks["PerennialUpstreamMiles"],
                        ),
                        0,
                    )
                ),
                "PercentResilient": percent(
                    pc.divide(sibling_networks["ResilientUpstreamMiles"], sibling_networks["TotalUpstreamMiles"])
                ),
                "PercentCold": percent(
                    pc.divide(sibling_networks["ColdUpstreamMiles"], sibling_networks["TotalUpstreamMiles"])
                ),
                "Landcover": percent(
                    pc.if_else(
                        pc.greater(sibling_networks["FloodplainAcres"], 0),
                        pc.divide(sibling_networks["NatFloodplainAcres"], sibling_networks["FloodplainAcres"]),
                        0,
                    )
                ),
            }

            updated.update(
                {
                    "EffectiveGainMiles": updated["GainMiles"],
                    "GainMilesUpstreamSide": pc.if_else(
                        pc.or_(
                            pc.equal(sibling_networks["upNetID"], 0),
                            np.isclose(updated["GainMiles"], sibling_networks["TotalUpstreamMiles"]),
                        ),
                        True,
                        False,
                    ),
                    "EffectivePerennialGainMiles": updated["PerennialGainMiles"],
                    "PerennialGainMilesUpstreamSide": pc.if_else(
                        pc.or_(
                            pc.equal(sibling_networks["upNetID"], 0),
                            np.isclose(updated["PerennialGainMiles"], sibling_networks["PerennialUpstreamMiles"]),
                        ),
                        True,
                        False,
                    ),
                }
            )

            sibling_networks = pa.Table.from_pydict(
                {c: updated.get(c, sibling_networks[c]) for c in sibling_networks.column_names}
            )

            ### copy network segments for each downstream sibling removed barrier
            # so that each extends to top of network
            tmp_segments = (
                cur_segments.join(
                    pairs.filter(pc.not_equal(pairs["downstream_barrier_id"], pairs["upstream_barrier_id"])),
                    "id",
                    "upstream_barrier_id",
                )
                .drop(["id"])
                .rename_columns({"downstream_barrier_id": "id"})
            )
            cur_segments = pa.concat_tables(
                [cur_segments, tmp_segments.select(cur_segments.column_names)]
            ).combine_chunks()

            # IMPORTANT: to query out the full aggregated upstream network for a barrier,
            # query segments on barrier_id == <id>
            # to query out the original unaggregated upstream network, use
            # (barrier_id == <id>) & (networkID == cur_networks.loc[<id>].upNetID)

            # recalculate size classes
            sizeclasses = (
                pa.Table.from_pydict(
                    {
                        "id": cur_segments["id"],
                        "sizeclass": cur_segments["sizeclass"],
                        "perennial_sizeclass": pc.if_else(
                            cur_segments["intermittent"], None, cur_segments["sizeclass"]
                        ),
                    }
                )
                .group_by("id")
                .aggregate([("sizeclass", "count_distinct"), ("perennial_sizeclass", "count_distinct")])
                .rename_columns(
                    {
                        "sizeclass_count_distinct": "SizeClasses",
                        "perennial_sizeclass_count_distinct": "PerennialSizeClasses",
                    }
                )
            )
            sibling_networks = sibling_networks.drop(["SizeClasses", "PerennialSizeClasses"]).join(sizeclasses, "id")

            # cast to enable merging
            mismatch = [c for c in sibling_networks.column_names if c not in other_networks.column_names] + [
                c for c in other_networks.column_names if c not in sibling_networks.column_names
            ]
            if mismatch:
                raise ValueError(f"ERROR: mismatched columns between sibling and other networks: {mismatch}")

            sibling_networks = sibling_networks.select(other_networks.column_names).cast(other_networks.schema)
            cur_barrier_networks = pa.concat_tables([sibling_networks, other_networks]).combine_chunks()

            ### Recalculate effective gain miles to avoid double-counting the
            # same parts of an upstream network already gained by a removed upstream barrier
            pairs = (
                # drop self-pairs; all calculations below rely on using only non-self upstream values
                pairs.filter(pc.not_equal(pairs["downstream_barrier_id"], pairs["upstream_barrier_id"]))
                .join(
                    cur_barrier_networks.select(
                        [
                            "id",
                            "GainMiles",
                            "GainMilesUpstreamSide",
                            "PerennialGainMiles",
                            "PerennialGainMilesUpstreamSide",
                        ]
                    ),
                    "downstream_barrier_id",
                    "id",
                )
                .rename_columns(
                    {
                        "GainMiles": "GainMiles_prev",
                        "PerennialGainMiles": "PerennialGainMiles_prev",
                        "downstream_barrier_id": "id",
                    }
                )
                .join(
                    cur_barrier_networks.select(["id", "GainMiles", "PerennialGainMiles"]),
                    "upstream_barrier_id",
                    "id",
                )
                .rename_columns(
                    {
                        "GainMiles": "GainMiles_upstream",
                        "PerennialGainMiles": "PerennialGainMiles_upstream",
                    }
                )
            )

            # only adjust gain miles that were from the upstream side of each downstream barrier in question
            # subtract the sum of gain miles for upstream barriers
            gain_miles_adj = (
                pairs.filter(pairs["GainMilesUpstreamSide"])
                .group_by("id", use_threads=False)
                .aggregate([("GainMiles_prev", "first"), ("GainMiles_upstream", "sum")])
                .rename_columns(
                    {
                        "GainMiles_prev_first": "GainMiles_prev",
                        "GainMiles_upstream_sum": "GainMiles_upstream",
                    }
                )
            )
            gain_miles_adj = gain_miles_adj.append_column(
                "GainMiles_updated",
                pc.subtract(gain_miles_adj["GainMiles_prev"], gain_miles_adj["GainMiles_upstream"]),
            )

            # do the same thing for perennial miles, which might gain from a different side
            perennial_gain_miles_adj = (
                pairs.filter(pairs["PerennialGainMilesUpstreamSide"])
                .group_by("id", use_threads=False)
                .aggregate([("PerennialGainMiles_prev", "first"), ("PerennialGainMiles_upstream", "sum")])
                .rename_columns(
                    {
                        "PerennialGainMiles_prev_first": "PerennialGainMiles_prev",
                        "PerennialGainMiles_upstream_sum": "PerennialGainMiles_upstream",
                    }
                )
            )
            perennial_gain_miles_adj = perennial_gain_miles_adj.append_column(
                "PerennialGainMiles_updated",
                pc.subtract(
                    perennial_gain_miles_adj["PerennialGainMiles_prev"],
                    perennial_gain_miles_adj["PerennialGainMiles_upstream"],
                ),
            )

            cur_barrier_networks = cur_barrier_networks.join(
                gain_miles_adj.select(["id", "GainMiles_updated"]), "id"
            ).join(perennial_gain_miles_adj.select(["id", "PerennialGainMiles_updated"]), "id")

            updated = {
                "EffectiveGainMiles": pc.if_else(
                    pc.is_valid(cur_barrier_networks["GainMiles_updated"]),
                    pc.cast(cur_barrier_networks["GainMiles_updated"], pa.float32()),
                    cur_barrier_networks["EffectiveGainMiles"],
                ),
                "EffectivePerennialGainMiles": pc.if_else(
                    pc.is_valid(cur_barrier_networks["PerennialGainMiles_updated"]),
                    pc.cast(cur_barrier_networks["PerennialGainMiles_updated"], pa.float32()),
                    cur_barrier_networks["EffectivePerennialGainMiles"],
                ),
            }
            cur_barrier_networks = pa.Table.from_pydict(
                {
                    c: updated.get(c, cur_barrier_networks[c])
                    for c in cur_barrier_networks.column_names
                    if c not in {"GainMiles_updated", "PerennialGainMiles_updated"}
                }
            )

        cur_barrier_networks = cur_barrier_networks.drop(
            ["GainMilesUpstreamSide", "PerennialGainMilesUpstreamSide", "TerminatesDownstream"]
        )

        if merged_networks is None:
            merged_networks = cur_barrier_networks
        else:
            merged_networks = pa.concat_tables([merged_networks, cur_barrier_networks])

        cur_segments = cur_segments.select(["id", "networkID", "lineID", "YearRemoved"])
        if merged_segments is None:
            merged_segments = cur_segments
        else:
            merged_segments = pa.concat_tables([merged_segments, cur_segments])

    # fill nulls and cast floats
    int_cols = [f.name for f in merged_networks.schema if pa.types.is_integer(f.type)]
    float_cols = [f.name for f in merged_networks.schema if pa.types.is_floating(f.type)]
    bool_cols = [f.name for f in merged_networks.schema if pa.types.is_boolean(f.type)]
    filled = {
        **{c: pc.fill_null(merged_networks[c], 0) for c in int_cols},
        # round floating point columns to 3 decimals
        **{c: pc.cast(pc.round(pc.fill_null(merged_networks[c], 0), 3), pa.float32()) for c in float_cols},
        **{c: pc.fill_null(merged_networks[c], False) for c in bool_cols},
    }
    merged_networks = pa.Table.from_pydict(
        {c: filled.get(c, merged_networks[c]) for c in merged_networks.column_names}
    ).combine_chunks()

    write_feather(merged_networks, out_dir / f"removed_{network_type}_networks.feather")
    write_feather(merged_segments, out_dir / f"removed_{network_type}_network_segments.feather")

print(f"\n\n=============================\nAll done in {time() - start:.2f}s")
