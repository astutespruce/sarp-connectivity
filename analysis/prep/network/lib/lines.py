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
    pids = flowlines.loc[flowlines.FType == 428].index
    pjoins = find_joins(
        joins, pids, downstream_col="downstream_id", upstream_col="upstream_id"
    )[["downstream_id", "upstream_id"]]
    print(
        "Found {:,} pipelines and {:,} pipeline-related joins".format(
            len(pids), len(pjoins)
        )
    )

    # drop any terminal joins before traversing network
    # otherwise the 0's close the loop
    pjoins = pjoins.loc[
        ~((pjoins.upstream_id == 0) | (pjoins.downstream_id == 0))
    ].copy()

    # create a network of pipelines to group them together
    network = nx.from_pandas_edgelist(pjoins, "downstream_id", "upstream_id")
    components = pd.Series(nx.connected_components(network)).apply(list)

    groups = (
        pd.DataFrame(flatten_series(components))
        .reset_index()
        .rename(columns={0: "lineID", "index": "group"})
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

    # TODO: watch for pipelines that intersect with non-pipelines at other places than their terminals
    # we want to drop these too

    return flowlines, joins
