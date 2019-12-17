import geopandas as gp
import pygeos as pg
import pandas as pd
import numpy as np
import networkx as nx

from analysis.pygeos_compat import to_pygeos, sjoin


def connect(start, end):
    """Convert a series or array of points to an array or series of lines.

    Parameters
    ----------
    start : Series or ndarray
    end : Series or ndarray

    Returns
    -------
    Series or ndarray
    """
    x1 = pg.get_x(start)
    y1 = pg.get_y(start)
    x2 = pg.get_x(end)
    y2 = pg.get_y(end)

    return pg.linestrings(np.array([[x1, x2], [y1, y2]]).T)


def window(points, tolerance):
    """Return windows around points, based on point as center +/- tolerance.

    Parameters
    ----------
    points : Series or ndarray
        points to window
    tolerance : number
        radius of window

    Returns
    -------
    Series or ndarray
        polygon windows
    """
    bounds = pg.bounds(points) + [-tolerance, -tolerance, tolerance, tolerance]
    return pg.box(*bounds.T)


def within_distance(source, target, distance=100):
    """Return target geometries within distance of source geometries.

    Only returns records from source that intersected at least one feature in target.

    Parameters
    ----------
    source : Series
        contains pygeos geometries
    target : Series
        contains target pygeos geometries to search against
    distance : number, optional (default 100)
        radius within which to find target geometries

    Returns
    -------
    DataFrame
        indexed on original index of source
        includes distance
    """

    left_index_name = source.index.name or "index"
    right_index_name = target.index.name or "index_right"
    near = sjoin(window(source, distance), target, how="inner").rename(right_index_name)
    near = (
        near.reset_index()
        .join(series, on=left_index_name)
        .join(target.rename("geometry_right"), on="index_right")
    )
    near["distance"] = pg.distance(near.geometry, near.geometry_right)
    return (
        near.loc[
            near.distance <= distance, [left_index_name, right_index_name, "distance"]
        ]
        .set_index(left_index_name)
        .copy()
    )


def find_nearest(source, target, distance):
    """Find the nearest target geometry for each record in source, if one
    can be found within distance.

    Parameters
    ----------
    source : Series
        contains pygeos geometries
    target : Series
        contains target pygeos geometries to search against
    distance : number, optional (default 100)
        radius within which to find target geometries

    Returns
    -------
    Series
        indexed by original index of series, has index of reference for each
        nearest reference geom.
    """
    left_index_name = source.index.name or "index"
    right_index_name = target.index.name or "index_right"
    near = (
        within_distance(source, target, distance)
        .reset_index()
        .sort_values(by=[left_index_name, "distance"])
    )
    return near.groupby(left_index_name).first()["index_right"].rename(right_index_name)


def find_neighborhoods(series, tolerance=100):
    """Find the neighborhoods for a given set of geometries.
    Neighborhoods are those where geometries overlap by distance; this gets
    at the outer neighborhood: if A,B; A,C; and C,D are each neighbors
    the neighborhood is A,B,C,D.

    Parameters
    ----------
    series : Series
        contains pygeos geometries
    tolerance : int, optional (default 100)
        max distance between pairs of geometries
    Returns
    -------
    Series
        returns neighborhoods ("group") indexed by original series index
    """

    left_index_name = source.index.name or "index"
    nearby = sjoin(window(series, tolerance), series, how="inner")
    # drop self-intersections
    nearby = (
        nearby.loc[joined.index != joined]
        .reset_index()
        .join(series, on=left_index_name)
        .join(series.rename("right"), on="index_right")
    )
    dist = pg.distance(nearby.geometry, joined.right)
    nearby = nearby.loc[dist <= tolerance].set_index(left_index_name)

    # Find all nodes that are neighbors of each other
    # WARNING: not all neighbors within a neighborhood are within distance of each other
    index_name = series.index.name or "index"
    network = nx.from_pandas_edgelist(nearby.reset_index(), index_name, "index_right")
    components = pd.Series(nx.connected_components(network)).apply(list)
    return (
        pd.DataFrame(components.explode().rename("index_right"))
        .reset_index()
        .rename(columns={"index": "group", "index_right": index_name})
        .set_index(index_name)
    )
