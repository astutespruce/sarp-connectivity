import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
from pyogrio import read_dataframe
import httpx

from analysis.constants import CRS
from analysis.lib.util import append


URL = "https://www2.census.gov/geo/tiger/TIGER2023/CD/tl_2023_{district:02d}_cd118.zip"

# NOTE: this is a discontiguous series between 01 and 78, some will be missing
DISTRICTS = range(1, 79)

MAX_WORKERS = 2
CONNECTION_TIMEOUT = 120  # seconds


async def download_districts():
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    loop = asyncio.get_event_loop()

    async with httpx.AsyncClient() as client:
        for i in range(0, len(DISTRICTS), MAX_WORKERS):
            chunk = DISTRICTS[i : i + MAX_WORKERS]
            futures = [await loop.run_in_executor(executor, download_district, district, client) for district in chunk]
            await asyncio.gather(*futures)


async def download_district(district, client):
    outzipname = tmp_dir / f"{district:01d}.zip"
    if outzipname.exists():
        # skip existing
        return

    r = await client.get(URL.format(district=district), timeout=CONNECTION_TIMEOUT)

    if r.status_code == 404:
        # this is OK
        return

    r.raise_for_status()

    with open(outzipname, "wb") as out:
        out.write(r.content)

    print(f"Downloaded {district:01d} ({outzipname.stat().st_size >> 20} MB)")


data_dir = Path("data")
out_dir = data_dir / "boundaries/source"
tmp_dir = Path("/tmp/cd")
tmp_dir.mkdir(exist_ok=True)

states = (
    pd.read_feather(data_dir / "boundaries/states.feather", columns=["id", "State", "STATEFIPS"])
    .rename(columns={"id": "state", "State": "state_name"})
    .set_index("STATEFIPS")
)


asyncio.run(download_districts())

merged = None
for filename in tmp_dir.glob("*.zip"):
    df = (
        read_dataframe(filename, columns=["STATEFP", "CD118FP", "NAMELSAD"], use_arrow=True)
        .rename(columns={"STATEFP": "STATEFIPS", "CD118FP": "District", "NAMELSAD": "name"})
        .to_crs(CRS)
    )
    merged = append(merged, df)

df = merged.reset_index(drop=True)
df = df.join(states, on="STATEFIPS")
df["name"] = df.state_name + " " + df.name
df["id"] = df.state + df.District

df.to_feather(out_dir / "congressional_districts.feather")
