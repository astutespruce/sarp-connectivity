import os
from time import time

import geopandas as gp
import pandas as pd
from shapely.geometry import MultiLineString

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


# Dissolve networks on networkID
start = time()
print("Aggregating flowlines to network geometries")
flowlines = gp.read_file("split_network.shp").set_index("networkID", drop=False)
flowlines = flowlines[["networkID", "geometry"]].join(stats_df)

network_ids = stats_df.index
# ['networkID', 'geometry', 'km', 'miles', 'sinuosity']
networks = gp.GeoDataFrame(
    columns=flowlines.columns, geometry="geometry", crs=flowlines.crs
)

copy_cols = list(set(flowlines.columns).difference({"networkID", "geometry"}))
print("copy cols", copy_cols)

# join in network stats
for id in network_ids:
    stats = stats_df.loc[id]

    geometries = flowlines.loc[id].geometry
    # converting to list is very inefficient but otherwise
    # we get an error in shapely internals
    if isinstance(geometries, gp.GeoSeries):
        geometry = MultiLineString(geometries.values.tolist())
    else:
        geometry = MultiLineString([geometries])

    columns = ["networkID", "geometry"] + copy_cols
    values = [id, geometry] + [stats[c] for c in copy_cols]
    networks.loc[id] = gp.GeoSeries(values, index=columns)

networks.to_file("network_dissolve.shp", driver="ESRI Shapefile")

print("Done in {:.2f}".format(time() - start))
