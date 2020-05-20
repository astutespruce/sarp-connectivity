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
from pyproj.transformer import Transformer


def to_pygeos(geoseries):
    """Converts a GeoSeries to a Series of pygeos geometry objects.

    Parameters
    ----------
    geoseries : GeoSeries

    Returns
    -------
    Series
    """
    return pd.Series(from_wkb(geoseries.apply(lambda g: g.wkb)), index=geoseries.index)


def from_pygeos(geometries):
    """Converts a Series or ndarray of pygeos geometry objects to a GeoSeries.

    Parameters
    ----------
    geometries : Series or ndarray of pygeos geometry objects

    Returns
    -------
    GeoSeries
    """

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


def sjoin(left, right, predicate="intersects", how="left"):
    """Join data frames on geometry, comparable to geopandas.

    NOTE: left vs right must be determined in advance for best performance, unlike geopandas.

    Parameters
    ----------
    left : DataFrame containing pygeos geometry in "geometry" column
    right : DataFrame containing pygeos geometry in "geometry" column
    predicate : str, optional (default "intersects")
    how : str, optional (default "left")

    Returns
    -------
    pandas DataFrame
        Includes all columns from left and all columns from right except geometry, suffixed by _right where
        column names overlap.
    """

    # spatial join is inner to avoid recasting indices to float
    joined = sjoin_geometry(left.geometry, right.geometry, predicate, how="inner")
    joined = left.join(joined, how=how).join(
        right.drop(columns=["geometry"]), on="index_right", rsuffix="_right"
    )
    return joined


def sjoin_geometry(left, right, predicate="intersects", how="inner"):
    """Use pygeos to do a spatial join between 2 series or ndarrays of geometries.

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
        indexed on index of left, containing values of right index
    """

    if not how in ("inner", "left"):
        raise NotImplementedError("Other join types not implemented")

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
    # hits are in 0-based indicates of right
    hits = tree.query_bulk(left_values, predicate=predicate)

    if how == "inner":
        index = left_index[hits[0]]
        values = right_index[hits[1]]

    elif how == "left":
        index = left_index.copy()
        values = np.empty(shape=index.shape)
        values.fill(np.nan)
        values[hits[0]] = right_index[hits[1]]

    return pd.Series(values, index=index, name="index_right")


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


def spatial_join(left, right):
    joined = sjoin(left, right).drop(columns=["index_right"])

    # WARNING: some places have overlapping areas (e.g., protected areas), this creates extra records!
    # Take the first entry in each case
    grouped = joined.groupby(level=0)
    if grouped.size().max() > 1:
        print(
            "WARNING: multiple target areas returned in spatial join for a single point"
        )

        # extract the right side indexed by the left, and take first record
        right = grouped[[c for c in right.columns.drop("geometry")]].first()
        joined = left.join(right)

    return joined


def to_crs(geometries, src_crs, target_crs):
    """Convert coordinates from one CRS to another CRS

    Parameters
    ----------
    geometries : ndarray of pygeos geometries
    src_crs : CRS or params to create it
    target_crs : CRS or params to create it
    """

    if src_crs == target_crs:
        return geometries.copy()

    transformer = Transformer.from_crs(src_crs, target_crs, always_xy=True)
    coords = pg.get_coordinates(geometries)
    new_coords = transformer.transform(coords[:, 0], coords[:, 1])
    result = pg.set_coordinates(geometries.copy(), np.array(new_coords).T)
    return result
