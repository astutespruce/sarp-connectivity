from pathlib import Path
import os
from time import time
import warnings

import pandas as pd
import geopandas as gp
import shapely
import numpy as np
from pyogrio import write_dataframe

from analysis.lib.geometry import explode, dissolve, write_geoms
from analysis.prep.network.lib.nhd import find_nhd_waterbody_breaks


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
# huc2s = [
# "02",
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
# "18",
# "21",
# ]

start = time()

print("Reading state level datasets")

overlaps_or_ca = False
overlaps_sd = False
if set(huc2s).intersection(["16", "17", "18"]):
    overlaps_or_ca = True
    ca_wb = gp.read_feather(
        "data/states/ca/ca_waterbodies.feather", columns=["geometry", "altered", "HUC2"]
    )
    or_wb = gp.read_feather(
        "data/states/or/or_waterbodies.feather", columns=["geometry", "altered", "HUC2"]
    )
    wa_wb = gp.read_feather(
        "data/states/wa/wa_waterbodies.feather", columns=["geometry", "altered"]
    )

if set(huc2s).intersection(["07", "09", "10"]):
    overlaps_sd = True
    sd_wb = gp.read_feather(
        "data/states/sd/sd_waterbodies.feather", columns=["geometry", "HUC2"]
    )
    sd_wb["altered"] = False


for huc2 in huc2s:
    huc2_start = time()
    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2
    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    nhd = gp.read_feather(
        nhd_dir / huc2 / "waterbodies.feather",
        columns=["geometry", "FType", "GNIS_Name"],
    )
    # determine altered types from NHD codes and names
    # note: other waterbodies may be altered but are not marked as such by NHD
    nhd["altered"] = (nhd.FType == 436) | nhd.GNIS_Name.str.lower().str.contains(
        "reservoir"
    )

    nwi = gp.read_feather(nwi_dir / huc2 / "waterbodies.feather")

    df = pd.concat(
        [nhd[["geometry", "altered"]], nwi[["geometry", "altered"]]],
        ignore_index=True,
        sort=False,
    )

    altered = df.loc[df.altered].copy()

    if huc2 == "03":
        sc_wb = gp.read_feather("data/states/sc/sc_waterbodies.feather", columns=[])
        sc_wb["altered"] = False  # unknown
        df = pd.concat(
            [df, sc_wb[["geometry", "altered"]]], ignore_index=True, sort=False
        )

    elif huc2 == "17":
        df = pd.concat(
            [df, wa_wb[["geometry", "altered"]]], ignore_index=True, sort=False
        )

    if overlaps_or_ca:
        df = pd.concat(
            [df, or_wb.loc[or_wb.HUC2 == huc2, ["geometry", "altered"]]],
            ignore_index=True,
            sort=False,
        )
        df = pd.concat(
            [df, ca_wb.loc[ca_wb.HUC2 == huc2, ["geometry", "altered"]]],
            ignore_index=True,
            sort=False,
        )

    if overlaps_sd:
        df = pd.concat(
            [df, sd_wb.loc[sd_wb.HUC2 == huc2, ["geometry", "altered"]]],
            ignore_index=True,
            sort=False,
        )

    print(f"Dissolving {len(df):,} waterbodies...")
    dissolve_start = time()
    df["tmp"] = 1
    df = dissolve(df, by="tmp").drop(columns=["tmp"])
    df = explode(df).reset_index(drop=True)
    print(f"Now have {len(df):,} waterbodies ({time() - dissolve_start:,.2f}s)")

    # assign altered if any resulting polygons intersect altered polygons
    tree = shapely.STRtree(df.geometry.values.data)
    left, right = tree.query(altered.geometry.values.data)
    df["altered"] = False
    df.loc[np.unique(right), "altered"] = True

    # cut at breaks from NHD
    nhd_lines_filename = nhd_dir / huc2 / "nhd_lines.feather"
    if nhd_lines_filename.exists():
        print("Checking for breaks between adjacent waterbodies")
        nhd_lines = gp.read_feather(nhd_lines_filename).geometry.values.data
        breaks = find_nhd_waterbody_breaks(nhd.geometry.values.data, nhd_lines)

        if breaks is not None:
            breaks = shapely.get_parts(breaks)
            write_geoms(breaks, f"/tmp/{huc2}breaks.fgb", crs=nhd.crs)
            print(
                f"Cutting NHD waterbodies by {len(breaks):,} breaks at dams to prevent dissolving together"
            )

            # find all pairs of waterbody and breaks, aggregate
            # breaks by waterbody, then calculate difference

            tree = shapely.STRtree(df.geometry.values.data)
            left, right = tree.query(breaks, predicate="intersects")
            pairs = pd.DataFrame(
                {"break_geometry": breaks.take(left)}, index=df.index.take(right)
            )
            grouped = pairs.groupby(level=0).break_geometry.apply(
                lambda g: shapely.multipolygons(g.values.data)
            )
            df.loc[grouped.index, "geometry"] = shapely.difference(
                df.loc[grouped.index].geometry.values.data, grouped.values
            )

            df = explode(df).reset_index(drop=True)

    # make sure all polygons are valid
    ix = ~shapely.is_valid(df.geometry.values.data)
    if ix.sum():
        print(f"Repairing {ix.sum()} invalid waterbodies")
        df.loc[ix, "geometry"] = shapely.make_valid(df.loc[ix].geometry.values.data)
        df = explode(explode(df))
        df = df.loc[shapely.get_type_id(df.geometry.values.data) == 3].reset_index()

    # assign a new unique wbID
    df["wbID"] = df.index.values.astype("uint32") + 1 + int(huc2) * 1000000
    df["km2"] = shapely.area(df.geometry.values.data) / 1e6

    df.to_feather(huc2_dir / "waterbodies.feather")
    write_dataframe(df, huc2_dir / "waterbodies.fgb")

    print("--------------------")
    print(f"HUC2: {huc2} done in {time() - huc2_start:.0f}s\n\n")

print(f"Done in {time() - start:.2f}s\n============================")
