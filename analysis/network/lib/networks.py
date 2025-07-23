from pathlib import Path
from time import time
import warnings

import pandas as pd
import numpy as np

from analysis.constants import HUC2_EXITS, NETWORK_TYPES

from analysis.lib.graph.speedups import DirectedGraph, LinearDirectedGraph
from analysis.network.lib.stats import (
    calculate_upstream_functional_network_stats,
    calculate_upstream_mainstem_network_stats,
    calculate_downstream_mainstem_network_stats,
    calculate_downstream_linear_network_stats,
)

pd.set_option("future.no_silent_downcasting", True)
warnings.filterwarnings("ignore", message=".*DataFrame is highly fragmented.*")

MAINSTEM_DRAINAGE_AREA = 2.58999  # (one square mile)


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


def coalesce_multiple_upstream_networks(up_network_df, joins, flowlines):
    """Coalesce networks that originate at same location (same barrier or network outlet)
    by setting all to the networkID of the largest drainage area / stream order.

    Note: This intentionally does not try to fuse sibling networks at a
    downstream-most origin point (downstream_id==0).


    Parameters
    ----------
    up_network_df : DataFrame
        upstream network DataFrame
    joins : DataFrame
        contains upstream_id, downstream_id
    flowlines : DataFrame
        flowline within analysis area, indexed on lineID

    Returns
    -------
    DataFrame
        same structure as up_network_df, with networkIDs updated for networks that
        were coalesced
    """
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

    return up_network_df


