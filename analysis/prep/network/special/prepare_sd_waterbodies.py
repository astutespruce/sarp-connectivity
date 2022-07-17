"""This script processes waterbodies in South Dakota to extract
waterbodies that intersect flowlines.

Limited to HUC2 == 07, 09, 10, .

Creates the following files in `data/states/sd`:
* `sd_waterbodies.feather`: feather file for internal use
* `sd_waterbodies.fgb`: Geopackage for use in GIS
"""


from pathlib import Path
import warnings

import pandas as pd
import geopandas as gp
import pygeos as pg
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS
from analysis.lib.geometry import dissolve, explode
from analysis.lib.io import read_feathers

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"  # intentionally use raw flowlines
src_dir = data_dir / "states/sd"


### Extract HUC4s that overlap South Dakota
huc4_df = gp.read_feather(data_dir / "boundaries/huc4.feather")
states = gp.read_feather(data_dir / "boundaries/states.feather")
states = states.loc[states.State == "South Dakota"].copy()
tree = pg.STRtree(huc4_df.geometry.values.data)
ix = tree.query(states.geometry.values.data[0], predicate="intersects")
huc4_df = huc4_df.iloc[ix].copy()
huc2s = sorted(huc4_df.HUC2.unique())

huc2_df = gp.read_feather(data_dir / "boundaries/huc2.feather")
huc2_df = huc2_df.loc[huc2_df.HUC2.isin(huc2s)].copy()

print("Reading flowlines...")
flowlines = read_feathers(
    [nhd_dir / huc2 / "flowlines.feather" for huc2 in huc2s],
    columns=["HUC4", "geometry"],
    geo=True,
)
flowlines = flowlines.loc[flowlines.HUC4.isin(huc4_df.HUC4.unique())].copy()
tree = pg.STRtree(flowlines.geometry.values.data)

print("Reading waterbodies...")
df = read_dataframe(src_dir / "Statewide_Waterbodies.shp", columns=[]).to_crs(CRS)
print(f"Extracted {len(df):,} waterbodies")

left, right = tree.query_bulk(df.geometry.values.data, predicate="intersects")
df = df.iloc[np.unique(left)].reset_index(drop=True)
print(f"Kept {len(df):,} that intersect flowlines")

df = explode(df)
# make valid
ix = ~pg.is_valid(df.geometry.values.data)
if ix.sum():
    print(f"Repairing {ix.sum():,} invalid waterbodies")
    df.loc[ix, "geometry"] = pg.make_valid(df.loc[ix].geometry.values.data)


print("Dissolving adjacent waterbodies...")
df["tmp"] = 1
df = dissolve(df, by="tmp")
df = explode(df).reset_index(drop=True)


### Split out by HUC2
tree = pg.STRtree(df.geometry.values.data)

# confirmed by hand, there are no waterbodies that show up in multiple HUC2s
left, right = tree.query_bulk(huc2_df.geometry.values.data, predicate="intersects")

df = df.join(
    pd.DataFrame(
        {"HUC2": huc2_df.HUC2.values.take(left)}, index=df.index.values.take(right)
    )
)

df.to_feather(src_dir / "sd_waterbodies.feather")
