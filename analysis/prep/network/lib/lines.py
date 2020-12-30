from time import time

import pandas as pd

from nhdnet.nhd.joins import (
    index_joins,
    find_joins,
    remove_joins,
)
from analysis.lib.network import connected_groups


def remove_pipelines(flowlines, joins, max_pipeline_length=100):
    """Remove pipelines that are above max length,
    based on contiguous length of pipeline segments.

    Parameters
    ----------
    flowlines : GeoDataFrame
    joins : DataFrame
            joins between flowlines
    max_pipeline_length : int, optional (default: 100)
            length above which pipelines are dropped

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
            (flowlines, joins)
    """

    start = time()
    pids = flowlines.loc[flowlines.FType == 428].index
    pjoins = find_joins(
        joins, pids, downstream_col="downstream_id", upstream_col="upstream_id"
    )[["downstream_id", "upstream_id"]]
    print(
        "Found {:,} pipelines and {:,} pipeline-related joins".format(
            len(pids), len(pjoins)
        )
    )

    # Drop any isolated pipelines no matter what size
    # these either are one segment long, or are upstream / downstream terminals for
    # non-pipeline segments
    join_idx = index_joins(
        pjoins, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    drop_ids = join_idx.loc[
        (
            join_idx.upstream_id == join_idx.downstream_id
        )  # has upstream and downstream of 0s
        | (
            ((join_idx.upstream_id == 0) & (~join_idx.downstream_id.isin(pids)))
            | ((join_idx.downstream_id == 0) & (~join_idx.upstream_id.isin(pids)))
        )
    ].index
    print("Removing {:,} isolated segments".format(len(drop_ids)))

    # remove from flowlines, joins, pjoins
    flowlines = flowlines.loc[~flowlines.index.isin(drop_ids)].copy()
    joins = remove_joins(
        joins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    pjoins = remove_joins(
        pjoins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    join_idx = join_idx.loc[~join_idx.index.isin(drop_ids)].copy()

    # Find single connectors between non-pipeline segments
    # drop those > max_pipeline_length
    singles = join_idx.loc[
        ~(join_idx.upstream_id.isin(pids) | join_idx.downstream_id.isin(pids))
    ].join(flowlines["length"])
    drop_ids = singles.loc[singles.length >= max_pipeline_length].index

    print(
        "Found {:,} pipeline segments between flowlines that are > {:,}m; they will be dropped".format(
            len(drop_ids), max_pipeline_length
        )
    )

    # remove from flowlines, joins, pjoins
    flowlines = flowlines.loc[~flowlines.index.isin(drop_ids)].copy()
    joins = remove_joins(
        joins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    pjoins = remove_joins(
        pjoins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    join_idx = join_idx.loc[~join_idx.index.isin(drop_ids)].copy()

    ### create a network of pipelines to group them together
    # Only use contiguous pipelines; those that are not contiguous should have been handled above
    pairs = pjoins.loc[pjoins.upstream_id.isin(pids) & pjoins.downstream_id.isin(pids)]
    groups = connected_groups(pairs, make_symmetric=True)

    groups = pd.DataFrame(groups).join(flowlines[["length"]])
    stats = groups.groupby("group").agg({"length": "sum"})
    drop_groups = stats.loc[stats.length >= max_pipeline_length].index
    drop_ids = groups.loc[groups.group.isin(drop_groups)].index

    print(
        "Dropping {:,} pipelines that are greater than {:,}".format(
            len(drop_ids), max_pipeline_length
        )
    )

    flowlines = flowlines.loc[~flowlines.index.isin(drop_ids)].copy()
    joins = remove_joins(
        joins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )

    # update NHDPlusIDs to match zeroed out ids
    joins.loc[
        (joins.downstream_id == 0) & (joins.type == "internal"), "type"
    ] = "former_pipeline_join"

    print("Done processing pipelines in {:.2f}s".format(time() - start))

    return flowlines, joins
