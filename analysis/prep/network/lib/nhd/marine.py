import warnings
from pyogrio import read_dataframe

from analysis.lib.geometry import explode


warnings.filterwarnings("ignore", message=".*does not have any features to read.*")


COLS = ["FType", "geometry"]

# estuary
WB_FTYPES = [493]

# Sea/ocean, bay/inlent,
AREA_FTYPES = [445, 312]


def extract_marine(gdb_path, target_crs):
    """Extract areas from NHDWaterbody and NHDArea that are marine connected.

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

    print("Reading marine areas...")
    area = read_dataframe(
        gdb_path,
        layer="NHDArea",
        columns=COLS,
        force_2d=True,
        where=f"FType in {tuple(AREA_FTYPES)}",
    )

    wb = read_dataframe(
        gdb_path,
        layer="NHDWaterbody",
        columns=COLS,
        force_2d=True,
        # more complex expression when list is size 1
        where=f"FType in ({','.join([str(t) for t in WB_FTYPES])})",
    )

    df = area.append(wb)

    if len(df):
        df = explode(df.to_crs(target_crs))

    return df

