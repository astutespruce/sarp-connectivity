import numpy as np
import pandas as pd
import shapely

from analysis.lib.graph.speedups import DirectedGraph
from analysis.lib.util import append


def near(source, target, distance):
    """Return all target geometries within distance of source geometries.  Is
    not limited to nearest geometries within distance.

    Only returns records from source that intersected at least one feature in target.

    Parameters
    ----------
    source : Series
        contains pygeos geometries
    target : Series
        contains target pygeos geometries to search against
    distance : number
        radius within which to find target geometries.

    Returns
    -------
    DataFrame
        indexed on original index of source
        includes distance
    """

    tree = shapely.STRtree(target.values)
    left, right = tree.query(source.values, predicate="dwithin", distance=distance)

    right_name = target.index.name or "index_right"
    return pd.DataFrame(
        {
            right_name: target.index.take(right),
            "distance": shapely.distance(
                source.values.take(left), target.values.take(right)
            ),
        },
        source.index.take(left),
    )


def nearest(source, target, max_distance, keep_all=False):
    """Find the nearest target geometry for each record in source, if one
    can be found within distance.

    Parameters
    ----------
    source : Series
        contains pygeos geometries
    target : Series
        contains target pygeos geometries to search against
    max_distance : number or ndarray
        radius within which to find target geometries
        If ndarray, must be equal length to source.
    keep_all : bool (default: False)
        If True, will keep all equidistant results

    Returns
    -------
    DataFrame
        indexed by original index of source, has index of target for each
        nearest target geom.
        Includes distance
    """

    left_index_name = source.index.name or "index"
    right_index_name = target.index.name or "index_right"

    tree = shapely.STRtree(target.values)

    if np.isscalar(max_distance):
        (left_ix, right_ix), distance = tree.query_nearest(
            source.values, max_distance=max_distance, return_distance=True
        )

        # Note: there may be multiple equidistant or intersected results, so we take the first
        df = pd.DataFrame(
            {
                right_index_name: target.index.take(right_ix),
                "distance": distance,
            },
            index=source.index.take(left_ix),
        )

    else:  # array
        merged = None
        for d in np.unique(max_distance):
            ix = max_distance == d
            left = source.loc[ix]
            (left_ix, right_ix), distance = tree.query_nearest(
                left.values, max_distance=d, return_distance=True
            )
            merged = append(
                merged,
                pd.DataFrame(
                    {
                        left_index_name: left.index.take(left_ix),
                        right_index_name: target.index.take(right_ix),
                        "distance": distance,
                    },
                ),
            )
        df = merged.set_index(left_index_name)

    if keep_all:
        df = df.reset_index().drop_duplicates().set_index(left_index_name)
    else:
        df = df.groupby(level=0).first()

    df.index.name = source.index.name

    return df


def neighborhoods(source, tolerance=100):
    """Find the neighborhoods for a given set of geometries.
    Neighborhoods are those where geometries overlap by distance; this gets
    at the outer neighborhood: if A,B; A,C; and C,D are each neighbors
    the neighborhood is A,B,C,D.

    WARNING: not all neighbors within a neighborhood are within distance of each other.

    Parameters
    ----------
    source : Series
        contains pygeos geometries
    tolerance : int, optional (default 100)
        max distance between pairs of geometries
    Returns
    -------
    Series
        returns neighborhoods ("group") indexed by original series index
    """
    index_name = source.index.name or "index"
    index_right = source.index.name or "index_right"

    pairs = near(source, source, distance=tolerance)

    # drop self-intersections; we only want neighborhoods with > 1 member
    pairs = (
        pairs.loc[pairs.index != pairs[index_right]]
        .rename(columns={index_right: "index_right"})
        .index_right
    )

    g = DirectedGraph(pairs.index.values.astype("int64"), pairs.values.astype("int64"))
    groups, values = g.flat_components()
    groups = pd.DataFrame(
        {"group": groups}, index=pd.Series(values, name=index_name)
    ).astype(source.index.dtype)

    return groups
