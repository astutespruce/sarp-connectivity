from time import time

import pandas as pd
import numpy as np


def generate_network(root_id, upstreams):
    """Generate the upstream network from a starting id.

    Intended to be used within an .apply() call

    Parameters
    ----------
    root_id : id type (int, str)
        starting segment id that forms the root node of the upstream network
    upstreams : dict
        Dictionary created from Pandas groupby().groups - keys are downstream_ids, values are upstream_ids

    Returns
    -------
    list of all upstream ids in network traversing upward from root_id
    """

    network = [root_id]
    ids = [root_id]
    while len(ids):
        upstream_ids = []
        for id in ids:
            upstream_ids.extend(upstreams.get(id, []))

        ids = upstream_ids
        network.extend(ids)

    return network


def generate_networks(root_ids, upstreams):
    """Generate the upstream networks for each root ID in root_ids.
    IMPORTANT: this will produce multiple upstream networks from a given starting point
    if the starting point is located at the junction of multiple upstream networks.

    Parameters
    ----------
    root_ids : pandas.Series
        Series of root IDs (downstream-most ID) for each network to be created
    upstreams : dict
        Dictionary created from Pandas groupby().groups - keys are downstream_ids, values are upstream_ids

    Returns
    -------
    pandas.DataFrame
        Contains networkID based on the value in root_id for each network, and the associated lineIDs in that network
    """

    # create the list of upstream segments per root ID
    network_segments = root_ids.apply(
        lambda id: generate_network(id, upstreams)
    ).rename("lineID")

    # transform into a flat dataframe, with one entry per lineID in each network
    return pd.DataFrame(
        {
            "networkID": np.repeat(root_ids, network_segments.apply(len)),
            "lineID": np.concatenate(network_segments.values),
        }
    )


def create_networks(flowlines, joins, barrier_joins):

    # create idx of all lines that are upstream of barriers; these are
    # "claimed" by the barriers for network analysis.
    # remove any segments that are at the upstream-most terminals of networks
    barrier_upstream_idx = barrier_joins.loc[
        barrier_joins.upstream_id != 0
    ].upstream_id.unique()

    ### Generate upstream index
    # Remove origin_idx, terminals, and barrier segments
    # then create an index of downstream_id to all upstream_ids from it (dictionary of downstream_id to the corresponding upstream_id(s)).
    # This is so that network building can start from a downstream-most
    # line ID, and then build upward for all segments that have that as a downstream segment.
    # NOTE: this looks backward but is correct for the way that grouping works.
    print("Generating upstream index...")
    index_start = time()

    upstreams = joins.loc[
        (joins.upstream_id != 0)
        & (joins.downstream_id != 0)
        & (~joins.upstream_id.isin(barrier_upstream_idx)),
        ["downstream_id", "upstream_id"],
    ]
    upstream_index = upstreams.set_index("upstream_id").groupby("downstream_id").groups

    print(f"Index complete in {time() - index_start:.2f}s")

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
            unterminated.downstream_id.isin(flowlines.index)
        ].downstream_id.unique(),
    )

    # otherwise add upstream id
    origin_idx = np.append(
        origin_idx,
        unterminated.loc[
            ~unterminated.downstream_id.isin(flowlines.index)
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
        np.append(origin_idx, barrier_upstream_idx), upstreams.downstream_id
    ).astype("uint64")

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

    ### Find all origins that are not single segments
    # origin segments are the root of each non-barrier origin point up to barriers
    # segments are indexed by the id of the segment at the root for each network
    origins_with_upstreams = pd.Series(
        np.setdiff1d(origin_idx, single_segment_networks.index), name="networkID"
    )

    print(f"Generating networks for {len(origins_with_upstreams):,} origin points")

    origin_network_segments = generate_networks(origins_with_upstreams, upstream_index)
    origin_network_segments["type"] = "origin"

    # barrier segments are the root of each upstream network from each barrier
    # segments are indexed by the id of the segment at the root for each network
    barriers_with_upstreams = pd.Series(
        np.setdiff1d(barrier_upstream_idx, single_segment_networks.index),
        name="networkID",
    )

    print(f"Generating networks for {len(barriers_with_upstreams):,} barriers")
    barrier_network_segments = generate_networks(
        barriers_with_upstreams, upstream_index
    )
    barrier_network_segments["type"] = "barrier"

    # Append network types back together
    network_df = (
        single_segment_networks.reset_index()
        .append(
            origin_network_segments.reset_index(drop=True),
            sort=False,
            ignore_index=False,
        )
        .append(
            barrier_network_segments.reset_index(drop=True),
            sort=False,
            ignore_index=False,
        )
    )
    network_df.networkID = network_df.networkID.astype("uint32")
    network_df.lineID = network_df.lineID.astype("uint32")

    ### Handle multiple upstreams
    # A given barrier may have > 1 upstream segment, some have 3+
    # Some might be single segments, so we can't just focus on barrier segments
    # Group by barrierID
    upstream_count = barrier_joins.groupby(level=0).size()
    multiple_upstreams = barrier_joins.loc[
        barrier_joins.index.isin(upstream_count.loc[upstream_count > 1].index)
    ]

    if len(multiple_upstreams):
        print(
            f"Merging multiple upstream networks for barriers at network junctions, affects {len(multiple_upstreams)} networks"
        )

        # For each barrier with multiple upstreams, coalesce their networkIDs
        for barrierID in multiple_upstreams.index.unique():
            upstream_ids = multiple_upstreams.loc[barrierID].upstream_id
            networkID = upstream_ids.iloc[0]

            # Set all upstream networks for this barrier to the ID of the first
            network_df.loc[
                network_df.networkID.isin(upstream_ids), ["networkID"]
            ] = networkID

    # Join back to flowlines, dropping anything that didn't get networks
    network_df = flowlines.join(network_df.set_index("lineID"), how="inner").set_index(
        "networkID"
    )

    return network_df
