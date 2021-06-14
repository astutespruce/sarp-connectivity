"""
Preprocess dams into data needed by API and tippecanoe for creating vector tiles.

Input:
* Dam inventory from SARP, including all network metrics and summary unit IDs (HUC12, ECO3, ECO4, State, County, etc).

Outputs:
* `data/api/dams.feather`: processed dam data for use by the API
* `data/api/removed_dams.feather`: dams that were removed for conservation
* `data/tiles/dams_with_networks.csv`: Dams with networks for creating vector tiles in tippecanoe
* `data/tiles/dams_without_networks.csv`: Dams without networks for creating vector tiles in tippecanoe
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
from api.constants import DAM_API_FIELDS, UNIT_FIELDS, DAM_CORE_FIELDS
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


huc4_df = pd.read_feather(
    # data_dir / "boundaries/sarp_huc4.feather",
    data_dir / "boundaries/huc4.feather",
    columns=["HUC2", "HUC4"],
)
# Convert to dict of sorted HUC4s per HUC2
units = huc4_df.groupby("HUC2").HUC4.unique().apply(sorted).to_dict()
huc2s = sorted(units.keys())

# manually subset keys from above for processing
huc2s = [
    "02",
    # "03",
    # "05",
    # "06",
    # "07",
    # "08",
    # "09",
    # "10",
    # "11",
    # "12",
    # "13",
    "14",
    # "15",
    # "16",
    # "17",
    # "21",
]


### Read in master
print("Reading master...")
df = (
    gp.read_feather(barriers_dir / "dams.feather")
    .set_index("id")
    .drop(
        columns=[
            "level_0",
            "index",
            "dup_group",
            "dup_count",
            "dup_sort",
            "dup_log",
            "snap_dist",
            "snap_tolerance",
            "snap_ref_id",
            "snap_log",
            "snap_group",
            "snapped",
            "ProtectedLand",
            "NHDPlusID",
            "SourceState",
            "lineID",
            "wbID",
            "waterbody",
            "src",
            "kind",
            "log",
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


### Save dams that were removed, for use in API (they are otherwise dropped below)
removed = df.loc[
    (df.Recon == 7) | (df.ManualReview == 8),
    [
        "geometry",
        "Name",
        "SARPID",
        "NIDID",
        "Source",
        "SourceDBID",
        "River",
        "Year",
        "Height",
        "Construction",
        "Purpose",
        "State",
        "County",
        "HUC8",
        "HUC12",
        "duplicate",
    ],
].to_crs(epsg=4326)
removed["lat"] = pg.get_y(removed.geometry.values.data).astype("float32")
removed["lon"] = pg.get_x(removed.geometry.values.data).astype("float32")
removed = removed.drop(columns=["geometry"])
removed.to_feather(api_dir / "removed_dams.feather")


### drop any that should be DROPPED (dropped or duplicate) from the analysis
# NOTE: excluded ones are retained but don't have networks; ones on loops are retained but also don't have networks
df = df.loc[~(df.dropped | df.duplicate)].copy()

### Read in network outputs and join to master

print("Reading network outputs")
merged = None
for huc2 in huc2s:
    # if from a HUC2 that was merged with adjacent HUC2s
    merged_filename = (
        data_dir / "networks/merged" / huc2 / "dams/barriers_network.feather"
    )
    if merged_filename.exists():
        network_df = pd.read_feather(merged_filename)

    else:
        network_df = pd.read_feather(
            data_dir / "networks" / huc2 / "dams/barriers_network.feather"
        )

    network_df = (
        network_df.loc[network_df.kind == "dam"]
        .drop(columns=["index", "segments", "kind", "barrierID"], errors="ignore")
        .rename(
            columns={
                "sinuosity": "Sinuosity",
                "natfldpln": "Landcover",
                "sizeclasses": "SizeClasses",
                "flows_to_ocean": "FlowsToOcean",
                "num_downstream": "NumBarriersDownstream",
            }
        )
    )

    merged = append(merged, network_df)

networks = merged.reset_index(drop=True)

# All barriers that came out of network analysis have networks
networks["HasNetwork"] = True

### Join in networks and fill N/A
df = df.join(networks.set_index("id"))
df.HasNetwork = df.HasNetwork.fillna(False)
df.upNetID = df.upNetID.fillna(-1).astype("int")
df.downNetID = df.downNetID.fillna(-1).astype("int")
df.Intermittent = df.Intermittent.fillna(-1).astype("int8")
df.loc[~df.HasNetwork, "Intermittent"] = -1

df.FlowsToOcean = df.FlowsToOcean.fillna(-1).astype("int8")
df.NumBarriersDownstream = df.NumBarriersDownstream.fillna(-1).astype("int")

df["Ranked"] = df.HasNetwork & (~df.unranked)
df = df.drop(columns=["unranked"])

print(f"Read {len(df):,} dams ({df.HasNetwork.sum():,} have networks)")

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
df.reset_index().to_feather(qa_dir / "dams_network_results.feather")
write_dataframe(df.reset_index(), qa_dir / "dams_network_results.gpkg")

# drop geometry, not needed from here on out
df = df.drop(columns=["geometry"])

# Debug
# print("Saving full results to CSV")
# df.to_csv(
#     qa_dir / "dams_network_results.csv", index_label="id", quoting=csv.QUOTE_NONNUMERIC
# )

# save for API
df[DAM_API_FIELDS].reset_index().to_feather(api_dir / "dams.feather")

# Drop fields that can be calculated on frontend
keep_fields = [
    c
    for c in DAM_API_FIELDS
    if not c in {"GainMiles", "TotalNetworkMiles", "Sinuosity"}
]
df = df[keep_fields].copy()


# Rename columns for easier use
df = df.rename(columns={"County": "CountyName", "COUNTYFIPS": "County"})


### Export data for use in tippecanoe to generate vector tiles

# Fill N/A values and fix dtypes
str_cols = df.dtypes.loc[df.dtypes == "object"].index
df[str_cols] = df[str_cols].fillna("")

# Update boolean fields so that they are output to CSV correctly
df.ProtectedLand = df.ProtectedLand.astype("uint8")
df["Excluded"] = df.Excluded.astype("uint8")

with_networks = df.loc[df.HasNetwork].drop(columns=["HasNetwork", "Excluded"])
without_networks = df.loc[~df.HasNetwork].drop(columns=["HasNetwork"])

with_networks.rename(
    columns={
        k: k.lower()
        for k in df.columns
        if k not in UNIT_FIELDS + ["Subbasin", "Subwatershed"]
    }
).to_csv(
    tile_dir / "dams_with_networks.csv", index_label="id", quoting=csv.QUOTE_NONNUMERIC
)

# Drop metrics, tiers, and units used only for filtering
keep_fields = DAM_CORE_FIELDS + ["CountyName", "State", "Excluded"]

without_networks[keep_fields].rename(
    columns={
        k: k.lower()
        for k in df.columns
        if k not in UNIT_FIELDS + ["Subbasin", "Subwatershed"]
    }
).to_csv(
    tile_dir / "dams_without_networks.csv",
    index_label="id",
    quoting=csv.QUOTE_NONNUMERIC,
)


print(f"Done in {time() - start:.2f}")
