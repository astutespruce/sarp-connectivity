"""
Download NHD Plus HR flowline data for every HUC4 in the SARP region.
"""


from pathlib import Path
import os
from requests import HTTPError

from nhdnet.nhd.download import download_huc4

from analysis.constants import REGIONS


nhd_dir = Path("data/nhd/source/huc4")
if not nhd_dir.exists():
    os.makedirs(nhd_dir)

for HUC2 in REGIONS:
    for i in REGIONS[HUC2]:
        HUC4 = "{0}{1:02d}".format(HUC2, i)
        filename = nhd_dir / "{HUC4}.zip".format(HUC4=HUC4)

        if not os.path.exists(filename):
            try:
                download_huc4(HUC4, filename)
            except HTTPError as ex:
                print(ex)
                pass
