from pathlib import Path
import os

import geopandas as gp
from pyogrio import write_dataframe

from analysis.lib.util import append


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

src_dir = Path("data/nhd/raw")
out_dir = Path("data/nhd/merged")

if not out_dir.exists():
    os.makedirs(out_dir)


for group in ["points", "lines", "poly"]:
    merged = None

    for huc2 in huc2s:
        huc2_dir = src_dir / huc2

        filename = huc2_dir / f"nhd_{group}.feather"
        if filename.exists():
            df = gp.read_feather(filename)
            merged = append(merged, df)

    df = merged.reset_index(drop=True)
    df.to_feather(out_dir / f"nhd_{group}.feather")
    write_dataframe(df, out_dir / f"nhd_{group}.gpkg")
