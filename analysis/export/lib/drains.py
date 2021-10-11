from pathlib import Path
from time import time

import geopandas as gp
from numba.core.decorators import njit
import numpy as np
from numpy.lib.function_base import extract
import pandas as pd
import pygeos as pg
from pyogrio import write_dataframe
from tqdm.auto import tqdm


from analysis.lib.geometry.lines import segment_length
from analysis.lib.geometry.speedups.lines import (
    simplify_vw,
    extract_straight_segments,
)


from analysis.lib.geometry.io import write_geoms

# Extract no more than 50 vertices on each side for complex waterbodies;
# 50 is arbitrary max number of vertices to extract on each side, could be less
MAX_SIDE_PTS = 50
MAX_STRAIGHT_ANGLE = 10  # 180 degrees +/- this value is considered straight
MIN_TRIANGLE_AREA = 1  # m2; if angle is > MAX_STRAIGHT_ANGLE but less than MIN_TRIANGLE_AREA, these can be dropped
MAX_SIMPLIFY_AREA = 100  # m2 or total area of waterbody / 100, whichever is smaller
MAX_TRIANGLE_AREA_RATIO = (
    0.01  # do not drop triangles that are greater than 1% of polygon area
)
MIN_DAM_WIDTH = 30  # meters; min width straight line must be in order to consider it a likely dam face
MAX_WIDTH_RATIO = 0.45  # the total length of the extracted dam can be no longer than this amount of the total ring length
MAX_GAP = (
    5  # meters; max space between 2 adjacent straight lines to consider them connected
)
MAX_DRAIN_DIST = 1  # meters; distance between line segments and drain
MAX_PERPINDICULAR_DISTANCE = 2  # meters; maximum perpindicular distance of a nearly straight vertex that can be dropped
MIN_INTERIOR_DIST = 1  # meters; minimum distance drain must be from edge of segment for segment to be considered a dam


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

    index, segments = loop(
        joined.waterbody.values, joined.geometry.values, joined.index.values
    )

    # NOTE: this may have duplicate geometries where there are widely spaced drains on the same long waterbody edge
    df = gp.GeoDataFrame(
        {"geometry": segments, "width": pg.length(segments)}, index=index, crs=wb.crs
    ).join(drains.drop(columns=["geometry"]))
    df.index.name = "drainID"

    print(f"Elapsed {time() - start:,.2f}s")
    write_dataframe(df, "/tmp/extracted2.fgb")

    return df


def loop(waterbodies, drains, index):
    out_index = []
    out_segments = []
    for i in tqdm(range(len(index))):
        segments = find_dam_face_from_waterbody(waterbodies[i], drains[i])
        out_segments.extend(segments)
        out_index.extend([index[i]] * len(segments))

    return np.array(out_index), np.array(out_segments)


def find_dam_face_from_waterbody(waterbody, drain_pt):
    total_area = pg.area(waterbody)
    ring = pg.get_exterior_ring(pg.normalize(waterbody))
    total_length = pg.length(ring)
    num_pts = pg.get_num_points(ring) - 1  # drop closing coordinate
    vertices = pg.get_point(ring, range(num_pts))

    ### Extract line segments that are no more than 1/3 coordinates of polygon
    # starting from the vertex nearest the drain
    # note: lower numbers are to the right
    tree = pg.STRtree(vertices)
    ix = tree.nearest(drain_pt)[1][0]
    side_width = min(num_pts // 3, MAX_SIDE_PTS)
    left_ix = ix + side_width
    right_ix = ix - side_width

    # extract these as a left-to-write line;
    pts = vertices[max(right_ix, 0) : min(num_pts, left_ix)][::-1]
    if left_ix >= num_pts:
        pts = np.append(vertices[0 : left_ix - num_pts][::-1], pts)

    if right_ix < 0:
        pts = np.append(pts, vertices[num_pts + right_ix : num_pts][::-1])

    coords = pg.get_coordinates(pts)

    if len(coords) > 2:
        # first run a simplification process to extract the major shape and bends
        # then run the straight line algorithm
        simp_coords, simp_ix = simplify_vw(
            coords, min(MAX_SIMPLIFY_AREA, total_area / 100)
        )

        if len(simp_coords) > 2:
            keep_coords, ix = extract_straight_segments(
                simp_coords, max_angle=MAX_STRAIGHT_ANGLE, loops=5
            )
            keep_ix = simp_ix.take(ix)

        else:
            keep_coords = simp_coords
            keep_ix = simp_ix

    else:
        keep_coords = coords
        keep_ix = np.arange(len(coords))

    ### Calculate the length of each run and drop any that are not sufficiently long
    lengths = segment_length(keep_coords)
    ix = (lengths >= MIN_DAM_WIDTH) & (lengths / total_length < MAX_WIDTH_RATIO)

    pairs = np.dstack([keep_ix[:-1][ix], keep_ix[1:][ix]])[0]

    # since ranges are ragged, we have to do this in a loop instead of vectorized
    segments = []
    for start, end in pairs:
        segments.append(pg.linestrings(coords[start : end + 1]))

    segments = np.array(segments)

    # only keep the segments that are close to the drain
    segments = segments[
        pg.intersects(segments, pg.buffer(drain_pt, MAX_DRAIN_DIST)),
    ]

    if not len(segments):
        return segments

    # only keep those where the drain is interior to the line
    pos = pg.line_locate_point(segments, drain_pt)
    lengths = pg.length(segments)

    ix = (pos >= MIN_INTERIOR_DIST) & (pos <= (lengths - MIN_INTERIOR_DIST))

    return segments[ix]
