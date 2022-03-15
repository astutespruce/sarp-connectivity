from pathlib import Path
import warnings

import pygeos as pg
import geopandas as gp
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
src_dir = data_dir / "barriers/source"


### load NABD dams (drop any that have duplicate NIDID)
df = (
    read_dataframe(src_dir / "NABD_V2_beta/NABD_V2_beta.shp", columns=["NIDID"])
    .dropna(subset=["NIDID"])
    .to_crs(CRS)
    .dropna(subset=["NIDID"])
    .drop_duplicates(subset=["NIDID"], keep=False)
    .set_index("NIDID")
)


### Select NABD within analysis HUC4s
huc4_df = gp.read_feather(boundaries_dir / "huc4.feather")
tree = pg.STRtree(df.geometry.values.data)
ix = np.unique(tree.query_bulk(huc4_df.geometry.values.data, predicate="intersects")[1])

df = df.iloc[ix].reset_index()

df["ManualReview"] = 2

df.to_feather(src_dir / "nabd.feather")
write_dataframe(df, src_dir / "nabd.fgb")
