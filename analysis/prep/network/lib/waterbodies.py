from time import time

import pandas as pd
import pygeos as pg
import numpy as np


def find_nhd_waterbody_breaks(geometries, nhd_lines):
    """Some large waterbody complexes are divided by dams; these breaks
    need to be preserved.  This is done by finding the shared edges between
    adjacent waterbodies that fall near NHD lines (which include dams) and
    buffering them by 5 meters.

    This should be skipped if nhd_lines is empty.

    Parameters
    ----------
    df : GeoDataFrame
    nhd_lines : GeoDataFrame

    Returns
    -------
    MultiPolygon containing all buffered lines between waterbodies that are near
        NHD lines.  Returns None if no adjacent waterbodies meet these criteria
    """

    boundaries = pg.polygons(pg.get_exterior_ring(geometries))
    tree = pg.STRtree(boundaries)
    left, right = tree.query_bulk(boundaries, predicate="intersects")
    # drop self intersections
    ix = left != right
    left = left[ix]
    right = right[ix]

    # extract unique pairs (dedup symmetric pairs)
    pairs = np.array([left, right]).T
    pairs = (
        pd.DataFrame({"left": pairs.min(axis=1), "right": pairs.max(axis=1)})
        .groupby(["left", "right"])
        .first()
        .reset_index()
    )

    if len(pairs) == 0:
        return None

    # calculate geometric intersection
    i = pg.intersection(
        geometries.take(pairs.left.values), geometries.take(pairs.right.values)
    )

    # extract individual parts (may be geom collections)
    parts = pg.get_parts(pg.get_parts(pg.get_parts(i)))

    # extract only the lines or polygons
    t = pg.get_type_id(parts)
    parts = parts[((t == 1) | (t == 3)) & (~pg.is_empty(parts))].copy()

    if len(parts) == 0:
        return None

    # buffer and merge
    split_lines = pg.get_parts(pg.union_all(pg.buffer(parts, 5)))

    # now find the ones that are within 100m of nhd lines
    tree = pg.STRtree(pg.get_parts(nhd_lines))
    left, right = tree.nearest_all(split_lines, max_distance=100)

    split_lines = split_lines[np.unique(left)]

    if len(split_lines) == 0:
        return None

    return pg.union_all(split_lines)
