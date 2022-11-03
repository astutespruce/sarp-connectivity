import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
from time import time

import geopandas as gp
import shapely
import numpy as np
import httpx

import pandas as pd


# Data are available within the NWI Viewer: https://www.fws.gov/wetlands/Data/Mapper.html
# Sometimes the HUC8 is not identified correctly here; if you get a 404 error on download,
# find the same location, download manually, and update to match the missing HUC8 code
URL = "https://www.fws.gov/wetlands/downloads/Watershed/HU8_{huc8}_watershed.zip"
MAX_WORKERS = 2
CONNECTION_TIMEOUT = 120  # seconds

# current HUC8 to NWI HUC8 codes
HUC8_ALIAS = {"08010300": "08020201", "10170104": "10150001"}


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


huc8_df = gp.read_feather(
    data_dir / "boundaries/huc8.feather", columns=["HUC8", "geometry"]
)
huc8_df["HUC2"] = huc8_df.HUC8.str[:2]

# need to filter to only those that occur in the US
states = gp.read_feather(data_dir / "boundaries/states.feather", columns=["geometry"])
tree = shapely.STRtree(huc8_df.geometry.values.data)
left, right = tree.query_bulk(states.geometry.values.data, predicate="intersects")
ix = np.unique(right)
print(f"Dropping {len(huc8_df) - len(ix):,} HUC8s that are outside U.S.")
huc8_df = huc8_df.iloc[ix].copy()


# Convert to dict of sorted HUC8s per HUC2
units = huc8_df.groupby("HUC2").HUC8.unique().apply(sorted).to_dict()

# manually subset keys from above for processing
huc2s = [
    # "02",
    # "03",
    # "05",
    # "06",
    # "07",
    # "08",  # fix: 08010300 => 08020201
    # "09",
    # "10", # fix: 10170104 => 10150001
    # "11",
    # "12",
    # "13",
    # "14",
    # "15",
    # "16",
    # "17",
    # "18",
    # "21",  # Missing: 21010007, 21010008 (islands)
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
