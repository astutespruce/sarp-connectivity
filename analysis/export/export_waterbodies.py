from pathlib import Path
import warnings

import pandas as pd
import geopandas as gp

from pyogrio import write_dataframe

warnings.filterwarnings("ignore", message=".*organizePolygons.*")


data_dir = Path("data")
src_dir = data_dir / "nhd/clean"
waterbodies_dir = data_dir / "waterbodies"
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True)

huc2_df = pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"])
huc2s = huc2_df.HUC2.sort_values().values

# huc2s = [
#     "01",
#     "02",
#     "03",
#     "04",
#     "05",
#     "06",
#     "07",
#     "08",
#     "09",
#     "10",
#     "11",
#     "12",
#     "13",
#     "14",
#     "15",
#     "16",
#     "17",
#     "18",
#     "19",
#     "20",
#     "21",
# ]


for huc2 in huc2s:
    print(f"Exporting {huc2}...")

    wb = gp.read_feather(waterbodies_dir / huc2 / "waterbodies.feather", columns=[])
    write_dataframe(wb, out_dir / f"region{huc2}_waterbodies.gdb", layer="waterbodies", driver="OpenFileGDB")

    drains = gp.read_feather(src_dir / huc2 / "waterbody_drain_points.feather", columns=[])
    write_dataframe(
        drains, out_dir / f"region{huc2}_waterbodies.gdb", layer="drain_points", driver="OpenFileGDB", append=True
    )
