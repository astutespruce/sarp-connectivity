def find_join(df, id, downstream_col="downstream", upstream_col="upstream"):
    """Find the joins for a given segment id in a joins table.

    Parameters
    ----------
    df : DataFrame
        data frame containing the joins
    id : any
        id to lookup in upstream or downstream columns
    downstream_col : str, optional (default "downstream")
        name of downstream column
    upstream_col : str, optional (default "upstream")
        name of upstream column

    Returns
    -------
    Joins that have the id as an upstream or downstream.
    """
    return df.loc[(df[upstream_col] == id) | (df[downstream_col] == id)]


def find_joins(df, ids, downstream_col="downstream", upstream_col="upstream", expand=0):
    """Find the joins for a given segment id in a joins table.

    Parameters
    ----------
    df : DataFrame
        data frame containing the joins
    ids : list-like
        ids to lookup in upstream or downstream columns
    downstream_col : str, optional (default "downstream")
        name of downstream column
    upstream_col : str, optional (default "upstream")
        name of upstream column
    expand : positive int, optional (default 0)
        If > 0, will expand the search to "expand" degrees from the original ids.
        E.g., if expand is 2, this will return all nonzero joins that are within 2
        joins of the original set of ids.

    Returns
    -------
    Joins that have the id as an upstream or downstream.
    """
    out = df.loc[(df[upstream_col].isin(ids)) | (df[downstream_col].isin(ids))]

    # find all upstream / downstream joins of ids returned at each iteration
    for i in range(expand):
        next_ids = (set(out[upstream_col]) | set(out[downstream_col])) - {0}
        out = df.loc[(df[upstream_col].isin(next_ids)) | (df[downstream_col].isin(next_ids))]

    return out


def index_joins(df, downstream_col="downstream", upstream_col="upstream"):
    """Create an index of joins based on a given segment id.
    Returns a dataframe indexed by id, listing the id of the next
    segment upstream and the id of the next segment downstream.

    Segments that have 0 for both upstream and downstream are 1 segment long.

    WARNING: 0 has special meaning, it denotes that there is no corresponding
    segment.

    Parameters
    ----------
    df : DataFrame
        data frame containing the joins.
    downstream_col : str, optional (default "downstream")
        downstream column name
    upstream_col : str, optional (default "upstream")
        upstream column name

    Returns
    -------
    DataFrame
    """

    df = (
        df.loc[df[downstream_col] != 0]
        .set_index(downstream_col)[[upstream_col]]
        .join(df.set_index(upstream_col)[[downstream_col]])
    )
    df.index.name = "index"

    return df.reset_index().drop_duplicates().set_index("index")


def create_upstream_index(df, downstream_col="downstream", upstream_col="upstream", exclude=None):
    """Create an index of downstream ids to all their respective upstream ids.
    This is so that network traversal can start from a downstream-most segment,
    and then traverse upward for all segments that have that as a downstream segment.

    Parameters
    ----------
    df : DataFrame
        Data frame containing the pairs of upstream_col and downstream_col that
        represent the joins between segments.
    downstream_col : str, optional (default "downstream")
        Name of column containing downstream ids
    upstream_col : str, optional (default "upstream")
        Name of column containing upstream ids
    exclude : list-like, optional (default None)
        List-like containing segment ids to exclude from the list of upstreams.
        For example, barriers that break the network should be in this list.
        Otherwise, network traversal will operate from the downstream-most point
        to all upstream-most points, which can be very large for some networks.

    Returns
    -------
    dict
        dictionary of downstream_id to the corresponding upstream_id(s)
    """

    ix = (df[upstream_col] != 0) & (df[downstream_col] != 0)

    if exclude is not None:
        ix = ix & (~df[upstream_col].isin(exclude))

    # NOTE: this looks backward but is correct for the way that grouping works.
    return df[ix, [downstream_col, upstream_col]].set_index(upstream_col).groupby(downstream_col).groups


