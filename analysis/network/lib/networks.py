from time import time

import pandas as pd
import numpy as np

from analysis.constants import HUC2_EXITS

from analysis.lib.graph.speedups import DirectedGraph
from analysis.network.lib.stats import (
    calculate_upstream_network_stats,
    calculate_downstream_stats,
)


def connect_huc2s(joins):
    """Find all connected groups of HUC2s.

    This reads in all flowline joins for all HUC2s and detects those that cross
    HUC2 boundaries to determine which HUC2s are connected.

    Region 03 is specifically prevented from connecting to 08.

    Parameters
    ----------
    joins : DataFrame
        contains HUC2, downstream_id, upstream_id, downstream, type

    Returns
    -------
    (groups, joins)
        groups: list of sets; each set contains one or more HUC2s
        joins: updated joins across HUC2 boundaries
    """

    ### Extract the joins that cross region boundaries, and set new upstream IDs for them
    # We can join on the ids we generate (upstream_id, downstream_id) because there are no
    # original flowlines split at HUC2 join areas

    cross_region = joins.loc[
        (joins.type == "huc_in") & (joins.upstream_id == 0),
        ["upstream", "downstream", "downstream_id", "type", "HUC2"],
    ].rename(columns={"HUC2": "downstream_HUC2"})

    cross_region = cross_region.join(
        joins.loc[
            joins.downstream.isin(cross_region.upstream),
            ["downstream", "downstream_id", "HUC2"],
        ]
        .set_index("downstream")
        .rename(columns={"downstream_id": "upstream_id", "HUC2": "upstream_HUC2"}),
        on="upstream",
        how="inner",
    ).drop_duplicates()

    # Drop connections from region 03 into 08; these are negligible with respect
    # to results but avoids lumping already very large analysis regions
    cross_region = cross_region.loc[cross_region.upstream_HUC2 != "03"].copy()

    # update joins to include those that cross region boundaries
    for row in cross_region.itertuples():
        # update the upstream side of the join
        ix = joins.upstream_id == row.upstream_id
        joins.loc[ix, "downstream"] = row.downstream
        joins.loc[ix, "downstream_id"] = row.downstream_id
        joins.loc[ix, "type"] = "huc2_join"
        # update the downstream side of the join
        ix = (joins.downstream_id == row.downstream_id) & (joins.upstream_id == 0)
        joins.loc[ix, "upstream_id"] = row.upstream_id

    joins = joins.drop_duplicates(subset=["downstream_id", "upstream_id"]).copy()

    # add information about the HUC2 drain points
    huc2_exits = set()
    for exits in HUC2_EXITS.values():
        huc2_exits.update(exits)

    joins.loc[
        (joins.downstream == 0) & joins.upstream.isin(huc2_exits), "type"
    ] = "huc2_drain"

    # make symmetric pairs of HUC2s so that we get all those that are connected
    tmp = cross_region[["upstream_HUC2", "downstream_HUC2"]]
    source = np.append(tmp.upstream_HUC2, tmp.downstream_HUC2)
    target = np.append(tmp.downstream_HUC2, tmp.upstream_HUC2)

    # Create a graph to coalesce into connected components
    # Note: these are temporarily converted to int64 to use DirectedGraph
    g = DirectedGraph(source.astype("int64"), target.astype("int64"))
    connected_huc2 = g.components()

    # convert back to strings
    connected_huc2 = [{f"{huc2:02}" for huc2 in group} for group in connected_huc2]

    isolated_huc2 = [
        {huc2}
        for huc2 in np.setdiff1d(
            joins.HUC2.unique(),
            np.unique(
                np.append(cross_region.upstream_HUC2, cross_region.downstream_HUC2)
            ),
        )
    ]

    return (connected_huc2 + isolated_huc2), joins


