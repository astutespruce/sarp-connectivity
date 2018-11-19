# https://www.packtpub.com/mapt/book/big_data_and_business_intelligence/9781783555079/5/ch05lvl1sec43/snapping-a-point-to-the-nearest-line

import os
from time import time

import geopandas as gp
import pandas as pd
from shapely.geometry import Point
import rtree


CRS = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"
TOLERANCE = 100  # meters

HUC4 = "0307"

start = time()

print("Importing dams")
dams = pd.read_csv("data/src/dams.csv", dtype={"HUC4": str})

dams = dams.loc[dams.HUC4 == HUC4].copy()  # TODO: do this after reprojecting

dams = dams[["id", "UniqueID", "lat", "lon"]]

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

print("reading flowlines")
flowlines = gp.read_file("data/src/tmp/{}/flowline.shp".format(HUC4)).to_crs(CRS)
flowlines.NHDPlusID = flowlines.NHDPlusID.astype("uint64")

# create spatial index
print("creating spatial index on flowlines")
sindex = flowlines.sindex

print("snapping points to lines")
for idx, dam in dams.iterrows():
    # print(idx)

    # nearby features
    hits = flowlines.loc[sindex.intersection(dam.window)].copy()

    # calculate distance to point and find nearest line segment that is within TOLERANCE
    hits["dist"] = hits.distance(
        dam.geometry
    )  # hits.geometry.apply(lambda g: g.project(dam.geometry))
    closest = hits[hits.dist <= TOLERANCE].nsmallest(1, columns=["dist"])

    # only snap if there is a closest one, and it is within 100 m
    if len(closest):
        closest["snapped"] = closest.geometry.apply(
            lambda g: g.interpolate(g.project(dam.geometry))
        )
        closest = (
            gp.GeoDataFrame(
                closest[["dist", "NHDPlusID"]],
                geometry=closest.snapped,
                crs=closest.crs,
            )
            .to_crs({"init": "EPSG:4326"})
            .iloc[0]
        )

        # index = dams.id == dam.id
        dams.loc[idx, "snapped_lon"] = closest.geometry.x
        dams.loc[idx, "snapped_lat"] = closest.geometry.y
        dams.loc[idx, "snapped_dist"] = closest.dist
        dams.loc[idx, "NHDPlusID"] = closest.NHDPlusID

    # else:
    #     print("no match for dam: {}".format(idx))


dams.to_csv(
    "data/src/tmp/{}/snapped.csv".format(HUC4),
    index_label="id",
    columns=["snapped_lat", "snapped_lon", "snapped_dist", "NHDPlusID"],
)


print("Done in {:.2f}".format(time() - start))
