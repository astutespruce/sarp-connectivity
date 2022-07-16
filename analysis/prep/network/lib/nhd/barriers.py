import numpy as np
from pyogrio import read_dataframe

from analysis.lib.geometry import make_valid


BARRIER_COLS = ["NHDPlusID", "FType", "FCode", "GNIS_Name", "geometry"]

# Dam, reservoir, waterfall
POINT_FTYPES = [343, 436, 487]

# Dam, Gate, Lock Chamber, Waterfall
LINE_FTYPES = [343, 369, 398, 487]

# Dam, Lock, Spillway
POLY_FTYPES = [343, 398, 455]


def extract_barrier_points(gdb_path, target_crs):
    """Extract NHDPoint records that are barrier types.

    Parameters
    ----------
    gdb_path : str
        path to the NHD HUC4 Geodatabase
    target_crs: GeoPandas CRS object
        target CRS to project NHD to for analysis, like length calculations.
        Must be a planar projection.

    Returns
    -------
    GeoDataFrame
    """

    df = read_dataframe(
        gdb_path,
        layer="NHDPoint",
        columns=BARRIER_COLS,
        force_2d=True,
        where=f"FType in {tuple(POINT_FTYPES)}",
    )

    df.NHDPlusID = df.NHDPlusID.astype("uint64")

    if len(df):
        df = df.to_crs(target_crs)
        df.geometry = make_valid(df.geometry.values.data)

    return df


def extract_barrier_lines(gdb_path, target_crs):
    """Extract NHDLine records that are barrier types.

    Parameters
    ----------
    gdb_path : str
        path to the NHD HUC4 Geodatabase
    target_crs: GeoPandas CRS object
        target CRS to project NHD to for analysis, like length calculations.
        Must be a planar projection.

    Returns
    -------
    GeoDataFrame
    """

    df = read_dataframe(
        gdb_path,
        layer="NHDLine",
        columns=BARRIER_COLS,
        force_2d=True,
        where=f"FType in {tuple(LINE_FTYPES)}",
    )

    df.NHDPlusID = df.NHDPlusID.astype("uint64")

    if len(df):
        df = df.to_crs(target_crs)
        df.geometry = make_valid(df.geometry.values.data)

    return df


def extract_barrier_polygons(gdb_path, target_crs):
    """Extract NHDArea records that are barrier types.

    Parameters
    ----------
    gdb_path : str
        path to the NHD HUC4 Geodatabase
    target_crs: GeoPandas CRS object
        target CRS to project NHD to for analysis, like length calculations.
        Must be a planar projection.

    Returns
    -------
    GeoDataFrame
    """

    df = read_dataframe(
        gdb_path,
        layer="NHDArea",
        columns=BARRIER_COLS,
        force_2d=True,
        where=f"FType in {tuple(POLY_FTYPES)}",
    )

    df.NHDPlusID = df.NHDPlusID.astype("uint64")

    if len(df):
        df = df.to_crs(target_crs)
        df.geometry = make_valid(df.geometry.values.data)

    return df
