import os
from pathlib import Path
from time import time
import warnings

import pandas as pd
import geopandas as gp
import pygeos as pg

from analysis.rank.lib.networks import get_network_results
from analysis.rank.lib.metrics import (
    classify_streamorder,
    classify_spps,
    classify_percent_altered,
)
from api.constants import SB_API_FIELDS


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
qa_dir = data_dir / "networks/qa"

if not os.path.exists(api_dir):
    os.makedirs(api_dir)


if not os.path.exists(qa_dir):
    os.makedirs(qa_dir)

### Read in master
print("Reading master...")
df = (
    gp.read_feather(barriers_dir / "small_barriers.feather")
    .set_index("id")
    .drop(
        columns=[
            "level_0",
            "index",
            "dup_group",
            "dup_count",
            "dup_log",
            "snap_dist",
            "snap_tolerance",
            "snap_ref_id",
            "snap_log",
            "snapped",
            "log",
            "lineID",
            "wbID",
        ],
        errors="ignore",
    )
    .rename(columns={"excluded": "Excluded", "intermittent": "Intermittent",})
)

# Drop any that are duplicates
# NOTE: we retain those that were dropped because these are relevant for folks to know what
# has been inventoried (e.g., those dropped because no barrier, etc)
# but do drop any that have no state or HUC2
df = df.loc[(~df.duplicate) & (df.State)].copy()


### Classify StreamOrder
df["StreamOrderClass"] = classify_streamorder(df.StreamOrder)


for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    df[f"{col}Class"] = classify_spps(df[col])


### Get network results
networks = get_network_results(df, "small_barriers")

df = df.join(networks)

# True if the barrier was snapped to a network and has network results in the
# all networks scenario
df["HasNetwork"] = df.index.isin(networks.index)
df["Ranked"] = df.HasNetwork & (~df.unranked)

# Intermittent is not applicable if it doesn't have a network
df["Intermittent"] = df["Intermittent"].astype("int8")
df.loc[~df.HasNetwork, "Intermittent"] = -1

### Classify PercentAltered
df["PercentAltered"] = -1
df.loc[df.HasNetwork, "PercentAltered"] = 100 - df.loc[df.HasNetwork].PercentUnaltered
df["PercentAlteredClass"] = classify_percent_altered(df.PercentAltered)


# fill columns and set proper type
for col in networks.columns:
    df[col] = df[col].fillna(-1).astype(networks[col].dtype)

### Sanity check
if df.groupby(level=0).size().max() > 1:
    raise ValueError(
        "Error - there are duplicate barriers in the results for small_barriers.  Check uniqueness of IDs and joins."
    )


### Write out data for API
print(f"Writing to output files...")

# Full results for SARP QA/QC
df.reset_index().to_feather(qa_dir / "small_barriers_network_results.feather")

# save for API
df[df.columns.intersection(SB_API_FIELDS)].reset_index().to_feather(
    api_dir / f"small_barriers.feather"
)

