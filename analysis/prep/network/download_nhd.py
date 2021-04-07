"""
Download NHD Plus HR flowline data for every HUC4 in the analysis region.
"""


from pathlib import Path
import os
from requests import HTTPError

import pandas as pd

from analysis.prep.network.lib.nhd.download import download_huc4

data_dir = Path("data")

huc4 = pd.read_feather(
    data_dir / "boundaries/huc4.feather", columns=["HUC4"]
).HUC4.sort_values()

nhd_dir = Path(data_dir / "nhd/source/huc4")
if not nhd_dir.exists():
    os.makedirs(nhd_dir)

for id in huc4:
    filename = nhd_dir / f"{id}.zip"

    if not os.path.exists(filename):
        try:
            download_huc4(id, filename)

        except HTTPError as ex:
            print(ex)
            pass
