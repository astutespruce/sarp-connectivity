import warnings

import numpy as np
import pandas as pd
import pygeos as pg
from pyogrio import read_dataframe

from analysis.lib.geometry import explode
from analysis.prep.network.lib.nhd.util import get_column_names


warnings.filterwarnings("ignore", message=".*does not have any features to read.*")
warnings.filterwarnings("ignore", message=".*Warning 1: organizePolygons.*")


COLS = ["FType"]

# estuary
WB_FTYPES = [493]

# Sea/ocean, bay/inlent
# WARNING: sometimes bay/inlet is coded for parts of inland waterbodies
AREA_FTYPES = [445, 312]


def extract_marine(gdb, target_crs):
    """Extract areas from NHDWaterbody and NHDArea that are marine connected.

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

    print("Reading marine areas...")

    layer = "NHDArea"
    read_cols, col_map = get_column_names(gdb, layer, COLS)
    ftype_col = col_map.get("FType", "FType")

    area = read_dataframe(
        gdb,
        layer=layer,
        columns=read_cols,
        force_2d=True,
        where=f"{ftype_col} in {tuple(AREA_FTYPES)}",
    ).rename(columns=col_map)

    layer = "NHDWaterbody"
    read_cols, col_map = get_column_names(gdb, layer, COLS)
    ftype_col = col_map.get("FType", "FType")

    wb = read_dataframe(
        gdb,
        layer=layer,
        columns=read_cols,
        force_2d=True,
        # more complex expression when list is size 1
        where=f"{ftype_col} in ({','.join([str(t) for t in WB_FTYPES])})",
    ).rename(columns=col_map)

    df = pd.concat([area, wb], ignore_index=True, sort=False)

    if len(df):
        df = explode(df).reset_index(drop=True)

        # only keep those that are not fully contained within land areas
        layer = "NHDPlusLandSea"
        read_cols, col_map = get_column_names(gdb, layer, ["Land"])
        land_col = col_map.get("Land", "Land")

        land = explode(
            read_dataframe(
                gdb,
                layer=layer,
                columns=[],
                force_2d=True,
                where=f'"{land_col}" = 1',
            )
        )
        land["geometry"] = pg.make_valid(land.geometry.values.data)
        tree = pg.STRtree(df.geometry.values.data)
        ix = tree.query_bulk(land.geometry.values.data, predicate="contains_properly")[
            1
        ]

        print(f"Dropping {len(ix)} areas that are fully contapined within land areas")

        df = df.iloc[np.setdiff1d(df.index.values, ix)].copy()

    return df.to_crs(target_crs)
