"""This script processes waterbody datasets in Oregon to extract
waterbodies that intersect flowlines.

Limited to HUC2 == 17.

This drops feature types that are not applicable as waterbodies.

Creates the following files in `data/states/or`:
* `or_waterbodies.feather`: feather file for internal use
* `or_waterbodies.fgb`: for use in GIS
"""


from pathlib import Path
import warnings

import geopandas as gp
import pygeos as pg
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS
from analysis.lib.geometry import dissolve, explode
from analysis.lib.io import read_feathers


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")
warnings.filterwarnings("ignore", message=".*geometry types are not supported*")

data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"  # intentionally use raw flowlines
src_dir = data_dir / "states/or"
huc2s = ["16", "17", "18"]

print("Reading flowlines...")
flowlines = read_feathers(
    [nhd_dir / huc2 / "flowlines.feather" for huc2 in huc2s], columns=[], geo=True
)
tree = pg.STRtree(flowlines.geometry.values.data)


### Read OR waterbody dataset
print("Reading waterbodies...")
df = read_dataframe(src_dir / "wb_oregon.shp", columns=["WB_HYDR_FT", "WB_CART_FT"])

# metadata for attributes not available, used values from WA hydro lakes dataset
# to deduce lookup of codes

# Keep Lake, Impoundment and appropriate subtypes
df = df.loc[
    df.WB_HYDR_FT.isin(["LA", "IM"])
    & df.WB_CART_FT.isin([101, 106, 107, 109, 110, 402, 421, 902])
].reset_index(drop=True)

# everything besides lakes are likely impoundment / altered types
df["altered"] = df.WB_HYDR_FT != "LA"

df = df.to_crs(CRS)

print(f"Extracted {len(df):,} WA hydro waterbodies")
left, right = tree.query_bulk(df.geometry.values.data, predicate="intersects")
df = df.iloc[np.unique(left)].reset_index(drop=True)
print(f"Kept {len(df):,} that intersect flowlines")

df = explode(df)
ix = ~pg.is_valid(df.geometry.values.data)
if ix.sum():
    print(f"Repairing {ix.sum():,} invalid waterbodies")
    df.loc[ix, "geometry"] = pg.make_valid(df.loc[ix].geometry.values.data)


### Dissolve waterbodies
print("Dissolving adjacent waterbodies...")

# dissolve by altered status first
df = explode(dissolve(df, by=["altered"])).reset_index(drop=True)

# dissolve contiguous
df["tmp"] = 1
wb = dissolve(df, by="tmp").drop(columns=["tmp"])
wb = explode(wb).reset_index(drop=True)
df = df.drop(columns=["tmp"])

# mark any that are more than 50% altered as altered
altered = df.loc[df.altered]
tree = pg.STRtree(altered.geometry.values.data)
left, right = tree.query_bulk(wb.geometry.values.data, predicate="intersects")
intersection = pg.area(
    pg.intersection(
        wb.geometry.values.data.take(left), altered.geometry.values.data.take(right)
    )
) / pg.area(wb.geometry.values.data.take(left))
ix = wb.index.values.take(np.unique(left[intersection >= 0.5]))
wb["altered"] = False
wb.loc[ix, "altered"] = True

wb.to_feather(src_dir / "or_waterbodies.feather")
write_dataframe(wb, src_dir / "or_waterbodies.fgb")

