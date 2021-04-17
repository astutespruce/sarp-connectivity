from pathlib import Path
import os

import pandas as pd
from pyogrio import write_dataframe

from analysis.lib.io import read_feathers


data_dir = Path("data")
out_dir = Path("/tmp/sarp")

if not out_dir.exists():
    os.makedirs(out_dir)


huc4_df = pd.read_feather(data_dir / "boundaries/huc4.feather", columns=["HUC2"],)
huc2s = huc4_df.HUC2.unique()

df = read_feathers(
    [data_dir / "nhd/raw" / huc2 / "nhd_altered_rivers.feather" for huc2 in huc2s],
    geo=True,
    new_fields={"HUC2": huc2s},
)


write_dataframe(df, out_dir / "nhd_altered_rivers.shp")


df = read_feathers(
    [data_dir / "nwi/raw" / huc2 / "altered_rivers.feather" for huc2 in huc2s],
    geo=True,
    new_fields={"HUC2": huc2s},
)


write_dataframe(df, out_dir / "nwi_altered_rivers.shp")
