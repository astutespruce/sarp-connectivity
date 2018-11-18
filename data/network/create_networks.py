import os
from time import time

import geopandas as gp
import pandas as pd
import numpy as np

from network_utils import calculate_upstream_network

# root_ids = (15001600076917, 15001600062310)
# start_id = 15001600076917
# start_id = 15001600112457
# start_id = 15001600063046
# start_id = 15001600062310

HUC4 = "0307"
data_dir = "data/src/tmp/{}".format(HUC4)
os.chdir(data_dir)

start = time()

print("Reading input data")
dam_segments = set()  # {15001600000190, 15001600046755}
df = pd.read_csv("flowline.csv").set_index("id")
join_df = pd.read_csv("connections.csv")


root_ids = join_df.loc[join_df.downstream == 0].upstream[:10]


get_upstream_ids = lambda id: join_df.loc[join_df.downstream == id].upstream
has_multiple_downstreams = (
    lambda id: len(join_df.loc[join_df.upstream == id].downstream) > 0
)

for start_id in root_ids:
    print("Calculating upstream network: {}".format(start_id))
    network = calculate_upstream_network(
        start_id, get_upstream_ids, has_multiple_downstreams, stop_segments=dam_segments
    )

    df.loc[df.index.isin(network), "networkID"] = start_id
    print("network has {} segments".format(len(network)))

network_df = df.loc[~df.networkID.isnull(), ["networkID"]].astype("uint64")
network_df.to_csv("network.csv", index_label="id")
print("Network traversal done in {:.2f}".format(time() - start))


start = time()
print("Reading flowline shapefile")
geo_df = gp.read_file("flowline.shp")
geo_df["id"] = geo_df.NHDPlusID.astype("uint64")
geo_df = geo_df.set_index(["id"])

geo_df = geo_df.join(network_df, how="inner")

print("Writing network shapefile")
geo_df.to_file("network.shp", driver="ESRI Shapefile")

print("Done in {:.2f}".format(time() - start))
