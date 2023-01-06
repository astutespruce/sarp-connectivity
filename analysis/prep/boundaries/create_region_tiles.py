from pathlib import Path
import subprocess

import geopandas as gp
import shapely
import pandas as pd
from pyogrio import write_dataframe

from analysis.constants import GEO_CRS
from analysis.post.lib.tiles import get_col_types


# use local clone of github.com/tippecanoe
tippecanoe = "../lib/tippecanoe/tippecanoe"


tippecanoe_args = [tippecanoe, "-f", "-pg", "--visvalingam", "--detect-shared-borders"]


src_dir = Path("data/boundaries")
tile_dir = Path("data/tiles")
tmp_dir = Path("/tmp")


### Full analysis area and regions
print("Creating region tiles")
df = gp.read_feather(src_dir / "region_boundary.feather").to_crs(GEO_CRS)
bnd = df.loc[df.id == "total"].geometry.values.data[0]
outfilename = tmp_dir / "region_boundary.fgb"
write_dataframe(df, outfilename)
mbtiles_filename = tile_dir / "boundary.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", "8"]
    + ["-l", "boundary"]
    + get_col_types(df)
    + ["-o", f"{str(mbtiles_filename)}", outfilename]
)
ret.check_returncode()
outfilename.unlink()


### Mask of full analysis area and regions
print("Creating mask tiles")
df = gp.read_feather(src_dir / "region_mask.feather").to_crs(GEO_CRS)
outfilename = tmp_dir / "region_mask.fgb"
write_dataframe(df, outfilename)
mbtiles_filename = tile_dir / "mask.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", "8"]
    + ["-l", "mask"]
    + get_col_types(df)
    + ["-o", f"{str(mbtiles_filename)}", str(outfilename)]
)
ret.check_returncode()
outfilename.unlink()


### States
print("Creating state tiles")
df = gp.read_feather(
    src_dir / "region_states.feather", columns=["geometry", "id"]
).to_crs(GEO_CRS)
outfilename = tmp_dir / "region_states.fgb"
write_dataframe(df, outfilename)
mbtiles_filename = tile_dir / "State.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", "8"]
    + ["-l", "State"]
    + get_col_types(df)
    + ["-o", f"{str(mbtiles_filename)}", str(outfilename)]
)
ret.check_returncode()
outfilename.unlink()


### Counties
print("Creating county tiles")
df = gp.read_feather(
    src_dir / "region_counties.feather", columns=["geometry", "id", "name"]
).to_crs(GEO_CRS)
outfilename = tmp_dir / "region_counties.fgb"
write_dataframe(df, outfilename)
mbtiles_filename = tile_dir / "County.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "3", "-z", "12"]
    + ["-l", "County"]
    + get_col_types(df)
    + ["-o", f"{str(mbtiles_filename)}", str(outfilename)]
)
ret.check_returncode()
outfilename.unlink()


## HUC2
print("Creating HUC2 tiles")
df = (
    gp.read_feather(src_dir / "HUC2.feather")
    .rename(columns={"HUC2": "id"})
    .to_crs(GEO_CRS)
)
outfilename = tmp_dir / "HUC2.fgb"
write_dataframe(df, outfilename)
mbtiles_filename = tile_dir / "HUC2.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", "8"]
    + ["-l", "HUC2"]
    + get_col_types(df)
    + ["-o", f"{str(mbtiles_filename)}", str(outfilename)]
)
ret.check_returncode()
outfilename.unlink()

### HUC6 - HUC12
# have to render all to zoom 14 or boundaries mismatch
huc_zoom_levels = {"HUC6": [0, 14], "HUC8": [0, 14], "HUC10": [6, 14], "HUC12": [8, 14]}

for huc, (minzoom, maxzoom) in huc_zoom_levels.items():
    print(f"Creating tiles for {huc}")
    df = (
        gp.read_feather(src_dir / f"{huc}.feather")
        .rename(columns={huc: "id"})
        .to_crs(GEO_CRS)
    )

    # join watershed priorities to HUC8
    if huc == "HUC8":
        priorities = pd.read_feather(
            "data/boundaries/huc8_priorities.feather",
            columns=["id", "coa"],
        ).set_index("id")
        df = df.join(priorities, on="id")
        df["coa"] = df.coa.fillna(0).astype("uint8")

    # only keep units that actually overlap the region at each level
    tree = shapely.STRtree(df.geometry.values.data)
    ix = tree.query(bnd, predicate="intersects")
    df = df.loc[ix]

    outfilename = tmp_dir / f"{huc}.fgb"
    write_dataframe(df, outfilename)
    mbtiles_filename = tile_dir / f"{huc}.mbtiles"
    ret = subprocess.run(
        tippecanoe_args
        + ["-Z", str(minzoom), "-z", str(maxzoom)]
        + ["-l", huc]
        + get_col_types(df)
        + ["-o", f"{str(mbtiles_filename)}", str(outfilename)]
    )
    ret.check_returncode()
    outfilename.unlink()


print("All done!")
