from pathlib import Path
import os
from time import time

import pandas as pd
import geopandas as gp
import shapely
import numpy as np
from pyogrio import write_dataframe


data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"
nwi_dir = data_dir / "nwi/raw"
out_dir = data_dir / "wetlands"

if not out_dir.exists():
    os.makedirs(out_dir)


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

    huc2_dir = out_dir / huc2
    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    df = gp.read_feather(nwi_dir / huc2 / "wetlands.feather", columns=["geometry", "altered"])
    df["source"] = "NWI"

    # exclude those that are altered
    df = df.loc[~df.altered].copy()

    nhd_filename = nhd_dir / huc2 / "wetlands.feather"
    if nhd_filename.exists():
        nhd = gp.read_feather(nhd_filename, columns=["geometry"])
        nhd["source"] = "NHD"

        # NOTE: NHD has no way to identify altered wetlands

        # only add NHD wetlands that don't intersect those in NWI
        ix = np.unique(shapely.STRtree(df.geometry.values).query(nhd.geometry.values, predicate="intersects")[0])
        nhd = nhd.loc[~nhd.index.isin(ix)]

        df = pd.concat([df[["geometry", "source"]], nhd], ignore_index=True, sort=False)

    df["km2"] = shapely.area(df.geometry.values) / 1e6

    # Exclude those that are effectively riverine
    # NOTE: threshold based on manual review and is arbitrary
    df = df.loc[(df.km2 / (shapely.length(df.geometry.values) / 1e3)) >= 0.0035].reset_index(drop=True)

    # assign a new unique id
    df["id"] = df.index.values.astype("uint32") + 1 + int(huc2) * 1000000

    df.to_feather(huc2_dir / "wetlands.feather")
    write_dataframe(df, huc2_dir / "wetlands.fgb")

    print("--------------------")
    print(f"HUC2: {huc2} done in {time() - huc2_start:.0f}s\n\n")

print(f"Done in {time() - start:.2f}s\n============================")
