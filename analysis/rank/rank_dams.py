"""
Preprocess dams into data needed by API and tippecanoe for creating vector tiles.

Input: 
* Dam inventory from SARP, including all network metrics and summary unit IDs (HUC12, ECO3, ECO4, State, County, etc).

Outputs:
* `dams.feather`: processed dam data for use by the API
* `dams_with_networks.csv`: Dams with networks for creating vector tiles in tippecanoe
* `dams_without_networks.csv`: Dams without networks for creating vector tiles in tippecanoe

"""
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
from analysis.rank.lib import (
    add_spatial_joins,
    update_network_metrics,
    calculate_tiers,
    to_tippecanoe,
)

start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
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
df = calculate_tiers(df)

### Export data for API
# TODO: double check against fields expected by API

# TODO: drop any fields not used by API

### Output results
print("Writing to output files...")

# Full results for SARP
print("Saving full results to feather")
to_geofeather(df.reset_index(), out_dir / "dams_full.feather")

# drop geometry, not needed from here on out
df = df.drop(columns=["geometry"])

print("Saving full results to CSV")
df.to_csv(out_dir / "dams.csv", index_label="id", quoting=csv.QUOTE_NONNUMERIC)


# Drop associated raw scores, they are not currently displayed on frontend.
df = df.drop(columns=[c for c in df.columns if c.endswith("_score")])

# save for API
# Fix index not being named correctly
serialize_df(df.reset_index(), out_dir / "dams.feather")

### Export data for use in tippecanoe to generate vector tiles
to_tippecanoe(df, "dams")


print("Done in {:.2f}".format(time() - start))
