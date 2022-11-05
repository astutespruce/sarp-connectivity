"""
Floodplain stats were generated in ArcGIS by SARP:
1. developing a floodplain mask from existing data sources and 90m around all flowlines
2. developing a binary map of natural landcover / not natural landcover
3. clipping landcover by floodplain mask
4. running zonal stats to calculate the area in natural landcover and not natural landcover in the floodplain mask

Note: some catchments have no floodplain, and some have floodplains but no NHDPlusID (outside HUC4s we processed).  These are filtered out.
"""

import re
from pathlib import Path
from time import time

import pandas as pd
import geopandas as gp
from pyogrio import read_dataframe, list_layers

from analysis.lib.util import append

# NLCD natural landcover classes
# descriptions here: https://www.mrlc.gov/data/legends/national-land-cover-database-2016-nlcd2016-legend
NATURAL_TYPES = {11, 12, 31, 41, 42, 43, 51, 52, 71, 72, 73, 74, 90, 95}


data_dir = Path("data")
src_dir = data_dir / "floodplains"
gdb_filename = src_dir / "HR_NLCD19_Floodplain_Stats_Tables_2022.gdb"


# layers have varying names, make a lookup from them
layers = list_layers(gdb_filename)[:, 0]
layers = {re.search("\d+", l).group()[-2:]: l for l in layers}

huc4_df = pd.read_feather(
    data_dir / "boundaries/huc4.feather", columns=["HUC2", "HUC4"]
)
# Convert to dict of sorted HUC4s per HUC2
units = huc4_df.groupby("HUC2").HUC4.unique().apply(sorted).to_dict()


start = time()

merged = None

for huc2 in units.keys():
    print(f"Processing floodplain stats for {huc2}")

    if not huc2 in layers:
        print(f"WARNING: region {huc2} not found in floodplain data")
        continue

    df = read_dataframe(gdb_filename, layer=layers[huc2])

    df["HUC2"] = huc2
    df["NHDPlusID"] = df.NHDIDSTR.astype("uint64")
    cols = [c for c in df.columns if c.startswith("VALUE_")]
    natural_cols = [c for c in cols if int(c.split("_")[1]) in NATURAL_TYPES]

    df["floodplain_km2"] = df[cols].sum(axis=1) * 1e-6
    df["nat_floodplain_km2"] = df[natural_cols].sum(axis=1) * 1e-6

    merged = append(
        merged, df[["NHDPlusID", "HUC2", "nat_floodplain_km2", "floodplain_km2"]]
    )

merged.reset_index(drop=True).to_feather(src_dir / "floodplain_stats.feather")

print(f"Done in {time() - start:.2f}")
