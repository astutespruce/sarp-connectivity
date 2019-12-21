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
    windows = pg.box(*bounds.T)

    if isinstance(points, pd.Series):
        return pd.Series(windows, index=points.index)

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
    distance : number
        radius within which to find target geometries

    Returns
    -------
    DataFrame
        indexed on original index of source
        includes distance
    """

    def single_query(source_geom, search_window, target, tree, tolerance):
        """Query the spatial index based on source_geom and return
        indices of all geometries in target that are <= tolerance

        Parameters
        ----------
        source_geom : pygeos geometry object
        search_window : pygeos geometry object
            search window is bounds of original geometry plus padding of tolerance on all sides
        target : ndarray of pygeos geometry objects
        tree : pygeos STRtree
        tolerance : number
            distance within which to keep hits from spatial index

        Returns
        -------
        ndarray of indices of target
        """
        hits = tree.query(search_window)
        return hits[pg.distance(source_geom, target[hits]) <= tolerance]

    query = np.vectorize(
        single_query, otypes=[np.ndarray], excluded=["target", "tree", "tolerance"]
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
        target_index_name = target.index.name

    else:
        target_values = target
        target_index = np.arange(0, len(target))
        target_index_name = "index_right"

    tree = pg.STRtree(target_values)

    # retrieve indices from target that are within tolerance
    near = query(
        source_values,
        # use a search window for spatial index based on tolerance
        window(source_values, distance),
        target=target_values,
        tree=tree,
        tolerance=distance,
    )

    # need to explode and then apply indices to get back to original index values
    near = (
        pd.Series(near, index=source_index)
        .explode()
        .dropna()
        .map(pd.Series(target_index))
        .rename(target_index_name)
        .astype(target_index.dtype)
    )

    # join back to source and target geometries so we can calculate distance
    # TODO: figure out a way to just use the distance we calculated above
    near = (
        pd.DataFrame(near)
        .join(source.geometry)
        .join(pd.Series(target, name="geometry_right"), on=target_index_name)
    )
    near["distance"] = pg.distance(near.geometry, near.geometry_right)
    return (
        near.drop(columns=["geometry", "geometry_right"])
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
    distance : number, optional (default 100)
        radius within which to find target geometries

    Returns
    -------
    DataFrame
        indexed by original index of source, has index of target for each
        nearest target geom.
        Includes distance
    """
    left_index_name = source.index.name or "index"
    return near(source, target, distance).reset_index().groupby(left_index_name).first()


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
