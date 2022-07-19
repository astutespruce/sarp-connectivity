import pandas as pd
import numpy as np

from analysis.lib.graph.speedups import DirectedGraph

from analysis.constants import HUC2_EXITS


def connect_huc2s(joins):
    """Find all connected groups of HUC2s.

    This reads in all flowline joins for all HUC2s and detects those that cross
    HUC2 boundaries to determine which HUC2s are connected.

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
        contains upstream_id, downstream_id; indexed on barrierID
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

    print(f"{len(single_segment_networks):,} networks are a single segment long")

    ### Create a directed graph facing upstream
    print("creating upstream graph")
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
    if s.max() > 1:
        raise ValueError(
            f"lineIDs are found in multiple networks: {s.loc[s>1].index.values.tolist()}"
        )

    ### Handle multiple upstreams
    # A given barrier may have > 1 upstream segment, some have 3+
    # Some might be single segments, so we can't just focus on barrier segments
    # Group by barrierID
    upstream_count = barrier_joins.groupby(level=0).size()
    multiple_upstreams = barrier_joins.loc[
        barrier_joins.index.isin(upstream_count.loc[upstream_count > 1].index.unique())
    ]

    if len(multiple_upstreams):
        print(
            f"Merging multiple upstream networks for barriers at network junctions, affects {len(multiple_upstreams):,} networks"
        )

        # For each barrier with multiple upstreams, coalesce their networkIDs
        for barrierID in multiple_upstreams.index.unique():
            upstream_ids = multiple_upstreams.loc[barrierID].upstream_id
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
