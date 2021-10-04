from pathlib import Path
from time import time

import geopandas as gp
import numpy as np
import pandas as pd
import pygeos as pg
from pyogrio import write_dataframe

from analysis.lib.geometry.lines import (
    vertex_angle,
    perpindicular_distance,
    segment_length,
)

# Extract no more than 50 vertices on each side for complex waterbodies;
# 50 is arbitrary max number of vertices to extract on each side, could be less
MAX_SIDE_PTS = 50
MAX_STRAIGHT_ANGLE = 10
MIN_DAM_WIDTH = 30  # meters; min width straight line must be in order to consider it a likely dam face
MAX_WIDTH_RATIO = 0.25  # the total length of the extracted dam can be no longer than this amount of the total ring length
MAX_GAP = (
    5  # meters; max space between 2 adjacent straight lines to consider them connected
)
MAX_DRAIN_DIST = 5  # meters; distance between line segments and drain
MIN_AREA = 10
MAX_PERPINDICULAR_DISTANCE = 2  # meters; maximum perpindicular distance of a nearly straight vertex that can be dropped


nhd_dir = Path("data/nhd/clean")


def find_dam_faces(huc2):
    wb = gp.read_feather(nhd_dir / huc2 / "waterbodies.feather").set_index("wbID")
    drains = gp.read_feather(
        nhd_dir / huc2 / "waterbody_drain_points.feather"
    ).set_index("drainID")

    # convert to plain dataframe
    joined = pd.DataFrame(
        drains[["geometry", "wbID"]].join(wb.geometry.rename("waterbody"), on="wbID",)
    )
    joined["geometry"] = joined.geometry.values.data
    joined["waterbody"] = joined.waterbody.values.data

    start = time()

    out = []
    for drainID, row in joined.iterrows():
        segments = find_dam_face_from_waterbody(row.waterbody, row.geometry)
        for segment in segments:
            out.append({"geometry": segment, "drainID": drainID})

    df = (
        gp.GeoDataFrame(out, geometry="geometry", crs=wb.crs)
        .set_index("drainID")
        .join(drains.drop(columns=["geometry"]))
    )

    print(f"Elapsed {time() - start:,.2f}s")
    write_dataframe(df, "/tmp/extracted_dams.fgb")


def find_dam_face_from_waterbody(waterbody, drain_pt):
    ring = pg.get_exterior_ring(pg.normalize(waterbody))
    total_length = pg.length(ring)
    num_pts = pg.get_num_points(ring) - 1  # drop closing coordinate
    vertices = pg.get_point(ring, range(num_pts))

    ### Extract line segments that are no more than 1/2 coordinates of polygon
    # starting from the vertex nearest the drain
    # note: lower numbers are to the right
    tree = pg.STRtree(vertices)
    ix = tree.nearest(drain_pt)[1][0]
    side_width = min(num_pts // 2, MAX_SIDE_PTS)
    left_ix = ix + side_width
    right_ix = ix - side_width

    # extract these as a left-to-write line
    pts = vertices[max(right_ix, 0) : min(num_pts, left_ix)][::-1]
    if left_ix > num_pts:
        pts = np.append(vertices[0 : left_ix - num_pts][::-1], pts)

    if right_ix < 0:
        pts = np.append(pts, vertices[num_pts + right_ix : num_pts][::-1])

    coords = pg.get_coordinates(pts)

    # FIXME: remove
    # write_geoms([pg.linestrings(coords)], "/tmp/line.fgb", crs=wb.crs)

    ### Loop up to 5 times or until the min angle of retained points
    # is greater than MAX_STRAIGHT_ANGLE or there are only the endpoints
    keep_coords = coords
    keep_ix = np.arange(len(coords))

    # print(f"before simplify, {len(keep_ix):,} coords")

    for i in range(0, 5):
        # print(f"pass {i+1}: removing low angle vertices")
        a = keep_coords[:-2]
        b = keep_coords[1:-1]
        c = keep_coords[2:]

        angles = np.abs(vertex_angle(b, a, c) - 180)
        distance = perpindicular_distance(b, a, c)

        # Drop all straight interior points that are not too far away
        keep_pts = (angles >= MAX_STRAIGHT_ANGLE) | (
            distance >= MAX_PERPINDICULAR_DISTANCE
        )

        # if there are no interior points to drop, then stop
        if (~keep_pts).sum() == 0:
            break

        # Keep the endpoints too
        keep_pts = np.insert(keep_pts, [0, len(a)], True)
        keep_ix = keep_ix[keep_pts]
        keep_coords = coords[keep_ix]

    # print(f"after simplify, {len(keep_ix):,} coords")

    # FIXME: remove
    # write_geoms([pg.linestrings(keep_coords)], f'/tmp/straight.fgb', crs=wb.crs)

    ### Calculate the length of each run and drop any that are not sufficiently long
    lengths = segment_length(keep_coords)
    ix = (lengths >= MIN_DAM_WIDTH) & (lengths / total_length < MAX_WIDTH_RATIO)

    # keep short gaps between 2 adjacent longer straight segments
    a = lengths[:-2]
    b = lengths[1:-1]
    c = lengths[2:]
    keep_gaps = (lengths[1:-1] < MAX_GAP) & ix[:-2] & ix[2:]
    ix[1:-1] = ix[1:-1] | keep_gaps

    pairs = np.dstack([keep_ix[:-1][ix], keep_ix[1:][ix]])[0]

    # since ranges are ragged, we have to do this in a loop instead of vectorized
    segments = []
    for start, end in pairs:
        segments.append(pg.linestrings(coords[start : end + 1]))

    segments = np.array(segments)

    # only keep the segments that are close to the drain
    ix = pg.intersects(segments, pg.buffer(drain_pt, MAX_DRAIN_DIST))

    return segments[ix]

    # last = -1
    # segments = []
    # i = 0
    # segment_coords = []
    # while i < len(pairs):
    # start, end = pairs[i]
    # seg = coords[start : end + 1]
    # if start == last:
    #     # don't add duplicate coord again
    #     segment_coords = np.concatenate([segment_coords, seg[1:]])
    # else:
    #     # add the previous segment
    #     if len(segment_coords):
    #         segments.append(pg.linestrings(segment_coords))

    #     segment_coords = seg

    # last = end
    # i += 1
