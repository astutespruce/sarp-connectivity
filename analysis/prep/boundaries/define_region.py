from pathlib import Path
import warnings

import geopandas as gp
import shapely
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import STATES, CRS, GEO_CRS, REGION_STATES
from analysis.lib.geometry import to_multipolygon


data_dir = Path("data")
out_dir = data_dir / "boundaries"
ui_dir = Path("ui/data")

state_filename = data_dir / "boundaries/source/tl_2021_us_state.shp"
wbd_gdb = data_dir / "nhd/source/wbd/WBD_National_GDB/WBD_National_GDB.gdb"


### Construct region boundary from states
# Note: STATEFIPS is needed to join to counties
print("Processing states...")
state_df = (
    read_dataframe(
        state_filename,
        columns=["STUSPS", "STATEFP", "NAME"],
    )
    .to_crs(CRS)
    .rename(columns={"STUSPS": "id", "NAME": "State", "STATEFP": "STATEFIPS"})
)
state_df.geometry = shapely.make_valid(state_df.geometry.values.data)
state_df.geometry = to_multipolygon(state_df.geometry.values.data)

# save all states for spatial joins
state_df.to_feather(out_dir / "states.feather")
write_dataframe(state_df, out_dir / "states.fgb")

state_df = state_df.loc[state_df.id.isin(STATES.keys())].copy()
state_df.to_feather(out_dir / "region_states.feather")

# dissolve to create outer state boundary for total analysis area and regions
bnd_df = gp.GeoDataFrame(
    [
        {"geometry": shapely.union_all(state_df.geometry.values.data), "id": "total"},
    ]
    + [
        {
            "geometry": shapely.union_all(
                state_df.loc[
                    state_df.id.isin(REGION_STATES[region])
                ].geometry.values.data
            ),
            "id": region,
        }
        for region in REGION_STATES
    ],
    crs=CRS,
)
bnd_df["geometry"] = to_multipolygon(bnd_df.geometry.values.data)
write_dataframe(bnd_df, out_dir / "region_boundary.fgb")
bnd_df.to_feather(out_dir / "region_boundary.feather")

bnd = bnd_df.geometry.values.data[0]
bnd_geo = bnd_df.to_crs(GEO_CRS)
bnd_geo["bbox"] = shapely.bounds(bnd_geo.geometry.values.data).round(2).tolist()

# create mask
world = shapely.box(-180, -85, 180, 85)
bnd_mask = bnd_geo.drop(columns=["bbox"])
bnd_mask["geometry"] = shapely.normalize(
    shapely.difference(world, bnd_mask.geometry.values.data)
)
bnd_mask.to_feather(out_dir / "region_mask.feather")


### Extract HUC4 units that intersect boundaries
print("Extracting HUC2...")
huc2_df = (
    read_dataframe(wbd_gdb, layer="WBDHU2", columns=["huc2", "name"])
    .to_crs(CRS)
    .rename(columns={"huc2": "HUC2"})
)

tree = shapely.STRtree(huc2_df.geometry.values.data)

# Subset out HUC2 in region
ix = tree.query(bnd, predicate="intersects")
huc2_df = huc2_df.iloc[ix].reset_index(drop=True)
write_dataframe(huc2_df, out_dir / "huc2.fgb")
huc2_df.to_feather(out_dir / "huc2.feather")
huc2 = sorted(huc2_df.HUC2)

# Next, determine the HUC4s that are within these HUC2s that also overlap the region
print("Extracting HUC4...")
huc4_df = read_dataframe(wbd_gdb, layer="WBDHU4", columns=["huc4"]).rename(
    columns={"huc4": "HUC4"}
)
huc4_df["HUC2"] = huc4_df.HUC4.str[:2]
huc4_df = huc4_df.loc[huc4_df.HUC2.isin(huc2)].to_crs(CRS).reset_index(drop=True)

# Extract HUC4s that intersect
tree = shapely.STRtree(huc4_df.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")
huc4_df = huc4_df.iloc[ix].reset_index(drop=True)

# Drop any that are at the edges only and have little overlap
tree = shapely.STRtree(huc4_df.geometry.values.data)
contains_ix = tree.query(bnd, predicate="contains")
edge_ix = np.setdiff1d(np.arange(len(huc4_df)), contains_ix)

# clip geometries by bnd
edge_df = huc4_df.iloc[edge_ix].reset_index(drop=True)
edge_df["clipped"] = shapely.intersection(bnd, edge_df.geometry.values.data)
edge_df["overlap_pct"] = (
    100
    * shapely.area(edge_df.clipped.values.data)
    / shapely.area(edge_df.geometry.values.data)
)

# keep areas that overlap by >= 1%
huc4 = np.unique(
    np.append(
        huc4_df.iloc[contains_ix].HUC4, edge_df.loc[edge_df.overlap_pct >= 1].HUC4
    )
)
huc4_df = huc4_df.loc[huc4_df.HUC4.isin(huc4)].reset_index(drop=True)
write_dataframe(huc4_df, out_dir / "huc4.fgb")
huc4_df.to_feather(out_dir / "huc4.feather")
