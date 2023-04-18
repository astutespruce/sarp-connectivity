"""
Download NHD Plus HR flowline data for every HUC4 in the analysis region.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import pandas as pd

from analysis.prep.network.lib.nhd.download import download_gdb

MAX_WORKERS = 2

# limit downloads in AK to where data are available (updated 4/11/2023)
AK_HUC8 = set(
    [
        # Beta
        "19020101",
        "19020102",
        "19020103",
        "19020104",
        "19020202",
        "19020301",
        "19020302",
        "19020401",
        "19020402",
        "19020501",
        "19020502",
        "19020503",
        "19020504",
        "19020505",
        "19020601",
        "19020602",
        "19020800",
        "19060102",
        "19070402",
        "19080301",
        "19080305",
    ]
    + [
        # Current
        "19020203",
        "19050401",
        "19060501",
        "19060502",
        "19060504",
        "19060505",
    ]
)


# FIXME: this seems to be downloading all hucs concurrently instead of only 2 at a time
async def download_gdbs(ids, out_dir):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        loop = asyncio.get_event_loop()

        async with httpx.AsyncClient() as client:
            futures = [
                await loop.run_in_executor(
                    executor, download_gdb, id, client, out_dir / f"{id}.zip"
                )
                for id in ids
            ]

            await asyncio.gather(*futures)


data_dir = Path("data")
huc4_dir = Path(data_dir / "nhd/source/huc4")
huc4_dir.mkdir(exist_ok=True, parents=True)
huc8_dir = Path(data_dir / "nhd/source/huc8")
huc8_dir.mkdir(exist_ok=True, parents=True)


### Download HUC2s in CONUS by HUC4
huc4s = pd.read_feather(
    data_dir / "boundaries/huc4.feather", columns=["HUC4"]
).HUC4.sort_values()

# skip HUC4s in AK
huc4s = [huc4 for huc4 in huc4s if not huc4.startswith("19")]

# skip any that already exist
huc4s = sorted([huc4 for huc4 in huc4s if not (huc4_dir / f"{huc4}.zip").exists()])

if len(huc4s):
    asyncio.run(download_gdbs(huc4s, huc4_dir))

### Download Alaska by HUC8
# NHD delivers data in AK by HUC8 instead of HUC4; shim these in so they behave
# like HUC4s for the downloader
huc8s = sorted([huc8 for huc8 in AK_HUC8 if not (huc8_dir / f"{huc8}.zip").exists()])

if len(huc8s):
    asyncio.run(download_gdbs(huc8s, huc8_dir))
