from time import time


import pandas as pd
import geopandas as gp
import numpy as np
import networkx as nx

from nhdnet.nhd.joins import (
    index_joins,
    find_joins,
    find_join,
    create_upstream_index,
    remove_joins,
)

from analysis.util import flatten_series


def remove_flowlines(flowlines, joins, ids):
    """Remove flowlines specified by ids from flowlines and joins

	Parameters
	----------
	flowlines : GeoDataFrame
	joins : DataFrame
		joins between flowlines
	ids : list-like
		list of ids of flowlines to remove

	Returns
	-------
	tuple of (GeoDataFrame, DataFrame)
		(flowlines, joins)
	"""
    # drop from flowlines
    flowlines = flowlines.loc[~flowlines.NHDPlusID.isin(ids)].copy()

    # IDs are based on NHDPlusID, make sure to use correct columns for joins
    joins = remove_joins(
        joins, ids, downstream_col="downstream", upstream_col="upstream"
    )

    # update our ids to match zeroed out ids
    joins.loc[joins.downstream == 0, "downstream_id"] = 0
    joins.loc[joins.downstream == 0, "type"] = "terminal"
    joins.loc[joins.upstream == 0, "upstream_id"] = 0

    return flowlines, joins


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

    # Drop any isolated pipelines
    # these either are one segment long, or are upstream / downstream terminals for
    # non-pipeline segments
    join_idx = index_joins(
        pjoins, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    drop_ids = join_idx.loc[
        (join_idx.upstream_id == join_idx.downstream_id)
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

    # logic error: we should be dropping long pipelines that are between regular segments, we still want to drop these

    contiguous_pjoins = pjoins.loc[
        (pjoins.upstream_id.isin(pids) & pjoins.downstream_id.isin(pids))
    ]

    isolated = pjoins.loc[~pjoins.index.isin(contiguous_pjoins.index)]
    # drop any that are > max_pipeline_length
    drop_ids = np.intersect1d(
        np.append(isolated.upstream_id, isolated.downstream_id), pids
    )

    ix = flowlines.loc[drop_ids, "length"] > max_pipeline_length
    ix = ix.loc[ix].index.astype("uint32")

    print("Removing {:,} non-contiguous segments".format(len(ix)))

    # remove from flowlines, joins, pjoins
    flowlines = flowlines.loc[~flowlines.index.isin(drop_ids)].copy()
    joins = remove_joins(
        joins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    pjoins = remove_joins(
        pjoins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )

    # create a network of pipelines to group them together

    # have to remove any that start or end in 0's
    nodes = pjoins.loc[(pjoins.upstream_id != 0) & (pjoins.downstream_id != 0)]
    network = nx.from_pandas_edgelist(nodes, "downstream_id", "upstream_id")
    components = pd.Series(nx.connected_components(network)).apply(list)

    groups = (
        pd.DataFrame(components.explode().rename("lineID"))
        .reset_index()
        .rename(columns={"index": "group"})
    )
    groups = groups.join(flowlines[["length"]], on="lineID")
    stats = groups.groupby("group").agg({"length": "sum"})
    drop_groups = stats.loc[stats.length >= max_pipeline_length].index
    drop_ids = groups.loc[groups.group.isin(drop_groups)].lineID

    print(
        "Dropping {:,} pipelines that are greater than the max allowed length".format(
            len(drop_ids)
        )
    )

    flowlines = flowlines.loc[~flowlines.index.isin(drop_ids)].copy()
    joins = remove_joins(
        joins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )

    # update NHDPlusIDs to match zeroed out ids
    joins.loc[joins.downstream_id == 0, "downstream"] = 0
    joins.loc[joins.downstream_id == 0, "type"] = "terminal"
    joins.loc[joins.upstream_id == 0, "upstream"] = 0

    print("Done processing pipelines in {:.2f}s".format(time() - start))

    return flowlines, joins
