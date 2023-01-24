"""This script processes LIDAR-derived waterbodies in South Carolina to extract
waterbodies that intersect flowlines.

Limited to HUC2 == 03.

Creates the following files in `data/states/sc`:
* `sc_waterbodies.feather`: feather file for internal use
* `sc_waterbodies.gpkg`: Geopackage for use in GIS
"""


from pathlib import Path
import warnings

import geopandas as gp
import shapely
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS
from analysis.lib.geometry import dissolve, explode


data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"  # intentionally use raw flowlines
src_dir = data_dir / "states/sc"
huc2 = "03"

print("Reading waterbodies...")
df = (
    read_dataframe(
        src_dir / "SCBreakline.gdb",
        layer="Waterbody",
        force_2d=True,
        columns=[],
    )
    .rename(columns={"NAME": "name"})
    .to_crs(CRS)
)

print("Reading flowlines...")
flowlines = gp.read_feather(nhd_dir / huc2 / "flowlines.feather", columns=[])
tree = shapely.STRtree(flowlines.geometry.values.data)


print(f"Extracted {len(df):,} SC waterbodies")
left, right = tree.query(df.geometry.values.data, predicate="intersects")
df = df.iloc[np.unique(left)].reset_index(drop=True)
print(f"Kept {len(df):,} that intersect flowlines")

df = explode(df)
# make valid
ix = ~shapely.is_valid(df.geometry.values.data)
if ix.sum():
    print(f"Repairing {ix.sum():,} invalid waterbodies")
    df.loc[ix, "geometry"] = shapely.make_valid(df.loc[ix].geometry.values.data)


print("Dissolving adjacent waterbodies...")
df["tmp"] = 1
df = dissolve(df, by="tmp").drop(columns=["tmp"])
df = explode(df).reset_index(drop=True)

df.to_feather(src_dir / "sc_waterbodies.feather")
