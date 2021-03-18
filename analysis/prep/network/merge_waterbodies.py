from pathlib import Path
import os
from time import time
import warnings

import pandas as pd
import geopandas as gp
import pygeos as pg
import numpy as np
from pyogrio import write_dataframe


from analysis.constants import CRS
from analysis.prep.network.lib.waterbodies import find_nhd_waterbody_breaks
from analysis.lib.pygeos_util import explode, dissolve, write_geoms


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"
nwi_dir = data_dir / "nwi/raw"
out_dir = data_dir / "waterbodies"

if not out_dir.exists():
    os.makedirs(out_dir)


huc2s = sorted(
    pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"]).HUC2.values
)
# manually subset keys from above for processing
huc2s = [
    # "02",
    "03",
    # "05",
    # "06",
    # "07",
    # "08",
    # "09",
    # "10",
    # "11",
    # "12",
    # "13",
    "14",
    # "15",
    # "16",
    # "17",
    # "21",
]

start = time()

for huc2 in huc2s:
    huc2_start = time()
    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2
    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    nwi = gp.read_feather(nwi_dir / huc2 / "waterbodies.feather")

    nhd = gp.read_feather(nhd_dir / huc2 / "waterbodies.feather")
    # determine altered types from NHD codes and names
    # note: other waterbodies may be altered but are not marked as such by NHD
    nhd["altered"] = (nhd.FType == 436) | nhd.GNIS_Name.str.lower().str.contains(
        "reservoir"
    )

    df = nhd[["geometry", "altered"]].append(nwi[["geometry", "altered"]])
    altered = df.loc[df.altered].copy()

    if huc2 == "03":
        sc = gp.read_feather("data/states/sc/sc_waterbodies.feather", columns=[])
        sc["altered"] = False  # unknown
        df = df.append(sc[["geometry", "altered"]])

    print(f"Dissolving {len(df):,} waterbodies...")
    dissolve_start = time()
    df["tmp"] = 1
    df = dissolve(df, by="tmp").drop(columns=["tmp"])
    df = explode(df).reset_index(drop=True)
    print(f"Now have {len(df):,} waterbodies ({time() - dissolve_start:,.2f}s)")

    # assign altered if any resulting polygons intersect altered polygons
    tree = pg.STRtree(df.geometry.values.data)
    left, right = tree.query_bulk(altered.geometry.values.data)
    df["altered"] = False
    df.loc[np.unique(right), "altered"] = True

    # cut at breaks from NHD
    nhd_lines_filename = nhd_dir / huc2 / "nhd_lines.feather"
    if nhd_lines_filename.exists():
        print("Checking for breaks between adjacent waterbodies")
        nhd_lines = gp.read_feather(nhd_lines_filename).geometry.values.data
        breaks = find_nhd_waterbody_breaks(nhd.geometry.values.data, nhd_lines)

        if breaks is not None:
            breaks = pg.get_parts(breaks)
            write_geoms(breaks, f"/tmp/{huc2}breaks.gpkg", crs=nhd.crs)
            print(
                f"Cutting NHD waterbodies by {len(breaks):,} breaks at dams to prevent dissolving together"
            )

            # find all pairs of waterbody and breaks, aggregate
            # breaks by waterbody, then calculate difference

            tree = pg.STRtree(df.geometry.values.data)
            left, right = tree.query_bulk(breaks, predicate="intersects")
            pairs = pd.DataFrame(
                {"break_geometry": breaks.take(left)}, index=df.index.take(right)
            )
            grouped = pairs.groupby(level=0).break_geometry.apply(
                lambda g: pg.multipolygons(g.values.data)
            )
            df.loc[grouped.index, "geometry"] = pg.difference(
                df.loc[grouped.index].geometry.values.data, grouped.values
            )

            df = explode(df).reset_index(drop=True)

    # assign a new unique wbID
    df["wbID"] = df.index.values.astype("uint32") + 1 + int(huc2) * 1000000

    df.to_feather(huc2_dir / "waterbodies.feather")
    write_dataframe(df, huc2_dir / "waterbodies.gpkg")

    print("--------------------")
    print(f"HUC2: {huc2} done in {time() - huc2_start:.0f}s\n\n")

print(f"Done in {time() - start:.2f}s\n============================")
