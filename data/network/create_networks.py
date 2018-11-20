import os
from time import time

import geopandas as gp
import pandas as pd

from network_utils import calculate_upstream_network

# root_ids = (15001600076917, 15001600062310)
# start_id = 15001600076917
# start_id = 15001600112457
# start_id = 15001600063046
# start_id = 15001600062310
# root_ids = (15001600062310,)
# dam_segments = set()  # {15001600000190, 15001600046755}


HUC4 = "0602"
data_dir = "data/src/tmp/{}".format(HUC4)
os.chdir(data_dir)

start = time()

print("Reading flowline data")
df = pd.read_csv("flowline.csv").set_index("id")
join_df = pd.read_csv("connections.csv")

# Read in snapped dams
print("Reading snapped dams")
dams_df = pd.read_csv("snapped_dams.csv")[["NHDPlusID"]]
dams_df = dams_df.loc[~dams_df.NHDPlusID.isnull()].copy()
dams_df.NHDPlusID = dams_df.NHDPlusID.astype("uint64")

# Read in snapped waterfalls
print("Reading snapped waterfalls")
wf_df = pd.read_csv("snapped_waterfalls.csv")[["NHDPlusID"]]
wf_df = wf_df.loc[~wf_df.NHDPlusID.isnull()].copy()
wf_df.NHDPlusID = wf_df.NHDPlusID.astype("uint64")

# Union dam and natural barriers together
barrier_segments = set(dams_df.NHDPlusID.unique()).union(wf_df.NHDPlusID.unique())


get_upstream_ids = lambda id: join_df.loc[join_df.downstream == id].upstream
has_multiple_downstreams = (
    lambda id: len(join_df.loc[join_df.upstream == id].downstream) > 0
)

# Create networks from all terminal nodes (no downstream nodes) up to origins or dams (but not including dam segments)
root_ids = join_df.loc[join_df.downstream == 0].upstream
for start_id in root_ids:
    print("Calculating upstream network: {}".format(start_id))
    network = calculate_upstream_network(
        start_id,
        get_upstream_ids,
        has_multiple_downstreams,
        stop_segments=barrier_segments.copy(),
    )

    rows = df.index.isin(network)
    df.loc[rows, "networkID"] = start_id
    df.loc[rows, "networkType"] = 0

    print("nonbarrier upstream network has {} segments".format(len(network)))

# Create networks UPSTREAM of barrier_segments
for start_id in barrier_segments:
    # print("Calculating network upstream of dam: {}".format(start_id))
    network = calculate_upstream_network(
        start_id,
        get_upstream_ids,
        has_multiple_downstreams,
        stop_segments=barrier_segments.copy(),
    )

    # remove the dam segment itself from the network but preserve full upstream network
    network.pop(0)

    rows = df.index.isin(network)
    df.loc[rows, "networkID"] = start_id
    df.loc[rows, "networkType"] = 0
    print("barrier upstream network has {} segments".format(len(network)))


network_df = df.loc[~df.networkID.isnull(), ["networkID"]].astype("uint64")
network_df.to_csv("network.csv", index_label="id")
print("Network traversal done in {:.2f}".format(time() - start))


start = time()
print("Reading flowline shapefile")
geo_df = gp.read_file("flowline.shp")
geo_df["id"] = geo_df.NHDPlusID.astype("uint64")
geo_df = geo_df.set_index(["id"])

geo_df = geo_df.join(network_df, how="inner")
geo_df.networkID = geo_df.networkID.astype(
    "float64"
)  # needs to be float64 or doesn't get converted properly for SHP


print("Writing network shapefile")
geo_df.to_file("network.shp", driver="ESRI Shapefile")

print("Done in {:.2f}".format(time() - start))
