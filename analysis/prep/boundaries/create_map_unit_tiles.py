from pathlib import Path
import subprocess

import geopandas as gp
import shapely
import pandas as pd
from pyogrio import write_dataframe

from analysis.constants import GEO_CRS
from analysis.post.lib.tiles import get_col_types

MAX_ZOOM = "12"

tippecanoe = "tippecanoe"
tile_join = "tile-join"
tippecanoe_args = [tippecanoe, "-f", "-pg", "--visvalingam", "--no-simplification-of-shared-nodes"]

src_dir = Path("data/boundaries")
tile_dir = Path("data/tiles")
out_dir = Path("tiles")
tmp_dir = Path("/tmp")


################################################################################
### Create tiles for full analysis area and regions
################################################################################
print("Creating region tiles")
regions = gp.read_feather(src_dir / "region_boundary.feather")
bnd = regions.loc[regions.id == "total"].geometry.values[0]
outfilename = tmp_dir / "region_boundary.fgb"
write_dataframe(regions, outfilename)
mbtiles_filename = tmp_dir / "region_boundary.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", MAX_ZOOM]
    + ["-l", "boundary"]
    + get_col_types(regions)
    + ["-o", str(mbtiles_filename), outfilename]
)
ret.check_returncode()
outfilename.unlink()


################################################################################
### Create tiles for Fish Habitat Partnership boundaries
################################################################################
print("Creating fish habitat partnership tiles")
fhp = gp.read_feather(src_dir / "fhp_boundary.feather").to_crs(GEO_CRS)
outfilename = tmp_dir / "fhp_boundary.fgb"
write_dataframe(fhp, outfilename)
mbtiles_filename = tmp_dir / "fhp_boundary.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", MAX_ZOOM]
    + ["-l", "fhp_boundary"]
    + get_col_types(fhp)
    + ["-o", str(mbtiles_filename), outfilename]
)
ret.check_returncode()
outfilename.unlink()


################################################################################
### Create state tiles
################################################################################
print("Creating state tiles")
states = gp.read_feather(src_dir / "region_states.feather", columns=["geometry", "id"]).to_crs(GEO_CRS)
outfilename = tmp_dir / "region_states.fgb"
write_dataframe(states, outfilename)
mbtiles_filename = tile_dir / "State.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", MAX_ZOOM]
    + ["-l", "State"]
    + get_col_types(states)
    + ["-o", f"{str(mbtiles_filename)}", str(outfilename)]
)
ret.check_returncode()
outfilename.unlink()


################################################################################
### Create tiles of masks outside regions, FHPs, and states
################################################################################
print("Creating mask tiles")
world = shapely.box(-180, -85, 180, 85)
mask = pd.concat([regions[["id", "geometry"]], fhp[["id", "geometry"]], states[["id", "geometry"]]], ignore_index=True)
mask["id"] = mask.id.values + "_mask"
mask["geometry"] = shapely.normalize(shapely.difference(world, mask.geometry.values))

outfilename = tmp_dir / "mask.fgb"
write_dataframe(mask, outfilename)
mbtiles_filename = tmp_dir / "mask.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", MAX_ZOOM]
    + ["-l", "mask"]
    + get_col_types(mask)
    + ["-o", str(mbtiles_filename), str(outfilename)]
)
ret.check_returncode()
outfilename.unlink()


################################################################################
### Counties
################################################################################
print("Creating county tiles")
df = gp.read_feather(src_dir / "region_counties.feather", columns=["geometry", "id", "name"]).to_crs(GEO_CRS)
outfilename = tmp_dir / "region_counties.fgb"
write_dataframe(df, outfilename)
mbtiles_filename = tile_dir / "County.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "3", "-z", MAX_ZOOM]
    + ["-l", "County"]
    + get_col_types(df)
    + ["-o", f"{str(mbtiles_filename)}", str(outfilename)]
)
ret.check_returncode()
outfilename.unlink()


################################################################################
## HUC2
################################################################################
print("Creating HUC2 tiles")
df = gp.read_feather(src_dir / "HUC2.feather").rename(columns={"HUC2": "id"}).to_crs(GEO_CRS)
outfilename = tmp_dir / "HUC2.fgb"
write_dataframe(df, outfilename)
mbtiles_filename = tile_dir / "HUC2.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", MAX_ZOOM]
    + ["-l", "HUC2"]
    + get_col_types(df)
    + ["-o", f"{str(mbtiles_filename)}", str(outfilename)]
)
ret.check_returncode()
outfilename.unlink()


################################################################################
### HUC6 - HUC12
################################################################################
# have to render all to zoom 14 or boundaries mismatch
huc_zoom_levels = {"HUC6": ["0", MAX_ZOOM], "HUC8": ["0", MAX_ZOOM], "HUC10": ["6", MAX_ZOOM], "HUC12": ["8", MAX_ZOOM]}

for huc, (minzoom, maxzoom) in huc_zoom_levels.items():
    print(f"Creating tiles for {huc}")
    df = gp.read_feather(src_dir / f"{huc}.feather").rename(columns={huc: "id"}).to_crs(GEO_CRS)

    # join watershed priorities to HUC8
    if huc == "HUC8":
        priorities = pd.read_feather(
            "data/boundaries/huc8_priorities.feather",
            columns=["id", "coa"],
        ).set_index("id")
        df = df.join(priorities, on="id")
        df["coa"] = df.coa.fillna(0).astype("uint8")

    # only keep units that actually overlap the region at each level
    tree = shapely.STRtree(df.geometry.values)
    ix = tree.query(bnd, predicate="intersects")
    df = df.loc[ix]

    outfilename = tmp_dir / f"{huc}.fgb"
    write_dataframe(df, outfilename)
    mbtiles_filename = tile_dir / f"{huc}.mbtiles"
    ret = subprocess.run(
        tippecanoe_args
        + ["-Z", minzoom, "-z", maxzoom]
        + ["-l", huc]
        + get_col_types(df)
        + ["-o", f"{str(mbtiles_filename)}", str(outfilename)]
    )
    ret.check_returncode()
    outfilename.unlink()

################################################################################
### Combine all unit tiles into a single tileset
################################################################################
print("Merging all summary unit tiles")
ret = subprocess.run(
    [
        tile_join,
        "-f",
        "-pg",
        "--no-tile-size-limit",
        "-o",
        f"{tile_dir}/map_units.mbtiles",
    ]
    + [
        f"{tmp_dir}/region_boundary.mbtiles",
        f"{tmp_dir}/fhp_boundary.mbtiles",
        f"{tmp_dir}/mask.mbtiles",
    ]
    + [f"{tile_dir}/{unit}.mbtiles" for unit in ["State", "County", "HUC2", "HUC6", "HUC8", "HUC10", "HUC12"]]
)
ret.check_returncode()

print("All done!")
