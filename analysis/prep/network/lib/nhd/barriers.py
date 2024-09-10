from pyogrio import read_dataframe
import shapely

from analysis.lib.geometry import make_valid
from analysis.prep.network.lib.nhd.util import get_column_names


BARRIER_COLS = ["NHDPlusID", "FType", "FCode", "GNIS_Name"]

# Dam, reservoir, waterfall
POINT_FTYPES = [343, 436, 487]

# Dam, Gate, Lock Chamber, Waterfall
LINE_FTYPES = [343, 369, 398, 487]

# Dam, Lock, Spillway
POLY_FTYPES = [343, 398, 455]


def extract_barrier_points(gdb, target_crs):
    """Extract NHDPoint records that are barrier types.

    Parameters
    ----------
    gdb : str
        path to the NHD HUC4 Geodatabase
    target_crs: GeoPandas CRS object
        target CRS to project NHD to for analysis, like length calculations.
        Must be a planar projection.

    Returns
    -------
    GeoDataFrame
    """

    layer = "NHDPoint"
    read_cols, col_map = get_column_names(gdb, layer, BARRIER_COLS)
    ftype_col = col_map.get("FType", "FType")

    df = read_dataframe(
        gdb, layer=layer, columns=read_cols, where=f"{ftype_col} in {tuple(POINT_FTYPES)}", use_arrow=True
    ).rename(columns=col_map)
    df["geometry"] = shapely.force_2d(df.geometry.values)

    df.NHDPlusID = df.NHDPlusID.astype("uint64")

    if len(df):
        df = df.to_crs(target_crs)
        df.geometry = make_valid(df.geometry.values)

    return df


def extract_barrier_lines(gdb, target_crs):
    """Extract NHDLine records that are barrier types.

    Parameters
    ----------
    gdb : str
        path to the NHD HUC4 Geodatabase
    target_crs: GeoPandas CRS object
        target CRS to project NHD to for analysis, like length calculations.
        Must be a planar projection.

    Returns
    -------
    GeoDataFrame
    """
    layer = "NHDLine"
    read_cols, col_map = get_column_names(gdb, layer, BARRIER_COLS)
    ftype_col = col_map.get("FType", "FType")

    df = read_dataframe(
        gdb, layer=layer, columns=read_cols, where=f"{ftype_col} in {tuple(LINE_FTYPES)}", use_arrow=True
    ).rename(columns=col_map)
    df["geometry"] = shapely.force_2d(df.geometry.values)

    df.NHDPlusID = df.NHDPlusID.astype("uint64")

    if len(df):
        df = df.to_crs(target_crs)
        df.geometry = make_valid(df.geometry.values)

    return df


def extract_barrier_polygons(gdb, target_crs):
    """Extract NHDArea records that are barrier types.

    Parameters
    ----------
    gdb : str
        path to the NHD HUC4 Geodatabase
    target_crs: GeoPandas CRS object
        target CRS to project NHD to for analysis, like length calculations.
        Must be a planar projection.

    Returns
    -------
    GeoDataFrame
    """

    layer = "NHDArea"
    read_cols, col_map = get_column_names(gdb, layer, BARRIER_COLS)
    ftype_col = col_map.get("FType", "FType")

    df = read_dataframe(
        gdb, layer=layer, columns=read_cols, where=f"{ftype_col} in {tuple(POLY_FTYPES)}", use_arrow=True
    ).rename(columns=col_map)
    df["geometry"] = shapely.force_2d(df.geometry.values)

    df.NHDPlusID = df.NHDPlusID.astype("uint64")

    if len(df):
        df = df.to_crs(target_crs)
        df.geometry = make_valid(df.geometry.values)

    return df
