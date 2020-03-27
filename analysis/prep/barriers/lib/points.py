import geopandas as gp
import pygeos as pg
import pandas as pd
import numpy as np
import networkx as nx

from analysis.pygeos_compat import to_pygeos, sjoin, sjoin_geometry


def connect_points(start, end):
    """Convert a series or array of points to an array or series of lines.

    Parameters
    ----------
    start : Series or ndarray
    end : Series or ndarray

    Returns
    -------
    Series or ndarray
    """

    is_series = False

    if isinstance(start, pd.Series):
        is_series = True
        index = start.index
        start = start.values
    if isinstance(end, pd.Series):
        end = end.values

    x1 = pg.get_x(start)
    y1 = pg.get_y(start)
    x2 = pg.get_x(end)
    y2 = pg.get_y(end)

    lines = pg.linestrings(np.array([[x1, x2], [y1, y2]]).T)

    if is_series:
        return pd.Series(lines, index=index)

    return lines


def window(geometries, distance):
    """Return windows around geometries bounds +/- distance

    Parameters
    ----------
    geometries : Series or ndarray
        geometries to window
    distance : number or ndarray
        radius of window
        if ndarry, must match length of geometries

    Returns
    -------
    Series or ndarray
        polygon windows
    """
    minx, miny, maxx, maxy = pg.bounds(geometries).T
    windows = pg.box(minx - distance, miny - distance, maxx + distance, maxy + distance)

    if isinstance(geometries, pd.Series):
        return pd.Series(windows, index=geometries.index)

    return windows


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
        pd.DataFrame(source)
        .join(idx, how="inner")
        .join(target.rename("geometry_right"), on="index_right", how="inner")
    )
    hits["distance"] = pg.distance(hits.geometry, hits.geometry_right)

    return (
        hits.drop(columns=["geometry", "geometry_right"])
        .rename(columns={"index_right": target.index.name or "index_right"})
        .sort_values(by="distance")
        .copy()
    )


def nearest(source, target, distance):
    """Find the nearest target geometry for each record in source, if one
    can be found within distance.

    Parameters
    ----------
    source : Series
        contains pygeos geometries
    target : Series
        contains target pygeos geometries to search against
    distance : number or ndarray
        radius within which to find target geometries
        If ndarray, must be equal length to source.

    Returns
    -------
    DataFrame
        indexed by original index of source, has index of target for each
        nearest target geom.
        Includes distance
    """
    source_index_name = source.index.name or "index"

    # results coming from near() already sorted by distance

    # TODO: fix this; reset_index() fails if this is empty

    return (
        near(source, target, distance).reset_index().groupby(source_index_name).first()
    )

    """Find the neighborhoods for a given set of geometries.
    Neighborhoods are those where geometries overlap by distance; this gets
    at the outer neighborhood: if A,B; A,C; and C,D are each neighbors
    the neighborhood is A,B,C,D.

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


def neighborhoods(source, tolerance=100):

    index_name = source.index.name or "index"

    nearby = near(source, source, distance=tolerance)

    # drop self-intersections
    nearby = nearby.loc[nearby.index != nearby[index_name]].rename(
        columns={index_name: "index_right"}
    )

    # Find all nodes that are neighbors of each other based on network adjacency
    # WARNING: not all neighbors within a neighborhood are within distance of each other
    network = nx.from_pandas_edgelist(nearby.reset_index(), index_name, "index_right")
    components = pd.Series(nx.connected_components(network)).apply(list)
    return (
        pd.DataFrame(components.explode().rename("index_right"))
        .reset_index()
        .rename(columns={"index": "group", "index_right": index_name})
        .set_index(index_name)
        .group
    )
