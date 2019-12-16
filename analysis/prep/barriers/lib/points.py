import geopandas as gp
import pygeos as pg
import pandas as pd
import numpy as np
import networkx as nx

from analysis.pygeos_compat import to_pygeos, sjoin


# pygeos version of nhdnet.geometry.points::find_nearby
def find_nearby(series, distance):
    """Return indices of points within radius of each point.
    This is symmetric, every original point will have a count of distances to
    all other points.

    Parameters
    ----------
    df : Series
        contains pygeos geometries

    distance : number
        radius within which to find nearby points

    Returns
    -------
    Series
        indexed according to the original index of the data frame, and
        containing `index_right` for the index of the nearby features.
    """

    print("Creating buffers...")
    buffers = pg.buffer(series, distance)
    joined = sjoin(buffers, buffers, how="inner")
    return joined.loc[joined.index != joined].copy()


def find_neighborhoods(series, distance=100):
    """Find the neighborhoods for a given set of geometries.
    Neighborhoods are those where geometries overlap by distance; this gets
    at the outer neighborhood: if A,B; A,C; and C,D are each neighbors
    the neighborhood is A,B,C,D.

    Parameters
    ----------
    series : Series
        contains pygeos geometries
    distance : int, optional (default 100)

    Returns
    -------
    Series
        returns neighborhoods ("group") indexed by original series index
    """
    nearby = find_nearby(series, distance)

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


def find_nearest(series, reference, tolerance):
    """Find the nearest reference geometry for each record in series, if one
    can be found within tolerance.

    Parameters
    ----------
    series : Series
        input pygeos geometry series
    reference : Series
        reference pygeos geometry series
    tolerance : number
        max distance within which to find nearest reference geometry

    Returns
    -------
    Series
        indexed by original index of series, has index of reference for each
        nearest reference geom.
    """
    buffered = pg.buffer(series, tolerance)
    left_index_name = series.index.name or "index"
    right_index_name = reference.index.name or "index_right"
    joined = pd.DataFrame(
        sjoin(buffered, reference, how="inner").rename(right_index_name)
    )
    joined = (
        joined.join(series)
        .join(reference.rename("right_geom"), on=right_index_name)
        .reset_index()
    )
    joined["dist"] = pg.distance(joined.geometry, joined.right_geom)
    joined = joined.sort_values(by=[left_index_name, "dist"])
    return joined.groupby(left_index_name).first()[right_index_name]

