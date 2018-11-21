"""
Attempt to snap dams in the inventory to NHD segments.  This snaps to the nearest segment within 100m.

Unfortunately, some very large dams are not always close enough to the centerline to snap:
e.g., https://en.wikipedia.org/wiki/Chickamauga_Dam

So an alternative method needs to be worked out for those.


TODO: add lat and lon snapped coords too

"""


import os
from time import time

import geopandas as gp
import pandas as pd
from shapely.geometry import Point
import rtree


CRS = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"
TOLERANCE = 200  # meters  FIXME: should be 100m
WF_TOLERANCE = 100  # meters - tolerance for waterfalls

HUC4 = "0602"

start = time()

print("reading flowlines")
flowlines = gp.read_file("data/src/tmp/{}/flowline.shp".format(HUC4))
# flowlines.NHDPlusID = flowlines.NHDPlusID.astype("uint64")

# create spatial index
print("creating spatial index on flowlines")
sindex = flowlines.sindex

############# Snap dams ################
print("Importing dams")
dams = pd.read_csv("data/src/dams.csv", dtype={"HUC4": str})

# Select out only the fields we need
dams = dams[
    ["id", "UniqueID", "Barrier_Name", "River", "Off_Network", "HUC4", "lat", "lon"]
]

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

# Create a window that is +/- tolerance
dams["window"] = dams.geometry.apply(
    lambda g: (g.x - TOLERANCE, g.y - TOLERANCE, g.x + TOLERANCE, g.y + TOLERANCE)
)

print("snapping points to lines")
for idx, dam in dams.iterrows():
    # print(idx)

    # nearby features
    hits = flowlines.loc[sindex.intersection(dam.window)].copy()

    # calculate distance to point and
    hits["dist"] = hits.distance(dam.geometry)
    within_tolerance = hits[hits.dist <= TOLERANCE]

    if len(within_tolerance):
        # find nearest line segment that is within TOLERANCE
        closest = within_tolerance.nsmallest(1, columns=["dist"])

        # calculate the snapped coordinate
        closest["snapped"] = closest.geometry.apply(
            lambda g: g.interpolate(g.project(dam.geometry))
        )
        # closest = gp.GeoDataFrame(closest, geometry=closest.snapped, crs=closest.crs)

        # Project to WGS84 and grab first record
        # closest = (
        #     gp.GeoDataFrame(closest, geometry=closest.snapped, crs=closest.crs)
        #     .to_crs({"init": "EPSG:4326"})
        # )

        # Select first record
        closest = closest.iloc[0]
        dams.loc[idx, "snap_x"] = closest.snapped.x
        dams.loc[idx, "snap_y"] = closest.snapped.y
        dams.loc[idx, "snap_dist"] = closest.dist
        dams.loc[idx, "num_within_tolerance"] = len(within_tolerance)

        # Copy attributes from NHD to dam
        for column in ("NHDPlusID", "GNIS_Name"):
            dams.loc[idx, column] = closest[column]


dams.to_csv(
    "data/src/tmp/{}/snapped_dams.csv".format(HUC4),
    index_label="id",
    columns=[
        "UniqueID",
        "snap_x",
        "snap_y",
        "snap_dist",
        "num_within_tolerance",
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
wf = gp.read_file("data/src/Waterfalls_USGS_2017.gdb", layer="Waterfalls_USGS_2018")
wf["HUC4"] = wf.HUC_8.str[:4]

# Extract out waterfalls in this HUC
wf = wf.loc[wf.HUC4 == HUC4].to_crs(CRS)

if len(wf):

    # Create a window that is +/- tolerance
    wf["window"] = wf.geometry.apply(
        lambda g: (
            g.x - WF_TOLERANCE,
            g.y - WF_TOLERANCE,
            g.x + WF_TOLERANCE,
            g.y + WF_TOLERANCE,
        )
    )

    print("snapping points to lines")
    for idx, waterfall in wf.iterrows():
        # nearby features
        hits = flowlines.loc[sindex.intersection(waterfall.window)].copy()

        # calculate distance to point and
        hits["dist"] = hits.distance(waterfall.geometry)
        within_tolerance = hits[hits.dist <= WF_TOLERANCE]

        if len(within_tolerance):
            # find nearest line segment that is within TOLERANCE
            closest = within_tolerance.nsmallest(1, columns=["dist"])

            # calculate the snapped coordinate
            closest["snapped"] = closest.geometry.apply(
                lambda g: g.interpolate(g.project(waterfall.geometry))
            )

            # Project to WGS84 and grab first record
            # closest = gp.GeoDataFrame(
            #     closest, geometry=closest.snapped, crs=closest.crs
            # ).to_crs({"init": "EPSG:4326"})

            # Select first record
            closest = closest.iloc[0]
            wf.loc[idx, "snap_x"] = closest.snapped.x
            wf.loc[idx, "snap_y"] = closest.snapped.y
            wf.loc[idx, "snap_dist"] = closest.dist
            wf.loc[idx, "num_within_tolerance"] = len(within_tolerance)

            # Copy attributes from NHD to waterfall
            for column in ("NHDPlusID", "GNIS_Name"):
                wf.loc[idx, column] = closest[column]

        wf.to_csv(
            "data/src/tmp/{}/snapped_waterfalls.csv".format(HUC4),
            index_label="id",
            columns=[
                "snap_x",
                "snap_y",
                "snap_dist",
                "num_within_tolerance",
                "NHDPlusID",
                "Name",
                "GNIS_Name",
            ],
        )

        # Write shapefile
        # wf = wf[
        #     [
        #         "snap_x",
        #         "snap_y",
        #         "snap_dist",
        #         "num_within_tolerance",
        #         "NHDPlusID",
        #         "Name",
        #         "GNIS_Name",
        #         "geometry",
        #     ]
        # ].copy()
        # wf.NHDPlusID = wf.NHDPlusID.astype("float64")
        # wf.to_file("data/src/tmp/{}/snapped_waterfalls.shp".format(HUC4))

print("Done in {:.2f}".format(time() - start))

