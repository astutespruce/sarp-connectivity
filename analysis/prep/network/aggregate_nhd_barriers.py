from pathlib import Path
import os
import warnings

import pandas as pd
import geopandas as gp
from pyogrio import write_dataframe

from analysis.lib.util import append


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")

huc2s = sorted(
    pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"]).HUC2.values
)

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
