import warnings

from pyogrio import read_dataframe

from analysis.lib.geometry import make_valid


warnings.filterwarnings("ignore", message=".*does not have any features to read.*")


COLS = ["NHDPlusID", "FType", "FCode", "GNIS_Name", "geometry"]

# Canal/ditch, flume, levee, lock chamber, spillway
FTYPES = [336, 362, 568, 398, 455]


def extract_altered_rivers(gdb_path, target_crs):
    """Extract NHDArea records that likely indicate altered riverways.

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
        columns=COLS,
        force_2d=True,
        where=f"FType in {tuple(FTYPES)}",
    )

    df.NHDPlusID = df.NHDPlusID.astype("uint64")

    if len(df):
        df = df.to_crs(target_crs)
        df.geometry = make_valid(df.geometry.values.data)

    return df
