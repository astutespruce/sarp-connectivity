from pathlib import Path
from time import time
import warnings

import pandas as pd
import numpy as np

from analysis.constants import HUC2_EXITS, NETWORK_TYPES

from analysis.lib.graph.speedups import DirectedGraph, LinearDirectedGraph
from analysis.network.lib.stats import (
    calculate_upstream_network_stats,
    calculate_upstream_mainstem_stats,
    calculate_downstream_stats,
)

pd.set_option("future.no_silent_downcasting", True)
warnings.filterwarnings("ignore", message=".*DataFrame is highly fragmented.*")

data_dir = Path("data")


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
    # Note: we drop connections from region 03 into 08; these are negligible with respect
    # to results but avoids lumping already very large analysis regions

    cross_region = joins.loc[
        (joins.type == "huc_in") & (joins.upstream_id == 0),
        ["upstream", "downstream", "downstream_id", "type", "HUC2"],
    ].rename(columns={"HUC2": "downstream_HUC2"})

    cross_region = cross_region.join(
        joins.loc[
            joins.downstream.isin(cross_region.upstream) & (joins.HUC2 != "03"),
            ["downstream", "downstream_id", "HUC2"],
        ]
        .set_index("downstream")
        .rename(columns={"downstream_id": "upstream_id", "HUC2": "upstream_HUC2"}),
        on="upstream",
        how="inner",
    ).drop_duplicates()

    # update joins to include those that cross region boundaries
    joins = joins.join(
        # upstream side of join
        cross_region[["upstream_id", "downstream", "downstream_id"]].set_index("upstream_id"),
        on="upstream_id",
        rsuffix="_new_upstream",
    ).join(
        # downstream side of join
        cross_region[["downstream_id", "upstream_id"]].set_index("downstream_id"),
        on="downstream_id",
        rsuffix="_new_downstream",
    )

    # update upstream side
    ix = joins.downstream_id_new_upstream.notnull()
    tmp = joins.loc[ix]
    joins.loc[ix, "downstream"] = tmp.downstream_new_upstream.astype(joins.downstream.dtype)
    joins.loc[ix, "downstream_id"] = tmp.downstream_id_new_upstream.astype(joins.downstream_id.dtype)
    joins.loc[ix, "type"] = "huc2_join"

    # update downstream side
    ix = joins.upstream_id_new_downstream.notnull() & (joins.upstream_id == 0)
    joins.loc[ix, "upstream_id"] = joins.loc[ix].upstream_id_new_downstream.astype(joins.upstream_id.dtype)

    joins = joins.drop(
        columns=[
            "downstream_new_upstream",
            "downstream_id_new_upstream",
            "upstream_id_new_downstream",
        ]
    )

    joins = joins.drop_duplicates(subset=["downstream_id", "upstream_id"]).copy()

    # add information about the HUC2 drain points
    huc2_exits = set()
    for exits in HUC2_EXITS.values():
        huc2_exits.update(exits)

    joins.loc[(joins.downstream == 0) & joins.upstream.isin(huc2_exits), "type"] = "huc2_drain"

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
            np.unique(np.append(cross_region.upstream_HUC2, cross_region.downstream_HUC2)),
        )
    ]

    return (connected_huc2 + isolated_huc2), joins


