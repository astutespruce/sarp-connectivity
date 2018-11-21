"""

Note: line geometries always start from upstream end.

"""


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
# df["remove"] = False

join_df = pd.read_csv("connections.csv")
join_df.upstream = join_df.upstream.astype("str")
join_df.downstream = join_df.downstream.astype("str")

updated_joins = join_df.copy()

# network_df = pd.read_csv("network.csv").set_index(["id"])

# Read in snapped dams and waterfalls, and merge them
# TODO: merge them before getting here
print("Reading snapped dams and waterfalls")
dams = pd.read_csv("snapped_dams.csv")
dams = dams.loc[~dams.NHDPlusID.isnull()].copy()
dams["id"] = dams.UniqueID
dams["kind"] = "dam"

wf = pd.read_csv("snapped_waterfalls.csv")
wf = wf.loc[~wf.NHDPlusID.isnull()].copy()
wf["id"] = wf.id.apply(lambda id: "wf{}".format(id))
wf["kind"] = "waterfall"

barriers = dams[["NHDPlusID", "id", "kind", "snap_x", "snap_y"]].append(
    wf[["NHDPlusID", "id", "kind", "snap_x", "snap_y"]], ignore_index=True, sort=False
)
barriers.NHDPlusID = barriers.NHDPlusID.astype("uint64").astype("str")
geometry = [Point(xy) for xy in zip(barriers.snap_x, barriers.snap_y)]
barriers = gp.GeoDataFrame(barriers, geometry=geometry, crs=CRS)


# create container for new geoms
new_flowlines = gp.GeoDataFrame(columns=df.columns, crs=df.crs, geometry="geometry")

# create join table for barriers
barrier_joins = []

# Loop over all segments that have barriers
print("Cutting in {} barriers".format(len(barriers)))
for idx, row in df.loc[df.index.isin(barriers.NHDPlusID.unique())].iterrows():
    # print("-----------------------\n\nNHDPlusID", idx)

    line = row.geometry
    length = line.length

    # Find upstream and downstream segments
    upstream_ids = join_df.loc[join_df.downstream == row.NHDPlusID]
    downstream_ids = join_df.loc[join_df.upstream == row.NHDPlusID]

    # Barriers on this line
    points = barriers.loc[barriers.NHDPlusID == idx].copy()

    # ordinate the barriers by their projected distance on the line
    # Reorder this so we are always moving from upstream end to downstream end
    points["linepos"] = points.geometry.apply(lambda p: line.project(p))
    points.sort_values("linepos", inplace=True, ascending=True)

    # If barriers are at the downstream-most point or upstream-most point
    us_points = points.loc[points.linepos <= 0]
    ds_points = points.loc[points.linepos >= length]

    # by definition, splits must occur after the first coordinate in the line and before the last coordinate
    split_points = points.loc[(points.linepos > 0) & (points.linepos < length)]

    segments = []
    if len(split_points):
        remainder = line
        counter = 1

        # Iterate through the splits moving in the DOWNSTREAM direction
        for _, barrier in split_points.iterrows():
            segment, remainder = cut_line(remainder, barrier.geometry)
            segment_id = generate_id(row.NHDPlusID, counter)
            segments.append([segment_id, segment, barrier])
            counter += 1

        # add the last segment
        remainder_id = generate_id(row.NHDPlusID, counter)
        segments.append([remainder_id, remainder, None])

        num_segments = len(segments)

        # write the new records
        for i, (segment_id, segment, barrier) in enumerate(segments):
            copy_cols = list(
                set(df.columns).difference({"geometry", "length", "sinuosity"})
            )
            columns = copy_cols + ["length", "sinuosity"]
            values = [row[c] for c in copy_cols] + [
                segment.length,
                calculate_sinuosity(segment),
            ]
            new_flowlines.loc[segment_id, columns] = values

            # geometry has to be written individually
            new_flowlines.loc[segment_id, "geometry"] = segment

            # add barrier info - barrier is None for last segment
            if barrier is not None:
                # Add segment info to the barriers join table
                barrier_joins.append(
                    {
                        "NHDPlusID": idx,
                        "id": barrier.id,
                        "upstream": segment_id,
                        "downstream": segments[i + 1][0],
                    }
                )

        # update upstream nodes to set first segment as their new downstream
        # update downstream nodes to set last segment as their new upstream
        updated_joins.loc[upstream_ids.index, "downstream"] = segments[0][0]
        updated_joins.loc[downstream_ids.index, "upstream"] = segments[-1][0]

        # add joins for everything after first node
        new_joins = [
            {"upstream": segments[i][0], "downstream": segment_id}
            for i, (segment_id, _, _) in enumerate(segments[1:])
        ]
        updated_joins = updated_joins.append(new_joins, ignore_index=True)

    # Handle any points on the upstream or downstream end of line
    if len(us_points):
        # Create a record for each that has downstream set to the first segment if any, or
        # NHDPlusID of this segment
        # Do this for every upstream segment (if there are multiple upstream nodes)
        downstream_id = segments[0] if segments else idx
        for _, barrier in us_points.iterrows():
            for _, upstream in upstream_ids.iterrows():
                barrier_joins.append(
                    {
                        "NHDPlusID": idx,
                        "id": barrier.id,
                        "upstream": upstream.upstream,
                        "downstream": downstream_id,
                    }
                )

    if len(ds_points):
        # Create a record for each that has upstream set to the last segment if any, or
        # NHDPlusID of this segment
        # Do this for every downstream segment (if there are multiple downstream nodes)
        upstream_id = segments[-1] if segments else idx
        for _, barrier in ds_points.iterrows():
            for _, downstream in downstream_ids.iterrows():
                barrier_joins.append(
                    {
                        "NHDPlusID": idx,
                        "id": barrier.id,
                        "upstream": upstream_id,
                        "downstream": downstream.downstream,
                    }
                )

# Drop all segments replaced by new segments
df = df.drop(df.loc[df.NHDPlusID.isin(new_flowlines.NHDPlusID)].index)
df = df.append(new_flowlines, sort=False)
print("Final number of segments", len(df))

barrier_joins = pd.DataFrame(
    barrier_joins, columns=["NHDPlusID", "id", "upstream", "downstream"]
)

print("Writing join tables")
barrier_joins.to_csv("barrier_joins.csv", index=False)
updated_joins.to_csv("updated_joins.csv", index=False)

print("Writing split flowlines shp")
df.to_file("split_flowlines.shp", driver="ESRI Shapefile")

print("Writing split flowlines CSV")
df.drop(columns=["geometry"]).to_csv("split_flowlines.csv", index_label="id")

# barriers.to_file("barriers.shp", driver="ESRI Shapefile")

print("Done in {:.2f}".format(time() - start))
