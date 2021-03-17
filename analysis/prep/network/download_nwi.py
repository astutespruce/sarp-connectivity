import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
from time import time

import httpx

import pandas as pd


# Data are available within the NWI Viewer: https://www.fws.gov/wetlands/Data/Mapper.html
# Sometimes the HUC8 is not identified correctly here; if you get a 404 error on download,
# find the same location, download manually, and update to match the missing HUC8 code
URL = "http://www.fws.gov/wetlands/downloads/Watershed/HU8_{huc8}_watershed.zip"
MAX_WORKERS = 2
CONNECTION_TIMEOUT = 120  # seconds


async def download_huc8s(huc8s):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    loop = asyncio.get_event_loop()

    async with httpx.AsyncClient() as client:
        futures = [
            await loop.run_in_executor(executor, download_huc8, huc8, client, out_dir)
            for huc8 in huc8s
        ]
        completed, pending = await asyncio.wait(futures)


async def download_huc8(huc8, client, out_dir):
    r = await client.get(URL.format(huc8=huc8), timeout=CONNECTION_TIMEOUT)
    r.raise_for_status()

    outzipname = out_dir / f"{huc8}.zip"
    with open(outzipname, "wb") as out:
        out.write(r.content)

    print(f"Downloaded {huc8} ({outzipname.stat().st_size >> 20} MB)")


data_dir = Path("data")
out_dir = data_dir / "nwi/source/huc8"

if not out_dir.exists():
    os.makedirs(out_dir)


huc8_df = pd.read_feather(data_dir / "boundaries/huc8.feather", columns=["HUC8"])
huc8_df["HUC2"] = huc8_df.HUC8.str[:2]
# Convert to dict of sorted HUC8s per HUC2
units = huc8_df.groupby("HUC2").HUC8.unique().apply(sorted).to_dict()

# manually subset keys from above for processing
huc2s = [
    "02",
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
    # "21",
]

start = time()

for huc2 in huc2s:
    huc2_start = time()
    print(f"----- {huc2} ------")

    # Skip any that already exist
    huc8s = [id for id in units[huc2] if not (out_dir / f"{id}.zip").exists()]

    if len(huc8s):
        asyncio.run(download_huc8s(huc8s))

    else:
        print("Nothing to download")

    print("--------------------")
    print("HUC2: {} done in {:.0f}s\n\n".format(huc2, time() - huc2_start))

print("Done in {:.2f}s\n============================".format(time() - start))
