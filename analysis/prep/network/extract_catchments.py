from pathlib import Path
import os
from time import time
import warnings

import pandas as pd
import pygeos as pg
import geopandas as gp
from pyogrio import read_dataframe, write_dataframe

from nhdnet.nhd.extract import extract_flowlines, extract_waterbodies

from analysis.constants import (
    CRS,
)
from analysis.lib.util import append


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

MAX_HUC4s = 5  # max number of HUC4s to include before considering a split


def process_huc4s(src_dir, huc4s):

    merged = None
    for HUC4 in huc4s:
        print("\n\n------------------- Reading {} -------------------".format(HUC4))

        gdb = src_dir / HUC4 / "NHDPLUS_H_{HUC4}_HU4_GDB.gdb".format(HUC4=HUC4)

        df = read_dataframe(gdb, layer="NHDPlusCatchment", columns=["NHDPlusID"])
        print(f"Read {len(df):,} catchments")

        df = df.dropna(subset=["NHDPlusID"])

        print(
            "Kept {:,} catchments after dropping those without NHDPlusID".format(
                len(df)
            )
        )

        df.NHDPlusID = df.NHDPlusID.astype("uint64")

        df = df.to_crs(CRS)
        merged = append(merged, df)

    df = merged

    # add uniqueID
    df["catchID"] = df.index.astype("uint32") + 1

    # add string version of NHDPlusID
    df["NHDIDSTR"] = df.NHDPlusID.astype("str")

    return df


data_dir = Path("data")
src_dir = data_dir / "nhd/source/huc4"
out_dir = data_dir / "nhd/raw"
tmp_dir = Path("/tmp/sarp")  # only need GIS files to provide to SARP

if not out_dir.exists():
    os.makedirs(out_dir)

if not tmp_dir.exists():
    os.makedirs(tmp_dir)

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
    print("----- {} ------".format(huc2))

    huc2_dir = out_dir / huc2
    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    huc4s = units[huc2]

    if len(huc4s) > MAX_HUC4s:
        # split into smaller groups to keep output files smaller
        for counter, i in enumerate(range(0, len(huc4s), MAX_HUC4s)):
            print(f"Processing subgroup {huc2}_{counter}")

            df = process_huc4s(src_dir, huc4s[i : i + MAX_HUC4s])

            print("serializing {:,} catchments".format(len(df)))
            df[["NHDPlusID", "geometry"]].to_feather(
                huc2_dir / f"catchments_{counter}.feather"
            )
            write_dataframe(df, tmp_dir / f"region{huc2}_catchments_{counter}.shp")

    else:
        df = process_huc4s(src_dir, huc4s)

        print("serializing {:,} catchments".format(len(df)))
        df[["NHDPlusID", "geometry"]].to_feather(huc2_dir / f"catchments.feather")
        write_dataframe(df, tmp_dir / f"region{huc2}_catchments.shp")


print("Done in {:.2f}s\n============================".format(time() - start))
