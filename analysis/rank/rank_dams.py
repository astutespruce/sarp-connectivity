import os
from pathlib import Path
from time import time
import warnings

import pandas as pd

from analysis.rank.lib.networks import get_network_results
from analysis.rank.lib.metrics import (
    classify_percent_altered,
    classify_streamorder,
    classify_spps,
)
from api.constants import DAM_API_FIELDS


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
results_dir = data_dir / "barriers/networks"

if not os.path.exists(api_dir):
    os.makedirs(api_dir)

if not os.path.exists(results_dir):
    os.makedirs(results_dir)


### Read in master
print("Reading master...")
df = (
    pd.read_feather(barriers_dir / "dams.feather")
    .set_index("id")
    .drop(
        columns=[
            "geometry",
            "level_0",
            "index",
            "dup_group",
            "dup_count",
            "dup_sort",
            "dup_log",
            "snap_dist",
            "snap_tolerance",
            "snap_ref_id",
            "snap_log",
            "snap_group",
            "snapped",
            "NHDPlusID",
            "lineID",
            "wbID",
            "waterbody",
            "src",
            "kind",
            "log",
            "SourceState",
        ],
        errors="ignore",
    )
    .rename(
        columns={
            "excluded": "Excluded",
            "intermittent": "Intermittent",
            "is_estimated": "Estimated",
        }
    )
)


### Save dams that were removed, for use in API (they are otherwise dropped below)
removed = pd.DataFrame(
    df.loc[
        (df.Recon == 7) | (df.ManualReview == 8),
        [
            "lat",
            "lon",
            "Name",
            "SARPID",
            "NIDID",
            "Source",
            "SourceDBID",
            "River",
            "Year",
            "Year_Removed",
            "Height",
            "Construction",
            "Purpose",
            "State",
            "County",
            "HUC8",
            "HUC12",
            "duplicate",
        ],
    ]
)
removed.reset_index().to_feather(api_dir / "removed_dams.feather")


### drop any that should be DROPPED (dropped or duplicate) from the analysis
# NOTE: excluded ones are retained but don't have networks; ones on loops are retained but also don't have networks
df = df.loc[~(df.dropped | df.duplicate)].copy()

### Classify StreamOrder
df["StreamOrderClass"] = classify_streamorder(df.StreamOrder)

for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    df[f"{col}Class"] = classify_spps(df[col])


### Get network results
networks = get_network_results(df, "dams")
df = df.join(networks)

# True if the barrier was snapped to a network and has network results in the
# all networks scenario
df["HasNetwork"] = df.index.isin(networks.index)
df["Ranked"] = df.HasNetwork & (~df.unranked)

# intermittent is not applicable if it doesn't have a network
df["Intermittent"] = df["Intermittent"].astype("int8")
df.loc[~df.HasNetwork, "Intermittent"] = -1

### Classify PercentAltered
df["PercentAltered"] = -1
df.loc[df.HasNetwork, "PercentAltered"] = 100 - df.loc[df.HasNetwork].PercentUnaltered
df["PercentAlteredClass"] = classify_percent_altered(df.PercentAltered)


# fill network columns and set proper type
for col in networks.columns:
    df[col] = df[col].fillna(-1).astype(networks[col].dtype)


### Sanity check
if df.groupby(level=0).size().max() > 1:
    raise ValueError(
        "Error - there are duplicate barriers in the results for dams.  Check uniqueness of IDs and joins."
    )

### Write out data for API
print("Writing to output files...")

# Full results for tiles, etc
df.reset_index().to_feather(results_dir / f"dams.feather")

# save for API
df[df.columns.intersection(DAM_API_FIELDS)].reset_index().to_feather(
    api_dir / f"dams.feather"
)

print(f"Done in {time() - start:.2f}")
