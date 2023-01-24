from pathlib import Path
import warnings

import shapely
import geopandas as gp
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
src_dir = data_dir / "barriers/source"


### load NABD dams (drop any that have duplicate NIDID)
nabd = (
    read_dataframe(src_dir / "NABD_V2_beta/NABD_V2_beta.shp", columns=["NIDID"])
    .dropna(subset=["NIDID"])
    .drop_duplicates(subset=["NIDID"], keep=False)
    .to_crs(CRS)
    .set_index("NIDID")
)
nabd["ManualReview"] = 2


### Select NABD within analysis HUC4s
huc4_df = gp.read_feather(boundaries_dir / "huc4.feather")
tree = shapely.STRtree(nabd.geometry.values.data)
ix = np.unique(tree.query(huc4_df.geometry.values.data, predicate="intersects")[1])
nabd = nabd.iloc[ix].copy()

### Load NID versions and determine which ones moved
# Note: prev version has duplicates on NIDID; discard these (will let NABD apply here)
prev_nid = (
    read_dataframe(src_dir / "Archive_Feb2022/NID_2021.gdb")
    .drop_duplicates(subset=["NIDID"], keep=False)
    .to_crs(CRS)
    .set_index("NIDID")
)
tree = shapely.STRtree(prev_nid.geometry.values.data)
ix = np.unique(tree.query(huc4_df.geometry.values.data, predicate="intersects")[1])
prev_nid = prev_nid.iloc[ix].copy()

nid = (
    read_dataframe(src_dir / "nid_2_25_2022.gpkg")
    .to_crs(CRS)
    .rename(columns={"federalId": "NIDID"})
    .set_index("NIDID")
)
tree = shapely.STRtree(nid.geometry.values.data)
ix = np.unique(tree.query(huc4_df.geometry.values.data, predicate="intersects")[1])
nid = nid.iloc[ix].copy()


# only join together those that are present current version and NABD
df = nid.join(nabd.geometry.rename("nabd_geometry"), how="inner").join(
    prev_nid[["geometry", "Barrier_Name"]].rename(columns={"geometry": "prev_geometry"})
)
df["update_dist"] = shapely.distance(
    df.geometry.values.data, df.prev_geometry.values.data
)
df["cur_nabd_dist"] = shapely.distance(
    df.geometry.values.data, df.nabd_geometry.values.data
)
df["prev_nabd_dist"] = shapely.distance(
    df.prev_geometry.values.data, df.nabd_geometry.values.data
)

# any that moved less than 10m in NABD can be ignored from NABD (not useful)
# any that moved over 100m in NABD can be ignored from NABD (too risky)
df = df.loc[(df.cur_nabd_dist >= 10) & (df.cur_nabd_dist < 1000)].copy()

# any that were moved by NID that are now > 150m further away from NABD point can be ignored
# due to data issues, some of the NABD / NID points swapped positions; we don't want these
ix = (df.update_dist >= 10) & ((df.cur_nabd_dist - df.prev_nabd_dist) > 150)

df = df.loc[~ix].copy()

nabd = nabd.loc[nabd.index.isin(df.index)].reset_index()

nabd.to_feather(src_dir / "nabd.feather")
write_dataframe(nabd, src_dir / "nabd.fgb")
