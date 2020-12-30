from pathlib import Path
import os
from time import time
import warnings

import pandas as pd
import geopandas as gp
import pygeos as pg
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS
from analysis.lib.util import append


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


COLS = ["NHDPlusID", "FType", "FCode", "GNIS_Name", "geometry"]

# Dam, reservoir, waterfall
POINT_FTYPES = [343, 436, 487]

# Dam, Gate, Lock Chamber, Waterfall
LINE_FTYPES = [343, 369, 398, 487]

# Dam, Lock, Spillway
POLY_FTYPES = [343, 398, 455]


def process_huc4s(src_dir, out_dir, huc4s):
    merged_points = None
    merged_lines = None
    merged_poly = None

    for huc4 in huc4s:
        print(f"Reading: {huc4}")

        gdb = src_dir / huc4 / f"NHDPLUS_H_{huc4}_HU4_GDB.gdb"

        df = read_dataframe(
            gdb,
            layer="NHDPoint",
            columns=COLS,
            force_2d=True,
            where=f"FType in {tuple(POINT_FTYPES)}",
        )
        if len(df):
            df = df.to_crs(CRS)
            df.NHDPlusID = df.NHDPlusID.astype("uint64")
            df["HUC4"] = huc4
            df.geometry = pg.make_valid(df.geometry.values.data)
            merged_points = append(merged_points, df)

        df = read_dataframe(
            gdb,
            layer="NHDLine",
            columns=COLS,
            force_2d=True,
            where=f"FType in {tuple(LINE_FTYPES)}",
        )
        if len(df):
            df = df.to_crs(CRS)
            df.NHDPlusID = df.NHDPlusID.astype("uint64")
            df["HUC4"] = huc4
            df.geometry = pg.make_valid(df.geometry.values.data)
            merged_lines = append(merged_lines, df)

        df = read_dataframe(
            gdb,
            layer="NHDArea",
            columns=COLS,
            force_2d=True,
            where=f"FType in {tuple(POLY_FTYPES)}",
        )
        if len(df):
            df = df.to_crs(CRS)
            df.NHDPlusID = df.NHDPlusID.astype("uint64")
            df["HUC4"] = huc4
            df.geometry = pg.make_valid(df.geometry.values.data)
            merged_poly = append(merged_poly, df)

    if merged_points is not None:
        points = merged_points.reset_index(drop=True)
        points.to_feather(out_dir / "nhd_points.feather")
        write_dataframe(points, out_dir / "nhd_points.gpkg")

    if merged_lines is not None:
        lines = merged_lines.reset_index(drop=True)
        lines.to_feather(out_dir / "nhd_lines.feather")
        write_dataframe(lines, out_dir / "nhd_lines.gpkg")

    if merged_poly is not None:
        poly = merged_poly.reset_index(drop=True)
        poly.to_feather(out_dir / "nhd_poly.feather")
        write_dataframe(poly, out_dir / "nhd_poly.gpkg")


data_dir = Path("data")
src_dir = data_dir / "nhd/source/huc4"
out_dir = data_dir / "nhd/raw"


start = time()

huc4_df = pd.read_feather(
    data_dir / "boundaries/huc4.feather", columns=["HUC2", "HUC4"]
)
# Convert to dict of sorted HUC4s per HUC2
units = huc4_df.groupby("HUC2").HUC4.unique().apply(sorted).to_dict()

# manually subset keys from above for processing
huc2s = [
    "02",
    "03",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "21",
]


for huc2 in huc2s:
    huc2_start = time()
    print(f"----- {huc2} ------")

    process_huc4s(src_dir, out_dir / huc2, units[huc2])

    print("HUC2: {} done in {:.0f}s\n\n".format(huc2, time() - huc2_start))

print("Done in {:.2f}s\n============================".format(time() - start))
