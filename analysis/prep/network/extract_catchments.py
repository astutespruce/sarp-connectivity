from pathlib import Path
from time import time
import warnings

import pandas as pd
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS
from analysis.lib.util import append
from analysis.prep.network.lib.nhd.util import get_column_names


warnings.filterwarnings("ignore", message=".*organizePolygons.*")


def process_gdbs(src_dir):
    merged = None

    gdbs = sorted(
        [gdb for gdb in src_dir.glob(f"{huc2}*/*.gdb")],
        key=lambda p: p.parent.name,
    )

    if len(gdbs) == 0:
        raise ValueError(f"No GDBs available for {huc2} within {src_dir}; did you forget to unzip them?")

    for gdb in gdbs:
        print(f"Reading {gdb.name}")
        layer = "NHDPlusCatchment"
        read_cols, col_map = get_column_names(gdb, layer, ["NHDPlusID"])

        df = read_dataframe(gdb, layer=layer, columns=read_cols, use_arrow=True).rename(columns=col_map)
        print(f"Read {len(df):,} catchments")

        missing = df.NHDPlusID.isnull().sum()
        if missing:
            df = df.dropna(subset=["NHDPlusID"])

            print(f"Kept {len(df):,} catchments after dropping {missing:,} without NHDPlusID")

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
huc4_dir = data_dir / "nhd/source/huc4"
huc8_dir = data_dir / "nhd/source/huc8"
out_dir = data_dir / "nhd/raw"
out_dir.mkdir(exist_ok=True)
tmp_dir = Path("/tmp/sarp")  # only need GIS files to provide to SARP
tmp_dir.mkdir(exist_ok=True, parents=True)


start = time()

huc2_df = pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"])
huc2s = huc2_df.HUC2.sort_values().values

# manually subset keys from above for processing
# huc2s = [
# "01",
# "02",
# "03",
# "04",
# "05",
# "06",
# "07",
# "08",
# "09",
# "10",
# "11",
# "12",
# "13",
# "14",
# "15",
# "16",
# "17",
# "18",
# "19",
# "20",
# "21",
# ]

for huc2 in huc2s:
    print(f"\n\n----- {huc2} ------")

    src_dir = huc8_dir if huc2 == "19" else huc4_dir
    df = process_gdbs(src_dir)

    print(f"\n====================================\nserializing {len(df):,} catchments")

    # just save listing of NHDPlusIDs that we expect from floodlpain data
    huc2_dir = out_dir / huc2
    huc2_dir.mkdir(exist_ok=True)
    df[["NHDPlusID"]].astype("uint64").to_feather(huc2_dir / "catchment_ids.feather")

    # convert to types allowed by GDB
    df = df.astype({"NHDPlusID": "float64", "catchID": "int32"})
    write_dataframe(df, tmp_dir / f"region{huc2}_catchments.gdb", driver="OpenFileGDB")

    del df


print(f"Done in {time() - start:.2f}s\n============================")