def generate_networks(network_graph, root_ids):
    """
    Parameters
    ----------
    network_graph : DirectedGraph
    root_ids : pandas.Series
        Series of starting points for each network.  For a network facing upstream,
        these are the downstream-most ID for each network to be created.  For
        a network facing downstream, these are the upstream-most ID for each.
    """

    segments = pd.Series(
        network_graph.descendants(root_ids),
        index=root_ids,
        name="lineID",
        dtype="object",
    ).explode()
    segments.index.name = "networkID"

    # add root to network
    segments = pd.concat(
        [
            segments.reset_index(),
            pd.DataFrame(
                {"lineID": root_ids, "networkID": root_ids},
            ),
        ],
        ignore_index=True,
        sort=False,
    ).set_index("networkID")

    segments.index.name = "networkID"
    segments = segments.reset_index()
    return segments.sort_values(by=["networkID", "lineID"])


def create_networks(joins, barrier_joins, lineIDs):
    """Create networks that start from natural origins in network or from
    barriers.

    Parameters
    ----------
    joins : DataFrame
        contains upstream_id, downstream_id
    barrier_joins : DataFrame
        contains upstream_id, downstream_id; indexed on id
    lineIDs : ndarray
        flowline IDs within analysis area

    Returns
    -------
    DataFrame
        contains networkID and lineID
    """

    # lineIDs of flowlines immediately upstream of barriers
    barrier_upstream_idx = barrier_joins.loc[
        barrier_joins.upstream_id != 0
    ].upstream_id.unique()

    # extract flowline joins that are not at the endpoints of the network and
    # are not cut by barriers
    upstream_joins = joins.loc[
        (joins.upstream_id != 0)
        & (joins.downstream_id != 0)
        & (~joins.upstream_id.isin(barrier_upstream_idx)),
        ["downstream_id", "upstream_id"],
    ].drop_duplicates(subset=["downstream_id", "upstream_id"])

    ### Get list of network root IDs
    # Create networks from all terminal nodes (have no downstream nodes) up to barriers.
    # Exclude any segments where barriers are also on the downstream terminals to prevent duplicates.
    # Note: origin_idx are also those that have a downstream_id but are not the upstream_id of another node

    # anything that has no downstream is an origin
    origin_idx = joins.loc[joins.downstream_id == 0].upstream_id.unique()

    # find joins that are not marked as terminated, but do not have upstreams in the region
    unterminated = joins.loc[
        (joins.downstream_id != 0) & ~joins.downstream_id.isin(joins.upstream_id)
    ]
    # if downstream_id is not in upstream_id for region, and is in flowlines, add downstream id as origin
    origin_idx = np.append(
        origin_idx,
        unterminated.loc[
            unterminated.downstream_id.isin(lineIDs)
        ].downstream_id.unique(),
    )

    # otherwise add upstream id
    origin_idx = np.append(
        origin_idx,
        unterminated.loc[
            ~unterminated.downstream_id.isin(lineIDs)
        ].upstream_id.unique(),
    )

    # remove any origins that have associated barriers
    # this also ensures a unique list
    origin_idx = np.setdiff1d(origin_idx, barrier_upstream_idx)

    ### Extract all origin points and barrier segments that immediately terminate upstream
    # these are single segments and don't need to go through the full logic for constructing
    # networks.

    # single segments are either origin or barrier segments that are not downstream of other segments
    # (meaning they are at the top of the network).
    single_segment_idx = np.setdiff1d(
        np.append(origin_idx, barrier_upstream_idx), upstream_joins.downstream_id
    ).astype("uint32")

    single_segment_networks = pd.DataFrame(
        index=pd.Series(single_segment_idx, name="lineID")
    )
    # their networkID is the same as the segment
    single_segment_networks["networkID"] = single_segment_networks.index
    single_segment_networks["type"] = "origin"
    single_segment_networks.loc[
        single_segment_networks.index.isin(barrier_upstream_idx), "type"
    ] = "barrier"

    if len(single_segment_networks) > 0:
        print(f"{len(single_segment_networks):,} networks are a single segment long")

    ### Create a directed graph facing upstream
    upstream_graph = DirectedGraph(
        upstream_joins.downstream_id.values.astype("int64"),
        upstream_joins.upstream_id.values.astype("int64"),
    )

    ### Find all origins that are not single segments
    # origin segments are the root of each non-barrier origin point up to barriers
    # segments are indexed by the id of the segment at the root for each network
    origins_with_upstreams = pd.Series(
        np.setdiff1d(origin_idx, single_segment_networks.index), name="networkID"
    )

    print(f"Generating networks for {len(origins_with_upstreams):,} origin points")

    origin_network_segments = generate_networks(
        upstream_graph, origins_with_upstreams.values
    )
    origin_network_segments["type"] = "origin"

    # barrier segments are the root of each upstream network from each barrier
    # segments are indexed by the id of the segment at the root for each network
    barriers_with_upstreams = pd.Series(
        np.setdiff1d(barrier_upstream_idx, single_segment_networks.index),
        name="networkID",
    )

    print(f"Generating networks for {len(barriers_with_upstreams):,} barriers")
    barrier_network_segments = generate_networks(
        upstream_graph, barriers_with_upstreams.values
    )
    barrier_network_segments["type"] = "barrier"

    # Append network types back together
    up_network_df = pd.concat(
        [
            single_segment_networks.reset_index(),
            origin_network_segments.reset_index(drop=True),
            barrier_network_segments.reset_index(drop=True),
        ],
        sort=False,
        ignore_index=False,
    ).reset_index(drop=True)
    up_network_df.networkID = up_network_df.networkID.astype("uint32")
    up_network_df.lineID = up_network_df.lineID.astype("uint32")

    # check for duplicates
    s = up_network_df.groupby("lineID").size()
    s = s.loc[s > 1]
    if len(s):
        s.rename("count").reset_index().to_feather("/tmp/dup_networks.feather")
        raise ValueError(
            f"lineIDs are found in multiple networks: {', '.join([str(v)  for v in s.index.values.tolist()[:10]])}..."
        )

    ### Handle multiple upstreams
    # A given barrier may have > 1 upstream segment, some have 3+
    # Some might be single segments, so we can't just focus on barrier segments
    # Group by id
    upstream_count = barrier_joins.groupby(level=0).size()
    multiple_upstreams = barrier_joins.loc[
        barrier_joins.index.isin(upstream_count.loc[upstream_count > 1].index.unique())
    ]

    if len(multiple_upstreams):
        print(
            f"Merging multiple upstream networks for barriers at network junctions, affects {len(multiple_upstreams):,} networks"
        )

        # For each barrier with multiple upstreams, coalesce their networkIDs
        for id in multiple_upstreams.index.unique():
            upstream_ids = multiple_upstreams.loc[id].upstream_id
            networkID = upstream_ids.iloc[0]

            # Set all upstream networks for this barrier to the ID of the first
            up_network_df.loc[
                up_network_df.networkID.isin(upstream_ids), ["networkID"]
            ] = networkID

    ### Extract linear networks facing downstream
    # This assumes that there are no divergences because loops are removed
    # from the joins
    # NOTE: it is expected that a given lineID will be claimed as a downstream
    # of many downstream networks.
    print("Extracting downstream linear networks for each barrier")

    # lineIDs of flowlines immediately downstream of barriers
    barrier_downstream_idx = barrier_joins.loc[
        barrier_joins.downstream_id != 0
    ].downstream_id.unique()

    # break joins at barriers
    downstream_joins = joins.loc[
        (joins.upstream_id != 0)
        & (joins.downstream_id != 0)
        & (~joins.downstream_id.isin(barrier_downstream_idx)),
        ["downstream_id", "upstream_id"],
    ].drop_duplicates(subset=["downstream_id", "upstream_id"])

    downstream_graph = DirectedGraph(
        downstream_joins.upstream_id.values.astype("int64"),
        downstream_joins.downstream_id.values.astype("int64"),
    )

    down_network_df = generate_networks(downstream_graph, barrier_downstream_idx)

    # lineIDs that are null are single-segment networks; fill them with the
    # networkID
    ix = down_network_df.lineID.isnull()
    down_network_df.loc[ix, "lineID"] = down_network_df.loc[ix].networkID

    down_network_df = down_network_df.drop_duplicates()

    down_network_df.networkID = down_network_df.networkID.astype("uint32")
    down_network_df.lineID = down_network_df.lineID.astype("uint32")

    return (up_network_df, down_network_df)


