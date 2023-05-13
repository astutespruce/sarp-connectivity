import warnings

from pyogrio import read_dataframe

from analysis.lib.geometry import make_valid
from analysis.prep.network.lib.nhd.util import get_column_names


warnings.filterwarnings("ignore", message=".*does not have any features to read.*")
warnings.filterwarnings("ignore", message=".*Warning 1: organizePolygons.*")


COLS = ["NHDPlusID", "FType", "FCode", "GNIS_Name"]

# Canal/ditch, flume, levee, lock chamber, spillway
FTYPES = [336, 362, 568, 398, 455]


def extract_altered_rivers(gdb, target_crs):
    """Extract NHDArea records that likely indicate altered riverways.

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
    read_cols, col_map = get_column_names(gdb, layer, COLS)
    ftype_col = col_map.get("FType", "FType")

    df = read_dataframe(
        gdb,
        layer=layer,
        columns=read_cols,
        force_2d=True,
        where=f"{ftype_col} in {tuple(FTYPES)}",
    ).rename(columns=col_map)

    df.NHDPlusID = df.NHDPlusID.astype("uint64")

    if len(df):
        df = df.to_crs(target_crs)
        df.geometry = make_valid(df.geometry.values.data)

    return df
