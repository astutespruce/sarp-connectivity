import os
from time import time

import geopandas as gp
import pandas as pd
from shapely.geometry import MultiLineString

from line_utils import (
    cut_line_at_points,
    calculate_sinuosity,
    create_points,
    snap_to_line,
    cut_flowlines,
)

from network_utils import calculate_upstream_network, calculate_network_stats


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
barrier_start = time()
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

print("Done preparing barriers in {:.2f}s".format(time() - barrier_start))

##################### Cut flowlines #################
cut_start = time()
print("------------------- Cutting flowlines -----------")
print("Starting from {} original segments".format(len(flowlines)))

joins = pd.read_csv(
    "flowline_joins.csv", dtype={"upstream_id": "uint32", "downstream_id": "uint32"}
)

flowlines, joins, barrier_joins = cut_flowlines(flowlines, barriers, joins)

barrier_joins.upstream_id = barrier_joins.upstream_id.astype("uint32")
barrier_joins.downstream_id = barrier_joins.downstream_id.astype("uint32")

joins.to_csv("updated_joins.csv", index=False)
barrier_joins.to_csv("barrier_joins.csv", index=False)
flowlines.drop(columns=["geometry"]).to_csv("split_flowlines.csv", index=False)

# print("Writing split flowlines shp")
# flowlines.NHDPlusID = flowlines.NHDPlusID.astype("float64")
# flowlines.to_file("split_flowlines.shp", driver="ESRI Shapefile")

print("Done cutting in {:.2f}".format(time() - cut_start))

##################### Create networks #################
print("------------------- Creating networks -----------")
network_start = time()
# remove any origin segments
barrier_segments = set(barrier_joins.upstream_id.unique()).difference({0})

get_upstream_ids = lambda id: joins.loc[joins.downstream_id == id].upstream_id
has_multiple_downstreams = lambda id: len(joins.loc[joins.upstream_id == id]) > 1

# Create networks from all terminal nodes (no downstream nodes) up to origins or dams (but not including dam segments)
root_ids = joins.loc[joins.downstream_id == 0].upstream_id
print(
    "Starting non-barrier functional network creation for {} origin points".format(
        len(root_ids)
    )
)
for start_id in root_ids:
    network = calculate_upstream_network(
        start_id,
        get_upstream_ids,
        has_multiple_downstreams,
        stop_segments=barrier_segments.copy(),
    )

    rows = flowlines.index.isin(network)
    flowlines.loc[rows, "networkID"] = start_id
    flowlines.loc[rows, "networkType"] = "origin_upstream"

    # print("nonbarrier upstream network has {} segments".format(len(network)))

print(
    "Starting barrier functional network creation for {} barriers".format(
        len(barrier_segments)
    )
)
for start_id in barrier_segments:
    network = calculate_upstream_network(
        start_id,
        get_upstream_ids,
        has_multiple_downstreams,
        stop_segments=barrier_segments.copy(),
    )

    rows = flowlines.index.isin(network)
    flowlines.loc[rows, "networkID"] = start_id
    flowlines.loc[rows, "networkType"] = "barrier_upstream"
    # print("barrier upstream network has {} segments".format(len(network)))

# drop anything that didn't get assigned a network
network_df = flowlines.loc[~flowlines.networkID.isnull()].copy()
network_df.networkID = network_df.networkID.astype("uint32")
network_df.drop(columns=["geometry"]).to_csv("network_segments.csv", index=False)
network_df.to_file("network_segments.shp", driver="ESRI Shapefile")

print(
    "Created {0} networks in {1:.2f}s".format(
        len(network_df.networkID.unique()), time() - network_start
    )
)


##################### Network stats #################
print("------------------- Aggregating network info -----------")

network_stats = calculate_network_stats(network_df)

network_stats.to_csv(
    "network_stats.csv", columns=["km", "miles", "sinuosity"], index_label="networkID"
)
network_miles = network_stats[["miles"]]

# join to upstream networks
barriers = (
    barriers.join(barrier_joins.upstream_id)
    .join(network_miles, on="upstream_id")
    .rename(columns={"upstream_id": "upNetID", "miles": "UpstreamMiles"})
)
downstream_networks = (
    barrier_joins.join(network_df[["networkID"]], on="downstream_id")
    .join(network_miles, on="networkID")
    .rename(columns={"networkID": "downNetID", "miles": "DownstreamMiles"})[
        ["downNetID", "DownstreamMiles"]
    ]
)
barriers = barriers.join(downstream_networks)

# Absolute gain is minimum of upstream or downstream miles
barriers["AbsoluteGainMi"] = barriers[["UpstreamMiles", "DownstreamMiles"]].min(axis=1)
barriers.upNetID = barriers.upNetID.fillna(0).astype("uint32")
barriers.downNetID = barriers.downNetID.fillna(0).astype("uint32")


barriers.to_csv("barriers_network.csv", index_label="joinID")

# TODO: if downstream network extends off this HUC, it will be null in the above and AbsoluteGainMin will be wrong

##################### Dissolve networks on networkID ########################
network_ids = network_stats.index

columns = ["networkID", "geometry"] + list(network_stats.columns)
networks = gp.GeoDataFrame(columns=columns, geometry="geometry", crs=flowlines.crs)

network_df = network_df.set_index("networkID", drop=False)

# join in network stats
for id in network_ids:
    stats = network_stats.loc[id]

    geometries = network_df.loc[id].geometry
    # converting to list is very inefficient but otherwise
    # we get an error in shapely internals
    if isinstance(geometries, gp.GeoSeries):
        geometry = MultiLineString(geometries.values.tolist())
    else:
        geometry = MultiLineString([geometries])

    values = [id, geometry] + [stats[c] for c in network_stats.columns]
    networks.loc[id] = gp.GeoSeries(values, index=columns)

print("Writing dissolved network shapefile")
networks.to_file("network.shp", driver="ESRI Shapefile")
networks.drop(columns=["geometry"]).to_csv("network.csv", index=False)


print("All done in {:.2f}".format(time() - start))

