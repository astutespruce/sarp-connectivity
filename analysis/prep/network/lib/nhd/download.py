from pathlib import Path
import warnings
from xml.etree import ElementTree

from tqdm import tqdm

MAX_WORKERS = 2  # max number of concurrent downloads
CONNECTION_TIMEOUT = 120  # seconds


### NHDPlus High Resolution URLs

# Beta is for everything delivered up until 2022
# Listing URL: https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/
# HUC_type is HU4 or HU8
BETA_DATA_URL = (
    "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/NHDPLUS_H_{HUC}_{HUC_type}_GDB.zip"
)

# Current is for anything delivered starting in 2022, with different naming schemes
# Listing URL https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Hydrography/NHDPlusHR/VPU/Current/GDB/
DATA_LIST_URL = (
    "https://prd-tnm.s3.amazonaws.com/?delimiter=/&prefix=StagedProducts/Hydrography/NHDPlusHR/VPU/Current/GDB/"
)

HUC_URL_CACHE = None


async def get_gdb_urls(client):
    """Fetch listing of current HUC4 GDB urls

    Parameters
    ----------
    client : httpx client

    Returns
    -------
    dict
        {<huc4>: <url>, ...}
    """
    r = await client.get(DATA_LIST_URL, timeout=CONNECTION_TIMEOUT)
    r.raise_for_status()

    xml = ElementTree.fromstring(r.text)
    keys = xml.findall("s3:Contents/s3:Key", {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"})
    gdbs = [k.text for k in keys if k.text.endswith("_GDB.zip")]

    urls = {Path(gdb).name.split("_")[2]: f"https://prd-tnm.s3.amazonaws.com/{gdb}" for gdb in gdbs}

    return urls


async def download_gdb(urls, id, client, filename):
    """Download HUC4 or HUC8 geodatabase (flowlines and boundaries) from NHD
    Plus HR data distribution site

    Parameters
    ----------
    urls: dict
        lookup table of HUC4 or HUC8 code to data URL
    id : str
        HUC4 or HUC8 code
    client : httpx client
    filename : str
        output filename.  Will always overwrite this filename.
    """

    if id not in urls:
        raise ValueError(f"{id} not available in listing of data URLs")

    url = urls[id]
    # print(f"Requesting data from: {url}")

    async with client.stream("GET", url, timeout=CONNECTION_TIMEOUT) as r:
        if r.status_code == 404:
            warnings.warn(f"WARNING: {id} not found for download")
            return

        r.raise_for_status()

        total_bytes = int(r.headers["Content-Length"])

        # print(f"Downloading {id} ({total_bytes / 1e6:.2f} MB)")

        with open(filename, "wb") as out:
            with tqdm(
                total=total_bytes / 1e6,
                desc=f"HUC {id} ({total_bytes / 1e6:.2f} MB)",
                bar_format="{desc}{bar}| {percentage:3.0f}%",
            ) as bar:
                prev_bytes_downloaded = 0

                async for chunk in r.aiter_bytes():
                    out.write(chunk)

                    bar.update(r.num_bytes_downloaded / 1e6 - prev_bytes_downloaded / 1e6)
                    prev_bytes_downloaded = r.num_bytes_downloaded
