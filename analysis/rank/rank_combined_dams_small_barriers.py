from pathlib import Path
from time import time
import warnings

import geopandas as gp
import pandas as pd

from analysis.lib.util import pack_bits, get_signed_dtype
from analysis.rank.lib.networks import get_network_results
from analysis.rank.lib.metrics import (
    classify_percent_altered,
    classify_streamorder,
    classify_spps,
)
from api.constants import DAM_API_FIELDS, SB_API_FIELDS, DAM_PACK_BITS, DOMAINS, unique

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
api_dir.mkdir(exist_ok=True, parents=True)
results_dir = data_dir / "barriers/networks"
results_dir.mkdir(exist_ok=True, parents=True)

### Read in master
# cols must include all fields used in API and tiles

# common columns
cols = [
    "AnnualFlow",
    "AnnualVelocity",
    "BarrierOwnerType",
    "BarrierSeverity",
    "Condition",
    "Basin",
    "COUNTYFIPS",
    "County",
    "ECO3",
    "ECO4",
    "EditDate",
    "Editor",
    "FCode",
    "HUC10",
    "HUC12",
    "HUC2",
    "HUC4",
    "HUC6",
    "HUC8",
    "HUC8_COA",
    "HUC8_SGCN",
    "HUC8_USFS",
    "ManualReview",
    "NHDPlusID",
    "Name",
    "OwnerType",
    "ProtectedLand",
    "Recon",
    "RegionalSGCNSpp",
    "SARPID",
    "Source",
    "State",
    "StateSGCNSpp",
    "StreamOrder",
    "Subbasin",
    "Subwatershed",
    "TESpp",
    "TotDASqKm",
    "Trout",
    "YearRemoved",
    "dropped",
    "duplicate",
    "excluded",
    "geometry",
    "id",
    "intermittent",
    "invasive",
    "lat",
    "lon",
    "loop",
    "removed",
    "sizeclass",
    "snapped",
    "stream_type",
    "unranked",
]

dam_cols = [
    "BarrierStatus",
    "Construction",
    "Diversion",
    "Feasibility",
    "FishScreen",
    "Height",
    "HeightClass",
    "Length",
    "Link",
    "LowheadDam",
    "NIDID",
    "OtherName",
    "PassageFacility",
    "PassageFacilityClass",
    "Purpose",
    "River",
    "ScreenType",
    "SourceDBID",
    "StructureCategory",
    "WaterbodyKM2",
    "WaterbodySizeClass",
    "Width",
    "YearCompleted",
    "is_estimated",
]


barrier_cols = [
    "Constriction",
    "CrossingCode",
    "CrossingType",
    "LocalID",
    "PotentialProject",
    "Road",
    "RoadType",
    "SARP_Score",
    "Stream",
]


### Read dams and small barriers and their associated networks
# NOTE: we are intentionally not setting the index to "id" column
print("Reading barriers and networks")
dams = gp.read_feather(barriers_dir / "dams.feather", columns=cols + dam_cols)
dams["BarrierType"] = "dam"
dams = dams.loc[~(dams.dropped | dams.duplicate)]

barriers = gp.read_feather(
    barriers_dir / "small_barriers.feather", columns=cols + barrier_cols
)
barriers["BarrierType"] = "Inventoried road-related barrier"
barriers = barriers.loc[~(barriers.dropped | barriers.duplicate)]

df = (
    pd.concat([dams, barriers], ignore_index=True, sort=False)
    .rename(
        columns={
            "excluded": "Excluded",
            "intermittent": "Intermittent",
            "is_estimated": "Estimated",
            "invasive": "Invasive",
            # "nostructure": "NoStructure",
            "unranked": "Unranked",
            "loop": "OnLoop",
            "sizeclass": "StreamSizeClass",
        }
    )
    .set_index("id")
)

networks = get_network_results(
    df,
    network_type="small_barriers",
    barrier_types=["dams", "small_barriers"],
    state_ranks=True,
)
df = df.join(networks)
df["HasNetwork"] = df.index.isin(networks.index)

### Set ranked status
# True if the barrier was snapped to a network, is not a loop, has network
# results, and is not excluded from ranking
df["Ranked"] = df.HasNetwork & (~df.Unranked)


### Calculate classes for API
df["StreamOrderClass"] = classify_streamorder(df.StreamOrder)

for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    df[f"{col}Class"] = classify_spps(df[col])

df["PercentAltered"] = -1
df.loc[df.HasNetwork, "PercentAltered"] = 100 - df.loc[df.HasNetwork].PercentUnaltered
df["PercentAlteredClass"] = classify_percent_altered(df.PercentAltered)


### Fill missing data
# set -1 when network not available for barrier
for col in networks.columns:
    df[col] = df[col].fillna(-1).astype(get_signed_dtype(networks[col].dtype))

# flowline properties not applicable if it doesn't have a network
df["NHDPlusID"] = df.NHDPlusID.fillna(-1).astype("int64")
df["Intermittent"] = df["Intermittent"].astype("int8")
df.loc[~df.snapped, "Intermittent"] = -1
df["AnnualFlow"] = df.AnnualFlow.fillna(-1).astype("float32")
df["AnnualVelocity"] = df.AnnualVelocity.fillna(-1).astype("float32")
df["TotDASqKm"] = df.TotDASqKm.fillna(-1).astype("float32")

# fill bool columns
bool_columns = ["Estimated"]
for col in bool_columns:
    df[col] = df[col].fillna(False)

# fill string columns
dt = df.dtypes
str_columns = dt[dt == object].index
for col in str_columns:
    df[col] = df[col].fillna("")


# fill most domain columns with -1 (not applicable)
fill_columns = [
    # dam columns
    "Construction",
    "Diversion",
    "Feasibility",
    "FishScreen",
    "Height",
    "HeightClass",
    "Length",
    "LowheadDam",
    "PassageFacility",
    "PassageFacilityClass",
    "Purpose",
    "ScreenType",
    "StructureCategory",
    "WaterbodyKM2",
    "WaterbodySizeClass",
    "Width",
    "YearCompleted",
    # small barrier columns
    "BarrierStatus",
    "Constriction",
    "CrossingType",
    "RoadType",
    "SARP_Score",
]

for col in fill_columns:
    orig_dtype = dams[col].dtype if col in dams.columns else barriers[col].dtype
    df[col] = df[col].fillna(-1).astype(get_signed_dtype(orig_dtype))


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


# FIXME: bit packing is likely no longer valid for categorical values that have -1

# TODO: pack combined fields?
# ### Pack bits for categorical fields not used for filtering
# # IMPORTANT: this needs to happen here, before backfilling fields with -1
# pack_cols = [e["field"] for e in DAM_PACK_BITS]
# tmp = df[pack_cols].copy()
# # recode streamorder -1 to 0 for packing
# tmp.loc[tmp.StreamOrder == -1, "StreamOrder"] = 0

# df["packed"] = pack_bits(tmp, DAM_PACK_BITS)


### Sanity check
if df.groupby(level=0).size().max() > 1:
    raise ValueError(
        "Error - there are duplicate barriers in the results for dams and barriers.  Check uniqueness of IDs and joins."
    )


# TODO:
### Write out data for API
print("Writing to output files...")

df = df.reset_index()

# Full results for tiles, etc
df.to_feather(results_dir / f"dams_small_barriers.feather")

# save for API
fields = unique(["id", "BarrierType"] + DAM_API_FIELDS + SB_API_FIELDS)
cols = [c for c in fields if c in df.columns]
df[cols].to_feather(api_dir / f"dams_small_barriers.feather")

print(f"Done in {time() - start:.2f}")
