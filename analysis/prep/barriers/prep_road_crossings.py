"""
Preprocess road / stream crossings into data needed by tippecanoe for creating vector tiles.

Input:
* USGS Road / Stream crossings, projected to match SARP standard projection (Albers CONUS).
* pre-processed and snapped small barriers


Outputs:
`data/barriers/intermediate/road_crossings.feather`: road / stream crossing data for merging in with small barriers that do not have networks
"""

from pathlib import Path
from time import time
import warnings

import geopandas as gp
import numpy as np
import pygeos as pg
import pandas as pd
from pyogrio import write_dataframe

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

# considered to duplicate an inventoried road barriers if within this value
DUPLICATE_TOLERANCE = 10  # meters

start = time()

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
out_dir = barriers_dir / "master"
qa_dir = barriers_dir / "qa"


print("Reading road crossings")
df = gp.read_feather(src_dir / "road_crossings.feather")

### Remove those that otherwise duplicate existing small barriers
print("Removing crossings that duplicate existing barriers")
barriers = gp.read_feather(barriers_dir / "master/small_barriers.feather")

tree = pg.STRtree(df.geometry.values.data)
ix = tree.query_bulk(
    barriers.geometry.values.data, predicate="dwithin", distance=DUPLICATE_TOLERANCE
)[1]
drop_ids = df.id.values.take(ix)

print(
    f"Dropping {len(drop_ids):,} road crossings that are within {DUPLICATE_TOLERANCE} of inventoried barriers"
)
df = df.loc[~df.id.isin(drop_ids)].copy()

print(f"Serializing {len(df):,} road crossings")

df = df.reset_index(drop=True)
df.to_feather(out_dir / "road_crossings.feather")
write_dataframe(df, qa_dir / "road_crossings.fgb")


# Extract out only the snapped ones not on loops
print(f"Serializing {df.snapped.sum():,} snapped road crossings")
df = df.loc[
    df.snapped & (~df.loop),
    ["geometry", "id", "HUC2", "lineID", "NHDPlusID", "loop", "intermittent"],
].reset_index(drop=True)

df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

df.to_feather(barriers_dir / "snapped/road_crossings.feather")


print("Done in {:.2f}".format(time() - start))
