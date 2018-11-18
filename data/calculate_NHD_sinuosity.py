"""Calculate the sinuosity of each line

Sinuosity is the ratio of the flow length of a line versus the straight line length between the endpoints:
https://en.wikipedia.org/wiki/Sinuosity

The key attribute to join back to is NHDPlusID

Features need to be projected to a planar system first

"""
from time import time
from math import sqrt
import pandas as pd
import geopandas as gp


filename = "NHDPLUS_H_0316_HU4_GDB.gdb"


start = time()

# Use USGS CONUS Albers (EPSG:102003): https://epsg.io/102003    (same as other SARP datasets)
# use Proj4 syntax, since GeoPandas doesn't properly recognize it's EPSG Code.
crs = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

print("Reading file...")
df = gp.read_file("data/src/tmp/{}".format(filename), layer="NHDFlowline")[
    ["NHDPlusID", "geometry"]
]

print("Projecting to USGS Albers CONUS")
df.to_crs(crs)


def calculate_distance(first, last):
    return sqrt((last[0] - first[0]) ** 2 + (last[1] - first[1]) ** 2)


def calculate_sinuosity(line):
    # By definition, sinuosity should not be less than 1
    straight_line_distance = calculate_distance(line.coords[0], line.coords[-1])
    if straight_line_distance != 0:
        return max(line.length / straight_line_distance, 1)

    return 1  # if there is no straight line distance, there is no sinuosity


df["sinuosity"] = df.apply(
    lambda row: calculate_sinuosity(row.geometry.geoms[0]), axis=1
)

df.to_csv("data/src/tmp/sinuosity.csv", columns=["NHDPlusID", "sinuosity"], index=False)

print("Done in {:.2f}".format(time() - start))

