"""
Download NHD Plus HR flowline data for every HUC4 in the analysis region.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import warnings

import httpx
import pandas as pd

from analysis.prep.network.lib.nhd.download import download_gdb, get_gdb_urls

MAX_WORKERS = 2

# limit downloads in AK to where data are available (updated 8/28/2024)
AK_HUC8 = set(
    [
        # all are on Current (not Beta)
        "19020101",
        "19020102",
        "19020103",
        "19020104",
        "19020201",
        "19020202",
        "19020203",
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
        "19050401",
        "19060102",
        "19060501",
        "19060502",
        "19060504",
        "19060505",
        "19070402",
        "19080301",
        "19080305",
    ]
)


async def download_gdbs(ids, out_dir):
    async with httpx.AsyncClient() as client:
        urls = await get_gdb_urls(client)

        # find any missing ids
        available = [id for id in ids if id in urls]
        missing = sorted(set(ids) - set(available))
        if len(missing):
            warnings.warn(f"units missing from download URLs: {', '.join(missing)}")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            loop = asyncio.get_event_loop()

            for i in range(0, len(available), MAX_WORKERS):
                chunk = available[i : i + MAX_WORKERS]

                futures = [
                    await loop.run_in_executor(executor, download_gdb, urls, id, client, out_dir / f"{id}.zip")
                    for id in chunk
                ]

                await asyncio.gather(*futures)


data_dir = Path("data")
huc4_dir = Path(data_dir / "nhd/source/huc4")
huc4_dir.mkdir(exist_ok=True, parents=True)
huc8_dir = Path(data_dir / "nhd/source/huc8")
huc8_dir.mkdir(exist_ok=True, parents=True)


### Download HUC2s in CONUS by HUC4
huc4s = pd.read_feather(data_dir / "boundaries/huc4.feather", columns=["HUC4"]).HUC4.sort_values()

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