def create_networks(joins, barrier_joins, flowlines):
    """Create networks that start from natural origins in network or from
    barriers.

    Parameters
    ----------
    joins : DataFrame
        contains upstream_id, downstream_id
    barrier_joins : DataFrame
        contains upstream_id, downstream_id; indexed on id
    flowlines : DataFrame
        flowline within analysis area, indexed on lineID

    Returns
    -------
    (Series, Series, Series)
        (upstream functional network, upstream mainstem network, downstream linear network)
        where each contains is indexed on lineID and haves values for networkID
    """

    lineIDs = flowlines.index

    # lineIDs of flowlines immediately upstream of barriers
    barrier_upstream_idx = barrier_joins.loc[barrier_joins.upstream_id != 0].upstream_id.unique()

    ### Create a directed graph facing upstream
    # extract flowline joins that are not at the endpoints of the network and
    # are not cut by barriers
    upstream_joins = joins.loc[
        (joins.upstream_id != 0) & (joins.downstream_id != 0) & (~joins.upstream_id.isin(barrier_upstream_idx)),
        ["downstream_id", "upstream_id"],
    ].drop_duplicates()

    upstream_graph = DirectedGraph(
        upstream_joins.downstream_id.values.astype("int64"),
        upstream_joins.upstream_id.values.astype("int64"),
    )

    ### Get list of network root IDs
    # Create networks from all terminal nodes (have no downstream nodes) up to barriers.
    # Exclude any segments where barriers are also on the downstream terminals to prevent duplicates.
    # Note: origin_idx are also those that have a downstream_id but are not the upstream_id of another node

    # anything that has no downstream is an origin
    origin_idx = joins.loc[joins.downstream_id == 0].upstream_id.unique()

    # find joins that are not marked as terminated, but do not have upstreams in the region
    unterminated = joins.loc[(joins.downstream_id != 0) & ~joins.downstream_id.isin(joins.upstream_id)]
    # if downstream_id is not in upstream_id for region, and is in flowlines, add downstream id as origin
    origin_idx = np.append(
        origin_idx,
        unterminated.loc[unterminated.downstream_id.isin(lineIDs)].downstream_id.unique(),
    )

    # otherwise add upstream id
    origin_idx = np.append(
        origin_idx,
        unterminated.loc[~unterminated.downstream_id.isin(lineIDs)].upstream_id.unique(),
    )

    # remove any origins that have associated barriers
    # this also ensures a unique list
    origin_idx = np.setdiff1d(origin_idx, barrier_upstream_idx)

    print(f"Generating networks for {len(origin_idx):,} origin points")
    if len(origin_idx) > 0:
        origin_network_segments = pd.DataFrame(
            upstream_graph.network_pairs(origin_idx.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")

    else:
        origin_network_segments = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    origin_network_segments["type"] = "origin"

    print(f"Generating networks for {len(barrier_upstream_idx):,} barriers")
    if len(barrier_upstream_idx):
        # barrier segments are the root of each upstream network from each barrier
        # segments are indexed by the id of the segment at the root for each network
        barrier_network_segments = pd.DataFrame(
            upstream_graph.network_pairs(barrier_upstream_idx.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")

    else:
        barrier_network_segments = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")
    #     barrier_network_segments = pd.DataFrame({"networkID": np.array([], "uint32"), "lineID": np.array([], "uint32")})

    barrier_network_segments["type"] = "barrier"

    # Append network types back together
    up_network_df = pd.concat(
        [
            origin_network_segments,
            barrier_network_segments,
        ],
        sort=False,
        ignore_index=False,
    ).reset_index(drop=True)

    ### Handle multiple upstreams for origin / barrier networks
    # A given barrier may have > 1 upstream segment, some have 3+
    # Note: we do this for origin networks because those may actually be barrier
    # networks when calculating removed barrier networks, as well as trying to
    # create better downstream total networks.  This intentionally does not try
    # to fuse sibling networks at a downstream-most origin point though (downstream_id==0)

    # find all networks where the downstream side of the network origin is a junction
    networks_at_junctions = np.intersect1d(
        up_network_df.networkID.unique(), joins.loc[joins.junction].upstream_id.unique()
    )
    if len(networks_at_junctions):
        print(
            f"Merging multiple upstream networks at network junctions, affects {len(networks_at_junctions):,} networks"
        )
        up_network_df = up_network_df.join(flowlines[["TotDASqKm", "StreamOrder"]], on="lineID")

        downstreams = joins.loc[joins.upstream_id.isin(networks_at_junctions)].downstream_id.unique()
        for downstream_id in downstreams:
            # find all the networks that have the same downstream and fuse them
            # sort to preserve the one with largest drainage area / stream order
            networkIDs = (
                up_network_df.loc[
                    up_network_df.networkID.isin(joins.loc[joins.downstream_id == downstream_id].upstream_id)
                ]
                .groupby("networkID")
                .agg({"TotDASqKm": "max", "StreamOrder": "max"})
                .sort_values(by=["TotDASqKm", "StreamOrder"], ascending=False)
                .index.values
            )
            # use the networkID with longest number of segments as out networkID
            networkID = networkIDs[0]
            up_network_df.loc[up_network_df.networkID.isin(networkIDs), "networkID"] = networkID

        up_network_df = up_network_df.drop(columns=["TotDASqKm", "StreamOrder"])

    # check for duplicates
    s = up_network_df.groupby("lineID").size()
    s = s.loc[s > 1]
    if len(s):
        s.rename("count").reset_index().to_feather("/tmp/dup_networks.feather")
        raise ValueError(
            f"lineIDs are found in multiple networks: {', '.join([str(v) for v in s.index.values.tolist()[:10]])}..."
        )

    ### Extract mainstem networks facing upstream
    # drop upstream joins < 1 square mile drainage area or any
    # join where the upstream StreamOrder is different than downstream
    # (avoids smaller incoming tributaries)
    mainstem_ids = flowlines.loc[(flowlines.TotDASqKm >= 2.58999)].index.values
    mainstem_barrier_upstream_idx = barrier_joins.loc[
        (barrier_joins.upstream_id != 0) & barrier_joins.upstream_id.isin(mainstem_ids)
    ].upstream_id.unique()

    if len(mainstem_barrier_upstream_idx):
        upstream_mainstem_joins = (
            upstream_joins.loc[
                upstream_joins.downstream_id.isin(mainstem_ids) & upstream_joins.upstream_id.isin(mainstem_ids)
            ]
            .join(flowlines.StreamOrder.rename("downstream_streamorder"), on="downstream_id")
            .join(flowlines.StreamOrder.rename("upstream_streamorder"), on="upstream_id")
        )
        upstream_mainstem_joins = upstream_mainstem_joins.loc[
            upstream_mainstem_joins.downstream_streamorder == upstream_mainstem_joins.upstream_streamorder
        ].drop(columns=["downstream_streamorder", "upstream_streamorder"])

        upstream_mainstem_graph = DirectedGraph(
            upstream_mainstem_joins.downstream_id.values.astype("int64"),
            upstream_mainstem_joins.upstream_id.values.astype("int64"),
        )
        up_mainstem_network_df = pd.DataFrame(
            upstream_mainstem_graph.network_pairs(mainstem_barrier_upstream_idx.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")

    else:
        up_mainstem_network_df = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    # handle multiple upstreams like full networks above
    # find all networks where the downstream side of the network origin is a junction
    networks_at_junctions = np.intersect1d(
        up_mainstem_network_df.networkID.unique(), joins.loc[joins.junction].upstream_id.unique()
    )
    if len(networks_at_junctions):
        print(
            f"Merging multiple upstream mainstem networks at network junctions, affects {len(networks_at_junctions):,} networks"
        )

        up_mainstem_network_df = up_mainstem_network_df.join(flowlines[["TotDASqKm", "StreamOrder"]], on="lineID")

        downstreams = joins.loc[joins.upstream_id.isin(networks_at_junctions)].downstream_id.unique()
        for downstream_id in downstreams:
            # find all the networks that have the same downstream and fuse them
            networkIDs = (
                up_mainstem_network_df.loc[
                    up_mainstem_network_df.networkID.isin(joins.loc[joins.downstream_id == downstream_id].upstream_id)
                ]
                .groupby("networkID")
                .agg({"TotDASqKm": "max", "StreamOrder": "max"})
                .sort_values(by=["TotDASqKm", "StreamOrder"], ascending=False)
                .index.values
            )
            # use the networkID with longest number of segments as out networkID
            networkID = networkIDs[0]
            up_mainstem_network_df.loc[up_mainstem_network_df.networkID.isin(networkIDs), "networkID"] = networkID

        up_mainstem_network_df = up_mainstem_network_df.drop(columns=["TotDASqKm", "StreamOrder"])

    s = up_mainstem_network_df.groupby("lineID").size()
    s = s.loc[s > 1]
    if len(s):
        s.rename("count").reset_index().to_feather("/tmp/dup_mainstem_networks.feather")
        raise ValueError(
            f"lineIDs are found in multiple mainstem networks: {', '.join([str(v) for v in s.index.values.tolist()[:10]])}..."
        )

    ### Extract linear networks facing downstream
    # This assumes that there are no divergences because loops are removed
    # from the joins
    # NOTE: it is expected that a given lineID will be claimed as a downstream
    # of many downstream networks.
    print("Extracting downstream linear networks for each barrier")

    # lineIDs of flowlines immediately downstream of barriers
    barrier_downstream_idx = barrier_joins.loc[barrier_joins.downstream_id != 0].downstream_id.unique()

    # break joins at barriers
    downstream_joins = joins.loc[
        (joins.upstream_id != 0) & (joins.downstream_id != 0) & (~joins.downstream_id.isin(barrier_downstream_idx)),
        ["downstream_id", "upstream_id"],
    ].drop_duplicates(subset=["downstream_id", "upstream_id"])

    if len(barrier_downstream_idx):
        downstream_graph = LinearDirectedGraph(
            downstream_joins.upstream_id.values.astype("int64"),
            downstream_joins.downstream_id.values.astype("int64"),
        )

        down_network_df = pd.DataFrame(
            downstream_graph.network_pairs(barrier_downstream_idx.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")

    else:
        # down_network_df = pd.DataFrame({"networkID": np.array([], "uint32"), "lineID": np.array([], "uint32")})
        down_network_df = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    return (
        up_network_df.set_index("lineID").networkID,
        up_mainstem_network_df.set_index("lineID").networkID,
        down_network_df.set_index("lineID").networkID,
    )


def create_barrier_networks(
    barriers,
    barrier_joins,
    focal_barrier_joins,
    joins,
    flowlines,
    unaltered_waterbodies,
    unaltered_wetlands,
    network_type,
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
    unaltered_waterbodies : DataFrame
        join table between flowlines and unaltered waterbodies
    unaltered_wetlands : DataFrame
        join table between flowlines and unaltered wetlands
    network_type : str
        name of network network_type, one of NETWORK_TYPES keys

    Returns
    -------
    (DataFrame, DataFrame, DataFrame)
        tuple of barrier_networks, network_stats, flowlines
    """
    network_start = time()

    upstream_networks, upstream_mainstem_networks, downstream_linear_networks = create_networks(
        joins,
        focal_barrier_joins,
        flowlines,
    )

    print(f"{len(upstream_networks.unique()):,} networks created in {time() - network_start:.2f}s")

    # join networkID to flowlines
    flowlines = flowlines.join(upstream_networks.rename(network_type)).join(
        upstream_mainstem_networks.rename(f"{network_type}_mainstem")
    )

    # any segment that wasn't assigned to a network can use its lineID as its network
    # assume that these are isolated segments whose upstream / downstreams were
    # removed because they were loops
    ix = flowlines[network_type].isnull()
    if ix.sum() > 0:
        print(f"Backfilling {ix.sum():,} flowlines that weren't assigned to a network")
        flowlines.loc[ix, network_type] = flowlines.loc[ix].index.values
        flowlines[network_type] = flowlines[network_type].astype("uint32")

    up_network_df = (
        flowlines.dropna(subset=[network_type])
        .rename(columns={network_type: "networkID"})
        .reset_index()
        .set_index("networkID")
    )

    # For any barriers that had multiple upstreams, those were coalesced to a single network above
    # So drop any dangling upstream references (those that are not in networks and non-zero)
    # NOTE: these are not persisted because we want the original barrier_joins to reflect multiple upstreams
    focal_barrier_joins = focal_barrier_joins.loc[
        focal_barrier_joins.upstream_id.isin(upstream_networks.unique()) | (focal_barrier_joins.upstream_id == 0)
    ].copy()

    mainstem_network_df = (
        flowlines[["length", "intermittent", "altered", "sizeclass"]]
        .join(upstream_mainstem_networks, how="inner")
        .reset_index()
        .set_index("networkID")
    )

    down_network_df = (
        flowlines[["length", "free_flowing", "intermittent", "altered"]]
        .join(downstream_linear_networks, how="inner")
        .reset_index()
        .set_index("networkID")
    )

    ### Calculate network statistics
    print("Calculating network stats...")

    stats_start = time()

    upstream_stats = calculate_upstream_network_stats(
        up_network_df, joins, focal_barrier_joins, barrier_joins, unaltered_waterbodies, unaltered_wetlands
    )
    # WARNING: because not all flowlines have associated catchments, they are missing
    # natfldpln

    upstream_mainstem_stats = calculate_upstream_mainstem_stats(mainstem_network_df)

    # downstream_stats are indexed on the ID of the barrier
    downstream_stats = calculate_downstream_stats(down_network_df, focal_barrier_joins, barrier_joins)

    ### Join upstream network stats to downstream network stats
    # NOTE: a network will only have downstream stats if it is upstream of a
    # barrier
    network_stats = upstream_stats.join(upstream_mainstem_stats).join(
        downstream_stats.join(focal_barrier_joins.upstream_id).set_index("upstream_id")
    )
    network_stats.index.name = "networkID"

    # Fill missing data
    for kind in ["waterfalls", "dams", "small_barriers", "road_crossings"]:
        col = f"totd_{kind}"
        network_stats[col] = network_stats[col].fillna(0).astype("uint32")

    for col in ["flows_to_ocean", "flows_to_great_lakes", "invasive_network"]:
        network_stats[col] = network_stats[col].fillna(False).astype("bool")

    for col in ["perennial_sizeclasses", "mainstem_sizeclasses"]:
        network_stats[col] = network_stats[col].fillna(0).astype("uint8")

    network_stats["barrier"] = network_stats.barrier.fillna("")

    for col in [c for c in network_stats.columns if c.endswith("_miles")] + ["miles_to_outlet"]:
        network_stats[col] = network_stats[col].fillna(0).astype("float32")

    print(f"calculated stats in {time() - stats_start:.2f}s")

    #### Calculate up and downstream network attributes for barriers
    # NOTE: some statistics (totd_*, miles_to_outlet, flows_to_ocean, flows_to_great_lakes)
    # are evaluated from the upstream functional network (i.e., these are statistics)
    # downstream of the barrier associated with that functional network
    # WARNING: some barriers are on the upstream end or downstream end of the
    # total network and are missing either upstream or downstream network
    print("calculating upstream and downstream networks for barriers")

    upstream_cols = [c for c in upstream_stats.columns if not c.startswith("free_")]
    upstream_networks = (
        focal_barrier_joins[["upstream_id"]]
        .join(
            upstream_stats[upstream_cols],
            on="upstream_id",
        )
        .join(upstream_mainstem_stats, on="upstream_id")
        .rename(
            columns={
                "upstream_id": "upNetID",
                "pct_unaltered": "PercentUnaltered",
                "pct_perennial_unaltered": "PercentPerennialUnaltered",
                "pct_resilient": "PercentResilient",
                "pct_cold": "PercentCold",
                "pct_mainstem_unaltered": "PercentMainstemUnaltered",
                "unaltered_waterbody_acres": "UpstreamUnalteredWaterbodyAcres",
                "unaltered_wetland_acres": "UpstreamUnalteredWetlandAcres",
                **{
                    c: c.title()
                    .replace("_Mainstem_Miles", "UpstreamMainstemMiles")
                    .replace("_Miles", "UpstreamMiles")
                    .replace("_", "")
                    for c in [
                        col
                        for col in upstream_cols + upstream_mainstem_stats.columns.tolist()
                        if col.endswith("_miles")
                    ]
                },
            }
        )
    )

    downstream_functional_network_cols = [
        c for c in network_stats if (c.startswith("free_") or c == "total_miles") and "linear" not in c
    ]
    downstream_functional_network_stats = (
        # find the network that contains the segment immediately downstream of the barrier;
        # this is the downstream functional network
        focal_barrier_joins[["downstream_id"]]
        .join(
            up_network_df.reset_index().set_index("lineID").networkID,
            on="downstream_id",
        )
        .join(
            network_stats[downstream_functional_network_cols].rename(
                columns={
                    c: c.title().replace("_Miles", "DownstreamMiles").replace("_", "")
                    for c in [col for col in downstream_functional_network_cols if col.endswith("_miles")]
                }
            ),
            on="networkID",
        )
        .rename(columns={"networkID": "downNetID"})
        .drop(columns=["downstream_id"])
    )

    # downstream stats are indexed on barrier ID
    downstream_linear_network_cols = [
        c
        for c in downstream_stats
        if "linear" in c and c.endswith("_miles") and (c.startswith("free_") or c == "total_linear_downstream_miles")
    ]
    downstream_linear_network_stats = downstream_stats[downstream_linear_network_cols].rename(
        columns={
            c: c.title().replace("_Linear_Downstream_Miles", "LinearDownstreamMiles").replace("_", "")
            for c in downstream_linear_network_cols
        }
    )

    # Note: the join creates duplicates if there are multiple upstream or downstream
    # networks for a given barrier, so we drop these duplicates after the join just to be sure.
    barrier_networks = (
        upstream_networks.join(downstream_functional_network_stats)
        .join(downstream_linear_network_stats)
        .join(
            downstream_stats[
                list(
                    {
                        c
                        for c in downstream_stats.columns
                        if c not in set(downstream_functional_network_cols + downstream_linear_network_cols)
                    }
                )
            ]
        )
        .join(barriers.set_index("id")[["kind", "HUC2"]])
    )

    # fill missing data
    # if there is no upstream network, the network of a barrier is in the
    # same HUC2 as the barrier
    ix = barrier_networks.origin_HUC2.isnull()
    barrier_networks.loc[ix, "origin_HUC2"] = barrier_networks.loc[ix].HUC2

    barrier_networks.barrier = barrier_networks.barrier.fillna("")
    barrier_networks.origin_HUC2 = barrier_networks.origin_HUC2.fillna("")

    for col in ["flows_to_ocean", "flows_to_great_lakes", "invasive_network"]:
        barrier_networks[col] = barrier_networks[col].fillna(False).astype("bool")

    # if isolated network or connects to marine / Great Lakes / exit, there
    # are no further miles downstream from this network
    barrier_networks.miles_to_outlet = barrier_networks.miles_to_outlet.fillna(0).astype("float32")
    # total drainage area will be 0 for barriers at top of network
    barrier_networks.fn_da_acres = barrier_networks.fn_da_acres.fillna(0).astype("float32")

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

    for col in length_cols + ["natfldpln"]:
        barrier_networks[col] = barrier_networks[col].astype("float32")

    for col in ["sizeclasses", "perennial_sizeclasses", "mainstem_sizeclasses"]:
        barrier_networks[col] = barrier_networks[col].astype("uint8")

    # copy to degragment data frame
    barrier_networks = barrier_networks.copy()

    ### Calculate miles GAINED if barrier is removed
    # this is the lesser of the upstream or free downstream lengths.
    # Non-free miles downstream (downstream waterbodies) are omitted from this analysis.

    # For barriers that flow directly into marine areas or Great Lakes
    # (no downstream barriers), their GainMiles is only based on the upstream miles
    # add count of downstream breaking barriers
    downstream_cols = [f"totd_{kind}s" for kind in NETWORK_TYPES[network_type]["kinds"]]
    barrier_networks["totd_barriers"] = barrier_networks[downstream_cols].sum(axis=1)

    terminates_downstream_ix = (barrier_networks.totd_barriers == 0) & (
        (barrier_networks.flows_to_ocean == 1) | (barrier_networks.flows_to_great_lakes)
    )
    no_mainstem_upstream_ix = barrier_networks.TotalUpstreamMainstemMiles == 0

    # Calculate gain miles for full functional networks on upstream and downstream sides
    cols = ["TotalUpstreamMiles", "PerennialUpstreamMiles"]
    # TODO: add gain miles for species habitat columns
    # + [
    #     c for c in length_cols if c.endswith("HabitatUpstreamMiles")
    # ]
    for upstream_col in cols:
        out_col = upstream_col.replace("Total", "").replace("Upstream", "Gain")
        downstream_col = f"Free{upstream_col.replace('Total', '').replace('Upstream', 'Downstream')}"
        barrier_networks[out_col] = barrier_networks[[upstream_col, downstream_col]].min(axis=1)
        # if it terminates downstream only use upstream value
        barrier_networks.loc[terminates_downstream_ix, out_col] = barrier_networks.loc[
            terminates_downstream_ix, upstream_col
        ]

    # TotalNetworkMiles is sum of upstream and free downstream miles
    barrier_networks["TotalNetworkMiles"] = barrier_networks[["TotalUpstreamMiles", "FreeDownstreamMiles"]].sum(axis=1)
    barrier_networks["TotalPerennialNetworkMiles"] = barrier_networks[
        ["PerennialUpstreamMiles", "FreePerennialDownstreamMiles"]
    ].sum(axis=1)

    # Calculate gain miles for mainstem networks
    cols = ["TotalUpstreamMainstemMiles", "PerennialUpstreamMainstemMiles"]
    for upstream_col in cols:
        out_col = upstream_col.replace("Total", "").replace("UpstreamMainstem", "MainstemGain")
        downstream_col = f"Free{upstream_col.replace('Total', '').replace('UpstreamMainstem', 'LinearDownstream')}"
        barrier_networks[out_col] = barrier_networks[[upstream_col, downstream_col]].min(axis=1)
        barrier_networks.loc[terminates_downstream_ix, out_col] = barrier_networks.loc[
            terminates_downstream_ix, upstream_col
        ]
        # set to -1 where there is no upstream mainstem, so there can be no gain of mainstem miles
        barrier_networks.loc[no_mainstem_upstream_ix, out_col] = -1

    # TotalMainstemNetworkMiles is sum of upstream and free downstream miles IF
    # upstream has mainstem miles, otherwise unavailable
    barrier_networks["TotalMainstemNetworkMiles"] = barrier_networks[
        ["TotalUpstreamMainstemMiles", "FreeLinearDownstreamMiles"]
    ].sum(axis=1)
    barrier_networks["TotalMainstemPerennialNetworkMiles"] = barrier_networks[
        ["PerennialUpstreamMainstemMiles", "FreePerennialLinearDownstreamMiles"]
    ].sum(axis=1)
    barrier_networks.loc[no_mainstem_upstream_ix, "TotalMainstemNetworkMiles"] = -1
    barrier_networks.loc[no_mainstem_upstream_ix, "TotalMainstemPerennialNetworkMiles"] = -1

    # Round floating point columns to 3 decimals
    for column in [c for c in barrier_networks.columns if c.endswith("Miles")]:
        barrier_networks[column] = barrier_networks[column].round(3).fillna(0)

    ### Round PercentUnaltered and PercentAltered to integers
    for subset in ["", "Perennial", "Mainstem"]:
        barrier_networks[f"Percent{subset}Unaltered"] = (
            barrier_networks[f"Percent{subset}Unaltered"].round().astype("int8")
        )
        barrier_networks[f"Percent{subset}Altered"] = 100 - barrier_networks[f"Percent{subset}Unaltered"]

    barrier_networks["PercentResilient"] = barrier_networks.PercentResilient.round().astype("int8")
    barrier_networks["PercentCold"] = barrier_networks.PercentCold.round().astype("int8")

    # assign downstream linear networks to barrier IDs
    if len(focal_barrier_joins) > 0:
        downstream_linear_networks = (
            focal_barrier_joins[["downstream_id"]]
            .join(downstream_linear_networks.reset_index().set_index("networkID"), on="downstream_id", how="inner")
            .lineID.reset_index()
        )
    else:
        downstream_linear_networks = pd.DataFrame([], columns=["id", "lineID"])

    return barrier_networks, network_stats, flowlines, downstream_linear_networks, downstream_stats
