from pathlib import Path

import geopandas as gp
import shapely
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import STATES, CRS, GEO_CRS, REGION_STATES
from analysis.lib.geometry import to_multipolygon


# HUC4s in Mexico that are not available from NHD
MISSING_HUC4 = ["1310", "1311", "1312"]


data_dir = Path("data")
out_dir = data_dir / "boundaries"
ui_dir = Path("ui/data")

state_filename = data_dir / "boundaries/source/tl_2022_us_state.shp"
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

# drop holes within HUC2s (04, 19)
huc2_df = huc2_df.explode(ignore_index=True)
huc2_df["geometry"] = shapely.polygons(
    shapely.get_exterior_ring(huc2_df.geometry.values)
)
huc2_df = gp.GeoDataFrame(
    huc2_df.groupby("HUC2").agg({"name": "first", "geometry": shapely.multipolygons}),
    geometry="geometry",
    crs=huc2_df.crs,
).reset_index()

write_dataframe(huc2_df, out_dir / "huc2.fgb")
huc2_df.to_feather(out_dir / "huc2.feather")
huc2 = sorted(huc2_df.HUC2)

# Use all HUC4s in these HUC2s
print("Extracting HUC4...")
huc4_df = read_dataframe(wbd_gdb, layer="WBDHU4", columns=["huc4"]).rename(
    columns={"huc4": "HUC4"}
)
huc4_df["HUC2"] = huc4_df.HUC4.str[:2]
huc4_df = (
    huc4_df.loc[huc4_df.HUC2.isin(huc2) & (~huc4_df.HUC4.isin(MISSING_HUC4))]
    .to_crs(CRS)
    .reset_index(drop=True)
)

write_dataframe(huc4_df, out_dir / "huc4.fgb")
huc4_df.to_feather(out_dir / "huc4.feather")
