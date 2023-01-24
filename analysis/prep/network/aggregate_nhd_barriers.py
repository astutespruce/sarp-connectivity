from pathlib import Path
import os
import warnings

import pandas as pd
import geopandas as gp
from pyogrio import write_dataframe

from analysis.lib.io import read_feathers


data_dir = Path("data")

huc2s = sorted(
    pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"]).HUC2.values
)

src_dir = Path("data/nhd/raw")
out_dir = Path("data/nhd/merged")

if not out_dir.exists():
    os.makedirs(out_dir)


for group in ["points", "lines", "poly"]:
    df = read_feathers(
        [src_dir / huc2 / f"nhd_{group}.feather" for huc2 in huc2s], geo=True
    )
    df.to_feather(out_dir / f"nhd_{group}.feather")
    write_dataframe(df, out_dir / f"nhd_{group}.fgb")
