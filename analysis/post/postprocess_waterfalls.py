"""
Process waterfalls into data needed by tippecanoe for creating vector tiles.

For these outputs, waterfalls do not need to be processed through the network analysis.
There is code below, that if uncommented, can be used to integrate the network results.

Inputs:
* waterfalls

Outputs:
* `data/tiles/waterfalls.csv`: waterfalls for creating vector tiles in tippecanoe

"""

import os
from pathlib import Path
from time import time
import csv
import warnings

import pygeos as pg
import geopandas as gp

from api.constants import WF_CORE_FIELDS


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
qa_dir = data_dir / "barriers/qa"
tile_dir = data_dir / "tiles"

if not os.path.exists(tile_dir):
    os.makedirs(tile_dir)


### Read in master
print("Reading master...")
df = (
    gp.read_feather(barriers_dir / "waterfalls.feather")
    .set_index("id")
    .drop(
        columns=[
            "level_0",
            "index",
            "dup_group",
            "dup_count",
            "dup_log",
            "snap_dist",
            "snap_tolerance",
            "snap_log",
            "snapped",
            "log",
            "lineID",
            "wbID",
        ],
        errors="ignore",
    )
    .rename(
        columns={
            "StreamOrde": "StreamOrder",
        }
    )
)

# drop any that should be DROPPED (dropped or duplicate) from the analysis
# NOTE: excluded ones are retained but don't have networks
df = df.loc[~(df.dropped | df.duplicate)].copy()

### Add lat / lon
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(epsg=4326)
geo["lat"] = pg.get_x(geo.geometry.values.data).astype("float32")
geo["lon"] = pg.get_y(geo.geometry.values.data).astype("float32")
df = df.join(geo[["lat", "lon"]])


### Output results
print("Writing to output files...")

# drop geometry and other fields not needed
df = df[WF_CORE_FIELDS].copy()

### Export data for use in tippecanoe to generate vector tiles

# Fill N/A values and fix dtypes
str_cols = df.dtypes.loc[df.dtypes == "object"].index
df[str_cols] = df[str_cols].fillna("")

df.rename(columns={k: k.lower() for k in df.columns}).to_csv(
    tile_dir / "waterfalls.csv",
    index_label="id",
    quoting=csv.QUOTE_NONNUMERIC,
)


print(f"Done in {time() - start:.2f}")
