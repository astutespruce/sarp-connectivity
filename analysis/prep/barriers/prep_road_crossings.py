"""
Preprocess road / stream crossings into data needed by tippecanoe for creating vector tiles.

Input: 
USGS Road / Stream crossings, projected to match SARP standard projection (Albers CONUS):

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
from nhdnet.geometry.points import add_lat_lon

from analysis.constants import CRS
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

# Rename columns to standardize with small barriers dataset
df = df.rename(columns={"FULLNAME": "road", "GNIS_NAME": "stream", "RDXID": "sarpid"})
df.sarpid = df.sarpid.astype("uint")
df["id"] = df.index.astype("uint")

# Cleanup fields
df.stream = df.stream.str.strip().fillna("")
df.road = df.road.str.strip().fillna("")

df.loc[
    (df.stream.str.strip().str.len() > 0) & (df.road.str.strip().str.len() > 0), "name"
] = (df.stream + " / " + df.road)

df.name = df.name.fillna("")

### Spatial joins to boundary layers
# TODO: these are not currently used, and take a lot of compute time to create
# df = add_spatial_joins(df)


print("Adding lat / lon fields")
df = add_lat_lon(df)

to_geofeather(df.reset_index(drop=True), out_dir / "road_crossings.feather")

print("Done in {:.2f}".format(time() - start))
