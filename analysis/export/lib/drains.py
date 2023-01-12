from pathlib import Path
from time import time

import geopandas as gp
import numpy as np
import pandas as pd
import shapely
from tqdm.auto import tqdm


from analysis.lib.geometry.lines import segment_length
from analysis.lib.geometry.speedups.lines import (
    simplify_vw,
    extract_straight_segments,
)


# Extract no more than 50 vertices (arbitrary) on each side for complex waterbodies;
MAX_SIDE_PTS = 50
MAX_STRAIGHT_ANGLE = 10  # 180 degrees +/- this value is considered straight
MAX_SIMPLIFY_AREA = 100  # m2 or total area of waterbody / 100, whichever is smaller
MIN_DAM_WIDTH = 30  # meters; min width straight line must be in order to consider it a likely dam face
MAX_WIDTH_RATIO = 0.45  # the total length of the extracted dam can be no longer than this amount of the total ring length
MAX_DRAIN_DIST = 1  # meters; distance between line segments and drain
MIN_INTERIOR_DIST = 1  # meters; minimum distance drain must be from edge of segment for segment to be considered a dam


nhd_dir = Path("data/nhd/clean")


def find_dam_faces(drains, waterbodies):
    # drop any on large size classes; these do not reliably pick up actual dams correctly
    drains = drains.loc[drains.sizeclass.isin(["1a", "1b", "2"])]

    # convert to plain dataframe
    joined = pd.DataFrame(
        drains[["geometry", "wbID"]].join(
            waterbodies.geometry.rename("waterbody"),
            on="wbID",
        )
    )
    joined["geometry"] = joined.geometry.values.data
    joined["waterbody"] = joined.waterbody.values.data

    ids, segments = loop(
        joined.waterbody.values, joined.geometry.values, joined.index.values
    )

    # NOTE: this may have duplicate geometries where there are widely spaced drains on the same long waterbody edge
    df = gp.GeoDataFrame(
        {"drainID": ids, "geometry": segments, "width": shapely.length(segments)},
        crs=drains.crs,
    ).join(drains.drop(columns=["geometry"]), on="drainID")

    return df


def loop(waterbodies, drains, index, verbose=False):
    out_index = []
    out_segments = []

    iter = range(len(index))
    if verbose:
        iter = tqdm(iter)

    for i in iter:
        segments = find_dam_face_from_waterbody(waterbodies[i], drains[i])
        out_segments.extend(segments)
        out_index.extend([index[i]] * len(segments))

    return np.array(out_index), np.array(out_segments)


def find_dam_face_from_waterbody(waterbody, drain_pt):
    total_area = shapely.area(waterbody)
    ring = shapely.get_exterior_ring(shapely.normalize(waterbody))
    total_length = shapely.length(ring)
    num_pts = shapely.get_num_points(ring) - 1  # drop closing coordinate
    vertices = shapely.get_point(ring, range(num_pts))

    ### Extract line segments that are no more than 1/3 coordinates of polygon
    # starting from the vertex nearest the drain
    # note: lower numbers are to the right
    tree = shapely.STRtree(vertices)
    ix = tree.nearest(drain_pt)
    side_width = min(num_pts // 3, MAX_SIDE_PTS)
    left_ix = ix + side_width
    right_ix = ix - side_width

    # extract these as a left-to-write line;
    pts = vertices[max(right_ix, 0) : min(num_pts, left_ix)][::-1]
    if left_ix >= num_pts:
        pts = np.append(vertices[0 : left_ix - num_pts][::-1], pts)

    if right_ix < 0:
        pts = np.append(pts, vertices[num_pts + right_ix : num_pts][::-1])

    coords = shapely.get_coordinates(pts)

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
        segments.append(shapely.linestrings(coords[start : end + 1]))

    segments = np.array(segments)

    # only keep the segments that are close to the drain
    segments = segments[
        shapely.intersects(segments, shapely.buffer(drain_pt, MAX_DRAIN_DIST)),
    ]

    if not len(segments):
        return segments

    # only keep those where the drain is interior to the line
    pos = shapely.line_locate_point(segments, drain_pt)
    lengths = shapely.length(segments)

    ix = (pos >= MIN_INTERIOR_DIST) & (pos <= (lengths - MIN_INTERIOR_DIST))

    return segments[ix]
