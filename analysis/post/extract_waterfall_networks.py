from pathlib import Path

import geopandas as gp

from api.constants import WF_CORE_FIELDS, WF_PACK_BITS
from analysis.lib.util import pack_bits, get_signed_dtype
from analysis.rank.lib.metrics import classify_streamorder, classify_spps
from analysis.rank.lib.networks import get_network_results


data_dir = Path("data")
api_dir = data_dir / "api"
barriers_dir = data_dir / "barriers/master"
results_dir = data_dir / "barriers/networks"
results_dir.mkdir(exist_ok=True, parents=True)

df = (
    gp.read_feather(barriers_dir / "waterfalls.feather")
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
            "snap_log",
            "log",
            "lineID",
            "wbID",
        ],
        errors="ignore",
    )
    .rename(
        columns={
            "excluded": "Excluded",
            "intermittent": "Intermittent",
            "fall_type": "FallType",
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


# drop any that should be DROPPED (dropped or duplicate) from the analysis
# NOTE: excluded ones are retained but don't have networks
df = df.loc[~(df.dropped | df.duplicate)].copy()


### Classify StreamOrder
df["StreamOrderClass"] = classify_streamorder(df.StreamOrder)


for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    df[f"{col}Class"] = classify_spps(df[col])


### Get network results
# NOTE: we drop gain / total network miles here since these are not removable
print("Joining to networks for dams and small barriers")
dam_networks = get_network_results(df, network_type="dams", barrier_type="waterfalls")

dam_networks.columns = [f"{c}_dams" for c in dam_networks.columns]
barrier_networks = get_network_results(
    df, network_type="small_barriers", barrier_type="waterfalls"
)

barrier_networks.columns = [f"{c}_small_barriers" for c in barrier_networks.columns]
# copy used to defragment DataFrame (warning from pandas)
df = df.join(dam_networks).join(barrier_networks).copy()

for col in dam_networks.columns:
    df[col] = df[col].fillna(-1).astype(get_signed_dtype(dam_networks[col].dtype))

for col in barrier_networks.columns:
    df[col] = df[col].fillna(-1).astype(get_signed_dtype(barrier_networks[col].dtype))


df["HasNetwork"] = df.index.isin(dam_networks.index)

### Pack bits for categorical fields not used for filtering
# IMPORTANT: this needs to happen here, before backfilling fields with -1
pack_cols = [e["field"] for e in WF_PACK_BITS]
tmp = df[pack_cols].copy()
# recode streamorder -1 to 0 for packing
tmp.loc[tmp.StreamOrder == -1, "StreamOrder"] = 0

df["packed"] = pack_bits(tmp, WF_PACK_BITS)


df = df[["geometry"] + WF_CORE_FIELDS + ["HasNetwork", "packed"]].copy()

df.reset_index().to_feather(api_dir / "waterfalls.feather")
