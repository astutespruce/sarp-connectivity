"""This script processes waterbody datasets in Washington State to extract
waterbodies that intersect flowlines.

Limited to HUC2 == 17.

This drops feature types that are not applicable as waterbodies.

Creates the following files in `data/states/wa`:
* `wa_waterbodies.feather`: feather file for internal use
* `wa_waterbodies.fgb`: for use in GIS
"""


from pathlib import Path
import warnings

import geopandas as gp
import pygeos as pg
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS
from analysis.lib.geometry import dissolve, explode


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")
warnings.filterwarnings("ignore", message=".*geometry types are not supported*")

data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"  # intentionally use raw flowlines
src_dir = data_dir / "states/wa"
huc2 = "17"

print("Reading flowlines...")
flowlines = gp.read_feather(nhd_dir / huc2 / "flowlines.feather", columns=[])
tree = pg.STRtree(flowlines.geometry.values.data)


### Read WA hydro waterbody dataset
print("Reading hydro waterbodies...")
df = read_dataframe(
    src_dir / "hydro.gdb",
    layer="wbhydro",
    columns=["WB_CART_FTR_LABEL_NM", "WB_HYDR_FTR_LABEL_NM", "WB_GNIS_NM"],
)

# extract features that may be of interest to SARP for crossref against barriers
# tmp = df.loc[df.WB_CART_FTR_LABEL_NM.isin(['Canal lock/s', 'Dam/weir', 'Ditch/canal', 'Falls', 'Fish ladder', 'Penstock', 'Spillway'])].reset_index(drop=True)
# write_dataframe(tmp, '/tmp/sarp/wa_hydro_potential_barriers.shp')

# keep only waterbody types
df = df.loc[
    (
        df.WB_CART_FTR_LABEL_NM.isin(["Impoundment", "Lake/pond", "Reservoir"])
        | df.WB_HYDR_FTR_LABEL_NM.isin(["Lake", "Impoundment"])
    )
    & (~df.WB_HYDR_FTR_LABEL_NM.isin(["Island", "Alkali flat"]))
].reset_index(drop=True)

# everything besides lakes are impoundment / altered types
df["altered"] = df.WB_CART_FTR_LABEL_NM != "Lake/pond"
df["source"] = "wa_hydro"

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

waterbodies = df[["geometry", "altered", "source"]].copy()
del df


### Read WA visible surface water dataset
print("Reading visible surface waterbodies...")
df = read_dataframe(
    src_dir / "SurfaceWaterUnified_forGeoWA.gdb",
    layer="VisibleSurfaceWater",
    columns=["WClass", "WSubClass"],
    force_2d=True,
)

# keep only waterbody types
df = df.loc[df.WClass == "WaterBody"].reset_index(drop=True)

# everything besides lakes are impoundment / altered types
df["altered"] = df.WSubClass == "Manmade"
df["source"] = "wa_visiblesurfacewater"

# reduce precision of geometry to 0.25ft; we'll cleanup topology later
df["geometry"] = pg.simplify(df.geometry.values.data, 0.25, preserve_topology=False)

df = df.to_crs(CRS)

print(f"Extracted {len(df):,} WA surface waterbodies")
left, right = tree.query_bulk(df.geometry.values.data, predicate="intersects")
df = df.iloc[np.unique(left)].reset_index(drop=True)
print(f"Kept {len(df):,} that intersect flowlines")

df = explode(df)
ix = ~pg.is_valid(df.geometry.values.data)
if ix.sum():
    print(f"Repairing {ix.sum():,} invalid waterbodies")
    df.loc[ix, "geometry"] = pg.make_valid(df.loc[ix].geometry.values.data)


df = waterbodies.append(
    df[["geometry", "altered", "source"]], ignore_index=True, sort=False
).reset_index(drop=True)

### Dissolve waterbodies
print("Dissolving contiguous waterbodies")
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

wb.to_feather(src_dir / "wa_waterbodies.feather")
write_dataframe(wb, src_dir / "wa_waterbodies.fgb")

