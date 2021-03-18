from pathlib import Path
import os
from time import time
import warnings
from numpy.matrixlib import defmatrix

import pandas as pd
import geopandas as gp
import pygeos as pg
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS
from analysis.lib.pygeos_util import dissolve, explode


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"  # intentionally use raw flowlines
src_dir = data_dir / "states/sc"
huc2 = "03"

print("Reading waterbodies...")
df = (
    read_dataframe(
        src_dir / "SCBreakline.gdb", layer="Waterbody", force_2d=True, columns=[],
    )
    .rename(columns={"NAME": "name"})
    .to_crs(CRS)
)

print("Reading flowlines...")
flowlines = gp.read_feather(nhd_dir / huc2 / "flowlines.feather", columns=[])
tree = pg.STRtree(flowlines.geometry.values.data)


print(f"Extracted {len(df):,} SC waterbodies")
left, right = tree.query_bulk(df.geometry.values.data, predicate="intersects")
df = df.iloc[np.unique(left)].reset_index(drop=True)
print(f"Kept {len(df):,} that intersect flowlines")

df = explode(df)
df["tmp"] = 1

print("Dissolving adjacent waterbodies...")
df = dissolve(df, by="tmp")
df = explode(df).reset_index(drop=True)

df.to_feather(src_dir / "sc_waterbodies.feather")
write_dataframe(df, src_dir / "sc_waterbodies.gpkg")

