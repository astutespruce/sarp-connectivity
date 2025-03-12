import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
from time import time

import geopandas as gp
import pandas as pd
import shapely
import numpy as np
import httpx


# Data are available within the NWI Viewer: https://www.fws.gov/wetlands/Data/Mapper.html
# Sometimes the HUC8 is not identified correctly here; if you get a 404 error on download,
# find the same location, download manually, and update to match the missing HUC8 code
URL = "https://documentst.ecosphere.fws.gov/wetlands/downloads/watershed/HU8_{huc8}_Watershed.zip"

MAX_WORKERS = 2
CONNECTION_TIMEOUT = 120  # seconds


async def download_huc8s(huc8s):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    loop = asyncio.get_event_loop()

    async with httpx.AsyncClient() as client:
        for i in range(0, len(huc8s), MAX_WORKERS):
            chunk = huc8s[i : i + MAX_WORKERS]
            futures = [await loop.run_in_executor(executor, download_huc8, huc8, client, out_dir) for huc8 in chunk]
            await asyncio.gather(*futures)


async def download_huc8(huc8, client, out_dir):
    r = await client.get(URL.format(huc8=huc8), timeout=CONNECTION_TIMEOUT)

    if r.status_code == 404 or r.status_code == 403:
        print(f"WARNING: {huc8} not found for download")
        return

    r.raise_for_status()

    outzipname = out_dir / f"{huc8}.zip"
    with open(outzipname, "wb") as out:
        out.write(r.content)

    print(f"Downloaded {huc8} ({outzipname.stat().st_size / 1e6} MB)")


data_dir = Path("data")
out_dir = data_dir / "nwi/source/huc8"

if not out_dir.exists():
    os.makedirs(out_dir)


huc8_df = gp.read_feather(data_dir / "boundaries/huc8.feather", columns=["HUC8", "geometry"])
huc8_df["HUC2"] = huc8_df.HUC8.str[:2]

# need to filter to only those that occur in the US
states = gp.read_feather(data_dir / "boundaries/states.feather", columns=["geometry"])
tree = shapely.STRtree(huc8_df.geometry.values)
left, right = tree.query(states.geometry.values, predicate="intersects")
ix = np.unique(right)
print(f"Dropping {len(huc8_df) - len(ix):,} HUC8s that are outside U.S.")
huc8_df = huc8_df.iloc[ix].copy()


# Convert to dict of sorted HUC8s per HUC2
units = huc8_df.groupby("HUC2").HUC8.unique().apply(sorted).to_dict()

huc2s = sorted(pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"]).HUC2.values)

# manually subset keys from above for processing
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

start = time()

for huc2 in huc2s:
    huc2_start = time()
    print(f"----- {huc2} ------")

    # Skip any that already exist
    huc8s = [id for id in units[huc2] if not (out_dir / f"{NWI_HUC8_ALIAS.get(id, id)}.zip").exists()]

    if len(huc8s):
        asyncio.run(download_huc8s(huc8s))

    else:
        print("Nothing to download")

    print("--------------------")
    print("HUC2: {} done in {:.0f}s\n\n".format(huc2, time() - huc2_start))

print("Done in {:.2f}s\n============================".format(time() - start))
