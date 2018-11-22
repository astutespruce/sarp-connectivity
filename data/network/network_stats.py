import os
from time import time

import geopandas as gp
import pandas as pd

HUC4 = "0602"
data_dir = "data/src/tmp/{}".format(HUC4)
os.chdir(data_dir)

start = time()

df = pd.read_csv(
    "split_network.csv", dtype={"lineID": "uint32", "networkID": "uint32"}
).set_index("lineID", drop=False)

# for every network, calc length-weighted sinuosity and sum length
sum_length_df = (
    df[["networkID", "length"]]
    .groupby(["networkID"])
    .sum()
    .reset_index()
    .set_index("networkID")
)
stats_df = df.join(sum_length_df, on="networkID", rsuffix="_total")
stats_df["wtd_sinuosity"] = stats_df.sinuosity * (
    stats_df.length / stats_df.length_total
)

stats_df = (
    stats_df[["networkID", "length_total", "wtd_sinuosity"]]
    .groupby(["networkID"])
    .sum()
    .reset_index()
    .set_index("networkID")
)

stats_df = stats_df.rename(
    columns={"length_total": "meters", "wtd_sinuosity": "sinuosity"}
)

# convert units
stats_df["km"] = stats_df.meters / 1000.0
stats_df["miles"] = stats_df.meters * 0.000621371

stats_df.to_csv(
    "network_stats.csv", columns=["km", "miles", "sinuosity"], index_label="networkID"
)

print("Done in {:.2f}".format(time() - start))
