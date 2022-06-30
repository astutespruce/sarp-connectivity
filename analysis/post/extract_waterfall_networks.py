from pathlib import Path

import pandas as pd
import geopandas as gp

from api.constants import WF_CORE_FIELDS, WF_PACK_BITS
from analysis.lib.util import pack_bits
from analysis.rank.lib.metrics import classify_streamorder, classify_spps
from analysis.rank.lib.networks import get_network_results

data_dir = Path("data")
api_dir = data_dir / "api"
barriers_dir = data_dir / "barriers/master"
out_dir = Path("tiles")
tmp_dir = Path("/tmp")


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

# drop geometry; no longer needed
df = pd.DataFrame(df.drop(columns=["geometry"]))


### Get network results
# NOTE: we drop gain / total network miles here since these are not removable
print("Joining to networks for dams and small barriers")
dam_networks = get_network_results(
    df, network_type="dams", barrier_type="waterfalls", rank=False
)
# .drop(
#     columns=[
#         "GainMiles",
#         "GainMilesClass",
#         "PerennialGainMiles",
#         "PerennialGainMilesClass",
#         "TotalNetworkMiles",
#         "TotalPerennialNetworkMiles",
#         "NumBarriersDownstream",
#         "FlowsToOcean",
#     ],
#     errors="ignore",
# )
dam_networks.columns = [f"{c}_dams" for c in dam_networks.columns]
barrier_networks = get_network_results(
    df, network_type="small_barriers", barrier_type="waterfalls", rank=False
)
# .drop(
#     columns=[
#         "GainMiles",
#         "GainMilesClass",
#         "PerennialGainMiles",
#         "PerennialGainMilesClass",
#         "TotalNetworkMiles",
#         "TotalPerennialNetworkMiles",
#         "NumBarriersDownstream",
#         "FlowsToOcean",
#     ],
#     errors="ignore",
# )
barrier_networks.columns = [f"{c}_small_barriers" for c in barrier_networks.columns]
df = df.join(dam_networks).join(barrier_networks)

for col in dam_networks.columns:
    df[col] = df[col].fillna(-1).astype(dam_networks[col].dtype)

for col in barrier_networks.columns:
    df[col] = df[col].fillna(-1).astype(barrier_networks[col].dtype)


df["HasNetwork"] = df.index.isin(dam_networks.index)

### Pack bits for categorical fields not used for filtering
# IMPORTANT: this needs to happen here, before backfilling fields with -1
pack_cols = [e["field"] for e in WF_PACK_BITS]
tmp = df[pack_cols].copy()
# recode streamorder -1 to 0 for packing
tmp.loc[tmp.StreamOrder == -1, "StreamOrder"] = 0

df["packed"] = pack_bits(tmp, WF_PACK_BITS)


df = df[
    WF_CORE_FIELDS
    # + list(dam_networks.columns)
    # + list(barrier_networks.columns)
    + ["HasNetwork", "packed"]
].copy()

df.reset_index().to_feather(api_dir / "waterfalls.feather")
