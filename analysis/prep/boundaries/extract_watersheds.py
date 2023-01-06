from pathlib import Path
import warnings

import geopandas as gp
import shapely
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
out_dir = data_dir / "boundaries"

wbd_gdb = data_dir / "nhd/source/wbd/WBD_National_GDB/WBD_National_GDB.gdb"


huc4_df = gp.read_feather(out_dir / "huc4.feather")
huc4 = sorted(huc4_df.HUC4.unique())

### Extract HUC6 within HUC4
print("Processing HUC6...")
huc6_df = (
    read_dataframe(
        wbd_gdb,
        layer="WBDHU6",
        columns=["huc6", "name"],
        where=f"SUBSTR(huc6, 0, 4) IN {tuple(huc4)}",
    )
    .rename(columns={"huc6": "HUC6"})
    .to_crs(CRS)
)
huc6_df.to_feather(out_dir / "huc6.feather")
write_dataframe(huc6_df.rename(columns={"HUC6": "id"}), out_dir / "huc6.fgb")

### Extract HUC8 within HUC4
print("Processing HUC8...")
huc8_df = (
    read_dataframe(
        wbd_gdb,
        layer="WBDHU8",
        columns=["huc8", "name"],
        where=f"SUBSTR(huc8, 0, 4) IN {tuple(huc4)}",
    )
    .rename(columns={"huc8": "HUC8"})
    .to_crs(CRS)
)
huc8_df.to_feather(out_dir / "huc8.feather")
write_dataframe(huc8_df.rename(columns={"HUC8": "id"}), out_dir / "huc8.fgb")

### Extract HUC10 within HUC4
print("Processing HUC10...")
huc10_df = (
    read_dataframe(
        wbd_gdb,
        layer="WBDHU10",
        columns=["huc10", "name"],
        where=f"SUBSTR(huc10, 0, 4) IN {tuple(huc4)}",
    )
    .rename(columns={"huc10": "HUC10"})
    .to_crs(CRS)
)
huc10_df.to_feather(out_dir / "huc10.feather")
write_dataframe(huc10_df.rename(columns={"HUC10": "id"}), out_dir / "huc10.fgb")


### Extract HUC12 within HUC4
print("Processing HUC12...")
huc12_df = (
    read_dataframe(
        wbd_gdb,
        layer="WBDHU12",
        columns=["huc12", "name"],
        where=f"SUBSTR(huc12, 0, 4) IN {tuple(huc4)}",
    )
    .rename(columns={"huc12": "HUC12"})
    .to_crs(CRS)
)
huc12_df.to_feather(out_dir / "huc12.feather")
write_dataframe(huc12_df.rename(columns={"HUC12": "id"}), out_dir / "huc12.fgb")
