"""
Download NHD Plus HR flowline data for every HUC4 in the analysis region.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import pandas as pd

from analysis.prep.network.lib.nhd.download import download_huc4

MAX_WORKERS = 2


# FIXME: this seems to be downloading all huc4s concurrently instead of only 2 at a time
async def download_huc4s(huc4s, out_dir):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        loop = asyncio.get_event_loop()

        async with httpx.AsyncClient() as client:
            futures = [
                await loop.run_in_executor(
                    executor, download_huc4, huc4, client, out_dir / f"{huc4}.zip"
                )
                for huc4 in huc4s
            ]

            await asyncio.gather(*futures)


data_dir = Path("data")
out_dir = Path(data_dir / "nhd/source/huc4")
out_dir.mkdir(exist_ok=True, parents=True)

huc4s = pd.read_feather(
    data_dir / "boundaries/huc4.feather", columns=["HUC4"]
).HUC4.sort_values()


# skip any that already exist
huc4s = sorted([huc4 for huc4 in huc4s if not (out_dir / f"{huc4}.zip").exists()])

if len(huc4s):
    asyncio.run(download_huc4s(huc4s, out_dir))
