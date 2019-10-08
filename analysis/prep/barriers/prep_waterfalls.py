"""
Extract waterfalls from original data source, process for use in network analysis, and convert to feather format.
1. Remove records with bad coordinates (one waterfall was represented in wrong projection)
2. Cleanup data values (as needed) and add tracking fields
3. Snap to networks by HUC2

This creates 2 files:
`barriers/master/waterfalls.feather` - master waterfalls dataset, including coordinates updated from snapping
`barriers/snapped/waterfalls.feather` - snapped waterfalls dataset for network analysis

"""

from pathlib import Path
import pandas as pd
from time import time
from geofeather import from_geofeather, to_geofeather
import geopandas as gp
import numpy as np

from nhdnet.io import deserialize_df, deserialize_sindex, to_shp

# from nhdnet.geometry.lines import snap_to_line
from nhdnet.geometry.points import mark_duplicates, add_lat_lon

from analysis.constants import REGION_GROUPS, REGIONS, CRS, DUPLICATE_TOLERANCE

from analysis.prep.barriers.lib.snap import snap_by_region, update_from_snapped

# Snap waterfalls by 100 meters
SNAP_TOLERANCE = 100


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
master_dir = barriers_dir / "master"
snapped_dir = barriers_dir / "snapped"
qa_dir = barriers_dir / "qa"
gdb_filename = "Waterfalls2019.gdb"


start = time()

print("Reading waterfalls")

df = gp.read_file(src_dir / gdb_filename)

### Drop records with bad coordinates
# must be done before projecting coordinates
print(
    "Dropping {} waterfalls with bad coordinates".format(
        len(df.loc[df.geometry.y > 90])
    )
)
df = df.loc[df.geometry.y.abs() <= 90]

### Reproject to CONUS Albers
df = df.to_crs(CRS)


### Add IDs for internal use
# internal ID
df["id"] = df.index.astype("uint32")

### Add tracking fields
# dropped: records that should not be included in any later analysis
df["dropped"] = False

# excluded: records that should be retained in dataset but not used in analysis
# NOTE: no waterfalls are currently excluded from analysis
df["excluded"] = False


### Cleanup data
df.Source = df.Source.str.strip()
amy_idx = df.Source == "Amy Cottrell, Auburn"
df.loc[amy_idx, "Source"] = "Amy Cotrell, Auburn University"

### Add persistant sourceID based on original IDs
df["sourceID"] = df.LocalID
usgs_idx = ~df.fall_id.isnull()
df.loc[usgs_idx, "sourceID"] = df.loc[usgs_idx].fall_id.astype("int").astype("str")


print("Reading HUC2 boundaries and joining to waterfalls")
huc12 = from_geofeather(boundaries_dir / "HUC12.feather")
df.sindex
huc12.sindex
df = gp.sjoin(df, huc12, how="left").drop(columns=["index_right"])
# Calculate HUC codes for other levels from HUC12
df["HUC2"] = df["HUC12"].str.slice(0, 2)  # region
df["HUC6"] = df["HUC12"].str.slice(0, 6)  # basin
df["HUC8"] = df["HUC12"].str.slice(0, 8)  # subbasin

print("Joining to counties")
counties = from_geofeather(boundaries_dir / "counties.feather")[
    ["geometry", "County", "COUNTYFIPS", "STATEFIPS"]
]
counties.sindex
df.sindex
df = gp.sjoin(df, counties, how="left").drop(columns=["index_right"])

# Join in state name based on STATEFIPS from county
states = deserialize_df(boundaries_dir / "states.feather")[
    ["STATEFIPS", "State"]
].set_index("STATEFIPS")
df = df.join(states, on="STATEFIPS")


# TODO: migrate to post

# print("Joining to ecoregions")
# # Only need to join in ECO4 dataset since it has both ECO3 and ECO4 codes
# eco4 = from_geofeather(boundaries_dir / "eco4.feather")[["geometry", "ECO3", "ECO4"]]
# eco4.sindex
# df.sindex
# df = gp.sjoin(df, eco4, how="left").drop(columns=["index_right"])

# Drop any that didn't intersect HUCs or states
drop_idx = df.HUC12.isnull() | df.STATEFIPS.isnull()
print("{} waterfalls are outside HUC12 / states".format(len(df.loc[drop_idx])))
df.loc[drop_idx, "dropped"] = True


### Snap by region group
print("Starting snapping for {} waterfalls".format(len(df)))

# retain only fields needed for snapping
to_snap = df.loc[~df.dropped, ["geometry", "HUC2", "id"]]
snapped = snap_by_region(to_snap, REGION_GROUPS, SNAP_TOLERANCE)

# join back to master
df = update_from_snapped(df, snapped)

# TODO: remove, move to post
### Add lat / lon
# print("Adding lat / lon fields")
# df = add_lat_lon(df)

### Remove duplicates after snapping, in case any snapped to the same position
# These are completely dropped from the analysis from here on out
df = mark_duplicates(df, DUPLICATE_TOLERANCE)
print(
    "{} duplicate waterfalls removed after snapping".format(len(df.loc[df.duplicate]))
)

print("\n--------------\n")
df = df.reset_index(drop=True)


to_geofeather(df, master_dir / "waterfalls.feather")

print("writing shapefiles for QA/QC")
to_shp(df, qa_dir / "waterfalls.shp")

# Extract out only the snapped ones
df = df.loc[df.snapped & ~df.duplicate].reset_index(drop=True)
df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

print("Serializing {0} snapped waterfalls".format(len(df)))
to_geofeather(
    df[["geometry", "id", "HUC2", "lineID", "NHDPlusID"]],
    snapped_dir / "waterfalls.feather",
)

print("All done in {:.2f}s".format(time() - start))