def create_barrier_networks(
    barriers, barrier_joins, focal_barrier_joins, joins, flowlines, network_type
):
    """Calculate networks based on barriers and network origins

    Parameters
    ----------
    barriers : DataFrame
        barrier info for all barriers within the HUC2 group to joined back to
        barrier networks (inner join)
    barrier_joins : DataFrame
        all barriers joins within the HUC2 group (all types)
    focal_barrier_joins : DataFrame
        barrier joins that denote network breaks
    joins : DataFrame
        all joins within the HUC2 group, used as the basis for constructing the
        networks
    flowlines : DataFrame
        flowline info that gets joined to the networkID for this type
    network_type : str
        name of network type, one of NETWORK_TYPES keys

    Returns
    -------
    (DataFrame, DataFrame, DataFrame)
        tuple of barrier_networks, network_stats, flowlines
    """
    network_start = time()

    upstream_networks, downstream_linear_networks = create_networks(
        joins,
        focal_barrier_joins,
        flowlines.index,
    )

    upstream_networks = upstream_networks.set_index("lineID").networkID
    print(
        f"{len(upstream_networks.unique()):,} networks created in {time() - network_start:.2f}s"
    )

    # join networkID to flowlines
    flowlines = flowlines.join(upstream_networks.rename(network_type))

    up_network_df = (
        flowlines.join(upstream_networks, how="inner")
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

    upstream_stats = calculate_upstream_network_stats(
        up_network_df,
        joins,
        focal_barrier_joins,
        barrier_joins,
    )
    # WARNING: because not all flowlines have associated catchments, they are missing
    # natfldpln

    # lineIDs that terminate in marine or downstream exits of HUC2
    marine_ids = joins.loc[joins.marine].upstream_id.unique()
    great_lake_ids = joins.loc[joins.great_lakes].upstream_id.unique()
    exit_ids = joins.loc[joins.type == "huc2_drain"].upstream_id.unique()

    # downstream_stats are indexed on the ID of the barrier
    downstream_stats = calculate_downstream_stats(
        down_network_df,
        focal_barrier_joins,
        barrier_joins,
        marine_ids,
        great_lake_ids,
        exit_ids,
    )

    ### Join upstream network stats to downstream network stats
    # NOTE: a network will only have downstream stats if it is upstream of a
    # barrier
    network_stats = upstream_stats.join(
        downstream_stats.join(focal_barrier_joins.upstream_id).set_index("upstream_id")
    )
    network_stats.index.name = "networkID"

    # Fill missing data
    for kind in ["waterfalls", "dams", "small_barriers", "road_crossings"]:
        col = f"totd_{kind}"
        network_stats[col] = network_stats[col].fillna(0).astype("uint32")

    for col in ["flows_to_ocean", "flows_to_great_lakes", "exits_region"]:
        network_stats[col] = network_stats[col].fillna(False).astype("bool")

    network_stats.barrier = network_stats.barrier.fillna("")
    network_stats.miles_to_outlet = network_stats.miles_to_outlet.fillna(0)

    # set to_ocean, to_great_lakes, and exits_region for functional networks that terminate
    # in marine or Great Lakes or leave region and have no downstream barrier
    network_stats.loc[network_stats.index.isin(marine_ids), "flows_to_ocean"] = True
    network_stats.loc[
        network_stats.index.isin(great_lake_ids), "flows_to_great_lakes"
    ] = True
    # if segments connect to marine they also leave the region
    network_stats.loc[
        network_stats.index.isin(np.unique(np.append(marine_ids, exit_ids))),
        "exits_region",
    ] = True

    print(f"calculated stats in {time() - stats_start:.2f}s")

    #### Calculate up and downstream network attributes for barriers
    # NOTE: some statistics (totd_*, miles_to_outlet, flows_to_ocean, exits_region)
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
        .join(barriers.set_index("id")[["kind", "intermittent", "HUC2"]])
    )

    # fill missing data
    # if there is no upstream network, the network of a barrier is in the
    # same HUC2 as the barrier
    ix = barrier_networks.origin_HUC2.isnull()
    barrier_networks.loc[ix, "origin_HUC2"] = barrier_networks.loc[ix].HUC2

    barrier_networks.barrier = barrier_networks.barrier.fillna("")
    barrier_networks.origin_HUC2 = barrier_networks.origin_HUC2.fillna("")
    barrier_networks.flows_to_ocean = barrier_networks.flows_to_ocean.fillna(False)
    barrier_networks.flows_to_great_lakes = (
        barrier_networks.flows_to_great_lakes.fillna(False)
    )
    barrier_networks.exits_region = barrier_networks.exits_region.fillna(False)
    # if isolated network or connects to marine / Great Lakes / exit, there
    # are no further miles downstream from this network
    barrier_networks.miles_to_outlet = barrier_networks.miles_to_outlet.fillna(
        0
    ).astype("float32")
    # total drainage area will be 0 for barriers at top of network
    barrier_networks.fn_dakm2 = barrier_networks.fn_dakm2.fillna(0).astype("float32")

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
                barrier_networks[col] = barrier_networks[col].fillna(0).astype("uint32")

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

    ### Calculate miles GAINED if barrier is removed
    # this is the lesser of the upstream or free downstream lengths.
    # Non-free miles downstream (downstream waterbodies) are omitted from this analysis.
    barrier_networks["GainMiles"] = barrier_networks[
        ["TotalUpstreamMiles", "FreeDownstreamMiles"]
    ].min(axis=1)
    barrier_networks["PerennialGainMiles"] = barrier_networks[
        ["PerennialUpstreamMiles", "FreePerennialDownstreamMiles"]
    ].min(axis=1)

    # For barriers that terminate in marine areas or Great Lakes, their GainMiles is only based on the upstream miles
    ix = (barrier_networks.miles_to_outlet == 0) & (
        (barrier_networks.flows_to_ocean == 1) | (barrier_networks.flows_to_great_lakes)
    )
    barrier_networks.loc[ix, "GainMiles"] = barrier_networks.loc[ix].TotalUpstreamMiles
    barrier_networks.loc[ix, "PerennialGainMiles"] = barrier_networks.loc[
        ix
    ].PerennialUpstreamMiles

    # TotalNetworkMiles is sum of upstream and free downstream miles
    barrier_networks["TotalNetworkMiles"] = barrier_networks[
        ["TotalUpstreamMiles", "FreeDownstreamMiles"]
    ].sum(axis=1)
    barrier_networks["TotalPerennialNetworkMiles"] = barrier_networks[
        ["PerennialUpstreamMiles", "FreePerennialDownstreamMiles"]
    ].sum(axis=1)

    # Round floating point columns to 3 decimals
    for column in [c for c in barrier_networks.columns if c.endswith("Miles")]:
        barrier_networks[column] = barrier_networks[column].round(3).fillna(-1)

    ### Round PercentUnaltered and PercentAltered to integers
    for subset in ["", "Perennial"]:
        barrier_networks[f"Percent{subset}Unaltered"] = (
            barrier_networks[f"Percent{subset}Unaltered"].round().astype("int8")
        )
        barrier_networks[f"Percent{subset}Altered"] = (
            100 - barrier_networks[f"Percent{subset}Unaltered"]
        )

    return barrier_networks, network_stats, flowlines
