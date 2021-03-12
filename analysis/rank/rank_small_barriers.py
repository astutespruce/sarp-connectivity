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
import warnings

import pygeos as pg
import geopandas as gp
import pandas as pd
from pyogrio import write_dataframe

from analysis.rank.lib.spatial_joins import add_spatial_joins
from analysis.rank.lib.tiers import calculate_tiers
from analysis.rank.lib.metrics import update_network_metrics
from api.constants import SB_API_FIELDS, SB_CORE_FIELDS, UNIT_FIELDS
from analysis.lib.util import append


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


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

# TODO: expand to full region
huc4_df = pd.read_feather(
    data_dir / "boundaries/sarp_huc4.feather", columns=["HUC2", "HUC4"]
)
# Convert to dict of sorted HUC4s per HUC2
units = huc4_df.groupby("HUC2").HUC4.unique().apply(sorted).to_dict()
huc2s = sorted(units.keys())


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
    .rename(columns={"StreamOrde": "StreamOrder", "excluded": "Excluded"})
)


# Drop any that are duplicates
# NOTE: we retain those that were dropped because these are relevant for folks to know what
# has been inventoried (e.g., those dropped because no barrier, etc)
df = df.loc[~df.duplicate].copy()

### Read in network outputs and join to master
print("Reading network outputs")
merged = None
for huc2 in huc2s:
    # if from a HUC2 that was merged with adjacent HUC2s
    merged_filename = (
        data_dir / "networks/merged" / huc2 / "small_barriers/barriers_network.feather"
    )
    if merged_filename.exists():
        network_df = pd.read_feather(merged_filename)

    else:
        network_df = pd.read_feather(
            data_dir / "networks" / huc2 / "small_barriers/barriers_network.feather"
        )

    network_df = (
        network_df.loc[network_df.kind == "small_barrier"]
        .drop(columns=["index", "segments", "kind", "barrierID"], errors="ignore")
        .rename(
            columns={
                "sinuosity": "Sinuosity",
                "natfldpln": "Landcover",
                "sizeclasses": "SizeClasses",
            }
        )
    )

    merged = append(merged, network_df)

networks = merged.reset_index(drop=True)

# fix data type issues
networks.up_nsbs = networks.up_nsbs.astype("uint32")


# All barriers that came out of network analysis have networks
networks["HasNetwork"] = True

### Join in networks and fill N/A
df = df.join(networks.set_index("id"))
df.HasNetwork = df.HasNetwork.fillna(False)


print(f"Read {len(df):,} small barriers ({df.HasNetwork.sum():,} have networks)")

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


### Update network metrics and calculate classes
df = update_network_metrics(df)


### Add spatial joins to other units
df = add_spatial_joins(df)


### Add lat / lon
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(epsg=4326)
geo["lat"] = pg.get_y(geo.geometry.values.data).astype("float32")
geo["lon"] = pg.get_x(geo.geometry.values.data).astype("float32")
df = df.join(geo[["lat", "lon"]])

### Calculate tiers for the region and by state
df = calculate_tiers(df, prefix="SE")
df = calculate_tiers(df, group_field="State", prefix="State")


### Sanity check
if df.groupby(level=0).size().max() > 1:
    raise ValueError(
        "Error - there are duplicate barriers in the results.  Check uniqueness of IDs and joins."
    )


### Output results
print("Writing to output files...")


# Full results for SARP
print("Saving full results to feather")
df.reset_index().to_feather(qa_dir / "small_barriers_network_results.feather")
write_dataframe(df.reset_index(), qa_dir / "small_barriers_network_results.gpkg")

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
df[SB_API_FIELDS].reset_index().to_feather(api_dir / "small_barriers.feather")

# Drop fields that can be calculated on frontend
keep_fields = [
    c for c in SB_API_FIELDS if not c in {"GainMiles", "TotalNetworkMiles"}
] + ["SinuosityClass", "upNetID", "downNetID"]
df = df[keep_fields].copy()

### Export data for use in tippecanoe to generate vector tiles
# Rename columns for easier use
df = df.rename(columns={"County": "CountyName", "COUNTYFIPS": "County"})

# Fill N/A values and fix dtypes
str_cols = df.dtypes.loc[df.dtypes == "object"].index
df[str_cols] = df[str_cols].fillna("")

# Fix boolean types
df.ProtectedLand = df.ProtectedLand.astype("uint8")
df["Excluded"] = df.Excluded.astype("uint8")

with_networks = df.loc[df.HasNetwork].drop(columns=["HasNetwork", "Excluded"])
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

# Drop fields we don't need and merge
keep_fields = SB_CORE_FIELDS + ["CountyName", "State", "Excluded"]
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

print(f"Done in {time() - start:.2f}")
