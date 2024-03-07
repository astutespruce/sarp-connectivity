"""
Floodplain stats were generated in ArcGIS by SARP:
1. developing a floodplain mask from existing data sources and 90m around all flowlines
2. developing a binary map of natural landcover / not natural landcover
3. clipping landcover by floodplain mask
4. running zonal stats to calculate the area in natural landcover and not natural landcover in the floodplain mask

Note: some catchments have no floodplain, and some have floodplains but no NHDPlusID (outside HUC4s we processed).  These are filtered out.
"""

from pathlib import Path
from time import time

import pandas as pd
from pyogrio import read_dataframe, list_layers

from analysis.lib.util import append

# NLCD natural landcover classes
# descriptions here: https://www.mrlc.gov/data/legends/national-land-cover-database-2016-nlcd2016-legend
NATURAL_TYPES = {11, 12, 31, 41, 42, 43, 51, 52, 71, 72, 73, 74, 90, 95}


data_dir = Path("data")
src_dir = data_dir / "floodplains"
gdb_filename = src_dir / "NLCD2021_Floodplain_Stats_FINAL_2024.gdb"
gdb2023_filename = src_dir / "HR_NLCD_Floodplain_Stats_Tables_2023.gdb"

start = time()

huc2_df = pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"])
huc2s = huc2_df.HUC2.sort_values().values.tolist()

layers = list_layers(gdb_filename)[:, 0]

merged = None
for layer in layers:
    huc2 = layer[-2:]
    print(f"Processing floodplain stats for {huc2}...")

    df = read_dataframe(gdb_filename, layer=layer)
    df["HUC2"] = huc2

    df = df.loc[df.NHDIDSTR != "None"].reset_index(drop=True)

    df["NHDPlusID"] = df.NHDIDSTR.astype("uint64")
    cols = [c for c in df.columns if c.startswith("VALUE_")]
    natural_cols = [c for c in cols if int(c.split("_")[1]) in NATURAL_TYPES]

    df["floodplain_km2"] = df[cols].sum(axis=1) * 1e-6
    df["nat_floodplain_km2"] = df[natural_cols].sum(axis=1) * 1e-6

    merged = append(merged, df[["HUC2", "NHDPlusID", "nat_floodplain_km2", "floodplain_km2"]])


### read region 21 from old GDB
print("Processing floodplain stats for 21...")
df = read_dataframe(gdb2023_filename, layer="statsHR_region21_catchments_021")
df["HUC2"] = "21"
df["NHDPlusID"] = df.NHDIDSTR.astype("uint64")
cols = [c for c in df.columns if c.startswith("VALUE_")]

# NOTE: region 21 is from a different landcover dataset; VALUE_1 is natural
natural_cols = ["VALUE_1"]

df["floodplain_km2"] = df[cols].sum(axis=1) * 1e-6
df["nat_floodplain_km2"] = df[natural_cols].sum(axis=1) * 1e-6

merged = append(merged, df[["HUC2", "NHDPlusID", "nat_floodplain_km2", "floodplain_km2"]])


merged.reset_index(drop=True).to_feather(src_dir / "floodplain_stats.feather")

print(f"Done in {time() - start:.2f}")