def remove_joins(joins, ids, downstream_col="downstream", upstream_col="upstream"):
    """Remove any joins to or from ids.
    This sets any joins that terminate downstream to one of these ids to 0 in order to mark them
    as new downstream terminals.  A join that includes other downstream ids not in ids will be left as is.

    Parameters
    ----------
    joins : DataFrame
        Data frame containing the pairs of upstream_col and downstream_col that
        represent the joins between segments.
    ids : list-like
        List of ids to remove from the joins
    downstream_col : str, optional (default "downstream")
        Name of column containing downstream ids
    upstream_col : str, optional (default "upstream")
        Name of column containing upstream ids

    Returns
    -------
    DataFrame
    """

    # Update any joins that would have connected to these ids
    # on their downstream end
    upstreams = joins.loc[(joins[downstream_col].isin(ids)) & (joins[upstream_col] != 0), upstream_col]
    has_other_joins = joins.loc[joins[upstream_col].isin(upstreams) & ~joins[downstream_col].isin(ids), upstream_col]

    # new terminals are ones that end ONLY in these ids
    new_terminals = upstreams.loc[~upstreams.isin(has_other_joins)]
    ix = joins.loc[joins[upstream_col].isin(new_terminals)].index
    joins.loc[ix, downstream_col] = 0
    # make sure this is applied to the downstream_id as well
    if downstream_col == "downstream" and "downstream_id" in joins.columns:
        joins.loc[ix, "downstream_id"] = 0

    # Update any joins that would have connected to these ids
    # on their upstream end
    downstreams = joins.loc[joins[upstream_col].isin(ids) & (joins[downstream_col] != 0), downstream_col]
    has_other_joins = joins.loc[
        joins[downstream_col].isin(downstreams) & ~joins[upstream_col].isin(ids),
        downstream_col,
    ]
    new_terminals = downstreams.loc[~downstreams.isin(has_other_joins)]
    ix = joins.loc[joins[downstream_col].isin(new_terminals)].index
    joins.loc[ix, upstream_col] = 0
    # make sure this is applied to the upstream_id as well
    if upstream_col == "upstream" and "upstream_id" in joins.columns:
        joins.loc[ix, "upstream_id"] = 0

    # now that we've marked terminals for flowlines that connected to the removed
    # flowlines, now remove any that still reference them
    return joins.loc[~(joins[upstream_col].isin(ids) | (joins[downstream_col].isin(ids)))].drop_duplicates()


def update_joins(
    joins,
    new_downstreams,
    new_upstreams,
    downstream_col="downstream",
    upstream_col="upstream",
):
    """
    Update new upstream and downstream segment IDs into joins table.

    Parameters
    ----------
    joins : DataFrame
        contains records with upstream_id and downstream_id representing joins between segments
    new_downstreams : Series
        Series, indexed on original line ID, with the new downstream ID for each original line ID
    new_upstreams : Series
        Series, indexed on original line ID, with the new upstream ID for each original line ID
    downstream_col : str, optional (default "downstream")
        Name of column containing downstream ids
    upstream_col : str, optional (default "upstream")
        Name of column containing upstream ids

    Returns
    -------
    DataFrame
    """

    new_downstream_col = f"new_{downstream_col}"
    new_upstream_col = f"new_{upstream_col}"

    joins = joins.join(new_downstreams.rename(new_downstream_col), on=downstream_col).join(
        new_upstreams.rename(new_upstream_col), on=upstream_col
    )

    # copy new downstream IDs across
    idx = joins[new_downstream_col].notnull()
    joins.loc[idx, downstream_col] = joins[idx][new_downstreams.name].astype("uint32")

    # copy new upstream IDs across
    idx = joins[new_upstream_col].notnull()
    joins.loc[idx, upstream_col] = joins[idx][new_upstreams.name].astype("uint32")

    return joins.drop(columns=[new_downstream_col, new_upstream_col])


def find_downstream_terminals(df, downstream_col="downstream", upstream_col="upstream"):
    """Find the downstream-most segments of a set of segments.
    By definition, their downstream is not in the set of joins.

    Returns a series containing the IDs of these downstream-most segments.

    Parameters
    ----------
    df : DataFrame
        Data frame containing the pairs of upstream_col and downstream_col that
        represent the joins between segments.
    downstream_col : str, optional (default "downstream")
        Name of column containing downstream ids
    upstream_col : str, optional (default "upstream")
        Name of column containing upstream ids

    Returns
    -------
    Series
    """
    return df.loc[~df[downstream_col].isin(df[upstream_col]), upstream_col]
