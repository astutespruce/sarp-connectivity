"""
Preprocess small barriers into data needed by API and tippecanoe for creating vector tiles.

This is run AFTER `preprocess_road_crossings.py`.

Inputs:
* Small barriers inventory from SARP, processed through the network analysis
* `data/barriers/master/road_crossings.feather` created using `preprocess_road_crossings.py`

Outputs:
* `data/api/small_barriers.feather`: processed small barriers data for use by the API
* `data/tiles/barriers_with_networks.csv`: small barriers with networks for creating vector tiles in tippecanoe
* `data/tiles/barriers_background.csv`: small barriers without networks and road crossings for creating vector tiles in tippecanoe

"""

import os
from pathlib import Path
from time import time
import csv
import sys
import geopandas as gp
import pandas as pd
from geofeather import from_geofeather, to_shp, to_geofeather
from nhdnet.io import deserialize_dfs, deserialize_df, serialize_df
from nhdnet.geometry.points import add_lat_lon


from analysis.constants import REGION_GROUPS
from analysis.network.lib.barriers import DAMS_ID
from analysis.rank.lib.spatial_joins import add_spatial_joins
from analysis.rank.lib.tiers import calculate_tiers
from analysis.rank.lib.metrics import update_network_metrics
from api.constants import SB_API_FIELDS, SB_CORE_FIELDS, UNIT_FIELDS

start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
qa_dir = data_dir / "barriers/qa"
api_dir = data_dir / "api"
tile_dir = data_dir / "tiles"

if not os.path.exists(api_dir):
    os.makedirs(api_dir)

if not os.path.exists(tile_dir):
    os.makedirs(tile_dir)


### Read in master
print("Reading master...")
df = (
    from_geofeather(barriers_dir / "small_barriers.feather")
    .set_index("id")
    .drop(
        columns=[
            "level_0",
            "index",
            "dup_group",
            "dup_count",
            "snap_dist",
            "snapped",
            "ProtectedLand",
        ],
        errors="ignore",
    )
)

# drop any that should be DROPPED (dropped or duplicate) from the analysis
# NOTE: excluded ones are retained but don't have networks
df = df.loc[~(df.dropped | df.duplicate)].copy()


# TODO: remove on next run of prep_small_barriers.py
df.loc[df.Stream.str.contains("\r\n", ""), "Stream"] = "Unnamed"
df.Road = df.Road.str.replace("\r\n", "")

df["Name"] = ""

df.loc[
    (~df.Stream.isin(["Unknown", "Unnamed", ""]))
    & (~df.Road.isin(["Unknown", "Unnamed", ""])),
    "Name",
] = (df.Stream + " / " + df.Road)

df.Name = df.Name.fillna("")


### Read in network outputs and join to master
print("Reading network outputs")
networks = (
    deserialize_dfs(
        [
            data_dir / "networks" / region / "small_barriers/barriers_network.feather"
            for region in REGION_GROUPS
        ],
        src=[region for region in REGION_GROUPS],
    )
    .drop(columns=["index", "segments"], errors="ignore")
    .rename(
        columns={
            "sinuosity": "Sinuosity",
            "natfldpln": "Landcover",
            "sizeclasses": "SizeClasses",
        }
    )
)

# Select out only dams because we are joining on "id"
# which may have duplicates across barrier types
networks = networks.loc[networks.kind == "small_barrier"].copy()

# All barriers that came out of network analysis have networks
networks["HasNetwork"] = True

### Join in networks and fill N/A
df = df.join(networks.set_index("id"))
df.HasNetwork = df.HasNetwork.fillna(False)


print(
    "Read {:,} small barriers ({:,} have networks)".format(
        len(df), len(df.loc[df.HasNetwork])
    )
)

### Join in T&E Spp stats
spp_df = deserialize_df(data_dir / "species/derived/spp_HUC12.feather").set_index(
    "HUC12"
)
df = df.join(spp_df.NumTEspp.rename("TESpp"), on="HUC12")
df.TESpp = df.TESpp.fillna(0).astype("uint8")


### Update network metrics and calculate classes
df = update_network_metrics(df)


### Add spatial joins to other units
df = add_spatial_joins(df)


### Add lat / lon
print("Adding lat / lon fields")
df = add_lat_lon(df)

### Calculate tiers for the region and by state
df = calculate_tiers(df, prefix="SE")
df = calculate_tiers(df, group_field="State", prefix="State")


### Output results
print("Writing to output files...")


# Full results for SARP
print("Saving full results to feather")
to_geofeather(df.reset_index(), qa_dir / "small_barriers_network_results.feather")

# drop geometry, not needed from here on out
df = df.drop(columns=["geometry"])

print("Saving full results to CSV")
df.to_csv(
    qa_dir / "small_barriers_network_results.csv",
    index_label="id",
    quoting=csv.QUOTE_NONNUMERIC,
)


# Drop any fields we don't need for API or tippecanoe
# save for API
serialize_df(df[SB_API_FIELDS].reset_index(), api_dir / "small_barriers.feather")

# Drop fields that can be calculated on frontend
keep_fields = [
    c for c in SB_API_FIELDS if not c in {"GainMiles", "TotalNetworkMiles"}
] + ["SinuosityClass"]
df = df[keep_fields].copy()

### Export data for use in tippecanoe to generate vector tiles
# Rename columns for easier use
df = df.rename(columns={"County": "CountyName", "COUNTYFIPS": "County"})

# Fill N/A values and fix dtypes
str_cols = df.dtypes.loc[df.dtypes == "object"].index
df[str_cols] = df[str_cols].fillna("")

# Fix boolean types
df.ProtectedLand = df.ProtectedLand.astype("uint8")

with_networks = df.loc[df.HasNetwork].drop(columns=["HasNetwork"])
without_networks = df.loc[~df.HasNetwork].drop(columns=["HasNetwork"])

with_networks.rename(
    columns={k: k.lower() for k in df.columns if k not in UNIT_FIELDS}
).to_csv(
    tile_dir / "barriers_with_networks.csv",
    index_label="id",
    quoting=csv.QUOTE_NONNUMERIC,
)


### Combine barriers that don't have networks with road / stream crossings
print("Reading road / stream crossings")
road_crossings = from_geofeather(barriers_dir / "road_crossings.feather").rename(
    columns={"County": "CountyName"}
)


# bring in TESpp
road_crossings = road_crossings.join(spp_df.NumTEspp.rename("TESpp"), on="HUC12")
road_crossings.TESpp = road_crossings.TESpp.fillna(0).astype("uint8")

# Standardize other fields before merge
road_crossings["Source"] = "USGS"

# Drop fields we don't need and merge
keep_fields = SB_CORE_FIELDS + ["CountyName", "State"]
road_crossings = road_crossings[road_crossings.columns.intersection(keep_fields)]
combined = (
    without_networks[keep_fields]
    .append(road_crossings, ignore_index=True, sort=False)
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
    tile_dir / "barriers_background.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
)

print("Done in {:.2f}".format(time() - start))
