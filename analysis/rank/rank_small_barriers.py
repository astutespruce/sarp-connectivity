import csv
import os
from pathlib import Path
from time import time
import warnings

import numpy as np
import pandas as pd
import geopandas as gp
import pygeos as pg

from analysis.constants import STATES
from analysis.rank.lib.networks import get_network_results
from analysis.rank.lib.metrics import classify_streamorder, classify_spps
from analysis.rank.lib.spatial_joins import add_spatial_joins
from api.constants import SB_API_FIELDS, SB_CORE_FIELDS, UNIT_FIELDS


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
tile_dir = data_dir / "tiles"

if not os.path.exists(api_dir):
    os.makedirs(api_dir)

if not os.path.exists(tile_dir):
    os.makedirs(tile_dir)


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
            "ProtectedLand",
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
        }
    )
)

# Drop any that are duplicates
# NOTE: we retain those that were dropped because these are relevant for folks to know what
# has been inventoried (e.g., those dropped because no barrier, etc)
# but do drop any that have no state or HUC2
df = df.loc[(~df.duplicate) & (df.State)].copy()


### Classify StreamOrder
df.StreamOrder = df.StreamOrder.fillna(-1).astype("int8")
df["StreamOrderClass"] = classify_streamorder(df.StreamOrder)


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

### Add lat / lon
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(epsg=4326)
geo["lat"] = pg.get_y(geo.geometry.values.data).astype("float32")
geo["lon"] = pg.get_x(geo.geometry.values.data).astype("float32")
df = df.join(geo[["lat", "lon"]])


### Get network results
networks = {
    "all": get_network_results(df, "small_barriers", "all"),
    # FlowsToOcean and NumBarriersDownstream are less relevant for perennial networks
    "perennial": get_network_results(df, "small_barriers", "perennial").drop(
        columns=["FlowsToOcean", "NumBarriersDownstream"], errors="ignore"
    ),
}

### Write out data for API
for network_scenario in ["all", "perennial"]:
    network = networks[network_scenario]
    tmp = df.join(network)

    tmp["HasNetwork"] = tmp.index.isin(network.index)
    tmp["Ranked"] = tmp.HasNetwork & (~tmp.unranked)

    # intermittent is not applicable if it doesn't have a network
    tmp["Intermittent"] = tmp["Intermittent"].astype("int8")
    tmp.loc[~tmp.HasNetwork, "Intermittent"] = -1

    # fill columns and set proper type
    for col in network.columns:
        tmp[col] = tmp[col].fillna(-1).astype(network[col].dtype)

    ### Sanity check
    if tmp.groupby(level=0).size().max() > 1:
        raise ValueError(
            f"Error - there are duplicate barriers in the results for small_barriers in {network_scenario} .  Check uniqueness of IDs and joins."
        )

    print(f"Writing to output files for {network_scenario}...")

    # Full results for SARP QA/QC
    tmp.reset_index().to_feather(
        barriers_dir.parent
        / "qa"
        / f"small_barriers_{network_scenario}__network_results.feather"
    )

    # save for API
    tmp[np.intersect1d(SB_API_FIELDS, tmp.columns)].reset_index().to_feather(
        api_dir / f"small_barriers_{network_scenario}.feather"
    )


# True if the barrier was snapped to a network and has network results in the
# all networks scenario
df["HasNetwork"] = df.index.isin(networks["all"].index)
df["Ranked"] = df.HasNetwork & (~df.unranked)

# intermittent is not applicable if it doesn't have a network
df["Intermittent"] = df["Intermittent"].astype("int8")
df.loc[~df.HasNetwork, "Intermittent"] = -1


### Export data for generating tiles
# Drop fields that can be calculated on frontend
keep_fields = [
    c for c in SB_API_FIELDS if not c in {"GainMiles", "TotalNetworkMiles", "Sinuosity"}
]

# Note: this drops geometry, which is no longer needed
df = pd.DataFrame(df[np.intersect1d(df.columns, keep_fields)]).rename(
    columns={"County": "CountyName", "COUNTYFIPS": "County"}
)

# join in both networks, suffixing perennial networks
all_network_cols = np.intersect1d(networks["all"].columns, keep_fields)
perennial_network_cols = np.intersect1d(networks["perennial"].columns, keep_fields)
df = df.join(networks["all"][all_network_cols]).join(
    networks["perennial"][perennial_network_cols], rsuffix="_perennial",
)

# fill missing data and set dtypes
for col in all_network_cols:
    df[col] = df[col].fillna(-1).astype(networks["all"][col].dtype)

for col in perennial_network_cols:
    df[f"{col}_perennial"] = (
        df[f"{col}_perennial"].fillna(-1).astype(networks["perennial"][col].dtype)
    )

str_cols = df.dtypes.loc[df.dtypes == "object"].index
df[str_cols] = df[str_cols].fillna("")

# Update boolean fields so that they are output to CSV correctly
for col in ["ProtectedLand", "Ranked", "Excluded"]:
    df[col] = df[col].astype("uint8")


# Split into separate datasets with and without networks; without networks have fewer cols
with_networks = df.loc[df.HasNetwork].drop(columns=["HasNetwork", "Excluded"])
without_networks = df.loc[~df.HasNetwork].drop(columns=["HasNetwork"])

# lowercase all fields except unit fields
with_networks.rename(
    columns={
        k: k.lower()
        for k in df.columns
        if k not in UNIT_FIELDS + ["Subbasin", "Subwatershed"]
    }
).to_csv(
    tile_dir / "small_barriers_with_networks.csv",
    index_label="id",
    quoting=csv.QUOTE_NONNUMERIC,
)


### Combine barriers that don't have networks with road / stream crossings
print("Reading road / stream crossings")
road_crossings = gp.read_feather(barriers_dir / "road_crossings.feather").rename(
    columns={"County": "CountyName"}
)

# bring in Species info
road_crossings = road_crossings.join(spp_df, on="HUC12")
for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    road_crossings[col] = road_crossings[col].fillna(0).astype("uint8")

# Standardize other fields before merge
road_crossings["Source"] = "USGS"
road_crossings["Excluded"] = 0

keep_fields = without_networks.columns.intersection(
    SB_CORE_FIELDS + ["CountyName", "State", "Excluded"]
)
road_crossing_fields = road_crossings.columns.intersection(
    SB_CORE_FIELDS + ["CountyName", "State", "Excluded"]
)

combined = (
    without_networks[keep_fields]
    .append(road_crossings[road_crossing_fields], ignore_index=True, sort=False)
    .rename(columns={k: k.lower() for k in df.columns if k not in UNIT_FIELDS})
    .reset_index(drop=True)
)

# create a new consolidated ID
combined["id"] = combined.index.values.astype("uint32")

# Fill in N/A values
# cols = combined.dtypes.loc[combined.dtypes == "object"].index
cols = [
    "name",
    "sarpid",
    "localid",
    "crossingcode",
    "source",
    "stream",
    "road",
    "roadtype",
    "crossingtype",
    "condition",
    "potentialproject",
    "basin",
    "countyname",
    "State",
]
combined[cols] = combined[cols].fillna("").astype(str)

combined.protectedland = combined.protectedland.fillna(0).astype("uint8")
combined.ownertype = combined.ownertype.fillna(-1).astype("int8")
combined.severityclass = combined.severityclass.fillna(0).astype("uint8")


print("Writing combined file")
combined.to_csv(
    tile_dir / "small_barriers_background.csv",
    index=False,
    quoting=csv.QUOTE_NONNUMERIC,
)

print(f"Done in {time() - start:.2f}")
