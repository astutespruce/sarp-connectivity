"""Extract NHD data to simpler data formats for later processing

1. Read NHDFlowline and convert to 2D lines
2. Join to VAA and bring in select attributes
2. Project to USGS CONUS Albers (transient geom)
3. Calculate sinuosity and length
4. Write to shapefile
5. Write to CSV

Note: NHDPlusIDs are converted to 64bit ints

"""

import os
from time import time
import geopandas as gp
import pandas as pd

from line_utils import to2D, calculate_sinuosity


# Use USGS CONUS Albers (EPSG:102003): https://epsg.io/102003    (same as other SARP datasets)
# use Proj4 syntax, since GeoPandas doesn't properly recognize it's EPSG Code.
CRS = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

# TODO: loop on this
HUC4 = "0307"

src_dir = "data/src/tmp"
out_dir = "data/src/tmp/{}".format(HUC4)

gdb = "{0}/NHDPLUS_H_{1}_HU4_GDB.gdb".format(src_dir, HUC4)

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# Read in data and convert to data frame (no need for geometry)
start = time()
print("Reading flowlines")
df = gp.read_file(gdb, layer="NHDFlowline")

df = df[["NHDPlusID", "FlowDir", "FType", "FCode", "geometry"]]
# df.NHDPlusID = df.NHDPlusID.astype("int64")
df["id"] = df.NHDPlusID.astype("uint64")
# df = df.set_index(["NHDPlusID"], drop=False)
df = df.set_index(["id"])

print("Read {} features".format(len(df)))

print("Converting geometry to 2D")
df.geometry = df.geometry.apply(to2D)

# Filter out loops - this is not working properly for NHDPlus High resolution
# loops = (df.StreamLeve == df.StreamCalc) & ~df.FlowDir.isnull() & (df.FType != 566)
# df = df[~loops]


# FIXME
# df = df.head(100).copy()

# Read in VAA and convert to data frame
# NOTE: not all records in Flowlines have corresponding records in VAA
print("Reading VAA table and joining...")
vaa_df = gp.read_file(gdb, layer="NHDPlusFlowlineVAA")[
    ["NHDPlusID", "StreamLeve", "StreamOrde", "StreamCalc"]
]
vaa_df.NHDPlusID = vaa_df.NHDPlusID.astype("uint64")
vaa_df = vaa_df.set_index(["NHDPlusID"])

df = df.join(vaa_df, how="inner")  # drop any segments where we don't have info
print("{} features after join".format(len(df)))


# Project to USGS Albers CONUS so that we can calculate lengths
print("projecting to USGS Albers")
sinuosity_df = df[["geometry"]].to_crs(CRS)

print("Calculating sinuosity")
sinuosity_df["sinuosity"] = sinuosity_df.geometry.apply(calculate_sinuosity).astype(
    "float32"
)
sinuosity_df["length"] = sinuosity_df.geometry.length.astype("float32")
df = df.join(sinuosity_df[["sinuosity", "length"]])

# Write to shapefile and CSV for easier processing later
print("Writing flowlines to disk")
df.to_file("{}/flowline.shp".format(out_dir), driver="ESRI Shapefile")
df.drop(columns=["geometry"]).to_csv(
    "{}/flowline.csv".format(out_dir), index_label="id"
)

# Flow has the connections between segments
# Upstream is the upstream side of the connection, which would actually correspond to the downstream node of the upstream segment
print("Reading segment connections")
join_df = gp.read_file(gdb, layer="NHDPlusFlow")[["FromNHDPID", "ToNHDPID"]].rename(
    columns={"FromNHDPID": "upstream", "ToNHDPID": "downstream"}
)
join_df.upstream = join_df.upstream.astype("uint64")
join_df.downstream = join_df.downstream.astype("uint64")

print("Writing segment connections")
join_df.to_csv("{}/connections.csv".format(out_dir), index=False)

print("Done in {:.2f}".format(time() - start))
