import asyncio
from copy import deepcopy
import httpx
from math import ceil
from pathlib import Path

import geopandas as gp
import pandas as pd

from analysis.constants import CRS
from analysis.prep.barriers.lib.arcgis import get_json


URL = "https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_WildScenicRiverEligibleSuitable_01/MapServer/1"


data_dir = Path("data")
out_dir = data_dir / "boundaries/source"


async def download_feature_layer(client, url, fields, batch_size=250):
    # NOTE: this feature layer does not seem able to return as many features as
    # claims to
    # Get total count we expect
    count = (
        await get_json(
            client,
            f"{url}/query",
            params={"where": "1=1", "returnCountOnly": "true"},
        )
    )["count"]

    query = {"where": "1=1", "resultType": "standard", "outFields": ",".join(fields), "f": "geojson"}

    batches = ceil(count / batch_size)

    ### Download batches and merge
    tasks = []
    for offset in range(0, batches * batch_size, batch_size):
        batch_query = deepcopy(query)
        batch_query["resultOffset"] = offset
        batch_query["resultRecordCount"] = batch_size
        tasks.append(asyncio.ensure_future(get_json(client, f"{url}/query", params=batch_query)))

    completed = await asyncio.gather(*tasks)

    merged = None
    for features in completed:
        df = gp.GeoDataFrame.from_features(features, crs="EPSG:4326")

        # drop missing columns to prevent miscasting them based on missing data
        missing = df.columns[df.isnull().all()]
        if len(missing):
            df = df.drop(columns=missing)

        if merged is None:
            merged = df
        else:
            merged = pd.concat([merged, df], ignore_index=True, sort=False)

    return merged


async def download_eligible_suitable():
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=60.0), http2=True) as client:
        df = await download_feature_layer(client, URL, fields=["RIVER_NAME", "ELIGIBLE", "SUITABLE", "STATUS"])

    return df.to_crs(CRS)


df = asyncio.run(download_eligible_suitable())
df = df.rename(columns={"RIVER_NAME": "name", "ELIGIBLE": "eligible", "SUITABLE": "suitable", "STATUS": "status"})
df.to_feather(out_dir / "wsr_eligible_suitable.feather")
