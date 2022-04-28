from pathlib import Path
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
import pygeos as pg
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import (
    CRS,
    DAM_FS_COLS,
)
from analysis.lib.io import read_feathers

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
src_dir = data_dir / "barriers/source"


### Read NID + NE TNC data, and standardize to internal structure
df = read_dataframe(
    src_dir / "OuterHUC4_Dams_2022.gdb", layer="NEW_NID_OUTERHUC4_2022"
).to_crs(CRS)
cols = [c for c in df.columns if c in DAM_FS_COLS]
df = df[cols + ["geometry"]].rename(
    columns={
        "SARPUniqueID": "SARPID",
        "PotentialFeasibility": "Feasibility",
        "Barrier_Name": "Name",
        "Other_Barrier_Name": "OtherName",
        "DB_Source": "Source",
        "Year_Completed": "Year",
        "Year_Removed": "YearRemoved",
        "ConstructionMaterial": "Construction",
        "PurposeCategory": "Purpose",
        "StructureCondition": "Condition",
    }
)
df["ManualReview"] = 0
df["SourceState"] = df.SARPID.str[:2]

# Dams without NIDID came from NE TNC data
df["NIDID"] = df.NIDID.fillna("")
df = df.set_index("NIDID")

s = df.groupby("SARPID").size().sort_values()
dup_sarpid = s[s > 1]
if len(dup_sarpid):
    print(f"WARNING: duplicate SARPIDs detected\n{dup_sarpid}")

# TEMP: drop sub-NIDIDs; Kat is fixing the SARPIDs for these
drop_ids = (
    df.loc[df.SARPID.isin(dup_sarpid.index.sort_values())].set_index("SourceDBID").index
)
drop_ids = drop_ids[drop_ids.str.contains("S00")]
df = df.loc[~df.SourceDBID.isin(drop_ids)].copy()

df.to_feather(src_dir / "dams_outer_huc4.feather")
write_dataframe(df, src_dir / "dams_outer_huc4.fgb")

