# TODO: do we need igraph?  http://igraph.org/python/doc/tutorial/tutorial.html
# Also see ideas here: http://matthewrocklin.com/blog/work/2017/09/21/accelerating-geopandas-1


def calculate_upstream_network(
    id, get_upstream_ids, has_multiple_downstreams, stop_segments={}
):
    # print("segment {}".format(id))
    ret = [id]

    upstream_ids = get_upstream_ids(id)
    # upstream_ids = join_df.loc[join_df.downstream == id].upstream

    for upstream_id in upstream_ids:
        if upstream_id == 0:  # Origin
            # print("encountered origin segment: {}".format(id))
            continue
        # TODO: what about upstream IDs that are not in our table - e.g., connecting to nodes in next HUC

        if upstream_id in stop_segments:
            # Add to a separate tracking table
            # Start a new network upstream from the upstream end of this one
            # print("encountered segment with dam: {}".format(id))
            continue

        if has_multiple_downstreams(upstream_id):
            # Make sure that we don't pass through this one multiple times!
            stop_segments.add(upstream_id)

        upstream_network = calculate_upstream_network(
            upstream_id, get_upstream_ids, has_multiple_downstreams, stop_segments
        )
        ret.extend(upstream_network)

    return ret
