from pathlib import Path
import os
from time import time
import warnings

import geopandas as gp
import pygeos as pg
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS
from analysis.lib.geometry import dissolve, explode
from analysis.lib.util import append

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


MODIFIERS = {
    "d": "Drained/Ditched",
    "h": "Diked/Impounded",
    "r": "Artificial Substrate",
    "x": "Excavated",
}

# see: https://www.fws.gov/wetlands/documents/NWI_Wetlands_and_Deepwater_Map_Code_Diagram.pdf
PERMANENCE_MODIFIERS = {
    "A": "Temporarily Flooded",
    "B": "Seasonally Saturated",
    "C": "Seasonally Flooded",
    "D": "Continuously Saturated",
    "E": "Seasonally Flooded / Saturated",
    "F": "Semipermanently Flooded",
    "G": "Intermittently Exposed",
    "H": "Permanently Flooded",
    "J": "Intermittently Flooded",
    "K": "Artificially Flooded",
}


data_dir = Path("data")
src_dir = data_dir / "nwi/source/huc8"
nhd_dir = data_dir / "nhd/raw"  # intentionally use raw flowlines
out_dir = data_dir / "nwi/raw"

if not out_dir.exists():
    os.makedirs(out_dir)

start = time()


huc8_df = gp.read_feather(
    data_dir / "boundaries/huc8.feather", columns=["HUC8", "geometry"]
)
huc8_df["HUC2"] = huc8_df.HUC8.str[:2]

# need to filter to only those that occur in the US
states = gp.read_feather(data_dir / "boundaries/states.feather", columns=["geometry"])
tree = pg.STRtree(huc8_df.geometry.values.data)
left, right = tree.query_bulk(states.geometry.values.data, predicate="intersects")
ix = np.unique(right)
print(f"Dropping {len(huc8_df) - len(ix):,} HUC8s that are outside U.S.")
huc8_df = huc8_df.iloc[ix].copy()


# Convert to dict of sorted HUC8s per HUC2
units = huc8_df.groupby("HUC2").HUC8.unique().apply(sorted).to_dict()
huc2s = units.keys()

# manually subset keys from above for processing
huc2s = [
    #     "02",
    #     "03",
    # "05",
    #     "06",
    #     "07",
    # "08",
    #     "09",
    #     "10",
    #     "11",
    #     "12",
    #     "13",
    #     "14",
    #     "15",
    "16",
    "17",
    "18",
    #     "21",  # Missing: 21010008 (islands)
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

        filename = src_dir.resolve() / f"{huc8}.zip"
        if not filename.exists():
            print(f"WARNING: {filename} not found")
            continue

        # Extract and merge lakes and wetlands
        df = read_dataframe(
            f"/vsizip/{filename}/HU8_{huc8}_Watershed/HU8_{huc8}_Wetlands.shp",
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

        df["modifier"] = df.nwi_code.str.rstrip("123456789").str[-1:]
        df["altered"] = df.modifier.isin(MODIFIERS)

        waterbodies = append(waterbodies, df.loc[df.nwi_type.isin(["Lake", "Pond"])])
        rivers = append(
            rivers,
            df.loc[(df.nwi_type == "Riverine") & (df.altered)].drop(
                columns=["nwi_type"]
            ),
        )

    ### Process waterbodies
    # only keep that intersect flowlines
    print(f"Extracted {len(waterbodies):,} NWI lakes and ponds")
    left, right = tree.query_bulk(
        waterbodies.geometry.values.data, predicate="intersects"
    )
    waterbodies = waterbodies.iloc[np.unique(left)].reset_index(drop=True)
    print(f"Kept {len(waterbodies):,} that intersect flowlines")

    # drop intermittent / seasonal waterbodies we don't want to include;
    # if they are permanent enough, NHD will pick them up
    waterbodies = waterbodies.loc[
        ~waterbodies.modifier.isin(["A", "B", "C", "D", "E", "G", "J"])
    ].reset_index(drop=True)

    # TODO: explode, repair, dissolve, explode, reset index
    waterbodies = explode(waterbodies)
    # make valid
    ix = ~pg.is_valid(waterbodies.geometry.values.data)
    if ix.sum():
        print(f"Repairing {ix.sum():,} invalid waterbodies")
        waterbodies.loc[ix, "geometry"] = pg.make_valid(
            waterbodies.loc[ix].geometry.values.data
        )

    # cleanup any that collapsed to other geometry types during make valid or import
    waterbodies = waterbodies.loc[
        pg.get_type_id(waterbodies.geometry.values.data) == 3
    ].reset_index()

    # note: nwi_code, nwi_type are discarded here since they aren't used later
    print("Dissolving adjacent waterbodies")
    waterbodies = dissolve(waterbodies, by=["altered"])
    waterbodies = explode(waterbodies).reset_index(drop=True)

    waterbodies["km2"] = pg.area(waterbodies.geometry.values.data) / 1e6

    waterbodies.to_feather(huc2_dir / "waterbodies.feather")
    write_dataframe(waterbodies, huc2_dir / "waterbodies.fgb")

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

    # cleanup any that collapsed to other geometry types during make valid or import
    rivers = rivers.loc[pg.get_type_id(rivers.geometry.values.data) == 3].reset_index()

    rivers["modifier"] = rivers.modifier.map(MODIFIERS)

    rivers.to_feather(huc2_dir / "altered_rivers.feather")
    write_dataframe(rivers, huc2_dir / "altered_rivers.fgb")

    print("--------------------")
    print("HUC2: {} done in {:.0f}s\n\n".format(huc2, time() - huc2_start))

print("Done in {:.2f}s\n============================".format(time() - start))
