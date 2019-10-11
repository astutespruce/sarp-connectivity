"""
Preprocess dams into data needed by API and tippecanoe for creating vector tiles.

Input: 
* Dam inventory from SARP, including all network metrics and summary unit IDs (HUC12, ECO3, ECO4, State, County, etc).

Outputs:
* `data/api/dams.feather`: processed dam data for use by the API
* `data/tiles/dams_with_networks.csv`: Dams with networks for creating vector tiles in tippecanoe
* `data/tiles/dams_without_networks.csv`: Dams without networks for creating vector tiles in tippecanoe

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
from analysis.rank.lib import add_spatial_joins, update_network_metrics, calculate_tiers
from api.constants import DAM_API_FIELDS, UNIT_FIELDS, DAM_CORE_FIELDS

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

# split this into tile dir vs api
out_dir = data_dir / "derived"


### Read in master
print("Reading master...")
df = (
    from_geofeather(barriers_dir / "dams.feather")
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
    .rename(
        columns={
            "SARPUniqueID": "SARPID"  # TODO: remove on next full run of download & analysis
        }
    )
)

# drop any that should be DROPPED (dropped or duplicate) from the analysis
# NOTE: excluded ones are retained but don't have networks
df = df.loc[~(df.dropped | df.duplicate)].copy()

### Read in network outputs and join to master
print("Reading network outputs")
networks = (
    deserialize_dfs(
        [
            data_dir / "networks" / region / "dams/barriers_network.feather"
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
networks = networks.loc[networks.kind == "dam"].copy()

# All barriers that came out of network analysis have networks
networks["HasNetwork"] = True

### Join in networks and fill N/A
df = df.join(networks.set_index("id"))
df.HasNetwork = df.HasNetwork.fillna(False)


print("Read {:,} dams ({:,} have networks)".format(len(df), len(df.loc[df.HasNetwork])))

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
to_geofeather(df.reset_index(), qa_dir / "dams_network_results.feather")

# drop geometry, not needed from here on out
df = df.drop(columns=["geometry"])

print("Saving full results to CSV")
df.to_csv(
    qa_dir / "dams_network_results.csv", index_label="id", quoting=csv.QUOTE_NONNUMERIC
)


# Drop any fields we don't need for API or tippecanoe
# TODO: sort out COUNTYFIPS vs COUNTY, it is confusing
df = df[DAM_API_FIELDS].copy()


# save for API
serialize_df(df.reset_index(), api_dir / "dams.feather")


# Rename columns for easier use
df = df.rename(
    columns={
        "County": "CountyName",
        "COUNTYFIPS": "County",
        # "SinuosityClass": "Sinuosity",  # Decoded to a label on frontend
    }
)


### Export data for use in tippecanoe to generate vector tiles

# create duplicate columns for those dropped by tippecanoe
# tippecanoe will use these ones and leave lat / lon
# so that we can use them for display in the frontend
# TODO: can this be replaced with the actual geometry available to mapbox GL?
df["latitude"] = df.lat
df["longitude"] = df.lon


with_networks = df.loc[df.HasNetwork].drop(columns=["HasNetwork"])
without_networks = df.loc[~df.HasNetwork].drop(columns=["HasNetwork"])


with_networks.rename(
    columns={k: k.lower() for k in df.columns if k not in UNIT_FIELDS}
).to_csv(
    tile_dir / "dams_with_networks.csv", index_label="id", quoting=csv.QUOTE_NONNUMERIC
)

# Drop metrics, tiers, and units used only for filtering
keep_fields = DAM_CORE_FIELDS + ["CountyName", "State", "latitude", "longitude"]


without_networks[keep_fields].rename(
    columns={k: k.lower() for k in df.columns if k not in UNIT_FIELDS}
).to_csv(
    tile_dir / "dams_without_networks.csv",
    index_label="id",
    quoting=csv.QUOTE_NONNUMERIC,
)


print("Done in {:.2f}".format(time() - start))
