from pathlib import Path
import warnings

import geopandas as gp
import pandas as pd
import shapely
import numpy as np
from pyogrio import read_dataframe

from analysis.constants import CRS
from analysis.lib.geometry import dissolve, explode
from analysis.lib.io import read_feathers


warnings.filterwarnings("ignore", message=".*geometry types are not supported*")

data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"  # intentionally use raw flowlines
src_dir = data_dir / "states/ri"

flowlines = gp.read_feather(nhd_dir / "01/flowlines.feather", columns=[])

df = (
    read_dataframe(src_dir / "lakes_ponds.gdb", columns=["NAME"], use_arrow=True)
    .rename(columns={"NAME": "name"})
    .to_crs(CRS)
)

# drop any with river in the name
df = df.loc[~df.name.str.lower().str.contains("river")].reset_index(drop=True)

df["altered"] = df.name.str.lower().str.contains("reservoir")

print(f"Extracted {len(df):,} RI waterbodies")
left, right = shapely.STRtree(flowlines.geometry.values).query(df.geometry.values, predicate="intersects")
df = df.iloc[np.unique(left)].reset_index(drop=True)
print(f"Kept {len(df):,} that intersect flowlines")

df = df.explode(ignore_index=True)
ix = ~shapely.is_valid(df.geometry.values)
if ix.sum():
    print(f"Repairing {ix.sum():,} invalid waterbodies")
    df.loc[ix, "geometry"] = shapely.make_valid(df.loc[ix].geometry.values)


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
tree = shapely.STRtree(altered.geometry.values)
left, right = tree.query(wb.geometry.values, predicate="intersects")
intersection = shapely.area(
    shapely.intersection(wb.geometry.values.take(left), altered.geometry.values.take(right))
) / shapely.area(wb.geometry.values.take(left))
ix = wb.index.values.take(np.unique(left[intersection >= 0.5]))
wb["altered"] = False
wb.loc[ix, "altered"] = True


wb.to_feather(src_dir / "ri_waterbodies.feather")
