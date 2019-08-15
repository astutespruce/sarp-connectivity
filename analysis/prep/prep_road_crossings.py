"""
Preprocess road / stream crossings into data needed by tippecanoe for creating vector tiles.

Input: 
USGS Road / Stream crossings, projected to match SARP standard projection (Albers CONUS):

```
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" road_crossings.shp RoadCrossings_USGS_10292018.gdb Rdx_Tiger2014_NHDplusV2Med_USGS -dim 2 -sql "SELECT FULLNAME, GNIS_NAME, RDXID from Rdx_Tiger2014_NHDplusV2Med_USGS"
```

Outputs:
`data/derived/road_crossings.feather`: road / stream crossing data for merging in with small barriers that do not have networks
"""

import sys
import os
from pathlib import Path
from time import time
import geopandas as gp
from nhdnet.io import deserialize_df, deserialize_gdf, serialize_df


# Lazy way to import from a shared file in a different directory, this allows us to import
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from analysis.constants import CRS


start = time()

data_dir = Path("data")
src_dir = data_dir / "barriers"
boundaries_dir = data_dir / "boundaries"
out_dir = data_dir / "derived"

print("Reading source FGDB dataset")

df = gp.read_file(src_dir / "road_crossings.shp")
print("Read {} road crossings".format(len(df)))

# Rename columns to standardize with small barriers dataset
df = df.rename(columns={"FULLNAME": "road", "GNIS_NAME": "stream", "RDXID": "sarpid"})
df.sarpid = df.sarpid.astype("uint")
df["id"] = df.index.astype("uint")

# Cleanup fields
df.stream = df.stream.str.strip()
df.road = df.road.str.strip()

df.loc[
    (df.stream.str.strip().str.len() > 0) & (df.road.str.strip().str.len() > 0), "name"
] = (df.stream + " / " + df.road)


### Spatial joins to boundary layers
print("Creating spatial index")
df.sindex

print("Joining to HUCs")
huc12 = deserialize_gdf(boundaries_dir / "huc12.feather")[["geometry", "HUC12"]]
huc12.sindex
df = gp.sjoin(df, huc12, how="left").drop(columns=["index_right"])

# drop any that don't have HUC12s
print(
    "Dropping {} crossings that are missing HUC12".format(
        len(df.loc[df.HUC12.isnull()])
    )
)
df = df.loc[df.HUC12.notnull()]


# Calculate other HUC  codes
df["HUC6"] = df["HUC12"].str.slice(0, 6)  # basin
df["HUC8"] = df["HUC12"].str.slice(0, 8)  # subbasin

# Read in HUC6 and join in basin name
huc6 = (
    deserialize_df(boundaries_dir / "HUC6.feather")[["HUC6", "NAME"]]
    .rename(columns={"NAME": "Basin"})
    .set_index("HUC6")
)
df = df.join(huc6, on="HUC6")


# Regenerate the spatial index if needed
df.sindex

print("Joining to counties")
counties = deserialize_gdf(boundaries_dir / "counties.feather")[
    ["geometry", "County", "COUNTYFIPS", "STATEFIPS"]
]
counties.sindex
df = gp.sjoin(df, counties, how="left").drop(columns=["index_right"])

# Join in state name based on STATEFIPS from county
states = deserialize_df(boundaries_dir / "states.feather")[
    ["STATEFIPS", "State"]
].set_index("STATEFIPS")
df = df.join(states, on="STATEFIPS")


# Regenerate the spatial index if needed
df.sindex

print("Joining to ecoregions")
# Only need to join in ECO4 dataset since it has both ECO3 and ECO4 codes
eco4 = deserialize_gdf(boundaries_dir / "eco4.feather")[["geometry", "ECO3", "ECO4"]]
eco4.sindex
df = gp.sjoin(df, eco4, how="left").drop(columns=["index_right"])


print("Projecting to WGS84 and adding lat / lon fields")
# Project to WGS84
df = df.to_crs(epsg=4326)

# Add lat / lon columns
df["lon"] = df.geometry.x.astype("float32")
df["lat"] = df.geometry.y.astype("float32")
df = df.drop(columns=["geometry"])


serialize_df(df, out_dir / "road_crossings.feather", index=False)

print("Done in {:.2f}".format(time() - start))
