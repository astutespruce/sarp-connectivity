"""

Remove all segments where StreamOrde == StreamCalc AND FlowDir is not null and FType != 566

"""


import geopandas as gp
import pandas as pd
from shapely.geometry import LineString, MultiLineString

filename = "NHDPLUS_H_0307_HU4_GDB.gdb"
start_id = 15001600062310


# def to2D(geometry):
#     if geometry.type == "MultiLineString":
#         return MultiLineString([LineString(c[:2] for c in g.coords) for g in geometry])
#     return LineString(c[:2] for c in geometry.coords)


# # Read in data and convert to data frame (no need for geometry)
# print("Reading flowlines")
# df = gp.read_file("data/src/tmp/{}".format(filename), layer="NHDFlowline")

# df = df[["NHDPlusID", "FlowDir", "FType", "FCode", "geometry"]].rename(
#     columns={"NHDPlusID": "id"}
# )
# df.id = df.id.astype("uint64")

# print("Converting geometry to 2D")
# df.geometry = df.geometry.apply(to2D)

# print("Writing flowlines to 2D shapefile")
# df.to_file("data/src/tmp/flowline.shp", driver="ESRI Shapefile")

# df = df.set_index(["id"])


# # Read in VAA and convert to data frame
# # NOTE: not all records in Flowlines have corresponding records in VAA
# print("Reading VAA table")
# vaa_df = gp.read_file("data/src/tmp/{}".format(filename), layer="NHDPlusFlowlineVAA")[
#     ["NHDPlusID", "StreamLeve", "StreamOrde", "StreamCalc"]
# ]
# vaa_df.NHDPlusID = vaa_df.NHDPlusID.astype("uint64")
# vaa_df = vaa_df.set_index(["NHDPlusID"])

# df = df.join(vaa_df, how="inner")  # drop any segments where we don't have info

# df.drop(columns=["geometry"]).to_csv("data/src/tmp/flowlines.csv", index_label="id")

# # Filter out loops - this is not working properly
# # loops = (df.StreamLeve == df.StreamCalc) & ~df.FlowDir.isnull() & (df.FType != 566)
# # df = df[~loops]

# # write out a copy to verify
# # df.head(100).to_file("data/src/tmp/test.shp", driver="ESRI Shapefile")

# Flow has the connections between segments
# Upstream is the upstream side of the connection, which would actually correspond to the downstream node of the upstream segment
# print("Reading flow table")
# join_df = gp.read_file("data/src/tmp/{}".format(filename), layer="NHDPlusFlow")[
#     ["FromNHDPID", "ToNHDPID"]
# ].rename(columns={"FromNHDPID": "upstream", "ToNHDPID": "downstream"})
# join_df.upstream = join_df.upstream.astype("uint64")
# join_df.downstream = join_df.downstream.astype("uint64")

# join_df.to_csv("data/src/tmp/join.csv", index=False)

