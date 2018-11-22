"""
TODO: this is not working properly, the adjacency matrix created from cutting network isn't correct

"""


import os
from time import time

import geopandas as gp
import pandas as pd

from network_utils import calculate_upstream_network

HUC4 = "0602"
data_dir = "data/src/tmp/{}".format(HUC4)
os.chdir(data_dir)

start = time()

print("Reading flowline data")
flowlines = pd.read_csv("split_flowlines.csv").set_index("lineID", drop=False)
join_df = pd.read_csv(
    "updated_joins.csv", dtype={"upstream_id": "uint32", "downstream_id": "uint32"}
)[["upstream_id", "downstream_id"]]

print("Reading barriers data")
barriers = pd.read_csv(
    "barrier_joins.csv", dtype={"upstream_id": "uint32", "downstream_id": "uint32"}
)[["upstream_id", "downstream_id"]]

# remove any origin segments
barrier_segments = set(barriers.upstream_id.unique()).difference({0})

get_upstream_ids = lambda id: join_df.loc[join_df.downstream_id == id].upstream_id
has_multiple_downstreams = lambda id: len(join_df.loc[join_df.upstream_id == id]) > 0

# Create networks from all terminal nodes (no downstream nodes) up to origins or dams (but not including dam segments)
root_ids = join_df.loc[join_df.downstream_id == 0].upstream_id
print(
    "Starting non-barrier functional network creation for {} origin points".format(
        len(root_ids)
    )
)
for start_id in root_ids:
    print("Calculating upstream network: {}".format(start_id))
    network = calculate_upstream_network(
        start_id,
        get_upstream_ids,
        has_multiple_downstreams,
        stop_segments=barrier_segments.copy(),
    )

    rows = flowlines.index.isin(network)
    flowlines.loc[rows, "networkID"] = start_id
    flowlines.loc[rows, "networkType"] = 0

    print("nonbarrier upstream network has {} segments".format(len(network)))

print(
    "Starting barrier functional network creation for {} barriers".format(
        len(barrier_segments)
    )
)
for start_id in barrier_segments:
    # print("Calculating network upstream of dam: {}".format(start_id))
    network = calculate_upstream_network(
        start_id,
        get_upstream_ids,
        has_multiple_downstreams,
        stop_segments=barrier_segments.copy(),
    )

    rows = flowlines.index.isin(network)
    flowlines.loc[rows, "networkID"] = start_id
    flowlines.loc[rows, "networkType"] = 1
    print("barrier upstream network has {} segments".format(len(network)))


# drop anything that didn't get assigned a network
network_df = flowlines.loc[~flowlines.networkID.isnull()].copy()
network_df.networkID = network_df.networkID.astype("uint32")
network_df.networkType = network_df.networkType.astype("uint8")
network_df.to_csv("split_network.csv", index=False)
print("Network traversal done in {:.2f}".format(time() - start))

start = time()
print("Reading flowline shapefile")
geo_df = gp.read_file("split_flowlines.shp")
geo_df.lineID = geo_df.lineID.astype("uint32")
geo_df.set_index("lineID", inplace=True, drop=False)

geo_df = geo_df.join(network_df[["networkID"]], how="inner")

print("Writing network shapefile")
geo_df.to_file("split_network.shp", driver="ESRI Shapefile")

print("Done in {:.2f}".format(time() - start))
