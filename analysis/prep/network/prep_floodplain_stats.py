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
import re

import pandas as pd
from pyogrio import read_dataframe, list_layers

from analysis.lib.util import append

# per instructions from Kat 3/28/2025, exclude the following for NLCD and assume the rest are natural
# types listed here https://www.mrlc.gov/data/legends/national-land-cover-database-class-legend-and-description
NON_NATURAL_TYPES = {21, 22, 23, 24, 81, 82}

# NOTE: other regions (AK, HI, PR, USVI) use LANDFIRE and only use VALUE_1 to indicate natural types
LANDFIRE_HUC2s = {"19", "20", "21"}

data_dir = Path("data")
src_dir = data_dir / "floodplains"
gdb_filename = src_dir / "Floodplain_Statistics_2025.gdb"

start = time()

huc2_df = pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"])
huc2s = huc2_df.HUC2.sort_values().values.tolist()

layers = sorted(list_layers(gdb_filename)[:, 0])

merged = None
for layer in layers:
    huc2 = re.search(r"(?<=Floodplain_stats_\d)\d\d", layer).group()

    print(f"Processing floodplain stats for {huc2}...")

    df = read_dataframe(gdb_filename, layer=layer)
    df["HUC2"] = huc2

    df = df.loc[df.NHDIDSTR != "None"].reset_index(drop=True)

    df["NHDPlusID"] = df.NHDIDSTR.astype("uint64")

    if huc2 in LANDFIRE_HUC2s:
        cols = [c for c in df.columns if c.startswith("VALUE_")]
        natural_cols = ["VALUE_1"]

    else:
        # exclude VALUE_0 (NODATA)
        cols = [c for c in df.columns if c.startswith("VALUE_") and c != "VALUE_0"]
        natural_cols = [c for c in cols if int(c.split("_")[1]) not in NON_NATURAL_TYPES]

    df["floodplain_km2"] = df[cols].sum(axis=1) * 1e-6
    df["nat_floodplain_km2"] = df[natural_cols].sum(axis=1) * 1e-6

    merged = append(
        merged, df.loc[df.floodplain_km2 > 0, ["HUC2", "NHDPlusID", "nat_floodplain_km2", "floodplain_km2"]]
    )


merged.reset_index(drop=True).to_feather(src_dir / "floodplain_stats.feather")

print(f"Done in {time() - start:.2f}")
