"""

Note: line geometries always start from upstream end.

"""


import os
from time import time

import geopandas as gp
import pandas as pd
import numpy as np
from shapely.geometry import Point

from line_utils import calculate_sinuosity, cut_line_at_points

# from utils import generate_id

EPS = (
    1e-6
)  # if points are within this distance of start or end coordinate, nothing is cut

CRS = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

HUC4 = "0602"
data_dir = "data/src/tmp/{}".format(HUC4)
os.chdir(data_dir)

start = time()

print("Reading flowline data")
flowlines = gp.read_file("flowline.shp").set_index(["lineID"], drop=False)
print("{} original segments".format(len(flowlines)))

next_segment_id = flowlines.index.max() + 1

copy_cols = list(
    set(flowlines.columns).difference({"lineID", "geometry", "length", "sinuosity"})
)


join_df = pd.read_csv("connections.csv")
updated_joins = join_df.copy()

# Read in snapped dams and waterfalls, and merge them
# TODO: merge them before getting here
print("Reading snapped dams and waterfalls")
barriers = pd.read_csv("barriers.csv")
# drop any not snapped to the network
barriers = barriers.loc[~barriers.NHDPlusID.isnull()].copy()
barriers.lineID = barriers.lineID.astype("uint64")
geometry = [Point(xy) for xy in zip(barriers.x, barriers.y)]
barriers = gp.GeoDataFrame(barriers, geometry=geometry, crs=CRS)

segments_with_barriers = flowlines.loc[flowlines.index.isin(barriers.lineID.unique())]


# create container for new geoms
new_flowlines = gp.GeoDataFrame(
    columns=flowlines.columns, crs=flowlines.crs, geometry="geometry"
)

# create join table for barriers
barrier_joins = []

# Loop over all segments that have barriers
print("Cutting in {} barriers".format(len(barriers)))

for idx, row in segments_with_barriers.iterrows():
    # print("-----------------------\n\nlineID", idx)

    # Find upstream and downstream segments
    upstream_ids = join_df.loc[join_df.downstream_id == idx]
    downstream_ids = join_df.loc[join_df.upstream_id == idx]

    # Barriers on this line
    points = barriers.loc[barriers.lineID == idx].copy()

    # ordinate the barriers by their projected distance on the line
    # Order this so we are always moving from upstream end to downstream end
    line = row.geometry
    length = line.length
    points["linepos"] = points.geometry.apply(lambda p: line.project(p))
    points.sort_values("linepos", inplace=True, ascending=True)

    # by definition, splits must occur after the first coordinate in the line and before the last coordinate
    split_points = points.loc[
        (points.linepos > EPS) & (points.linepos < (length - EPS))
    ]

    segments = []
    if len(split_points):
        lines = cut_line_at_points(line, split_points.geometry)
        num_segments = len(lines)
        ids = list(range(next_segment_id, next_segment_id + num_segments))
        next_segment_id += num_segments

        # make id, segment pairs
        segments = list(zip(ids, lines))

        # add these to flowlines
        for i, (id, segment) in enumerate(segments):
            columns = copy_cols + ["length", "sinuosity", "geometry", "lineID"]
            values = [row[c] for c in copy_cols] + [
                segment.length,
                calculate_sinuosity(segment),
                segment,
                id,
            ]
            new_flowlines.loc[id] = gp.GeoSeries(values, index=columns)

            if i < num_segments - 1:
                # Update the barrier so that it has the correct segment
                barrier = split_points.iloc[i]
                # name = index in this case
                barriers.loc[barrier.name, "lineID"] = id

                # add a join for this barrier
                barrier_joins.append(
                    {
                        "NHDPlusID": row.NHDPlusID,
                        "joinID": barrier.joinID,
                        "upstream_id": id,
                        "downstream_id": ids[i + 1],
                    }
                )

        # update upstream nodes to set first segment as their new downstream
        # update downstream nodes to set last segment as their new upstream
        updated_joins.loc[upstream_ids.index, "downstream_id"] = ids[0]
        updated_joins.loc[downstream_ids.index, "upstream_id"] = ids[-1]

        # add joins for everything after first node
        new_joins = [
            {
                "upstream_id": ids[i],
                "downstream_id": id,
                "upstream": np.nan,
                "downstream": np.nan,
            }
            for i, id in enumerate(ids[1:])
        ]
        updated_joins = updated_joins.append(new_joins, ignore_index=True)

    # If barriers are at the downstream-most point or upstream-most point
    us_points = points.loc[points.linepos <= EPS]
    ds_points = points.loc[points.linepos >= (length - EPS)]

    # Handle any points on the upstream or downstream end of line
    if len(us_points):
        # Create a record for each that has downstream set to the first segment if any, or
        # NHDPlusID of this segment
        # Do this for every upstream segment (if there are multiple upstream nodes)
        downstream_id = segments[0][0] if segments else idx
        for _, barrier in us_points.iterrows():
            for _, upstream in upstream_ids.iterrows():
                barrier_joins.append(
                    {
                        "NHDPlusID": row.NHDPlusID,
                        "joinID": barrier.joinID,
                        "upstream_id": upstream.upstream_id,
                        "downstream_id": downstream_id,
                    }
                )

    if len(ds_points):
        # Create a record for each that has upstream set to the last segment if any, or
        # NHDPlusID of this segment
        # Do this for every downstream segment (if there are multiple downstream nodes)
        upstream_id = segments[-1][0] if segments else idx
        for _, barrier in ds_points.iterrows():
            for _, downstream in downstream_ids.iterrows():
                barrier_joins.append(
                    {
                        "NHDPlusID": row.NHDPlusID,
                        "joinID": barrier.joinID,
                        "upstream_id": upstream_id,
                        "downstream_id": downstream.downstream_id,
                    }
                )


# Drop all segments replaced by new segments
flowlines = flowlines.drop(
    flowlines.loc[flowlines.NHDPlusID.isin(new_flowlines.NHDPlusID)].index
)
flowlines = flowlines.append(new_flowlines, sort=False)
print("Final number of segments", len(flowlines))

barriers.to_csv("updated_barriers.csv", index=False)

barrier_joins = pd.DataFrame(
    barrier_joins, columns=["NHDPlusID", "joinID", "upstream_id", "downstream_id"]
)

print("Writing join tables")
barrier_joins.to_csv("barrier_joins.csv", index=False)
updated_joins.to_csv("updated_joins.csv", index=False)

print("Writing split flowlines shp")
flowlines.NHDPlusID = flowlines.NHDPlusID.astype("float64")
flowlines.to_file("split_flowlines.shp", driver="ESRI Shapefile")

print("Writing split flowlines CSV")
flowlines.drop(columns=["geometry"]).to_csv("split_flowlines.csv", index=False)

barriers.to_file("updated_barriers.shp", driver="ESRI Shapefile")

print("Done in {:.2f}".format(time() - start))
