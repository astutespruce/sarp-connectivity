"""This script processes waterbody datasets in California to extract
waterbodies that intersect flowlines.

Limited to HUC2 == 16,17, 18.

This drops feature types that are not applicable as waterbodies.

Creates the following files in `data/states/or`:
* `ca_waterbodies.feather`: feather file for internal use
* `ca_waterbodies.fgb`: for use in GIS
"""


from pathlib import Path
import warnings

import geopandas as gp
import pandas as pd
import shapely
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS
from analysis.lib.geometry import dissolve, explode
from analysis.lib.io import read_feathers


warnings.filterwarnings("ignore", message=".*geometry types are not supported*")

data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"  # intentionally use raw flowlines
src_dir = data_dir / "states/ca"
huc2s = ["16", "17", "18"]

huc2_df = gp.read_feather(data_dir / "boundaries/huc2.feather")
huc2_df = huc2_df.loc[huc2_df.HUC2.isin(huc2s)].copy()

print("Reading flowlines...")
flowlines = read_feathers(
    [nhd_dir / huc2 / "flowlines.feather" for huc2 in huc2s], columns=[], geo=True
)
tree = shapely.STRtree(flowlines.geometry.values.data)


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
left, right = tree.query(df.geometry.values.data, predicate="intersects")
df = df.iloc[np.unique(left)].reset_index(drop=True)
print(f"Kept {len(df):,} that intersect flowlines")

df = explode(df)
ix = ~shapely.is_valid(df.geometry.values.data)
if ix.sum():
    print(f"Repairing {ix.sum():,} invalid waterbodies")
    df.loc[ix, "geometry"] = shapely.make_valid(df.loc[ix].geometry.values.data)

waterbodies = df[["geometry", "altered", "source"]].copy()
del df


print("Reading waterbodies...")
df = read_dataframe(src_dir / "CA_Lakes.shp", columns=["TYPE", "GNIS_NAME"])
df = df.loc[df.TYPE != "dry lake/playa"].reset_index(drop=True)

df["altered"] = df.GNIS_NAME.fillna("").str.contains("Reservoir")

df = df.to_crs(CRS)

print(f"Extracted {len(df):,} CA waterbodies")
left, right = tree.query(df.geometry.values.data, predicate="intersects")
df = df.iloc[np.unique(left)].reset_index(drop=True)
print(f"Kept {len(df):,} that intersect flowlines")

df = explode(df)
ix = ~shapely.is_valid(df.geometry.values.data)
if ix.sum():
    print(f"Repairing {ix.sum():,} invalid waterbodies")
    df.loc[ix, "geometry"] = shapely.make_valid(df.loc[ix].geometry.values.data)


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
tree = shapely.STRtree(altered.geometry.values.data)
left, right = tree.query(wb.geometry.values.data, predicate="intersects")
intersection = shapely.area(
    shapely.intersection(
        wb.geometry.values.data.take(left), altered.geometry.values.data.take(right)
    )
) / shapely.area(wb.geometry.values.data.take(left))
ix = wb.index.values.take(np.unique(left[intersection >= 0.5]))
wb["altered"] = False
wb.loc[ix, "altered"] = True

### Split out by HUC2
tree = shapely.STRtree(wb.geometry.values.data)

# confirmed by hand, there are no waterbodies that show up in multiple HUC2s
left, right = tree.query(huc2_df.geometry.values.data, predicate="intersects")

wb = wb.join(
    pd.DataFrame(
        {"HUC2": huc2_df.HUC2.values.take(left)}, index=wb.index.values.take(right)
    )
)


wb.to_feather(src_dir / "ca_waterbodies.feather")
