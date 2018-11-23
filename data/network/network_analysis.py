import os
from time import time

import geopandas as gp
import pandas as pd

from line_utils import (
    cut_line_at_points,
    calculate_sinuosity,
    create_points,
    snap_to_line,
    cut_flowlines,
)

SNAP_TOLERANCE_DAMS = 200  # meters  FIXME: should be 100m
SNAP_TOLERANCE = 100  # meters - tolerance for waterfalls

HUC4 = "0602"
src_dir = "/Users/bcward/projects/sarp/data/src"
working_dir = "data/src/tmp/{}".format(HUC4)
os.chdir(working_dir)

start = time()

##################### Read NHD data #################
print("------------------- Reading Flowlines -----------")
print("reading flowlines")
flowlines = gp.read_file("flowline.shp")
flowlines.NHDPlusID = flowlines.NHDPlusID.astype("uint64")
flowlines.lineID = flowlines.lineID.astype("uint32")
flowlines.set_index("lineID", inplace=True, drop=False)

##################### Read dams and waterfalls, and merge #################
print("------------------- Preparing barriers ----------")

##################### Read dams #################
print("Reading dams")
dams = pd.read_csv("{}/dams.csv".format(src_dir), dtype={"HUC4": str})
dams = create_points(dams, "lon", "lat", crs={"init": "EPSG:4326"}).to_crs(
    flowlines.crs
)
dams["joinID"] = dams.UniqueID

# Select out only the dams in this HUC
dams = dams.loc[dams.HUC4 == HUC4].copy()

snapper = snap_to_line(flowlines, SNAP_TOLERANCE_DAMS, prefer_endpoint=False)
snapped = dams.apply(snapper, axis=1)
dams = dams.drop(columns=["geometry"]).join(snapped)
# dams.to_csv("snapped_dams.csv", index=False)
# dams.to_file("snapped_dams.shp", driver="ESRI Shapefile")

##################### Read waterfalls #################
print("Reading waterfalls")
wf = gp.read_file(
    "{}/Waterfalls_USGS_2017.gdb".format(src_dir), layer="Waterfalls_USGS_2018"
).to_crs(flowlines.crs)
wf["joinID"] = wf.OBJECTID

# Extract out waterfalls in this HUC
wf["HUC4"] = wf.HUC_8.str[:4]
wf = wf.loc[wf.HUC4 == HUC4].copy()

snapper = snap_to_line(flowlines, SNAP_TOLERANCE, prefer_endpoint=False)
snapped = wf.apply(snapper, axis=1)
wf = wf.drop(columns=["geometry"]).join(snapped)
# wf.to_csv("snapped_waterfalls.csv", index=False)
# wf.to_file("snapped_waterfalls.shp", driver="ESRI Shapefile")

##################### Create combined barriers dataset #################
print("Merging and exporting single barriers file")
dams["kind"] = "dam"
wf["kind"] = "waterfall"

columns = [
    "lineID",
    "NHDPlusID",
    "joinID",
    "kind",
    "geometry",
    "snap_dist",
    "nearby",
    # "is_endpoint",
]

barriers = dams[columns].append(wf[columns], ignore_index=True, sort=False)
barriers.set_index("joinID", inplace=True, drop=False)

# drop any not on the network from all later processing
barriers = barriers.loc[~barriers.NHDPlusID.isnull()]
barriers.lineID = barriers.lineID.astype("uint32")
# barriers.to_csv("barriers.csv", index=False)
# barriers.to_file("barriers.shp", driver="ESRI Shapefile")


##################### Cut flowlines #################
print("------------------- Cutting flowlines -----------")
print("Starting from {} original segments".format(len(flowlines)))


joins = pd.read_csv("flowline_joins.csv")

flowlines, joins, barrier_joins = cut_flowlines(flowlines, barriers, joins)
joins.to_csv("updated_joins.csv", index=False)
barrier_joins.to_csv("barrier_joins.csv", index=False)
flowlines.drop(columns=["geometry"]).to_csv("split_flowlines.csv", index=False)

print("Writing split flowlines shp")
flowlines.NHDPlusID = flowlines.NHDPlusID.astype("float64")
flowlines.to_file("split_flowlines.shp", driver="ESRI Shapefile")


print("All done in {:.2f}".format(time() - start))

