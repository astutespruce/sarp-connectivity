from pathlib import Path
import warnings

import geopandas as gp
import pygeos as pg
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
out_dir = data_dir / "boundaries"

wbd_gdb = data_dir / "nhd/source/wbd/WBD_National_GDB/WBD_National_GDB.gdb"


huc4_df = gp.read_feather(out_dir / "huc4.feather")
huc4 = sorted(huc4_df.HUC4.unique())
sarp_huc4_df = gp.read_feather(out_dir / "sarp_huc4.feather")
sarp_huc4 = sorted(sarp_huc4_df.HUC4.unique())

### Extract HUC6 within HUC4
huc6_df = (
    read_dataframe(
        wbd_gdb,
        layer="WBDHU6",
        columns=["huc6"],
        where=f"SUBSTR(huc6, 0, 4) IN {tuple(huc4)}",
    )
    .rename(columns={"huc6": "HUC6"})
    .to_crs(CRS)
)
huc6_df["HUC2"] = huc6_df.HUC6.str[:2]
huc6_df["HUC4"] = huc6_df.HUC6.str[:4]
write_dataframe(huc6_df, out_dir / "huc6.gpkg")
huc6_df.to_feather(out_dir / "huc6.feather")

sarp_huc6_df = huc6_df.loc[huc6_df.HUC4.isin(sarp_huc4)].copy()
write_dataframe(sarp_huc6_df, out_dir / "sarp_huc6.gpkg")
sarp_huc6_df.to_feather(out_dir / "sarp_huc6.feather")


### Extract HUC8 within HUC4
huc8_df = (
    read_dataframe(
        wbd_gdb,
        layer="WBDHU8",
        columns=["huc8"],
        where=f"SUBSTR(huc8, 0, 4) IN {tuple(huc4)}",
    )
    .rename(columns={"huc8": "HUC8"})
    .to_crs(CRS)
)
huc8_df["HUC2"] = huc8_df.HUC8.str[:2]
huc8_df["HUC4"] = huc8_df.HUC8.str[:4]
write_dataframe(huc8_df, out_dir / "huc8.gpkg")
huc8_df.to_feather(out_dir / "huc8.feather")

sarp_huc8_df = huc8_df.loc[huc8_df.HUC4.isin(sarp_huc4)].copy()
write_dataframe(sarp_huc8_df, out_dir / "sarp_huc8.gpkg")
sarp_huc8_df.to_feather(out_dir / "sarp_huc8.feather")


### Extract HUC12 within HUC4
huc12_df = (
    read_dataframe(
        wbd_gdb,
        layer="WBDHU12",
        columns=["huc12"],
        where=f"SUBSTR(huc12, 0, 4) IN {tuple(huc4)}",
    )
    .rename(columns={"huc12": "HUC12"})
    .to_crs(CRS)
)
huc12_df["HUC2"] = huc12_df.HUC12.str[:2]
huc12_df["HUC4"] = huc12_df.HUC12.str[:4]
write_dataframe(huc12_df, out_dir / "huc12.gpkg")
huc12_df.to_feather(out_dir / "huc12.feather")

sarp_huc12_df = huc12_df.loc[huc12_df.HUC4.isin(sarp_huc4)].copy()
write_dataframe(sarp_huc12_df, out_dir / "sarp_huc12.gpkg")
sarp_huc12_df.to_feather(out_dir / "sarp_huc12.feather")
