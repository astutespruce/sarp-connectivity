from pathlib import Path
from time import time
import warnings

import pandas as pd
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS
from analysis.lib.util import append
from analysis.prep.network.lib.nhd.util import get_column_names

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")
warnings.filterwarnings("ignore", message=".*Warning 1: organizePolygons.*")

MAX_HUC4s = 5  # max number of HUC4s to include before considering a split
# For region 17:
# MAX_HUC4s = 3


def process_huc4s(src_dir, huc4s):
    merged = None
    for HUC4 in huc4s:
        print(f"\n\n------------------- Reading {HUC4} -------------------")

        # filenames vary for current NHD HR datasets; beta datasets had stable names
        gdb = next((src_dir / HUC4).glob("*.gdb"))

        layer = "NHDPlusCatchment"
        read_cols, col_map = get_column_names(gdb, layer, ["NHDPlusID"])

        df = read_dataframe(gdb, layer=layer, columns=read_cols).rename(columns=col_map)
        print(f"Read {len(df):,} catchments")

        missing = df.NHDPlusID.isnull().sum()
        if missing:
            df = df.dropna(subset=["NHDPlusID"])

            print(f"Kept {len(df):,} catchments after dropping those without NHDPlusID")

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
tmp_dir = Path("/tmp/sarp")  # only need GIS files to provide to SARP
tmp_dir.mkdir(exist_ok=True, parents=True)


start = time()

huc4_df = pd.read_feather(
    data_dir / "boundaries/huc4.feather", columns=["HUC2", "HUC4"]
)
# Convert to dict of sorted HUC4s per HUC2
units = huc4_df.groupby("HUC2").HUC4.unique().apply(sorted).to_dict()
huc2s = units.keys()


# manually subset keys from above for processing
huc2s = [
    # "02",
    # "03",
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
    # "21",
]

for huc2 in huc2s:
    print(f"----- {huc2} ------")

    huc4s = units[huc2]

    if len(huc4s) > MAX_HUC4s:
        # split into smaller groups to keep output files smaller
        for counter, i in enumerate(range(0, len(huc4s), MAX_HUC4s)):
            print(f"Processing subgroup {huc2}_{counter}")

            df = process_huc4s(src_dir, huc4s[i : i + MAX_HUC4s])

            print(f"serializing {len(df):,} catchments")
            write_dataframe(df, tmp_dir / f"region{huc2}_catchments_{counter}.shp")

            del df

    else:
        df = process_huc4s(src_dir, huc4s)

        print(f"serializing {len(df):,} catchments")
        write_dataframe(df, tmp_dir / f"region{huc2}_catchments.shp")

        del df


print(f"Done in {time() - start:.2f}s\n============================")
