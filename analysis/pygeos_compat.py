"""Provide compatibility and basic spatial operations.

This is a shim ONLY until https://github.com/geopandas/geopandas/pull/1154
lands in GeoPandas.

The following operations are derived from the above PR.
These convert data through WKB, but with NO validation (see PR for validation)
"""

from pygeos import from_wkb, to_wkb
from shapely.wkb import loads
from feather import read_dataframe


def to_pygeos(geoseries):
    return from_wkb(geoseries.apply(lambda g: g.wkb))


def from_pygeos(geometries):
    return geometries.apply(lambda g: loads(to_wkb(g)))


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
