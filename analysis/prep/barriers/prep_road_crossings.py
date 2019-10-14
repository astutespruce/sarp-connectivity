"""
Preprocess road / stream crossings into data needed by tippecanoe for creating vector tiles.

Input: 
* USGS Road / Stream crossings, projected to match SARP standard projection (Albers CONUS).
* pre-processed and snapped small barriers

In `data/barriers` directory:
```
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" src/road_crossings.shp src/RoadCrossings_USGS_10292018.gdb Rdx_Tiger2014_NHDplusV2Med_USGS -dim 2 -sql "SELECT FULLNAME, GNIS_NAME, RDXID from Rdx_Tiger2014_NHDplusV2Med_USGS"
```

Outputs:
`data/barriers/intermediate/road_crossings.feather`: road / stream crossing data for merging in with small barriers that do not have networks
"""

import sys
import os
from pathlib import Path
from time import time
from geofeather import to_geofeather, from_geofeather
import geopandas as gp
from nhdnet.io import deserialize_df
from nhdnet.geometry.points import add_lat_lon, mark_duplicates

from analysis.constants import CRS, DUPLICATE_TOLERANCE
from analysis.util import spatial_join
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins


start = time()

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
out_dir = barriers_dir / "master"

print("Reading road crossings")

df = gp.read_file(src_dir / "road_crossings_prj.shp")
print("Read {:,} road crossings".format(len(df)))

df["id"] = df.index.astype("uint32")
df = df.set_index("id", drop=False)

# There are a bunch of crossings with identical coordinates, remove them
# NOTE: they have different labels, but that seems like it is a result of
# them methods used to identify the crossings (e.g., named highways, roads, etc)
print("Removing duplicate crossings...")

# round to int
df["x"] = df.geometry.x.astype("int")
df["y"] = df.geometry.y.astype("int")

keep_ids = df[["x", "y", "id"]].groupby(["x", "y"]).first().reset_index().id
print("{:,} duplicate road crossings".format(len(df) - len(keep_ids)))

df = df.loc[keep_ids].copy()


### Remove crossings that are very close
print("Removing nearby road crossings...")
# consider 5 m nearby
df = mark_duplicates(df, 5)
print("{:,} very close road crossings dropped".format(len(df.loc[df.duplicate])))
df = df.loc[~df.duplicate].drop(columns=["duplicate", "dup_count", "dup_group"])

### Remove those that otherwise duplicate existing small barriers
print("Removing crossings that duplicate existing barriers")
barriers = from_geofeather(barriers_dir / "master/small_barriers.feather")
barriers = barriers.loc[~barriers.duplicate]
barriers["kind"] = "barrier"

df["joinID"] = (df.index * 1e6).astype("uint32")
df["kind"] = "crossing"

merged = barriers[["kind", "geometry"]].append(
    df[["joinID", "kind", "geometry"]], sort=False, ignore_index=True
)
merged = mark_duplicates(merged, tolerance=DUPLICATE_TOLERANCE)

dup_groups = merged.loc[
    (merged.dup_count > 1) & (merged.kind == "barrier")
].dup_group.unique()
remove_ids = merged.loc[
    merged.dup_group.isin(dup_groups) & (merged.kind == "crossing")
].joinID
print(
    "{:,} crossings appear to be duplicates of existing barriers".format(
        len(remove_ids)
    )
)

df = df.loc[~df.joinID.isin(remove_ids)].drop(columns=["joinID", "kind"])
print("Now have {:,} road crossings".format(len(df)))


# Rename columns to standardize with small barriers dataset
df = df.rename(columns={"FULLNAME": "Road", "GNIS_NAME": "Stream", "RDXID": "SARPID"})
df.SARPID = df.SARPID.astype("uint")
df["id"] = df.index.astype("uint")

# Cleanup fields
df.Stream = df.Stream.str.strip().fillna("")
df.Road = df.Road.str.strip().fillna("")

df.loc[
    (df.Stream.str.strip().str.len() > 0) & (df.Road.str.strip().str.len() > 0), "Name"
] = (df.Stream + " / " + df.Road)

df.Name = df.Name.fillna("")

### Spatial joins to boundary layers
# NOTE: these are used for summary stats, but not used in most of the rest of the stack
df = add_spatial_joins(df)

### Level 3 & 4 Ecoregions
print("Joining to ecoregions")
# Only need to join in ECO4 dataset since it has both ECO3 and ECO4 codes
eco4 = from_geofeather(boundaries_dir / "eco4.feather")[["geometry", "ECO3", "ECO4"]]
df = spatial_join(df, eco4)


print("Adding lat / lon fields")
df = add_lat_lon(df)

to_geofeather(df.reset_index(drop=True), out_dir / "road_crossings.feather")

print("Done in {:.2f}".format(time() - start))
