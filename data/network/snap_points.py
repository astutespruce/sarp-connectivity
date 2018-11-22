"""
Attempt to snap dams in the inventory to NHD segments.  This snaps to the nearest segment within 100m.

Unfortunately, some very large dams are not always close enough to the centerline to snap:
e.g., https://en.wikipedia.org/wiki/Chickamauga_Dam

So an alternative method needs to be worked out for those.


TODO: add lat and lon snapped coords too

Note: early attempts at snapping to end line produced undesirable results

"""


import os
from time import time

import geopandas as gp
import pandas as pd
from shapely.geometry import Point
import rtree

from line_utils import snap_to_line

CRS = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"
TOLERANCE = 200  # meters  FIXME: should be 100m
WF_TOLERANCE = 100  # meters - tolerance for waterfalls

DAM_COLS = [
    "id",
    "UniqueID",
    "Barrier_Name",
    "River",
    "Off_Network",
    "HUC4",
    "lat",
    "lon",
]


HUC4 = "0602"

start = time()

print("reading flowlines")
flowlines = gp.read_file("data/src/tmp/{}/flowline.shp".format(HUC4))
flowlines.NHDPlusID = flowlines.NHDPlusID.astype("uint64")

# create spatial index
print("creating spatial index on flowlines")
sindex = flowlines.sindex

############# Snap dams ################
print("Importing dams")
dams = pd.read_csv("data/src/dams.csv", dtype={"HUC4": str})[DAM_COLS]

# Select out only the dams in this HUC
dams = dams.loc[dams.HUC4 == HUC4].copy()  # TODO: do this after reprojecting

# Filter out any known to be off network
# TODO: this might not be right
# dams = dams.loc[dams.Off_Network != "Off Network"].copy()

# Create geometry field and project
print("Projecting points")
geometry = [Point(lonlat) for lonlat in zip(dams.lon, dams.lat)]
dams = (
    gp.GeoDataFrame(dams, geometry=geometry, crs={"init": "EPSG:4326"})
    .to_crs(CRS)
    .set_index("id")
)
dams["joinID"] = dams.UniqueID
# dams = dams.head(10).copy()  # FIXME

snapped = snap_to_line(
    dams,
    flowlines,
    TOLERANCE,
    prefer_endpoint=False,
    line_columns=["lineID", "NHDPlusID", "GNIS_Name"],
)

dams = dams.join(snapped)

dams.to_csv(
    "data/src/tmp/{}/snapped_dams.csv".format(HUC4),
    index_label="id",
    columns=[
        "UniqueID",
        "snap_x",
        "snap_y",
        "snap_dist",
        "nearby",
        # "is_endpoint",
        "lineID",
        "NHDPlusID",
        "GNIS_Name",
        "River",
        "Barrier_Name",
        "Off_Network",
    ],
)

print("Done in {:.2f}".format(time() - start))


############# Snap waterfalls ################

# Read in waterfalls and project to USGS Albers
print("Reading waterfalls")
wf = gp.read_file(
    "data/src/Waterfalls_USGS_2017.gdb", layer="Waterfalls_USGS_2018"
).to_crs(CRS)
wf["joinID"] = wf.OBJECTID
wf["HUC4"] = wf.HUC_8.str[:4]

# Extract out waterfalls in this HUC
wf = wf.loc[wf.HUC4 == HUC4].to_crs(CRS)

if len(wf):
    snapped = snap_to_line(
        wf,
        flowlines,
        WF_TOLERANCE,
        prefer_endpoint=False,
        line_columns=["lineID", "NHDPlusID", "GNIS_Name"],
    )

    wf = wf.join(snapped)

    wf.to_csv(
        "data/src/tmp/{}/snapped_waterfalls.csv".format(HUC4),
        index_label="id",
        columns=[
            "snap_x",
            "snap_y",
            "snap_dist",
            "nearby",
            # "is_endpoint",
            "lineID",
            "NHDPlusID",
            "Name",
            "GNIS_Name",
        ],
    )

print("Done in {:.2f}".format(time() - start))


print("Merging and exporting single barriers file")
dams["kind"] = "dam"
wf["kind"] = "waterfall"

barriers = (
    dams[
        [
            "lineID",
            "NHDPlusID",
            "joinID",
            "kind",
            "snap_x",
            "snap_y",
            "snap_dist",
            "nearby",
            # "is_endpoint",
        ]
    ]
    .append(
        wf[
            [
                "lineID",
                "NHDPlusID",
                "joinID",
                "kind",
                "snap_x",
                "snap_y",
                "snap_dist",
                "nearby",
                # "is_endpoint",
            ]
        ],
        ignore_index=True,
        sort=False,
    )
    .rename(columns={"snap_x": "x", "snap_y": "y"})
)

barriers.to_csv("data/src/tmp/{}/barriers.csv".format(HUC4), index=False)


# drop any that aren't on the network
barriers = barriers.loc[~barriers.NHDPlusID.isnull()]

gp.GeoDataFrame(
    barriers, geometry=[Point(xy) for xy in zip(barriers.x, barriers.y)], crs=CRS
).to_file("data/src/tmp/{}/barriers.shp".format(HUC4), driver="ESRI Shapefile")

