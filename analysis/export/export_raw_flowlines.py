from pathlib import Path

import pandas as pd
import geopandas as gp

from pyogrio import write_dataframe


data_dir = Path("data")
barriers_dir = data_dir / "barriers/snapped"
nhd_dir = data_dir / "nhd/raw"
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True)

huc2_df = pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"])
huc2s = huc2_df.HUC2.sort_values().values

huc2s = [
    # "02",
    # "03",
    # "05",
    # "06",
    # "07",
    # "08",
    # "09",
    # "10",
    # "11",
    # "12",
    # "13",
    # "14",
    # "15",
    # "16",
    # "17",
    # "18",
    # "21",
]


for huc2 in huc2s:
    print(f"Exporting {huc2}...")
    flowlines = gp.read_feather(nhd_dir / huc2 / "flowlines.feather")
    write_dataframe(flowlines, out_dir / f"region{huc2}_raw_flowlines.shp")
