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
out_dir = Path("tiles")
tmp_dir = Path("/tmp")


################################################################################
### Create tiles for full analysis area and regions
################################################################################
print("Creating region tiles")
df = gp.read_feather(src_dir / "priority_areas.feather").to_crs(GEO_CRS)
outfilename = tmp_dir / "priority_areas.fgb"
write_dataframe(df, outfilename)
mbtiles_filename = out_dir / "priority_areas.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", MAX_ZOOM]
    + ["-l", "priority_areas"]
    + get_col_types(df)
    + ["-o", str(mbtiles_filename), outfilename]
)
ret.check_returncode()
outfilename.unlink()
