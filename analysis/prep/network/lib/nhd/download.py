from pathlib import Path
from xml.etree import ElementTree

from tqdm import tqdm


CONNECTION_TIMEOUT = 120  # seconds


### NHDPlus High Resolution URLs

# Beta is for everything delivered up until 2022
# Listing URL: https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/
# HUC_type is HU4 or HU8
BETA_DATA_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/NHDPLUS_H_{HUC}_{HUC_type}_GDB.zip"

# Current is for anything delivered starting in 2022, with different naming schemes
# Listing URL https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Hydrography/NHDPlusHR/VPU/Current/GDB/
CURRENT_DATA_LIST_URL = "https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Hydrography/NHDPlusHR/VPU/Current/GDB/"
CURRENT_DATA_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/VPU/Current/GDB/NHDPLUS_H_{HUC}_{HUC_type}_{datestamp}_GDB.zip"

# NOTE: the updates in 19 are on a HUC8 by HUC8 basis
CURRENT_HUC2 = ["01", "02", "06", "14", "15", "16", "19"]

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
    r = await client.get(CURRENT_DATA_LIST_URL, timeout=CONNECTION_TIMEOUT)
    r.raise_for_status()

    xml = ElementTree.fromstring(r.text)
    keys = xml.findall(
        "s3:Contents/s3:Key", {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    )
    gdbs = [k.text for k in keys if k.text.endswith("_GDB.zip")]

    urls = {
        Path(gdb).name.split("_")[2]: f"https://prd-tnm.s3.amazonaws.com/{gdb}"
        for gdb in gdbs
    }

    return urls


async def download_gdb(id, client, filename):
    """Download HUC4 or HUC8 geodatabase (flowlines and boundaries) from NHD
    Plus HR data distribution site

    Parameters
    ----------
    id : str
        HUC4 or HUC8 code
    client : httpx client
    filename : str
        output filename.  Will always overwrite this filename.
    """

    huc_type = "HU8" if len(id) == 8 else "HU4"

    huc2 = id[:2]
    if huc2 in CURRENT_HUC2:
        global HUC_URL_CACHE
        if HUC_URL_CACHE is None:
            HUC_URL_CACHE = await get_gdb_urls(client)

        if id in HUC_URL_CACHE:
            url = HUC_URL_CACHE[id]
        else:
            url = BETA_DATA_URL.format(HUC=id, HUC_type=huc_type)

    else:
        url = BETA_DATA_URL.format(HUC=id, HUC_type=huc_type)

    print(f"Requesting data from: {url}")

    async with client.stream("GET", url, timeout=CONNECTION_TIMEOUT) as r:
        r.raise_for_status()

        total_bytes = int(r.headers["Content-Length"])

        print(f"Downloading {id} ({total_bytes / 1024**2:.2f} MB)")

        with open(filename, "wb") as out:
            with tqdm(total=total_bytes) as bar:
                prev_bytes_downloaded = 0

                async for chunk in r.aiter_bytes():
                    out.write(chunk)

                    bar.update(r.num_bytes_downloaded - prev_bytes_downloaded)
                    prev_bytes_downloaded = r.num_bytes_downloaded