def create_networks(joins, barrier_joins, flowlines):
    """Create 4 types of networks:
    - upstream functional networks that start from natural origins in network or from barriers
    - upstream mainstem networks that start from barriers
    - downstream mainstem networks that start from barriers
    - downstream linear networks that start from barriers


    Mainstems have >= 1 sq mile drainage area and are limited to joins of the same stream order.
    This avoids smaller incoming tributaries on the upstream side and confluences
    that result in a larger stream order on the downstream side.

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
    (Series, Series, Series, Series)
        (upstream functional network, upstream mainstem network, downstream mainstem network, downstream linear network)
        where each contains is indexed on lineID and haves values for networkID
    """

    lineIDs = flowlines.index
    mainstem_ids = flowlines.loc[(flowlines.TotDASqKm >= MAINSTEM_DRAINAGE_AREA)].index.values

    barrier_upstream_ids = barrier_joins.loc[barrier_joins.upstream_id != 0].upstream_id.unique()
    barrier_downstream_ids = barrier_joins.loc[barrier_joins.downstream_id != 0].downstream_id.unique()
    mainstem_barrier_upstream_ids = barrier_joins.loc[barrier_joins.upstream_id.isin(mainstem_ids)].upstream_id.unique()
    mainstem_barrier_downstream_ids = barrier_joins.loc[
        barrier_joins.downstream_id.isin(mainstem_ids)
    ].downstream_id.unique()

    ### Extract flowline joins for network traversal and break at barriers
    # Note: this drop any that are endpoints of the network
    interior_joins = (
        joins.loc[(joins.upstream_id != 0) & (joins.downstream_id != 0)]
        .join(
            flowlines[["StreamOrder", "TotDASqKm"]].rename(
                columns={"StreamOrder": "downstream_streamorder", "TotDASqKm": "downstream_drainage_km2"}
            ),
            on="downstream_id",
        )
        .join(
            flowlines[["StreamOrder", "TotDASqKm"]].rename(
                columns={"StreamOrder": "upstream_streamorder", "TotDASqKm": "upstream_drainage_km2"}
            ),
            on="upstream_id",
        )
    )

    interior_joins["mainstem"] = (
        (interior_joins.upstream_drainage_km2 >= MAINSTEM_DRAINAGE_AREA)
        & (interior_joins.downstream_drainage_km2 >= MAINSTEM_DRAINAGE_AREA)
        & (interior_joins.upstream_streamorder == interior_joins.downstream_streamorder)
    )

    upstream_joins = interior_joins.loc[
        ~interior_joins.upstream_id.isin(barrier_upstream_ids),
        ["downstream_id", "upstream_id", "mainstem"],
    ].drop_duplicates()

    downstream_joins = interior_joins.loc[
        ~interior_joins.downstream_id.isin(barrier_downstream_ids),
        ["downstream_id", "upstream_id", "mainstem"],
    ].drop_duplicates(subset=["downstream_id", "upstream_id"])

    ### Find network origins
    # find joins that are not marked as terminated, but do not have upstreams in the region;
    # this happens for flowlines that extend into CAN / MEX
    unterminated = joins.loc[(joins.downstream_id != 0) & ~joins.downstream_id.isin(joins.upstream_id)]

    origin_ids = np.concatenate(
        [
            # anything that has no downstream is an origin
            joins.loc[joins.downstream_id == 0].upstream_id.unique(),
            # if downstream_id is not in upstream_id for region, and is in flowlines, add downstream id as origin
            unterminated.loc[unterminated.downstream_id.isin(lineIDs)].downstream_id.unique(),
            # otherwise add upstream id
            unterminated.loc[~unterminated.downstream_id.isin(lineIDs)].upstream_id.unique(),
        ]
    )
    # remove any origins that have associated barriers (this also ensures a unique list)
    origin_ids = np.setdiff1d(origin_ids, barrier_upstream_ids)

    ### Create a directed graph facing upstream and traverse joins to create
    # origin networks and barrier networks
    upstream_graph = DirectedGraph(
        upstream_joins.downstream_id.values.astype("int64"),
        upstream_joins.upstream_id.values.astype("int64"),
    )

    print(f"Generating networks for {len(origin_ids):,} origin points")
    if len(origin_ids) > 0:
        origin_network_segments = pd.DataFrame(
            upstream_graph.network_pairs(origin_ids.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")
        origin_network_segments = coalesce_multiple_upstream_networks(origin_network_segments, joins, flowlines)

    else:
        origin_network_segments = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    print(f"Generating networks for {len(barrier_upstream_ids):,} barriers")
    if len(barrier_upstream_ids):
        # barrier segments are the root of each upstream network from each barrier
        # segments are indexed by the id of the segment at the root for each network
        barrier_network_segments = pd.DataFrame(
            upstream_graph.network_pairs(barrier_upstream_ids.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")
        barrier_network_segments = coalesce_multiple_upstream_networks(barrier_network_segments, joins, flowlines)

    else:
        barrier_network_segments = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    del upstream_graph

    # Append network types together
    origin_network_segments["type"] = "origin"
    barrier_network_segments["type"] = "barrier"
    up_network_df = pd.concat(
        [
            origin_network_segments,
            barrier_network_segments,
        ],
        sort=False,
        ignore_index=False,
    ).reset_index(drop=True)

    # check for duplicates
    s = up_network_df.groupby("lineID").size()
    s = s.loc[s > 1]
    if len(s):
        s.rename("count").reset_index().to_feather("/tmp/dup_networks.feather")
        raise ValueError(
            f"lineIDs are found in multiple networks: {', '.join([str(v) for v in s.index.values.tolist()[:10]])}..."
        )

    ### Extract mainstem networks
    # NOTE: mainstem networks are only calculated for barriers, not origins
    print("Extracting mainstem barrier networks")

    if len(mainstem_barrier_upstream_ids):
        upstream_mainstem_joins = upstream_joins.loc[upstream_joins.mainstem]

        upstream_mainstem_graph = DirectedGraph(
            upstream_mainstem_joins.downstream_id.values.astype("int64"),
            upstream_mainstem_joins.upstream_id.values.astype("int64"),
        )

        up_mainstem_network_df = pd.DataFrame(
            upstream_mainstem_graph.network_pairs(mainstem_barrier_upstream_ids.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")
        up_mainstem_network_df = coalesce_multiple_upstream_networks(up_mainstem_network_df, joins, flowlines)

        del upstream_mainstem_graph

        # check for duplicates
        s = up_mainstem_network_df.groupby("lineID").size()
        s = s.loc[s > 1]
        if len(s):
            s.rename("count").reset_index().to_feather("/tmp/dup_up_mainstem_networks.feather")
            raise ValueError(
                f"lineIDs are found in multiple upstream mainstem networks: {', '.join([str(v) for v in s.index.values.tolist()[:10]])}..."
            )
    else:
        up_mainstem_network_df = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    if len(mainstem_barrier_downstream_ids):
        downstream_mainstem_joins = downstream_joins.loc[downstream_joins.mainstem]

        downstream_mainstem_graph = LinearDirectedGraph(
            downstream_mainstem_joins.upstream_id.values.astype("int64"),
            downstream_mainstem_joins.downstream_id.values.astype("int64"),
        )

        down_mainstem_network_df = pd.DataFrame(
            downstream_mainstem_graph.network_pairs(mainstem_barrier_downstream_ids.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")

        del downstream_mainstem_graph
    else:
        down_mainstem_network_df = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    ### Extract linear networks facing downstream
    # This assumes that there are no divergences because loops are removed
    # from the joins
    # NOTE: it is expected that a given lineID will be claimed as a downstream
    # of many downstream networks.
    print("Extracting downstream linear networks for each barrier")

    if len(barrier_downstream_ids):
        downstream_graph = LinearDirectedGraph(
            downstream_joins.upstream_id.values.astype("int64"),
            downstream_joins.downstream_id.values.astype("int64"),
        )

        down_network_df = pd.DataFrame(
            downstream_graph.network_pairs(barrier_downstream_ids.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")

    else:
        down_network_df = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    return (
        up_network_df.set_index("lineID").networkID,
        up_mainstem_network_df.set_index("lineID").networkID,
        down_mainstem_network_df.set_index("lineID").networkID,
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
    (DataFrame, DataFrame, DataFrame, DataFrame, DataFrame, DataFrame, DataFrame)
        tuple of (
            barrier_networks, network_stats, flowlines,
            downstream_mainstem_network, downstream_mainstem_network_stats,
            downstream_linear_network, downstream_linear_network_stats
        )
    """
    network_start = time()

    upstream_networks, upstream_mainstem_networks, downstream_mainstem_networks, downstream_linear_networks = (
        create_networks(
            joins,
            focal_barrier_joins,
            flowlines,
        )
    )

    print(f"{len(upstream_networks.unique()):,} networks created in {time() - network_start:.2f}s")

    # join networkID to flowlines
    # NOTE: can't join either type of downstream network here because a given
    # flowline may be shared between downstream networks of multiple barriers
    flowlines = flowlines.join(upstream_networks.rename(network_type)).join(
        upstream_mainstem_networks.rename(f"{network_type}_upstream_mainstem")
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

    up_mainstem_network_df = (
        flowlines[["HUC2", "NHDPlusID", "length", "intermittent", "altered", "sizeclass"]]
        .join(upstream_mainstem_networks, how="inner")
        .reset_index()
        .set_index("networkID")
    )

    down_mainstem_network_df = (
        flowlines[["HUC2", "NHDPlusID", "length", "free_flowing", "intermittent", "altered", "sizeclass"]]
        .join(downstream_mainstem_networks, how="inner")
        .reset_index()
        .set_index("networkID")
    )

    down_linear_network_df = (
        flowlines[["length", "free_flowing", "intermittent", "altered"]]
        .join(downstream_linear_networks, how="inner")
        .reset_index()
        .set_index("networkID")
    )

    ### Calculate network statistics
    print("Calculating network stats...")

    stats_start = time()

    # WARNING: because not all flowlines have associated catchments, they are missing
    # natfldpln
    upstream_functional_network_stats = calculate_upstream_functional_network_stats(
        up_network_df, joins, focal_barrier_joins, barrier_joins, unaltered_waterbodies, unaltered_wetlands
    )
    upstream_mainstem_network_stats = calculate_upstream_mainstem_network_stats(up_mainstem_network_df)

    # downstream stats are indexed on the ID of the barrier
    downstream_mainstem_network_stats = calculate_downstream_mainstem_network_stats(
        down_mainstem_network_df, focal_barrier_joins
    )
    downstream_linear_network_stats = calculate_downstream_linear_network_stats(
        down_linear_network_df, focal_barrier_joins, barrier_joins
    )

    # find nearest upstream barrier id, type, and distance based on the downstream
    # linear networks in the functional network for a given barrier
    nearest_upstream_barrier = (
        up_network_df[["lineID"]]
        .join(
            downstream_linear_network_stats[["total_linear_downstream_miles"]]
            .join(focal_barrier_joins[["kind", "downstream_id"]])
            .reset_index()
            .set_index("downstream_id")
            .rename(
                columns={
                    "id": "upstream_barrier_id",
                    "kind": "upstream_barrier",
                    "total_linear_downstream_miles": "upstream_barrier_miles",
                }
            ),
            on="lineID",
            how="inner",
        )
        .sort_values(by="upstream_barrier_miles", ascending=True)
        .groupby(level=0)[["upstream_barrier_id", "upstream_barrier_miles", "upstream_barrier"]]
        .first()
    )

    ### Join upstream network stats to downstream network stats
    # NOTE: a network will only have downstream stats if it is upstream of a
    # barrier
    network_stats = (
        upstream_functional_network_stats.join(upstream_mainstem_network_stats)
        .join(nearest_upstream_barrier)
        .join(downstream_mainstem_network_stats.join(focal_barrier_joins.upstream_id).set_index("upstream_id"))
        .join(downstream_linear_network_stats.join(focal_barrier_joins.upstream_id).set_index("upstream_id"))
    )

    # Fill missing data
    for col in ["barrier_id", "upstream_barrier_id"]:
        network_stats[col] = network_stats[col].fillna(0).astype("uint64")
    for kind in ["waterfalls", "dams", "small_barriers", "road_crossings"]:
        col = f"totd_{kind}"
        network_stats[col] = network_stats[col].fillna(0).astype("uint32")

    for col in ["flows_to_ocean", "flows_to_great_lakes", "invasive_network"]:
        network_stats[col] = network_stats[col].fillna(False).astype("bool")

    for col in ["sizeclasses", "perennial_sizeclasses", "upstream_mainstem_sizeclasses"]:
        network_stats[col] = network_stats[col].fillna(0).astype("uint8")

    for col in ["barrier", "upstream_barrier", "upstream_mainstem_impairment", "downstream_mainstem_impairment"]:
        network_stats[col] = network_stats[col].fillna("")

    for col in [
        c for c in network_stats.columns if c.endswith("_miles") or c.endswith("acres") or c.startswith("pct_")
    ] + [
        "miles_to_outlet",
    ]:
        network_stats[col] = network_stats[col].fillna(0).astype("float32")

    print(f"calculated stats in {time() - stats_start:.2f}s")

    #### Calculate up and downstream network attributes for barriers
    # NOTE: some statistics (totd_*, miles_to_outlet, flows_to_ocean, flows_to_great_lakes)
    # are evaluated from the upstream functional network (i.e., these are statistics)
    # downstream of the barrier associated with that functional network
    # WARNING: some barriers are on the upstream end or downstream end of the
    # total network and are missing either upstream or downstream network
    print("calculating upstream and downstream networks for barriers")

    # Exclude free-flowing metrics, those are only used on downstream functional networks
    # and we already know the barrier here (it is the index)
    upstream_functional_network_cols = [
        c
        for c in upstream_functional_network_stats.columns
        if not c.startswith("free_") and c not in {"barrier_id", "barrier"}
    ]
    upstream_networks = (
        focal_barrier_joins[["upstream_id"]]
        .join(
            upstream_functional_network_stats[upstream_functional_network_cols].rename(
                columns={
                    "pct_unaltered": "PercentUnaltered",
                    "pct_perennial_unaltered": "PercentPerennialUnaltered",
                    "pct_resilient": "PercentResilient",
                    "pct_cold": "PercentCold",
                    "unaltered_waterbody_acres": "UpstreamUnalteredWaterbodyAcres",
                    "unaltered_wetland_acres": "UpstreamUnalteredWetlandAcres",
                    **{
                        c: c.title().replace("_Miles", "UpstreamMiles").replace("_", "")
                        for c in [col for col in upstream_functional_network_cols if col.endswith("_miles")]
                    },
                }
            ),
            on="upstream_id",
        )
        .join(
            nearest_upstream_barrier.rename(columns={"upstream_barrier_miles": "UpstreamBarrierMiles"}),
            on="upstream_id",
        )
        .join(
            upstream_mainstem_network_stats.rename(
                columns={
                    "pct_upstream_mainstem_unaltered": "PercentUpstreamMainstemUnaltered",
                    **{
                        c: c.title().replace("_Upstream_Mainstem_Miles", "UpstreamMainstemMiles").replace("_", "")
                        for c in [col for col in upstream_mainstem_network_stats.columns if col.endswith("_miles")]
                    },
                }
            ),
            on="upstream_id",
        )
        .rename(columns={"upstream_id": "upNetID"})
    )

    downstream_functional_network_cols = [
        c
        for c in network_stats
        if (c.startswith("free_") or c in {"total_miles", "barrier_id", "barrier"}) and "mainstem" not in c.lower()
    ]
    downstream_linear_network_cols = [
        c
        for c in downstream_linear_network_stats
        if "linear" in c and c.endswith("_miles") and (c.startswith("free_") or c == "total_linear_downstream_miles")
    ]
    downstream_networks = (
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
                    "barrier": "downstream_barrier",
                    "barrier_id": "downstream_barrier_id",
                    **{
                        c: c.title().replace("_Miles", "DownstreamMiles").replace("_", "")
                        for c in [col for col in downstream_functional_network_cols if col.endswith("_miles")]
                    },
                }
            ),
            on="networkID",
        )
        # downstream stats are indexed on barrier ID
        .join(
            downstream_mainstem_network_stats.rename(
                columns={
                    **{
                        c: c.title().replace("_Downstream_Mainstem_Miles", "DownstreamMainstemMiles").replace("_", "")
                        for c in [col for col in downstream_mainstem_network_stats.columns if col.endswith("_miles")]
                    },
                }
            )
        )
        .join(
            downstream_linear_network_stats.rename(
                columns={
                    c: c.title().replace("_Linear_Downstream_Miles", "LinearDownstreamMiles").replace("_", "")
                    for c in downstream_linear_network_cols
                }
            )
        )
        .rename(columns={"networkID": "downNetID"})
        .drop(columns=["downstream_id"])
    )

    # Note: the join creates duplicates if there are multiple upstream or downstream
    # networks for a given barrier, so we drop these duplicates after the join just to be sure.
    barrier_networks = upstream_networks.join(downstream_networks).join(
        barriers.set_index("id")[["kind", "HUC2"]].rename(columns={"kind": "barrier"})
    )

    ### fill missing data
    # NOTE: upNetID or downNetID may be null if there aren't networks on that side
    for col in ["upNetID", "downNetID"]:
        barrier_networks[col] = barrier_networks[col].fillna(0).astype("uint32")
    for col in ["upstream_barrier_id", "downstream_barrier_id"]:
        barrier_networks[col] = barrier_networks[col].fillna(0).astype("uint64")
    for col in [
        c
        for c in barrier_networks
        if c.lower().endswith("miles")
        or c.lower().endswith("acres")
        or c.lower().startswith("percent")
        or c == "natfldpln"
    ]:
        barrier_networks[col] = barrier_networks[col].fillna(0).astype("float32")

    for col in ["flows_to_ocean", "flows_to_great_lakes", "invasive_network"]:
        barrier_networks[col] = barrier_networks[col].fillna(False).astype("bool")

    for col in ["sizeclasses", "perennial_sizeclasses", "upstream_mainstem_sizeclasses"]:
        barrier_networks[col] = barrier_networks[col].fillna(0).astype("uint8")

    for col in [
        "upstream_barrier",
        "downstream_barrier",
        "upstream_mainstem_impairment",
        "downstream_mainstem_impairment",
    ]:
        barrier_networks[col] = barrier_networks[col].fillna("")

    # if there is no upstream network, the network of a barrier is in the
    # same HUC2 as the barrier
    ix = barrier_networks.origin_HUC2.isnull()
    barrier_networks.loc[ix, "origin_HUC2"] = barrier_networks.loc[ix].HUC2

    barrier_networks.barrier = barrier_networks.barrier.fillna("")
    barrier_networks.origin_HUC2 = barrier_networks.origin_HUC2.fillna("")

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

    # Calculate gain miles for full functional networks on upstream and downstream sides
    cols = ["TotalUpstreamMiles", "PerennialUpstreamMiles"]
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
        downstream_col = f"Free{upstream_col.replace('Total', '').replace('UpstreamMainstem', 'DownstreamMainstem')}"
        barrier_networks[out_col] = barrier_networks[[upstream_col, downstream_col]].min(axis=1)
        # if it terminates downstream only use upstream value
        barrier_networks.loc[terminates_downstream_ix, out_col] = barrier_networks.loc[
            terminates_downstream_ix, upstream_col
        ]

    # TotalMainstemNetworkMiles is sum of upstream and free downstream miles IF
    # upstream has mainstem miles, otherwise unavailable
    barrier_networks["TotalMainstemNetworkMiles"] = barrier_networks[
        ["TotalUpstreamMainstemMiles", "FreeDownstreamMainstemMiles"]
    ].sum(axis=1)
    barrier_networks["TotalMainstemPerennialNetworkMiles"] = barrier_networks[
        ["PerennialUpstreamMainstemMiles", "FreePerennialDownstreamMainstemMiles"]
    ].sum(axis=1)

    # Round floating point columns to 3 decimals
    for column in [c for c in barrier_networks.columns if c.endswith("Miles")]:
        barrier_networks[column] = barrier_networks[column].round(3).fillna(0)

    ### Round PercentUnaltered and PercentAltered to integers
    for subset in ["", "Perennial", "UpstreamMainstem"]:
        barrier_networks[f"Percent{subset}Unaltered"] = (
            barrier_networks[f"Percent{subset}Unaltered"].round().astype("int8")
        )
        barrier_networks[f"Percent{subset}Altered"] = 100 - barrier_networks[f"Percent{subset}Unaltered"]

    barrier_networks["PercentResilient"] = barrier_networks.PercentResilient.round().astype("int8")
    barrier_networks["PercentCold"] = barrier_networks.PercentCold.round().astype("int8")

    # assign downstream mainstem and linear networks to barrier IDs
    if len(focal_barrier_joins) > 0:
        downstream_mainstem_networks = (
            focal_barrier_joins[["downstream_id"]]
            .join(downstream_mainstem_networks.reset_index().set_index("networkID"), on="downstream_id", how="inner")
            .lineID.reset_index()
        )
        downstream_linear_networks = (
            focal_barrier_joins[["downstream_id"]]
            .join(downstream_linear_networks.reset_index().set_index("networkID"), on="downstream_id", how="inner")
            .lineID.reset_index()
        )
    else:
        downstream_mainstem_networks = pd.DataFrame([], columns=["id", "lineID"])
        downstream_linear_networks = pd.DataFrame([], columns=["id", "lineID"])

    return (
        barrier_networks,
        network_stats,
        flowlines,
        downstream_mainstem_networks,
        downstream_mainstem_network_stats,
        downstream_linear_networks,
        downstream_linear_network_stats,
    )
