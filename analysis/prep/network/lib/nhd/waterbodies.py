import warnings

import numpy as np
import pandas as pd
import shapely
from pyogrio import read_dataframe

from analysis.constants import WATERBODY_EXCLUDE_FTYPES
from analysis.lib.geometry import make_valid
from analysis.prep.network.lib.nhd.util import get_column_names

warnings.filterwarnings("ignore", message=".*Warning 1: organizePolygons.*")


WATERBODY_COLS = [
    "NHDPlusID",
    "FType",
    "FCode",
    "GNIS_ID",
    "GNIS_Name",
    "AreaSqKm",
]


def extract_waterbodies(gdb, target_crs):
    """Extract waterbodies from NHDPlusHR data product that are are not one of
    the excluded types (e.g., estuary, playa, swamp/marsh).

    Parameters
    ----------
    gdb : str
        path to the NHD HUC4 Geodatabase
    target_crs: GeoPandas CRS object
        target CRS to project NHD to for analysis, like length calculations.
        Must be a planar projection.

    Returns
    -------
    GeoDataFrame
    """
    print("Reading waterbodies")

    layer = "NHDWaterbody"
    read_cols, col_map = get_column_names(gdb, layer, WATERBODY_COLS)
    ftype_col = col_map.get("FType", "FType")

    df = read_dataframe(
        gdb,
        layer=layer,
        columns=read_cols,
        force_2d=True,
        use_arrow=True,
        where=f"{ftype_col} not in {tuple(WATERBODY_EXCLUDE_FTYPES)}",
    ).rename(columns=col_map)
    print(f"Read {len(df):,} waterbodies")

    # Convert multipolygons to polygons
    # those we checked that are true multipolygons are errors
    df.geometry = shapely.get_geometry(df.geometry.values.data, 0)
    df.geometry = make_valid(df.geometry.values.data)

    print("projecting to target projection")
    df = df.to_crs(target_crs)

    df.NHDPlusID = df.NHDPlusID.astype("uint64")
    df.AreaSqKm = df.AreaSqKm.astype("float32")
    df.FType = df.FType.astype("uint16")

    return df


def find_nhd_waterbody_breaks(geometries, nhd_lines):
    """Some large waterbody complexes are divided by dams; these breaks
    need to be preserved.  This is done by finding the shared edges between
    adjacent waterbodies that fall near NHD lines (which include dams) and
    buffering them by 10 meters (arbitrary, from trial and error).

    This must be run against NHD waterbodies, not merged waterbodies.

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

    buffer_dist = 10

    # find all nhd lines that intersect waterbodies
    # first, buffer them slightly
    nhd_lines = shapely.get_parts(shapely.union_all(shapely.buffer(nhd_lines, 0.1)))
    tree = shapely.STRtree(geometries)
    left, right = tree.query(nhd_lines, predicate="intersects")

    # remove nhd_lines any that are completely contained in a waterbody,
    # after accounting for 10m buffer
    tmp = pd.DataFrame(
        {
            "left": left,
            "left_geometry": nhd_lines.take(left),
            "right": right,
            "right_geometry": geometries.take(right),
        }
    )

    shapely.prepare(tmp.right_geometry.values)
    contained = shapely.contains_properly(
        tmp.right_geometry.values, tmp.left_geometry.values
    )
    print(
        f"Dropping {contained.sum()} NHD lines that are completely contained within waterbodies"
    )

    tmp = tmp.loc[~contained]

    # add these to the return
    keep_nhd_lines = nhd_lines[tmp.left.unique()]

    # find connected boundaries
    boundaries = shapely.polygons(shapely.get_exterior_ring(geometries))
    tree = shapely.STRtree(boundaries)
    left, right = tree.query(boundaries, predicate="intersects")
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

    # calculate geometric intersection
    i = shapely.intersection(
        geometries.take(pairs.left.values), geometries.take(pairs.right.values)
    )

    # extract individual parts (may be geom collections)
    parts = shapely.get_parts(shapely.get_parts(shapely.get_parts(i)))

    # extract only the lines or polygons
    t = shapely.get_type_id(parts)
    parts = parts[((t == 1) | (t == 3)) & (~shapely.is_empty(parts))].copy()

    # buffer and merge
    split_lines = shapely.get_parts(
        shapely.union_all(shapely.buffer(parts, buffer_dist))
    )

    # now find the ones that are within 100m of nhd lines
    nhd_lines = shapely.get_parts(nhd_lines)
    tree = shapely.STRtree(nhd_lines)
    left, right = tree.query_nearest(split_lines, max_distance=100)

    split_lines = split_lines[np.unique(left)]

    if len(split_lines) or len(keep_nhd_lines):
        return shapely.get_parts(
            shapely.union_all(np.append(split_lines, keep_nhd_lines))
        )

    return None
