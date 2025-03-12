from pathlib import Path
from time import time

import geopandas as gp
import shapely
import numpy as np
from pyogrio import read_dataframe, write_dataframe
from pyogrio.errors import DataSourceError

from analysis.constants import CRS
from analysis.lib.geometry import dissolve
from analysis.lib.util import append

# ignore natural modifiers (e.g., beaver)
MODIFIERS = {
    "d": "Drained/Ditched",
    "h": "Diked/Impounded",
    "f": "Farmed",
    "m": "managed",
    "r": "Artificial Substrate",
    "s": "Spoil",
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

WETLAND_PREFIXES = ["PFO", "PSS", "PEM"]


data_dir = Path("data")
src_dir = data_dir / "nwi/source/huc8"
nhd_dir = data_dir / "nhd/raw"  # intentionally use raw flowlines
out_dir = data_dir / "nwi/raw"
out_dir.mkdir(exist_ok=True)

start = time()


huc8_df = gp.read_feather(data_dir / "boundaries/huc8.feather", columns=["HUC8", "geometry"])
huc8_df["HUC2"] = huc8_df.HUC8.str[:2]

# need to filter to only those that occur in the US
states = gp.read_feather(data_dir / "boundaries/states.feather", columns=["geometry"])
tree = shapely.STRtree(huc8_df.geometry.values)
left, right = tree.query(states.geometry.values, predicate="intersects")
ix = np.unique(right)
print(f"Dropping {len(huc8_df) - len(ix):,} HUC8s that are outside U.S.")
huc8_df = huc8_df.iloc[ix].copy()


# Convert to dict of sorted HUC8s per HUC2
units = huc8_df.groupby("HUC2").HUC8.unique().apply(sorted).to_dict()
huc2s = units.keys()

# manually subset keys from above for processing
# huc2s = [
# "01",
# "02",
# "03",
# "04",
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
# "19",
# "20",
# "21",
# ]


for huc2 in huc2s:
    huc2_start = time()
    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2
    huc2_dir.mkdir(exist_ok=True)

    print("Reading flowlines")
    flowlines = gp.read_feather(nhd_dir / huc2 / "flowlines.feather", columns=[])
    tree = shapely.STRtree(flowlines.geometry.values)

    waterbodies = None
    rivers = None
    wetlands = None
    for huc8 in units[huc2]:
        print(f"Reading NWI data for {huc8}")

        filename = src_dir.resolve() / f"{huc8}.zip"
        if not filename.exists():
            print(f"WARNING: {filename} not found")
            continue

        # Extract and merge lakes and wetlands
        try:
            wetland_expr = " OR ".join(f"ATTRIBUTE LIKE '{prefix}%'" for prefix in WETLAND_PREFIXES)
            df = read_dataframe(
                f"/vsizip/{filename}/HU8_{huc8}_Watershed/HU8_{huc8}_Wetlands.shp",
                columns=["ATTRIBUTE", "WETLAND_TY"],
                use_arrow=True,
                where=f"WETLAND_TY in ('Lake', 'Pond', 'Riverine') OR {wetland_expr}",
            ).rename(columns={"ATTRIBUTE": "nwi_code", "WETLAND_TY": "nwi_type"})

        except DataSourceError:
            print(f"WARNING: wetlands could not be read from {filename}; shapefile might not exist")

        # some geometries are invalid, filter them out
        df = df.loc[shapely.is_geometry(df.geometry.values)].copy()

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
            df.loc[(df.nwi_type == "Riverine") & (df.altered)].drop(columns=["nwi_type"]),
        )

        wetland_ix = df.nwi_code.str.startswith(WETLAND_PREFIXES[0])
        for prefix in WETLAND_PREFIXES[1:]:
            wetland_ix = wetland_ix | df.nwi_code.str.startswith(prefix)
        wetlands = append(wetlands, df.loc[wetland_ix])

    ### Process waterbodies
    # only keep that intersect flowlines
    print(f"Extracted {len(waterbodies):,} NWI lakes and ponds")
    left, right = tree.query(waterbodies.geometry.values, predicate="intersects")
    waterbodies = waterbodies.iloc[np.unique(left)].reset_index(drop=True)
    print(f"Kept {len(waterbodies):,} that intersect flowlines")

    # drop intermittent / seasonal waterbodies we don't want to include;
    # if they are permanent enough, NHD will pick them up
    if huc2 in ["13", "15", "16", "17", "18"]:
        waterbodies = waterbodies.loc[~waterbodies.modifier.isin(["A", "B", "C", "D", "E", "G", "J"])].reset_index(
            drop=True
        )

    # TODO: explode, repair, dissolve, explode, reset index
    waterbodies = waterbodies.explode(ignore_index=True)
    # make valid
    ix = ~shapely.is_valid(waterbodies.geometry.values)
    if ix.sum():
        print(f"Repairing {ix.sum():,} invalid waterbodies")
        waterbodies.loc[ix, "geometry"] = shapely.make_valid(waterbodies.loc[ix].geometry.values)

    # cleanup any that collapsed to other geometry types during make valid or import
    waterbodies = waterbodies.loc[shapely.get_type_id(waterbodies.geometry.values) == 3].reset_index()

    # note: nwi_code, nwi_type are discarded here since they aren't used later
    print("Dissolving adjacent waterbodies")
    waterbodies = dissolve(waterbodies, by=["altered"])
    waterbodies = waterbodies.explode(ignore_index=True).reset_index(drop=True)

    waterbodies["km2"] = shapely.area(waterbodies.geometry.values) / 1e6

    waterbodies.to_feather(huc2_dir / "waterbodies.feather")
    write_dataframe(waterbodies, huc2_dir / "waterbodies.fgb")

    ### Process riverine
    print(f"Extracted {len(rivers):,} NWI altered river polygons")
    left, right = tree.query(rivers.geometry.values, predicate="intersects")
    rivers = rivers.iloc[np.unique(left)].reset_index(drop=True)
    print(f"Kept {len(rivers):,} that intersect flowlines")

    rivers = rivers.explode(ignore_index=True)
    # make valid
    ix = ~shapely.is_valid(rivers.geometry.values)
    if ix.sum():
        print(f"Repairing {ix.sum():,} invalid rivers")
        rivers.loc[ix, "geometry"] = shapely.make_valid(rivers.loc[ix].geometry.values)

    # cleanup any that collapsed to other geometry types during make valid or import
    rivers = rivers.loc[shapely.get_type_id(rivers.geometry.values) == 3].reset_index()

    rivers["modifier"] = rivers.modifier.map(MODIFIERS)

    rivers.to_feather(huc2_dir / "altered_rivers.feather")
    write_dataframe(rivers, huc2_dir / "altered_rivers.fgb")

    ### Process wetlands
    left, right = tree.query(wetlands.geometry.values, predicate="intersects")
    wetlands = wetlands.iloc[np.unique(left)].reset_index(drop=True)

    print(f"Kept {len(wetlands):,} that intersect flowlines")

    wetlands = wetlands.explode(ignore_index=True)
    # make valid
    ix = ~shapely.is_valid(wetlands.geometry.values)
    if ix.sum():
        print(f"Repairing {ix.sum():,} invalid wetlands")
        wetlands.loc[ix, "geometry"] = shapely.make_valid(wetlands.loc[ix].geometry.values)

    # cleanup any that collapsed to other geometry types during make valid or import
    wetlands = wetlands.loc[shapely.get_type_id(wetlands.geometry.values) == 3].reset_index(drop=True)
    wetlands.to_feather(huc2_dir / "wetlands.feather")
    write_dataframe(wetlands, huc2_dir / "wetlands.fgb")

    print("--------------------")
    print("HUC2: {} done in {:.0f}s\n\n".format(huc2, time() - huc2_start))

print("Done in {:.2f}s\n============================".format(time() - start))
