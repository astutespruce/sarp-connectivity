import subprocess
from pathlib import Path

import geopandas as gp
import pandas as pd
from pyogrio import write_dataframe

from analysis.constants import GEO_CRS
from analysis.lib.geometry import dissolve
from analysis.post.lib.tiles import get_col_types

MAX_ZOOM = "12"

tippecanoe = "tippecanoe"
tile_join = "tile-join"
tippecanoe_args = [
    tippecanoe,
    "-f",
    "-pg",
    "--visvalingam",
    "--no-simplification-of-shared-nodes",
    "--drop-smallest-as-needed",
]
tile_join_args = [tile_join, "-f", "-pg", "--no-tile-size-limit"]

src_dir = Path("data/boundaries")
out_dir = Path("tiles")
tmp_dir = Path("/tmp")


################################################################################
### Create tiles for priority areas
### NOTE: only show WSR for zoom >= 5
################################################################################
print("Creating priority area tiles")
df = gp.read_feather(src_dir / "priority_areas.feather").to_crs(GEO_CRS)

# combine protected areas by ownership
print("dissolving protected areas by ownership")
pa = gp.read_feather(src_dir / "protected_areas.feather", columns=["geometry", "OwnerType"])
# per direction from Kat (3/17/2026) drop USFS admin boundary
pa = pa.loc[~pa.OwnerType.isin([0, 7])].copy()
pa = dissolve(pa, by="OwnerType")
pa = pa.to_crs(GEO_CRS)
# do lookup client side to type
pa = pa.rename(columns={"OwnerType": "name"})
pa["name"] = pa.name.astype("str")
pa["type"] = "pa_" + pa.name.values


df = pd.concat([df, pa], ignore_index=True)

print("Creating tiles...")
tilesets = []

### show all types for zoom >= 5
outfilename = tmp_dir / "priority_areas_gt_z5.fgb"
write_dataframe(df, outfilename)
pmtiles_filename = tmp_dir / "priority_areas_gt_z5.pmtiles"
tilesets.append(pmtiles_filename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "5", "-z", MAX_ZOOM]
    + ["-l", "priority_areas"]
    + get_col_types(df)
    + ["-o", str(pmtiles_filename), outfilename],
    check=True,
)
ret.check_returncode()
outfilename.unlink()


### exclude WSR for zooms <= 5
outfilename = tmp_dir / "priority_areas_lt_z5.fgb"
write_dataframe(df.loc[(df["type"] != "wsr")], outfilename)
pmtiles_filename = tmp_dir / "priority_areas_lt_z5.pmtiles"
tilesets.append(pmtiles_filename)
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", "4"]
    + ["-l", "priority_areas"]
    + get_col_types(df)
    + ["-o", str(pmtiles_filename), outfilename],
    check=True,
)
ret.check_returncode()
outfilename.unlink()

### join tiles
pmtiles_filename = out_dir / "priority_areas.pmtiles"
ret = subprocess.run(tile_join_args + ["-o", str(pmtiles_filename)] + [str(f) for f in tilesets], check=True)

# remove intermediates
for filename in tilesets:
    filename.unlink()
