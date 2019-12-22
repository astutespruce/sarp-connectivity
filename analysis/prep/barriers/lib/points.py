import geopandas as gp
import pygeos as pg
import pandas as pd
import numpy as np
import networkx as nx

from analysis.pygeos_compat import to_pygeos, sjoin, query_tree


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

    def single_query(source_geom, search_window, tolerance, tree):
        """Query the spatial index based on source_geom and return
        indices of all geometries in tree that are <= tolerance

        Parameters
        ----------
        source_geom : pygeos geometry object
        search_window : pygeos geometry object
            search window is bounds of original geometry plus padding of tolerance on all sides
        tolerance : number
            distance within which to keep hits from spatial index
        tree : pygeos STRtree

        Returns
        -------
        ndarray of indices of target
        """
        hits = tree.query(search_window)
        return hits[pg.distance(source_geom, tree.geometries[hits]) <= tolerance]

    # vectorized version takes geometries, windows of equal length,
    # and tolerance as a number or ndarray of equal length
    query = np.vectorize(
        single_query, otypes=[np.ndarray], excluded=["tree"]  # , "tolerance"
    )

    if isinstance(source, pd.Series):
        source_values = source.values
        source_index = source.index

    else:
        source_values = source
        source_index = np.arange(0, len(source))

    if isinstance(target, pd.Series):
        target_values = target.values
        target_index = target.index
        target_index_name = target.index.name or "index_right"

    else:
        target_values = target
        target_index = np.arange(0, len(target))
        target_index_name = "index_right"

    tree = pg.STRtree(target_values)

    # retrieve indices from target that are within tolerance
    hits = query(
        source_values,
        # use a search window for spatial index based on tolerance
        window(source_values, distance),
        distance,
        tree=tree,
    )

    # need to explode and then apply indices to get back to original index values
    hits = (
        pd.Series(hits, index=source_index)
        .explode()
        .dropna()
        .map(pd.Series(target_index))
        .rename("index_right")
        .astype(target_index.dtype)
    )

    # join back to source and target geometries so we can calculate distance
    # TODO: figure out a way to just use the distance we calculated above
    hits = (
        pd.DataFrame(hits)
        .join(pd.Series(source, name="geometry"))
        .join(pd.Series(target, name="geometry_right"), on="index_right")
    )
    hits["distance"] = pg.distance(hits.geometry, hits.geometry_right)

    return (
        hits.drop(columns=["geometry", "geometry_right"])
        .rename(columns={"index_right": target_index_name})
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
    return (
        near(source, target, distance).reset_index().groupby(source_index_name).first()
    )


def neighborhoods(source, tolerance=100):
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

    left_index_name = source.index.name or "index"
    nearby = sjoin(window(source, tolerance), source, how="inner")
    # drop self-intersections
    nearby = (
        nearby.loc[nearby.index != nearby]
        .reset_index()
        .join(source, on=left_index_name)
        .join(source.rename("right"), on="index_right")
    )
    dist = pg.distance(nearby.geometry, nearby.right)
    nearby = nearby.loc[dist <= tolerance].set_index(left_index_name)

    # Find all nodes that are neighbors of each other
    # WARNING: not all neighbors within a neighborhood are within distance of each other
    index_name = source.index.name or "index"
    network = nx.from_pandas_edgelist(nearby.reset_index(), index_name, "index_right")
    components = pd.Series(nx.connected_components(network)).apply(list)
    return (
        pd.DataFrame(components.explode().rename("index_right"))
        .reset_index()
        .rename(columns={"index": "group", "index_right": index_name})
        .set_index(index_name)
        .group
    )
