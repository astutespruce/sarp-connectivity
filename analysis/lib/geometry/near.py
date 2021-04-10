import numpy as np
import pandas as pd
import pygeos as pg

from analysis.lib.geometry.sjoin import sjoin_geometry
from analysis.lib.graph import DirectedGraph
from analysis.lib.util import append


def near(source, target, distance):
    """Return target geometries within distance of source geometries.

    Only returns records from source that intersected at least one feature in target.

    Parameters
    ----------
    source : Series
        contains pygeos geometries
    target : Series
        contains target pygeos geometries to search against
    distance : number or ndarray
        radius within which to find target geometries.
        If ndarray, must be equal length to source.

    Returns
    -------
    DataFrame
        indexed on original index of source
        includes distance
    """

    # Get all indices from target_values that intersect buffers of input geometry
    idx = sjoin_geometry(pg.buffer(source, distance), target)
    hits = (
        pd.DataFrame(idx)
        .join(source.rename("geometry"), how="inner")
        .join(target.rename("geometry_right"), on="index_right", how="inner")
    )
    # this changes the index if hits is empty, causing downstream problems
    if not len(hits):
        hits.index.name = idx.index.name

    hits["distance"] = pg.distance(hits.geometry, hits.geometry_right).astype("float32")

    return (
        hits.drop(columns=["geometry", "geometry_right"])
        .rename(columns={"index_right": target.index.name or "index_right"})
        .sort_values(by="distance")
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

    tree = pg.STRtree(target.values.data)

    if np.isscalar(max_distance):
        (left_ix, right_ix), distance = tree.nearest_all(
            source.values.data, max_distance=max_distance, return_distance=True
        )

        # Note: there may be multiple equidistant or intersected results, so we take the first
        df = pd.DataFrame(
            {right_index_name: target.index.take(right_ix), "distance": distance,},
            index=source.index.take(left_ix),
        )

    else:  # array
        merged = None
        for d in np.unique(max_distance):
            ix = max_distance == d
            left = source.loc[ix]
            (left_ix, right_ix), distance = tree.nearest_all(
                left.values.data, max_distance=d, return_distance=True
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

    pairs = near(source, source, distance=tolerance)  # .reset_index()

    # drop self-intersections
    pairs = (
        pairs.loc[pairs.index != pairs[index_right]]
        .rename(columns={index_right: "index_right"})
        .index_right
    )

    g = DirectedGraph(pairs.reset_index(), source=index_name, target="index_right")

    groups = (
        pd.DataFrame(
            {i: list(g) for i, g in enumerate(g.components())}.items(),
            columns=["group", "index"],
        )
        .explode("index")
        .set_index("index")
    )
    groups.index.name = index_name

    return groups
