from pathlib import Path
import os
from time import time
import warnings

import pandas as pd
import geopandas as gp
import pygeos as pg
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS
from analysis.lib.pygeos_util import dissolve, explode
from analysis.lib.util import append


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
src_dir = data_dir / "nwi/source/huc8"
nhd_dir = data_dir / "nhd/raw"  # intentionally use raw flowlines
out_dir = data_dir / "nwi/raw"

if not out_dir.exists():
    os.makedirs(out_dir)

start = time()

huc8_df = pd.read_feather(data_dir / "boundaries/huc8.feather", columns=["HUC8"])
huc8_df["HUC2"] = huc8_df.HUC8.str[:2]
# Convert to dict of sorted HUC8s per HUC2
units = huc8_df.groupby("HUC2").HUC8.unique().apply(sorted).to_dict()

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
    # "14",
    # "15",
    # "16",
    # "17",
    # "21",
]


for huc2 in huc2s:
    huc2_start = time()
    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2
    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    print("Reading flowlines")
    flowlines = gp.read_feather(nhd_dir / huc2 / "flowlines.feather", columns=[])
    tree = pg.STRtree(flowlines.geometry.values.data)

    waterbodies = None
    rivers = None
    for huc8 in units[huc2]:
        print(f"Reading NWI data for {huc8}")

        # Extract and merge lakes and wetlands
        df = read_dataframe(
            f"/vsizip/{src_dir.resolve()}/{huc8}.zip/HU8_{huc8}_Watershed/HU8_{huc8}_Wetlands.shp",
            columns=["ATTRIBUTE", "WETLAND_TY"],
            where="WETLAND_TY in ('Lake', 'Pond', 'Riverine')",
        ).rename(columns={"ATTRIBUTE": "nwi_code", "WETLAND_TY": "nwi_type"})

        # some geometries are invalid, filter them out
        df = df.loc[pg.is_geometry(df.geometry.values.data)].copy()

        if not len(df):
            continue

        df = df.to_crs(CRS)

        # Mark structurally altered types where
        # codes with x (excavated), d (ditched), r (artificial substrate), h (diked)
        # strip any terminal numbers then take last character
        modifier = df.nwi_code.str.rstrip("123456789").str[-1:]
        df["altered"] = modifier.isin(["d", "h", "r", "x"])

        waterbodies = append(waterbodies, df.loc[df.nwi_type.isin(["Lake", "Pond"])])
        rivers = append(rivers, df.loc[(df.nwi_type == "Riverine") & (df.altered)])

    ### Process waterbodies
    # only keep that intersect flowlines
    print(f"Extracted {len(waterbodies):,} NWI lakes and ponds")
    left, right = tree.query_bulk(
        waterbodies.geometry.values.data, predicate="intersects"
    )
    waterbodies = waterbodies.iloc[np.unique(left)].reset_index(drop=True)
    print(f"Kept {len(waterbodies):,} that intersect flowlines")

    # TODO: explode, repair, dissolve, explode, reset index
    waterbodies = explode(waterbodies)
    # make valid
    ix = ~pg.is_valid(waterbodies.geometry.values.data)
    if ix.sum():
        print(f"Repairing {ix.sum():,} invalid waterbodies")
        waterbodies.loc[ix, "geometry"] = pg.make_valid(
            waterbodies.loc[ix].geometry.values.data
        )

    # note: nwi_code, nwi_type are discarded here since they aren't used later
    print("Dissolving adjacent waterbodies")
    waterbodies = dissolve(waterbodies, by=["altered"])
    waterbodies = explode(waterbodies).reset_index(drop=True)

    waterbodies["km2"] = pg.area(waterbodies.geometry.values.data) / 1e6

    waterbodies.to_feather(huc2_dir / "waterbodies.feather")
    write_dataframe(waterbodies, huc2_dir / "waterbodies.gpkg")

    ### Process riverine
    print(f"Extracted {len(rivers):,} NWI altered river polygons")
    left, right = tree.query_bulk(rivers.geometry.values.data, predicate="intersects")
    rivers = rivers.iloc[np.unique(left)].reset_index(drop=True)
    print(f"Kept {len(rivers):,} that intersect flowlines")

    rivers = explode(rivers)
    # make valid
    ix = ~pg.is_valid(rivers.geometry.values.data)
    if ix.sum():
        print(f"Repairing {ix.sum():,} invalid rivers")
        rivers.loc[ix, "geometry"] = pg.make_valid(rivers.loc[ix].geometry.values.data)

    print("Dissolving adjacent rivers")
    rivers = dissolve(rivers, by=["altered"])
    rivers = explode(rivers).reset_index(drop=True)

    rivers.to_feather(huc2_dir / "altered_rivers.feather")
    write_dataframe(rivers, huc2_dir / "altered_rivers.gpkg")

    print("--------------------")
    print("HUC2: {} done in {:.0f}s\n\n".format(huc2, time() - huc2_start))

print("Done in {:.2f}s\n============================".format(time() - start))