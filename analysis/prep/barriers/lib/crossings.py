from pathlib import Path
from time import time
import warnings

import pyarrow as pa
import pyarrow.compute as pc
import geopandas as gp

import pandas as pd
import shapely
from pyogrio import read_dataframe, write_dataframe
import numpy as np

from analysis.constants import (
    CROSSINGS_ID_OFFSET,
    CRS,
    FCODE_TO_STREAMTYPE,
    CROSSING_TYPE_TO_DOMAIN,
)
from analysis.lib.graph.speedups import DirectedGraph
from analysis.lib.io import read_arrow_tables
from analysis.prep.barriers.lib.snap import snap_to_flowlines
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins
from analysis.prep.species.lib.diadromous import get_diadromous_ids

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
nhd_dir = data_dir / "nhd"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"


def get_crossing_code(lon, lat):
    """Calculate Crossing Code based on longitude and latitude values, rounded
    to 7 decimal places (NAACC standard):
    "xy<7 digits lat><7digits lon>"

    NOTE: we use the numpy method instead of any other because it was the
    method used to calculate these in the past CrossingCode was used to calculate
    SARPID, which needs to be permanent.  Other methods produce differences in
    rounding which results in different IDs

    Parameters
    ----------
    lon : 1d array (float)
        array of longitude values
    lat : 1d array (float)
        array of latitude values

    Returns
    -------
    1d array (str)
    """
    return (
        "xy"
        + np.abs((lat * 1e7).round(0).astype("int")).astype("str")
        + np.abs((lon * 1e7).round(0).astype("int")).astype("str")
    )


# def dedup_crossings(df):
#     # we only want to dedup those that are really close, and some may occur in
#     # valid chains of crossings, so only dedup by distance not neighborhoods
#     tree = shapely.STRtree(df.geometry.values)
#     pairs = pd.DataFrame(
#         tree.query(df.geometry.values, predicate="dwithin", distance=DUPLICATE_TOLERANCE).T,
#         columns=["left", "right"],
#     )
#     g = DirectedGraph(
#         df.id.take(pairs.left.values).values.astype("int64"),
#         df.id.take(pairs.right.values).values.astype("int64"),
#     )

#     # note: components accounts for self-intersections and symmetric pairs
#     groups, values = g.flat_components()
#     # sort into deterministic order
#     groups = (
#         pd.DataFrame({"group": groups, "id": values})
#         .astype(df.id.dtype)
#         .join(df.set_index("id").dup_sort, on="id")
#         .sort_values(by=["group", "dup_sort", "id"])
#     )

#     keep_ids = groups.groupby("group").first().id.values.astype("uint64")

#     print(f"Dropping {len(df) - len(keep_ids):,} very close road crossings")
#     return df.loc[df.id.isin(keep_ids)].copy()


def mark_duplicates(geoseries, tolerance, start_group_index=0):
    """Find all sets of points that are within tolerance of each other and keep
    the minimum index for each.

    IMPORTANT: make sure that the index order of geoseries is in precedence sorted
    order because it will take the lowest index per group of duplicates.

    Parameters
    ----------
    geoseries : geopandas GeoSeries
        indexed in precedence order, with index values that are returned by
        operation
    tolerance : number
        distance within which to consider points duplicates
    start_group_index : int, optional (default: 0)
        if provided, group values will start from this index

    Returns
    -------
    pyarrow Table
        includes original index value, dup_group, index_keep, and duplicate (bool)
        columns
    """
    left, right = shapely.STRtree(geoseries.values).query(geoseries.values, predicate="dwithin", distance=tolerance)
    # NOTE: this doesn't need to be writable, but numba expects it to be a writable type
    graph = DirectedGraph(
        geoseries.index.values.take(left).astype("int64"),
        geoseries.index.values.take(right).astype("int64"),
    )

    # note: components accounts for self-intersections and symmetric pairs
    groups, values = graph.flat_components()
    if start_group_index:
        groups += start_group_index

    groups = pa.Table.from_pydict(
        {
            "index": values,
            "dup_group": groups,
        }
    )
    keep = groups.group_by("dup_group").aggregate([("index", "min")]).rename_columns({"index_min": "index_keep"})
    groups = groups.join(keep, "dup_group").sort_by("index")
    groups = groups.append_column("duplicate", pc.not_equal(groups["index"], groups["index_keep"]))

    return groups


def encode_hilbert(geometries, level=16):
    """Encode geoseries to Hilbert curve index

    Parameters
    ----------
    geometries : geopandas GeoSeries or array of shapely geometries
    level : int, optional (default 16)
        level of detail in Hilbert encoding; e.g., 16 = 16 bit range for each of
        x and y

    Returns
    -------
    1d array of Hilbert indices
    """
    level = 16
    side_length = (2**level) - 1
    total_bounds = shapely.total_bounds(geometries)
    x, y = shapely.get_coordinates(geometries).T
    x = pc.round(pc.multiply(pc.subtract(x, total_bounds[0]), side_length / (total_bounds[2] - total_bounds[0])))
    y = pc.round(pc.multiply(pc.subtract(y, total_bounds[1]), side_length / (total_bounds[3] - total_bounds[1])))

    return _encode_hilbert(level, x, y)
