"""Provide compatibility and basic spatial operations.

This is a shim ONLY until https://github.com/geopandas/geopandas/pull/1154
lands in GeoPandas.

The following operations are derived from the above PR.
These convert data through WKB, but with NO validation (see PR for validation)
"""

import numpy as np
import pandas as pd
import geopandas as gp
import pygeos as pg
from pygeos import from_wkb, to_wkb
from pygeos.strtree import STRtree
from shapely.wkb import loads
from feather import read_dataframe


def to_pygeos(geoseries):
    return pd.Series(from_wkb(geoseries.apply(lambda g: g.wkb)), index=geoseries.index)


def from_pygeos(geometries):
    def load_wkb(wkb):
        return loads(wkb)

    wkb = pg.to_wkb(geometries)

    if isinstance(geometries, pd.Series):
        return gp.GeoSeries(wkb.apply(load_wkb))

    return gp.GeoSeries(np.vectorize(load_wkb, otypes=[np.object])(wkb))


def explode(series):
    """Convert multipart geometries to a list of geometries

    Parameters
    ----------
    series : Series

    Returns
    -------
    Series

    """
    return series.apply(
        lambda g: [pg.get_geometry(g, i) for i in range(0, pg.get_num_geometries(g))]
    )


# def cut_lines_by_points(lines, points):
#     pass
#     1. explode intersecting points (maybe don't?)
#     2. calculate distance on the line
#     3. interpolate new points from those
#     4. sort points by distance from origin (or reverse - need to check)
#     5. cut lines at points - need to figure out impl


### WIP: basic STRtree based spatial join


def query(left_geom, right, tree, predicate):
    """Query strtree and return indices of right that intersect left
    right, tree, predicate must be called by keyword
    """
    hits = tree.query(left_geom)
    return hits[predicate(left_geom, right[hits])]


# vectorized
vec_query = np.vectorize(
    query, otypes=[np.ndarray], excluded=["right", "tree", "predicate"]
)


def sjoin(left, right, predicate="intersects", how="inner"):
    """Use pygeos to do a spatial join.
    NOTE: This seems to be faster than geopandas where there are fewer intersections per feature on left;
    it is slower than goepandas where there are many intersections per feature
    (will be better once there are prepared geoms in pygeos).

    Parameters
    ----------
    left : Series or ndarray
        left geometries, will form basis of index that is returned
    right : Series or ndarray
        right geometries, their indices will be returned where thy meet predicate
    predicate : str, optional (default: "intersects")
        name of pygeos predicate function (any of the pygeos predicates should work: intersects, contains, within, overlaps, crosses)
    how : str, optional (default: "inner")
        one of "inner" or "left"; "right" is not supported at this time.

    Returns
    -------
    Series
        indexed on index of left, containing values of right
    """
    if isinstance(left, pd.Series):
        left_values = left.values
        left_index = left.index

    else:
        left_values = left
        left_index = np.arange(0, len(left))

    if isinstance(right, pd.Series):
        right_values = right.values
        right_index = right.index

    else:
        right_values = right
        right_index = np.arange(0, len(right))

    tree = STRtree(right_values)
    predicate_func = getattr(pg, predicate)

    # hits are in 0-based indicates of right
    hits = vec_query(
        left_values, right=right_values, tree=tree, predicate=predicate_func
    )
    # need to explode and then apply indices
    hits = pd.Series(hits, index=left_index).explode()
    series = hits.map(pd.Series(right_index)).rename("index_right")

    if how == "inner":
        series = series.dropna().astype(right_index.dtype)

    return series


# NOTE: geometry column is a pygeos geom
def dissolve(df, by):
    """Dissolve a DataFrame by grouping records using "by".

    NOTE: the first record is used for all non-geometry columns.

    Parameters
    ----------
    df : DataFrame
        must contain pygeos geometry in "geometry" column
    by : str
        name of field for grouping records to dissolve together

    Returns
    -------
    GeoDataFrame
        dissolved geometries, indexed using "by" column from grouping
    """
    grouped = df.groupby(by=by)
    atts = grouped[df.columns.drop("geometry")].first()
    geoms = grouped.geometry.apply(pg.union_all)
    return atts.join(geoms)


def to_gdf(df, crs):
    """ Convert a data frame that has pygeos geometry to a GeoDataFrame

    Parameters
    ----------
    df : DataFrame
        must have pygeos geometry in "geometry" column
    crs : geopandas CRS object

    Returns
    -------
    GeoDataFrame
    """
    df = df.copy()
    df["geometry"] = from_pygeos(df.geometry)
    return gp.GeoDataFrame(df, crs=crs)


def get_hash(series):
    """Calculate hash of each geometry for easy equality check.

    The hash is based on the WKB of the geometry.

    Parameters
    ----------
    series : Series
        contains pygeos geometries

    Returns
    -------
    Series
        hash codes for each geometry
    """
    return to_wkb(series).apply(lambda wkb: hash(wkb))
