from pathlib import Path

import geopandas as gp
import pandas as pd
from pyogrio import write_dataframe

from analysis.lib.util import append


data_dir = Path("data")
src_dir = data_dir / "nhd/raw"
out_dir = data_dir / "nhd/merged"

out_dir.mkdir(exist_ok=True)

huc2s = sorted(
    pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"]).HUC2.values
)

merged = None

for huc2 in huc2s:
    marine_filename = src_dir / huc2 / "nhd_marine.feather"
    if marine_filename.exists():
        marine = gp.read_feather(marine_filename)

        if len(marine):
            marine["HUC2"] = huc2
            merged = append(merged, marine)


df = merged.reset_index(drop=True)
df.to_feather(out_dir / "nhd_marine.feather")
write_dataframe(df, out_dir / "nhd_marine.fgb")
