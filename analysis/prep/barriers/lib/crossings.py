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


def dedup_crossings(df):
    # we only want to dedup those that are really close, and some may occur in
    # valid chains of crossings, so only dedup by distance not neighborhoods
    tree = shapely.STRtree(df.geometry.values)
    pairs = pd.DataFrame(
        tree.query(df.geometry.values, predicate="dwithin", distance=DUPLICATE_TOLERANCE).T,
        columns=["left", "right"],
    )
    g = DirectedGraph(
        df.id.take(pairs.left.values).values.astype("int64"),
        df.id.take(pairs.right.values).values.astype("int64"),
    )

    # note: components accounts for self-intersections and symmetric pairs
    groups, values = g.flat_components()
    # sort into deterministic order
    groups = (
        pd.DataFrame({"group": groups, "id": values})
        .astype(df.id.dtype)
        .join(df.set_index("id").dup_sort, on="id")
        .sort_values(by=["group", "dup_sort", "id"])
    )

    keep_ids = groups.groupby("group").first().id.values.astype("uint64")

    print(f"Dropping {len(df) - len(keep_ids):,} very close road crossings")
    return df.loc[df.id.isin(keep_ids)].copy()
