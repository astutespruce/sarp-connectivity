"""
Preprocess road / stream crossings into data needed by tippecanoe for creating vector tiles.

Input:
* USGS Road / Stream crossings, projected to match SARP standard projection (Albers CONUS).
* pre-processed and snapped small barriers


Outputs:
`data/barriers/intermediate/road_crossings.feather`: road / stream crossing data for merging in with small barriers that do not have networks
"""

import sys
import os
from pathlib import Path
from time import time
import warnings


from pyogrio import read_dataframe, write_dataframe
import pygeos as pg
import geopandas as gp


from analysis.constants import CRS
from analysis.lib.util import spatial_join
from analysis.prep.barriers.lib.duplicates import mark_duplicates
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins
from analysis.rank.lib.spatial_joins import (
    add_spatial_joins as add_protectedland_priorities,
)

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

DUPLICATE_TOLERANCE = 10  # meters

start = time()

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
out_dir = barriers_dir / "master"
qa_dir = barriers_dir / "qa"

gdb = src_dir / "RoadCrossings_USGS_10292018.gdb"

print("Reading road crossings")

df = read_dataframe(
    gdb, columns=["FULLNAME", "GNIS_NAME", "RDXID"], force_2d=True
).to_crs(CRS)
print("Read {:,} road crossings".format(len(df)))

df["id"] = df.index.astype("uint32")
df = df.set_index("id", drop=False)

# There are a bunch of crossings with identical coordinates, remove them
# NOTE: they have different labels, but that seems like it is a result of
# them methods used to identify the crossings (e.g., named highways, roads, etc)
print("Removing duplicate crossings...")

# round to int
df["x"] = pg.get_x(df.geometry.values.data).astype("int")
df["y"] = pg.get_y(df.geometry.values.data).astype("int")

keep_ids = df[["x", "y", "id"]].groupby(["x", "y"]).first().reset_index().id
print(f"{len(df) - len(keep_ids):,} duplicate road crossings")

df = df.loc[keep_ids].copy()


### Remove crossings that are very close
print("Removing nearby road crossings...")
# consider 5 m nearby
df = mark_duplicates(df, 5)
print(f"{df.duplicate.sum():,} very close road crossings dropped")
df = df.loc[~df.duplicate].drop(columns=["duplicate", "dup_count", "dup_group"])

### Remove those that otherwise duplicate existing small barriers
print("Removing crossings that duplicate existing barriers")
barriers = gp.read_feather(barriers_dir / "master/small_barriers.feather")
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
print(f"{len(remove_ids):,} crossings appear to be duplicates of existing barriers")

df = df.loc[~df.joinID.isin(remove_ids)].drop(columns=["joinID", "kind"])
print(f"Now have {len(df):,} road crossings")


# Rename columns to standardize with small barriers dataset

df = df.rename(columns={"FULLNAME": "Road", "GNIS_NAME": "Stream", "RDXID": "SARPID"})
# Cleanup fields
df.SARPID = df.SARPID.astype("uint")
df["id"] = df.index.astype("uint")
df.Stream = df.Stream.str.strip().fillna("")
df.Road = df.Road.str.strip().fillna("")

df.loc[
    (df.Stream.str.strip().str.len() > 0) & (df.Road.str.strip().str.len() > 0), "Name"
] = (df.Stream + " / " + df.Road)

df.Name = df.Name.fillna("")

### Spatial joins to boundary layers
# NOTE: these are used for summary stats, but not used in most of the rest of the stack
df = add_spatial_joins(df)

### Spatial joins to protected lands and priority watersheds
df = add_protectedland_priorities(df)

# Cleanup HUC, state, county, and ecoregion columns that weren't assigned
for col in [
    "HUC2",
    "HUC6",
    "HUC8",
    "HUC12",
    "Basin",
    "County",
    "COUNTYFIPS",
    "STATEFIPS",
    "State",
    "ECO3",
    "ECO4",
]:
    df[col] = df[col].fillna("")


print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(epsg=4326)
geo["lat"] = pg.get_y(geo.geometry.values.data).astype("float32")
geo["lon"] = pg.get_x(geo.geometry.values.data).astype("float32")
df = df.join(geo[["lat", "lon"]])


df = df.reset_index(drop=True)

df.to_feather(out_dir / "road_crossings.feather")
write_dataframe(df, qa_dir / "road_crossings.gpkg")

print("Done in {:.2f}".format(time() - start))
