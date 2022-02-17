"""
Preprocess road / stream crossings into data needed by tippecanoe for creating vector tiles.

Input:
* USGS Road / Stream crossings, projected to match SARP standard projection (Albers CONUS).
* pre-processed and snapped small barriers


Outputs:
`data/barriers/intermediate/road_crossings.feather`: road / stream crossing data for merging in with small barriers that do not have networks
"""

from pathlib import Path
from time import time
import warnings

import geopandas as gp
import pygeos as pg
from pyogrio import read_dataframe


from analysis.constants import CRS
from analysis.prep.barriers.lib.duplicates import mark_duplicates
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

start = time()

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
qa_dir = barriers_dir / "qa"


print("Reading road crossings")


# rename columns to match small barriers
# NOTE: tiger2020_feature_names is a combination of multiple road names
df = read_dataframe(
    src_dir / "stream_crossings_united_states_feb_2022.gpkg",
    layer="stream_crossing_sites",
    columns=[
        "stream_crossing_id",
        "tiger2020_feature_names",
        "nhdhr_gnis_stream_name",
        "crossing_type",
    ],
).rename(
    columns={
        "tiger2020_feature_names": "Road",
        "nhdhr_gnis_stream_name": "Stream",
        "stream_crossing_id": "SARPID",
        "crossing_type": "crossingtype",
    }
)
print(f"Read {len(df):,} road crossings")

# project HUC4 to match crossings
huc4 = gp.read_feather(boundaries_dir / "huc4.feather", columns=["geometry"]).to_crs(
    df.crs
)

tree = pg.STRtree(df.geometry.values.data)
ix = tree.query_bulk(huc4.geometry.values.data, predicate="intersects")[1]

df = df.take(ix).reset_index(drop=True)
print(f"Selected {len(df):,} road crossings in region")

# use original latitude / longitude (NAD83) values
lon, lat = pg.get_coordinates(df.geometry.values.data).astype("float32").T
df["lon"] = lon
df["lat"] = lat

# project to match SARP CRS
df = df.to_crs(CRS)

df["id"] = df.index.astype("uint32")
df = df.set_index("id", drop=False)

# There are a bunch of crossings with identical coordinates, remove them
# NOTE: they have different labels, but that seems like it is a result of
# them methods used to identify the crossings (e.g., named highways, roads, etc)
print("Removing duplicate crossings...")

# round to int
x, y = pg.get_coordinates(df.geometry.values.data).astype("int").T
df["x"] = x
df["y"] = y

keep_ids = df[["x", "y", "id"]].groupby(["x", "y"]).first().reset_index().id
print(f"Dropping {len(df) - len(keep_ids):,} duplicate road crossings")

df = df.loc[keep_ids].copy()

### Remove crossings that are very close
print("Removing nearby road crossings...")
# consider 5 m nearby
df = mark_duplicates(df, 5)
print(f"Dropping {df.duplicate.sum():,} very close road crossings")
df = (
    df.loc[~df.duplicate]
    .drop(columns=["duplicate", "dup_count", "dup_group"])
    .reset_index(drop=True)
)

print(f"now have {len(df):,} road crossings")

# Cleanup fields
df.Stream = df.Stream.str.strip().fillna("")
df.Road = df.Road.str.strip().fillna("")

df.loc[
    (df.Stream.str.strip().str.len() > 0) & (df.Road.str.strip().str.len() > 0), "Name"
] = (df.Stream + " / " + df.Road)

df.Name = df.Name.fillna("")

# match dtype of SARPID elsewhere
df.SARPID = "cr" + df.SARPID.round().astype(int).astype(str)

df = add_spatial_joins(df)

print(f"now have {len(df):,} road crossings after spatial joins")

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


df.reset_index(drop=True).to_feather(src_dir / "road_crossings.feather")

print(f"Done in {time() - start:.2f}")
