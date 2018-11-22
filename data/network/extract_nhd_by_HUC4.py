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
FLOWLINE_COLS = [
    "NHDPlusID",
    "FlowDir",
    "FType",
    "FCode",
    "GNIS_Name",
    "ReachCode",
    "geometry",
]

# TODO: add elevation gradient info
VAA_COLS = ["NHDPlusID", "StreamOrde", "StreamCalc", "TotDASqKm"]


# TODO: loop on this
HUC4 = "0602"

src_dir = "data/src/tmp"
out_dir = "data/src/tmp/{}".format(HUC4)

gdb = "{0}/NHDPLUS_H_{1}_HU4_GDB.gdb".format(src_dir, HUC4)

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# Read in data and convert to data frame (no need for geometry)
start = time()
print("Reading flowlines")
df = gp.read_file(gdb, layer="NHDFlowline")[FLOWLINE_COLS]
# Set our internal master IDs to the original index of the file we start from
# Assume that we can always fit into a uint32, which is ~400 million records
# and probably bigger than anything we could ever read in
# df["id"] = df.index.values.astype("uint32") + 1
df["lineID"] = df.index + 1
# Index on NHDPlusID for easy joins to other NHD data
df.NHDPlusID = df.NHDPlusID.astype("uint64")
df = df.set_index(["NHDPlusID"], drop=False)

print("Read {} flowlines".format(len(df)))

# Read in VAA and convert to data frame
# NOTE: not all records in Flowlines have corresponding records in VAA
print("Reading VAA table and joining...")
vaa_df = gp.read_file(gdb, layer="NHDPlusFlowlineVAA")[VAA_COLS]
vaa_df.NHDPlusID = vaa_df.NHDPlusID.astype("uint64")
vaa_df = vaa_df.set_index(["NHDPlusID"])
df = df.join(vaa_df, how="inner")
print("{} features after join to VAA".format(len(df)))

# Filter out loops (query came from Kat) and other segments we don't want.
# 566 is coastlines type.
print("Filtering out loops and coastlines")
removed = df.loc[
    (df.StreamOrde != df.StreamCalc) | (df.FlowDir.isnull()) | (df.FType == 566)
]
df = df.loc[~df.index.isin(removed.index)].copy()
print("{} features after removing loops and coastlines".format(len(df)))

# Calculate size classes
print("Calculating size class")
drainage = df.TotDASqKm
df.loc[drainage < 10, "sizeclass"] = "1a"
df.loc[(drainage >= 10) & (drainage < 100), "sizeclass"] = "1b"
df.loc[(drainage >= 100) & (drainage < 518), "sizeclass"] = "2"
df.loc[(drainage >= 518) & (drainage < 2590), "sizeclass"] = "3a"
df.loc[(drainage >= 2590) & (drainage < 10000), "sizeclass"] = "3b"
df.loc[(drainage >= 10000) & (drainage < 25000), "sizeclass"] = "4"
df.loc[drainage >= 25000, "sizeclass"] = "5"

# Convert incoming data from XYZM to XY
print("Converting geometry to 2D")
df.geometry = df.geometry.apply(to2D)

# Project to USGS Albers CONUS so that we can calculate lengths
print("projecting to USGS Albers")
df = df.to_crs(CRS)

# Calculate length and sinuosity
print("Calculating length and sinuosity")
df["length"] = df.geometry.length.astype("float32")
df["sinuosity"] = df.geometry.apply(calculate_sinuosity).astype("float32")

# Drop unneeded attributes to speed up I/O
df = df[
    [
        "lineID",
        "NHDPlusID",
        "FType",
        "FCode",
        "GNIS_Name",
        "ReachCode",
        "sizeclass",
        "length",
        "sinuosity",
        "geometry",
    ]
]

# Write to shapefile and CSV for easier processing later
print("Writing flowlines to disk")
df.drop(columns=["geometry"]).to_csv("{}/flowline.csv".format(out_dir), index=False)

# Always write NHDPlusID back out as a float64
geo_df = df.copy()
geo_df.NHDPlusID = geo_df.NHDPlusID.astype("float64")
geo_df.to_file("{}/flowline.shp".format(out_dir), driver="ESRI Shapefile")


############# Connections between segments ###################
print("Reading segment connections")
join_df = gp.read_file(gdb, layer="NHDPlusFlow")[["FromNHDPID", "ToNHDPID"]].rename(
    columns={"FromNHDPID": "upstream", "ToNHDPID": "downstream"}
)
join_df.upstream = join_df.upstream.astype("uint64")
join_df.downstream = join_df.downstream.astype("uint64")

# remove any joins to or from segments we removed above
join_df = join_df.loc[
    ~(join_df.upstream.isin(removed.index) | join_df.downstream.isin(removed.index))
]

# Any join that is not a terminal or origin that we don't have in our data at this point
# is most likely a join between this HUC and the next
# TODO: validate this idea
huc_joins = join_df.loc[
    (~(join_df.upstream.isin(df.index) | (join_df.upstream == 0)))
    | (~(join_df.downstream.isin(df.index) | (join_df.downstream == 0)))
]

# origins = join_df.loc[join_df.upstream == 0]
# Some major rivers are coded as terminal segments - WHY???
# terminals = join_df.loc[join_df.downstream == 0]


# Drop any of the joins outside of this HUC for purposes of building the network
join_df = join_df.loc[~join_df.index.isin(huc_joins.index)]

# update joins with our ids
ids = df[["lineID"]]
join_df = (
    join_df.join(ids.rename(columns={"lineID": "upstream_id"}), on="upstream")
    .join(ids.rename(columns={"lineID": "downstream_id"}), on="downstream")
    .fillna(0)
    .astype("uint64")
)


print("Writing segment connections")
join_df.to_csv("{}/connections.csv".format(out_dir), index=False)
huc_joins.to_csv("{}/huc_joins.csv".format(out_dir), index=False)


print("Done in {:.2f}".format(time() - start))
