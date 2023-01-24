from pathlib import Path
from xml.etree import ElementTree

from tqdm import tqdm


CONNECTION_TIMEOUT = 120  # seconds


### NHDPlus High Resolution URLs

# Beta is for everything delivered up until 2022
# Listing URL: https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/
BETA_DATA_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/NHDPLUS_H_{HUC4}_HU4_GDB.zip"

# Current is for anything delivered starting in 2022, with different naming schemes
# Listing URL https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Hydrography/NHDPlusHR/VPU/Current/GDB/
CURRENT_DATA_LIST_URL = "https://prd-tnm.s3.amazonaws.com/?prefix=StagedProducts/Hydrography/NHDPlusHR/VPU/Current/GDB/"
CURRENT_DATA_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/VPU/Current/GDB/NHDPLUS_H_{HUC4}_HU4_{datestamp}_GDB.zip"
CURRENT_HUC2 = ["02", "06", "16"]


HUC4_URL_CACHE = None


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
    # ignore HUC8s for now
    gdbs = [k.text for k in keys if k.text.endswith("_GDB.zip") and "HU4" in k.text]

    huc4_urls = {
        Path(gdb).name.split("_")[2]: f"https://prd-tnm.s3.amazonaws.com/{gdb}"
        for gdb in gdbs
    }

    return huc4_urls


async def download_huc4(HUC4, client, filename):
    """Download HUC4 geodatabase (flowlines and boundaries) from NHD Plus HR data distribution site

    Parameters
    ----------
    HUC4 : str
        HUC4 ID code
    client : httpx client
    filename : str
        output filename.  Will always overwrite this filename.
    """

    huc2 = HUC4[:2]
    if huc2 in CURRENT_HUC2:
        global HUC4_URL_CACHE
        if HUC4_URL_CACHE is None:
            HUC4_URL_CACHE = await get_gdb_urls(client)

        url = HUC4_URL_CACHE[HUC4]

    else:
        url = BETA_DATA_URL.format(HUC4=HUC4)

    print(f"Requesting data from: {url}")

    async with client.stream("GET", url, timeout=CONNECTION_TIMEOUT) as r:
        r.raise_for_status()

        total_bytes = int(r.headers["Content-Length"])

        print(
            "Downloading HUC4: {HUC4} ({size:.2f} MB)".format(
                HUC4=HUC4, size=total_bytes / 1024**2
            )
        )

        with open(filename, "wb") as out:
            with tqdm(total=total_bytes) as bar:

                prev_bytes_downloaded = 0

                async for chunk in r.aiter_bytes():
                    out.write(chunk)

                    bar.update(r.num_bytes_downloaded - prev_bytes_downloaded)
                    prev_bytes_downloaded = r.num_bytes_downloaded
