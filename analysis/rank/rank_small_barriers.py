import os
from pathlib import Path
from time import time
import warnings

import pandas as pd

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
results_dir = data_dir / "barriers/networks"

if not os.path.exists(api_dir):
    os.makedirs(api_dir)

if not os.path.exists(results_dir):
    os.makedirs(results_dir)

### Read in master

cols = [
    "id",
    "SARPID",
    "lon",
    "lat",
    "Name",
    "LocalID",
    "Source",
    "Road",
    "RoadType",
    "RoadTypeClass",
    "PotentialProject",
    "SeverityClass",
    "SARP_Score",
    "YearRemoved",
    "Basin",
    "Stream",
    "Subbasin",
    "Subwatershed",
    "Recon",
    "Condition",
    "ConditionClass",
    "CrossingCode",
    "CrossingType",
    "CrossingTypeClass",
    "Constriction",
    "Editor",
    "EditDate",
    "FCode",
    "State",
    "COUNTYFIPS",
    "County",
    "HUC2",
    "HUC4",
    "HUC6",
    "HUC8",
    "HUC10",
    "HUC12",
    "ECO3",
    "ECO4",
    "HUC8_COA",
    "HUC8_SGCN",
    "HUC8_USFS",
    "ManualReview",
    "ProtectedLand",
    "OwnerType",
    "TESpp",
    "StateSGCNSpp",
    "RegionalSGCNSpp",
    "Trout",
    "dropped",
    "excluded",
    "duplicate",
    "unranked",
    "invasive",
    "NHDPlusID",
    "loop",
    "StreamOrder",
    "sizeclass",
    "AnnualFlow",
    "AnnualVelocity",
    "TotDASqKm",
    "stream_type",
    "intermittent",
]


print("Reading master...")
df = (
    pd.read_feather(barriers_dir / "small_barriers.feather", columns=cols)
    .set_index("id")
    .rename(
        columns={
            "excluded": "Excluded",
            "intermittent": "Intermittent",
            "invasive": "Invasive",
            "unranked": "Unranked",
            "sizeclass": "StreamSizeClass",
        }
    )
)

# flowline properties not applicable if it doesn't have a network
df["NHDPlusID"] = df.NHDPlusID.fillna(-1).astype("int64")
df["Intermittent"] = df["Intermittent"].astype("int8")
df.loc[~df.snapped, "Intermittent"] = -1
df["AnnualFlow"] = df.AnnualFlow.fillna(-1).astype("float32")
df["AnnualVelocity"] = df.AnnualVelocity.fillna(-1).astype("float32")
df["TotDASqKm"] = df.TotDASqKm.fillna(-1).astype("float32")

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
df["Ranked"] = df.HasNetwork & (~df.Unranked)

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
        "Error - there are duplicate barriers in the results for small_barriers.  Check uniqueness of IDs and joins."
    )


### Write out data for API
print(f"Writing to output files...")

df = df.reset_index()
df["id"] = df.id.astype("uint32")

# Full results for tiles, etc
df.to_feather(results_dir / "small_barriers.feather")

# save for API
df[df.columns.intersection(["id"] + SB_API_FIELDS)].to_feather(
    api_dir / f"small_barriers.feather"
)
