"""
Process waterfalls into data needed by tippecanoe for creating vector tiles.

For these outputs, waterfalls do not need to be processed through the network analysis.
There is code below, that if uncommented, can be used to integrate the network results.

Inputs:
* waterfalls

Outputs:
* `data/tiles/waterfalls.csv`: waterfalls for creating vector tiles in tippecanoe

"""

import os
from pathlib import Path
from time import time
import csv
import sys
import geopandas as gp
import pandas as pd
from geofeather import from_geofeather, to_geofeather
from nhdnet.io import deserialize_dfs, deserialize_df, serialize_df
from nhdnet.geometry.points import add_lat_lon


from analysis.constants import REGION_GROUPS
from analysis.network.lib.barriers import DAMS_ID
from analysis.rank.lib.metrics import update_network_metrics
from api.constants import WF_CORE_FIELDS

start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
qa_dir = data_dir / "barriers/qa"
tile_dir = data_dir / "tiles"

if not os.path.exists(tile_dir):
    os.makedirs(tile_dir)


### Read in master
print("Reading master...")
df = (
    from_geofeather(barriers_dir / "waterfalls.feather")
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
            "snapped",
            "log",
            "lineID",
            "wbID",
        ],
        errors="ignore",
    )
    .rename(
        columns={
            "streamorder": "StreamOrder",
            "name": "Name",
            "watercours": "Stream",
            "gnis_name_": "GNIS_Name",
        }
    )
)

### Fix data type issues
# TODO: move to prep script
df.Name = df.Name.fillna("").str.strip()
df.LocalID = df.LocalID.fillna("").str.strip()
df.Stream = df.Stream.fillna("").str.strip()
df.GNIS_Name = df.GNIS_Name.fillna("").str.strip()
ix = (df.Stream == "") & (df.GNIS_Name != "")
df.loc[ix, "Stream"] = df.loc[ix].GNIS_Name

# drop any that should be DROPPED (dropped or duplicate) from the analysis
# NOTE: excluded ones are retained but don't have networks
df = df.loc[~(df.dropped | df.duplicate)].copy()

# ### Read in network outputs and join to master
# print("Reading network outputs")
# networks = (
#     deserialize_dfs(
#         [
#             data_dir / "networks" / region / "natural/barriers_network.feather"
#             for region in REGION_GROUPS
#         ],
#         src=[region for region in REGION_GROUPS],
#     )
#     .drop(columns=["index", "segments"], errors="ignore")
#     .rename(
#         columns={
#             "sinuosity": "Sinuosity",
#             "natfldpln": "Landcover",
#             "sizeclasses": "SizeClasses",
#         }
#     )
# )

# # Select out only dams because we are joining on "id"
# # which may have duplicates across barrier types
# networks = networks.loc[networks.kind == "waterfall"].copy()

# # All barriers that came out of network analysis have networks
# networks["HasNetwork"] = True

# ### Join in networks and fill N/A
# df = df.join(networks.set_index("id"))
# df.HasNetwork = df.HasNetwork.fillna(False)


# print(
#     "Read {:,} waterfalls ({:,} have networks)".format(
#         len(df), len(df.loc[df.HasNetwork])
#     )
# )

# ### Update network metrics and calculate classes
# df = update_network_metrics(df)

# ### Add spatial joins to other units
# # df = add_spatial_joins(df)


### Add lat / lon
print("Adding lat / lon fields")
df = add_lat_lon(df)

# ### Update boolean fields
# df["excluded"] = df.excluded.astype("uint8")


### Output results
print("Writing to output files...")

# # Full results for SARP
# print("Saving full results to feather")
# to_geofeather(df.reset_index(), qa_dir / "waterfalls_network_results.feather")

# drop geometry, not needed from here on out
df = df.drop(columns=["geometry"])

# print("Saving full results to CSV")
# df.to_csv(
#     qa_dir / "waterfalls_network_results.csv",
#     index_label="id",
#     quoting=csv.QUOTE_NONNUMERIC,
# )

# Drop fields that can be calculated on frontend
# keep_fields = [
#     c for c in WF_CORE_FIELDS if not c in {"GainMiles", "TotalNetworkMiles"}
# ] + ["SinuosityClass", "upNetID", "downNetID"]

keep_fields = WF_CORE_FIELDS
df = df[keep_fields].copy()

### Export data for use in tippecanoe to generate vector tiles
# Rename columns for easier use
# df = df.rename(columns={"County": "CountyName", "COUNTYFIPS": "County"})

# Fill N/A values and fix dtypes
str_cols = df.dtypes.loc[df.dtypes == "object"].index
df[str_cols] = df[str_cols].fillna("")

# df.rename(columns={k: k.lower() for k in df.columns if k not in UNIT_FIELDS}).to_csv(
#     tile_dir / "waterfalls.csv", index_label="id", quoting=csv.QUOTE_NONNUMERIC,
# )

df.rename(columns={k: k.lower() for k in df.columns}).to_csv(
    tile_dir / "waterfalls.csv", index_label="id", quoting=csv.QUOTE_NONNUMERIC,
)


print("Done in {:.2f}".format(time() - start))
