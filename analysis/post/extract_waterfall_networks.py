from pathlib import Path

import pandas as pd
import geopandas as gp

from api.constants import WF_CORE_FIELDS
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
        }
    )
)

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
).drop(
    columns=[
        "GainMiles",
        "GainMilesClass",
        "PerennialGainMiles",
        "PerennialGainMilesClass",
        "TotalNetworkMiles",
        "TotalPerennialNetworkMiles",
        "NumBarriersDownstream",
        "FlowsToOcean",
    ],
    errors="ignore",
)
dam_networks.columns = [f"{c}_dams" for c in dam_networks.columns]
barrier_networks = get_network_results(
    df, network_type="small_barriers", barrier_type="waterfalls", rank=False
).drop(
    columns=[
        "GainMiles",
        "GainMilesClass",
        "PerennialGainMiles",
        "PerennialGainMilesClass",
        "TotalNetworkMiles",
        "TotalPerennialNetworkMiles",
        "NumBarriersDownstream",
        "FlowsToOcean",
    ],
    errors="ignore",
)
barrier_networks.columns = [f"{c}_small_barriers" for c in barrier_networks.columns]
df = df.join(dam_networks).join(barrier_networks)

for col in dam_networks.columns:
    df[col] = df[col].fillna(-1).astype(dam_networks[col].dtype)

for col in barrier_networks.columns:
    df[col] = df[col].fillna(-1).astype(barrier_networks[col].dtype)


df["HasNetwork"] = df.index.isin(dam_networks.index)

# set intermittent to -1 where waterfalls were not snapped to networks
df.Intermittent = df.Intermittent.astype("int8")
df.loc[~df.snapped, "Intermittent"] = -1


df = df[
    WF_CORE_FIELDS
    + list(dam_networks.columns)
    + list(barrier_networks.columns)
    + ["HasNetwork"]
].copy()

df.reset_index().to_feather(api_dir / "waterfalls.feather")

