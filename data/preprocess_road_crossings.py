"""
Preprocess road / stream crossings into data needed by tippecanoe for creating vector tiles.

Input: 
* USGS Road / Stream corssings SARP.
*  created using `preprocess_road_crossings.py`

Outputs:
* `road_crossings.csv`: road / stream crossing data for merging in with small barriers that do not have networks
"""

from time import time
import geopandas as gp
import pandas as pd
import numpy as np


start = time()

print("Reading source FGDB dataset")
df = gp.read_file(
    "data/src/RoadCrossings_USGS_10292018.gdb", layer="Rdx_Tiger2014_NHDplusV2Med_USGS"
)[["FULLNAME", "GNIS_NAME", "RDXID", "geometry"]]

print("Read {} road crossings".format(len(df)))

print("Projecting to WGS84 and adding lat / lon fields")
# Project to WGS84
df = df.to_crs(epsg=4326)

# Add lat / lon columns
df["lon"] = df.geometry.x.astype("float32")
df["lat"] = df.geometry.y.astype("float32")

df = df.drop(columns=["geometry"])

df.rename(
    columns={"FULLNAME": "Road", "GNIS_NAME": "Stream", "RDXID": "SARPID"}, inplace=True
)

df.SARPID = df.SARPID.astype("uint")

df.to_csv("data/derived/road_crossings.csv", index=False)

print("Done in {:.2f}".format(time() - start))
