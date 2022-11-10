from pathlib import Path
from time import time
import warnings

import geopandas as gp

from analysis.lib.util import pack_bits, get_signed_dtype
from analysis.rank.lib.networks import get_network_results
from analysis.rank.lib.metrics import (
    classify_streamorder,
    classify_spps,
    classify_percent_altered,
)
from api.constants import SB_API_FIELDS, SB_PACK_BITS, DOMAINS


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
api_dir.mkdir(exist_ok=True, parents=True)
results_dir = data_dir / "barriers/networks"
results_dir.mkdir(exist_ok=True, parents=True)


### Read in master

cols = [
    "geometry",
    "id",
    "SARPID",
    "lon",
    "lat",
    "Name",
    "LocalID",
    "Source",
    "Road",
    "RoadType",
    "PotentialProject",
    "BarrierSeverity",
    "SARP_Score",
    "YearRemoved",
    "Basin",
    "Stream",
    "Subbasin",
    "Subwatershed",
    "Recon",
    "Condition",
    "CrossingCode",
    "CrossingType",
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
    "HUC8_COA",
    "ManualReview",
    "ProtectedLand",
    "OwnerType",
    "BarrierOwnerType",
    "TESpp",
    "StateSGCNSpp",
    "RegionalSGCNSpp",
    "Trout",
    "dropped",
    "excluded",
    "removed",
    "duplicate",
    "snapped",
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
    gp.read_feather(barriers_dir / "small_barriers.feather", columns=cols)
    .set_index("id")
    .rename(
        columns={
            "excluded": "Excluded",
            "intermittent": "Intermittent",
            "invasive": "Invasive",
            "unranked": "Unranked",
            "loop": "OnLoop",
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
# NOTE: not calculating state ranks, per guidance from SARP
# (not enough barriers to have appropriate ranks)
networks = get_network_results(df, "small_barriers")

df = df.join(networks)

# True if the barrier was snapped to a network and has network results in the
# all networks scenario
df["HasNetwork"] = df.index.isin(networks.index)
df["Ranked"] = df.HasNetwork & (~df.Unranked)

### Pack bits for categorical fields not used for filtering
# IMPORTANT: this needs to happen here, before backfilling fields with -1
pack_cols = [e["field"] for e in SB_PACK_BITS]
tmp = df[pack_cols].copy()
# recode streamorder -1 to 0 for packing
tmp.loc[tmp.StreamOrder == -1, "StreamOrder"] = 0

df["packed"] = pack_bits(tmp, SB_PACK_BITS)


### Classify PercentAltered
df["PercentAltered"] = -1
df.loc[df.HasNetwork, "PercentAltered"] = 100 - df.loc[df.HasNetwork].PercentUnaltered
df["PercentAlteredClass"] = classify_percent_altered(df.PercentAltered)


# fill network columns and set proper type
for col in networks.columns:
    df[col] = df[col].fillna(-1).astype(get_signed_dtype(networks[col].dtype))

### Sanity check
if df.groupby(level=0).size().max() > 1:
    raise ValueError(
        "Error - there are duplicate barriers in the results for small_barriers.  Check uniqueness of IDs and joins."
    )


### Verify domains
print("Verifying domain values")
failed = False
for col in df.columns.intersection(DOMAINS.keys()):
    diff = set(df[col].unique()).difference(DOMAINS[col].keys())
    if diff:
        print(f"Missing values from domain lookup: {col}: {diff}")
        failed = True

if failed:
    raise ValueError(
        "ERROR: stopping; one or more domain fields includes values not present in domain lookup"
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
