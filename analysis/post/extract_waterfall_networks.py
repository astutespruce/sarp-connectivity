import csv
from pathlib import Path
from time import time

import pandas as pd
import geopandas as gp
import pygeos as pg

from api.constants import (
    WF_CORE_FIELDS,
    UNIT_FIELDS,
)
from analysis.constants import GEO_CRS
from analysis.rank.lib.metrics import classify_streamorder, classify_spps
from analysis.rank.lib.networks import get_network_results
from analysis.rank.lib.spatial_joins import add_spatial_joins

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
            "StreamOrde": "StreamOrder",
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
df.StreamOrder = df.StreamOrder.fillna(-1).astype("int8")
df["StreamOrderClass"] = classify_streamorder(df.StreamOrder)


df.FallType = df.FallType.fillna("")

### Join in T&E Spp stats
spp_df = (
    pd.read_feather(
        data_dir / "species/derived/spp_HUC12.feather",
        columns=["HUC12", "federal", "sgcn", "regional"],
    )
    .rename(
        columns={
            "federal": "TESpp",
            "sgcn": "StateSGCNSpp",
            "regional": "RegionalSGCNSpp",
        }
    )
    .set_index("HUC12")
)
df = df.join(spp_df, on="HUC12")
for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    df[col] = df[col].fillna(0).astype("uint8")
    df[f"{col}Class"] = classify_spps(df[col])


### Add spatial joins to other things, like priority watersheds
df = add_spatial_joins(df)


### Add lat / lon and drop geometry
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(GEO_CRS)
geo["lat"] = pg.get_y(geo.geometry.values.data).astype("float32")
geo["lon"] = pg.get_x(geo.geometry.values.data).astype("float32")
df = pd.DataFrame(df.join(geo[["lat", "lon"]]).drop(columns=["geometry"]))


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
    ],
    errors="ignore",
)
barrier_networks.columns = [f"{c}_barriers" for c in barrier_networks.columns]
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

