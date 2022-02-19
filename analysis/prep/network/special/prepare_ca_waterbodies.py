"""This script processes waterbody datasets in California to extract
waterbodies that intersect flowlines.

Limited to HUC2 == 16,18.

This drops feature types that are not applicable as waterbodies.

Creates the following files in `data/states/or`:
* `ca_waterbodies.feather`: feather file for internal use
* `ca_waterbodies.fgb`: for use in GIS
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
src_dir = data_dir / "states/ca"
huc2s = ["16", "18"]

print("Reading flowlines...")
flowlines = read_feathers(
    [nhd_dir / huc2 / "flowlines.feather" for huc2 in huc2s], columns=[], geo=True
)
tree = pg.STRtree(flowlines.geometry.values.data)


### Read CA waterbody dataset
df = read_dataframe(src_dir / "CARIv0.3.gdb", columns=["orig_class", "name"])
df["group"] = df.orig_class.fillna("").apply(lambda x: x.split(" - ")[0]).str.strip()
df = df.loc[
    df.group.str.startswith("Lake")
    | df.group.str.startswith("Open Water")
    | df.group.str.contains("Pond")
    | df.group.isin(["Lacustrine"])
].reset_index(drop=True)

# if one of the wetland code types, use same altered codes as extract_nwi.py
df["altered"] = df.name.fillna("").str.contains("Reservoir") | (
    df.orig_class.str.contains(" - ")
    & (
        df.orig_class.str.endswith("d")
        | df.orig_class.str.endswith("h")
        | df.orig_class.str.endswith("r")
        | df.orig_class.str.endswith("x")
    )
)
df["source"] = "cari_0.3"
df = df.to_crs(CRS)

print(f"Extracted {len(df):,} CA waterbodies")
left, right = tree.query_bulk(df.geometry.values.data, predicate="intersects")
df = df.iloc[np.unique(left)].reset_index(drop=True)
print(f"Kept {len(df):,} that intersect flowlines")

df = explode(df)
ix = ~pg.is_valid(df.geometry.values.data)
if ix.sum():
    print(f"Repairing {ix.sum():,} invalid waterbodies")
    df.loc[ix, "geometry"] = pg.make_valid(df.loc[ix].geometry.values.data)

waterbodies = df[["geometry", "altered", "source"]].copy()
del df


print("Reading waterbodies...")
df = read_dataframe(src_dir / "CA_Lakes.shp", columns=["TYPE", "GNIS_NAME"])
df = df.loc[df.TYPE != "dry lake/playa"].reset_index(drop=True)

df["altered"] = df.GNIS_NAME.fillna("").str.contains("Reservoir")

df = df.to_crs(CRS)

print(f"Extracted {len(df):,} CA waterbodies")
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

wb.to_feather(src_dir / "ca_waterbodies.feather")
write_dataframe(wb, src_dir / "ca_waterbodies.fgb")

