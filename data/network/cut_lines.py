import os
from time import time

import geopandas as gp
import pandas as pd
from shapely.geometry import Point

from line_utils import cut_line, calculate_sinuosity
from utils import generate_id


CRS = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

HUC4 = "0602"
data_dir = "data/src/tmp/{}".format(HUC4)
os.chdir(data_dir)

start = time()

print("Reading flowline data")
df = gp.read_file("flowline.shp")
df.NHDPlusID = df.NHDPlusID.astype("uint64").astype("str")
df.set_index(["NHDPlusID"], inplace=True, drop=False)

join_df = pd.read_csv("connections.csv")
join_df.upstream = join_df.upstream.astype("str")
join_df.downstream = join_df.downstream.astype("str")

network_df = pd.read_csv("network.csv").set_index(["id"])

# Read in snapped dams and waterfalls, and merge them
print("Reading snapped dams and waterfalls")
dams = pd.read_csv("snapped_dams.csv")
dams = dams.loc[~dams.NHDPlusID.isnull()].copy()
dams["dam"] = dams.UniqueID

wf = pd.read_csv("snapped_waterfalls.csv")
wf = wf.loc[~wf.NHDPlusID.isnull()].copy()
wf["waterfall"] = "wf{}".format(wf.id)

barriers = dams[["NHDPlusID", "dam", "snap_x", "snap_y"]].append(
    wf[["NHDPlusID", "waterfall"]], ignore_index=True, sort=False
)
barriers.NHDPlusID = barriers.NHDPlusID.astype("uint64").astype("str")
geometry = [Point(xy) for xy in zip(barriers.snap_x, barriers.snap_y)]
barriers = gp.GeoDataFrame(barriers, geometry=geometry, crs=CRS)

# create container for new geoms
new_flowlines = gp.GeoDataFrame(columns=df.columns, crs=df.crs, geometry="geometry")

# Union dam and natural barriers together, and select out associated segments
df = df.loc[df.index.isin(barriers.NHDPlusID.unique())].copy()

for idx, row in df.iterrows():
    break

# Find upstream and downstream segments
upstream_ids = join_df.loc[join_df.downstream == row.NHDPlusID]
downstream_ids = join_df.loc[join_df.upstream == row.NHDPlusID]


# FIXME: this approach only works if the next upstream segment DOES NOT have barriers
# segment_upstream_networkID = row.NHDPlusID
# based on how we defined networks, the upstream network upstream
# of this segment is always given the NHDPlusID of this segment

# FIXME: this approach only works if the next downstream segment DOES NOT have barriers

# segment_downstream_networkID # TODO
# barriers.loc[barriers.NHDPlusID == downstream_segment]


line = row.geometry
length = line.length

# Barriers on this line
points = barriers.loc[barriers.NHDPlusID == idx].copy()

# ordinate the barriers by their projected distance on the line
points["linepos"] = points.geometry.apply(lambda p: line.project(p))
points.sort_values("linepos", inplace=True)

# set first point upstream


start_points = points.loc[points.linepos == 0]
end_points = points.loc[points.linepos == length]

# by definition, splits must occur after the first coordinate in the line and before the last coordinate
split_points = points.loc[(points.linepos) > 0 & (points.linepos < length)]

if len(split_points):
    new_segments = []
    remainder = line
    counter = 1
    prev_pt_idx = None
    for pt_idx, split_point in split_points.iterrows():
        is_dam = not pd.isnull(split_point.dam)
        segment, remainder = cut_line(remainder, split_point.geometry)
        segment_id = generate_id(row.NHDPlusID, counter)
        new_segments.append(segment_id)
        print("new segment id: {}".format(segment_id))
        counter += 1

        new_flowlines.loc[segment_id, "SplitID"] = segment_id
        new_flowlines.loc[segment_id, "geometry"] = segment
        new_flowlines.loc[segment_id, "length"] = segment.length
        new_flowlines.loc[segment_id, "sinuosity"] = calculate_sinuosity(segment)

        # add barrier info
        new_flowlines.loc[segment_id, "barrier_id"] = (
            split_point.dam if is_dam else split_point.waterfall
        )
        new_flowlines.loc[segment_id, "barrier_type"] = "dam" if is_dam else "waterfall"

        # copy all other cols across
        for column in set(df.columns).difference({"geometry", "length", "sinuosity"}):
            new_flowlines.loc[segment_id, column] = row[column]

        # update the barriers to track upstream / downstram segments.  NOT YET COMPLETE!!
        barriers.loc[pt_idx, "upstream_seg"] = segment_id
        if prev_pt_idx is not None:
            barriers.loc[prev_pt_idx, "downstream_seg"] = segment_id
        prev_pt_idx = pt_idx

    # update upstream nodes to set first segment as their new downstream
    join_df.loc[upstream_ids.index, "downstream"] = new_segments[0]

    # update downstream nodes to set last segment as their new upstream
    join_df.loc[downstream_ids.index, "upstream"] = new_segments[-1]

    # add joins for everything after first
    new_joins = []
    for i, segment_id in enumerate(new_segments):
        new_joins.append({"upstream": new_segments[i], "downstream": segment_id})

    join_df = join_df.append(new_joins, ignore_index=True)


# serialize data to make sure we are on the right track
join_df.to_csv("updated_joins.csv", index=False)

# new_flowines.barrier_id = new_flowines.barrier_id.astype("int")
new_flowlines.to_file("split_flowlines.shp", driver="ESRI Shapefile")
new_flowlines.drop(columns=["geometry"]).to_csv("split_flowlines.csv", index_label="id")

print("Done in {:.2f}".format(time() - start))

# for each split segment, we want to know the id of the barrier so that we can add this as the upstream segment ID for that barrier
# if there was a previous split, then we want that previous barrier and set this segment ID as the downstream segment for that barrier

# if there is just one barrier, then we have 3 cases:
# - no new segment: barrier is on last coordinate of line
# - split segment into an upstream and downstream part


# if there is more than one barrier


# remaining = line
# for pt_idx, point in points.iterrows():
#     # TODO: if any barriers are very close to each other, snap them to the same coordinate

#     if point.project <= 0:
#         # = first coordinate on the line, so the upstream network is the upstream network of this segment

#     elif point.project >= line.length:
#         # last coordinate on the line, so the downstream network is the

#     else:
#         # TODO: do we have the upstream vs downstream directions correct here?
#         # How do we know what direction they are going?
#         upstream, downstream = split


# Create a file cut_segments.csv
# NHDPlusID, networkID, length, sinuosity, sizeclass

# calculate network ID such that it is either the ID upstream of this segment (= this NHDplusID), the network dow


# Create a file that has barrier and upstream and downstream network IDs
