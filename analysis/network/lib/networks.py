from time import time

from nhdnet.nhd.network import generate_networks


def create_networks(flowlines, joins, barrier_joins):

    # remove any segments that are at the upstream-most terminals of networks
    barrier_segments = barrier_joins.loc[barrier_joins.upstream_id != 0].set_index(
        "upstream_id"
    )[[]]

    ### Generate upstream index
    # Remove origins, terminals, and barrier segments
    # then create an index of downstream_id to all upstream_ids from it (dictionary of downstream_id to the corresponding upstream_id(s)).
    # This is so that network building can start from a downstream-most
    # line ID, and then build upward for all segments that have that as a downstream segment.
    # NOTE: this looks backward but is correct for the way that grouping works.
    print("Generating upstream index...")
    index_start = time()

    upstreams = joins.loc[
        (joins.upstream_id != 0)
        & (joins.downstream_id != 0)
        & (~joins.upstream_id.isin(barrier_segments.index)),
        ["downstream_id", "upstream_id"],
    ]
    upstream_index = upstreams.set_index("upstream_id").groupby("downstream_id").groups

    print("Index complete in {:.2f}s".format(time() - index_start))

    ### Get list of network root IDs
    # Create networks from all terminal nodes (have no downstream nodes) up to barriers.
    # Exclude any segments where barriers are also on the downstream terminals to prevent duplicates.
    # Note: origins are also those that have a downstream_id but are not the upstream_id of another node
    downstream_terminal_idx = (joins.downstream_id == 0) | (
        ~joins.downstream_id.isin(joins.upstream_id)
    )
    origins = joins.loc[
        (downstream_terminal_idx & (~joins.upstream_id.isin(barrier_segments.index)))
    ].set_index("upstream_id")[[]]

    ### Extract all origin points and barrier segments that immediately terminate upstream
    single_segment_networks = origins.append(barrier_segments).join(
        upstreams.set_index("downstream_id")
    )
    single_segment_networks = single_segment_networks.loc[
        single_segment_networks.upstream_id.isnull()
    ][[]]
    single_segment_networks.index.rename("lineID", inplace=True)
    single_segment_networks["networkID"] = single_segment_networks.index
    single_segment_networks["type"] = "origin"
    single_segment_networks.loc[
        single_segment_networks.index.isin(barrier_segments.index), "type"
    ] = "barrier"

    print(
        "{:,} networks are a single segment long".format(len(single_segment_networks))
    )

    # origin segments are the root of each non-barrier origin point up to barriers
    # segments are indexed by the id of the segment at the root for each network
    origins_with_upstreams = origins.loc[
        ~origins.index.isin(single_segment_networks.index)
    ].index.to_series(name="networkID")

    print(
        "Generating networks for {:,} origin points".format(len(origins_with_upstreams))
    )

    origin_network_segments = generate_networks(origins_with_upstreams, upstream_index)
    origin_network_segments["type"] = "origin"

    # barrier segments are the root of each upstream network from each barrier
    # segments are indexed by the id of the segment at the root for each network
    barriers_with_upstreams = barrier_segments.loc[
        ~barrier_segments.index.isin(single_segment_networks.index)
    ].index.to_series(name="networkID")
    print("Generating networks for {:,} barriers".format(len(barriers_with_upstreams)))
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
            "Merging multiple upstream networks for barriers at network junctions, affects {} networks".format(
                len(multiple_upstreams)
            )
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
