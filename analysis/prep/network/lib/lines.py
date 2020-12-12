from time import time

import pandas as pd
import geopandas as gp
import pygeos as pg
import numpy as np

from nhdnet.nhd.joins import (
    index_joins,
    find_joins,
    find_join,
    create_upstream_index,
    remove_joins,
)
from analysis.lib.network import connected_groups


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


# pygeos version of nhdnet.geometry.lines::calculate_sinuosity
def calculate_sinuosity(geometries):
    """Calculate sinuosity of the line.

    This is the length of the line divided by the distance between the endpoints of the line.
    By definition, it is always >=1.

    Parameters
    ----------
    geometries : Series or ndarray of pygeos geometries

    Returns
    -------
    Series or ndarray
        sinuosity values
    """

    # By definition, sinuosity should not be less than 1
    first = pg.get_point(geometries, 0)
    last = pg.get_point(geometries, -1)
    straight_line_distance = pg.distance(first, last)

    sinuosity = np.ones((len(geometries),)).astype("float32")

    # if there is no straight line distance there can be no sinuosity
    ix = straight_line_distance > 0

    # by definition, all values must be at least 1, so clip lower bound
    sinuosity[ix] = (pg.length(geometries[ix]) / straight_line_distance).clip(1)

    if isinstance(geometries, pd.Series):
        return pd.Series(sinuosity, index=geometries.index)

    return sinuosity
