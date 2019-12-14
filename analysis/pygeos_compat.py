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


def from_geofeather_as_geos(path, columns=None):
    """Deserialize a pandas.DataFrame containing a GeoDataFrame stored in a feather file.

    WARNING: this is a very temporary shim until pygeos support lands in geopandas.  The only
    purpose of this is to have easy access to deserialized pygeos.Geometry objects (using
    the pygeos.from_wkb ufunc is ~3x faster than reading to shapely objects, and above
    conversions are slow and use large amounts of memory)

    This converts the internal WKB representation into an array of pygeos.Geometry.

    Parameters
    ----------
    path : str
        path to feather file to read
    columns : list-like (optional, default: None)
        Subset of columns to read from the file, must include 'geometry'.  If not provided,
        all columns are read.

    Returns
    -------
    pandas.DataFrame
    """

    if columns is not None and "geometry" not in columns:
        raise ValueError(
            "'geometry' must be included in list of columns to read from feather file"
        )

    # shim to support files created with geofeather 0.1.0
    if columns is not None and "wkb" not in columns:
        columns.append("wkb")

    df = read_dataframe(path, columns=columns)

    # shim to support files created with geofeather 0.1.0
    df = df.rename(columns={"wkb": "geometry"})

    df.geometry = from_wkb(df.geometry)
    return df


def split_multi_geoms(series):
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


def sjoin(left, right, predicate="intersects"):
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
    return hits.map(pd.Series(right_index))

