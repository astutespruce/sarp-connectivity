from pathlib import Path
import warnings

import geopandas as gp
import pygeos as pg
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import STATES, SARP_STATES, CRS

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

# HUC4s predetermined not to be in region
EXCLUDE_HUC4 = ["0204"]

data_dir = Path("data")
out_dir = data_dir / "boundaries"

### Construct region and SARP boundaries from states
print("Processing states...")
state_df = (
    read_dataframe(
        data_dir / "boundaries/source/tl_2019_us_state/tl_2019_us_state.shp",
        columns=["STUSPS", "STATEFP", "NAME"],
    )
    .to_crs(CRS)
    .rename(columns={"STUSPS": "id", "NAME": "State", "STATEFP": "STATEFIPS"})
)
state_df = state_df.loc[state_df.id.isin(STATES.keys())]
state_df.geometry = pg.make_valid(state_df.geometry.values.data)
write_dataframe(state_df, out_dir / "states.gpkg")

# dissolve to create outer boundary
bnd_df = gp.GeoDataFrame(
    {"geometry": pg.union_all(state_df.geometry.values.data)}, index=[0], crs=CRS
)
write_dataframe(bnd_df, out_dir / "region_boundary.gpkg")
bnd = bnd_df.geometry.values.data[0]

sarp_df = state_df.loc[state_df.id.isin(SARP_STATES)]
write_dataframe(sarp_df, out_dir / "sarp_states.gpkg")

sarp_bnd_df = gp.GeoDataFrame(
    {"geometry": pg.union_all(sarp_df.geometry.values.data)}, index=[0], crs=CRS
)
write_dataframe(sarp_bnd_df, out_dir / "sarp_boundary.gpkg")
sarp_bnd = sarp_bnd_df.geometry.values.data[0]

### Extract HUC4 units that intersect boundaries
wbd_gdb = data_dir / "nhd/source/wbd/WBD_National_GDB/WBD_National_GDB.gdb"

print("Extracting HUC2...")
# First determine the HUC2s that overlap the region
huc2_df = (
    read_dataframe(wbd_gdb, layer="WBDHU2", columns=["huc2"])
    .to_crs(CRS)
    .rename(columns={"huc2": "HUC2"})
)

tree = pg.STRtree(huc2_df.geometry.values.data)

# First extract SARP HUC2
sarp_ix = tree.query(sarp_bnd, predicate="intersects")
sarp_huc2_df = huc2_df.iloc[sarp_ix].copy()
write_dataframe(sarp_huc2_df, out_dir / "sarp_huc2.gpkg")
sarp_huc2_df.to_feather(out_dir / "sarp_huc2.feather")
sarp_huc2 = sorted(sarp_huc2_df.HUC2)

# Subset out HUC2 in region
ix = tree.query(bnd, predicate="intersects")
huc2_df = huc2_df.iloc[ix].copy()
write_dataframe(huc2_df, out_dir / "huc2.gpkg")
huc2_df.to_feather(out_dir / "huc2.feather")
huc2 = sorted(huc2_df.HUC2)

# Next, determine the HUC4s that are within these HUC2s that also overlap the region
print("Extracting HUC4...")
huc4_df = read_dataframe(wbd_gdb, layer="WBDHU4", columns=["huc4"]).rename(
    columns={"huc4": "HUC4"}
)
huc4_df["HUC2"] = huc4_df.HUC4.str[:2]
huc4_df = huc4_df.loc[huc4_df.HUC2.isin(huc2)].to_crs(CRS)
huc4_df = huc4_df.loc[~huc4_df.HUC4.isin(EXCLUDE_HUC4)].copy()

# Extract HUC4s that intersect
tree = pg.STRtree(huc4_df.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")
huc4_df = huc4_df.iloc[ix].copy()

# Drop any that are at the edges only and have little overlap
tree = pg.STRtree(huc4_df.geometry.values.data)
contains_ix = tree.query(bnd, predicate="contains")
edge_ix = np.setdiff1d(np.arange(len(huc4_df)), contains_ix)

# clip geometries by bnd
edge_df = huc4_df.iloc[edge_ix].copy()
edge_df["clipped"] = pg.intersection(bnd, edge_df.geometry.values.data)
edge_df["overlap_pct"] = (
    100 * pg.area(edge_df.clipped.values.data) / pg.area(edge_df.geometry.values.data)
)

# keep areas that overlap by >= 1%
huc4 = np.unique(
    np.append(
        huc4_df.iloc[contains_ix].HUC4, edge_df.loc[edge_df.overlap_pct >= 1].HUC4
    )
)
huc4_df = huc4_df.loc[huc4_df.HUC4.isin(huc4)].copy()
write_dataframe(huc4_df, out_dir / "huc4.gpkg")
huc4_df.to_feather(out_dir / "huc4.feather")


# repeat for SARP
tree = pg.STRtree(huc4_df.geometry.values.data)
intersects_ix = tree.query(sarp_bnd, predicate="intersects")
contains_ix = tree.query(sarp_bnd, predicate="contains")
edge_ix = np.setdiff1d(intersects_ix, contains_ix)
edge_df = huc4_df.iloc[edge_ix].copy()
edge_df["clipped"] = pg.intersection(sarp_bnd, edge_df.geometry.values.data)
edge_df["overlap_pct"] = (
    100 * pg.area(edge_df.clipped.values.data) / pg.area(edge_df.geometry.values.data)
).round(3)

# keep areas that overlap > 0%
sarp_huc4 = np.unique(
    np.append(huc4_df.iloc[contains_ix].HUC4, edge_df.loc[edge_df.overlap_pct > 0].HUC4)
)
sarp_huc4_df = huc4_df.loc[huc4_df.HUC4.isin(sarp_huc4)].copy()
write_dataframe(sarp_huc4_df, out_dir / "sarp_huc4.gpkg")
sarp_huc4_df.to_feather(out_dir / "sarp_huc4.feather")

