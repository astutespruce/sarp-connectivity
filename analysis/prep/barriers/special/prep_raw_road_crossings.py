from pathlib import Path
from time import time
import warnings

import geoarrow.pyarrow as ga
from geoarrow.pyarrow.io import read_pyogrio_table
import pyarrow as pa
import pyarrow.compute as pc
from pyarrow.dataset import dataset
import geopandas as gp
from geopandas.tools.hilbert_curve import _encode as encode_hilbert
import pandas as pd
import shapely
from pyogrio import read_dataframe, write_dataframe, read_arrow
import numpy as np

from analysis.constants import (
    CROSSINGS_ID_OFFSET,
    CRS,
    FCODE_TO_STREAMTYPE,
    CROSSING_TYPE_TO_DOMAIN,
)
from analysis.lib.arrow import map_values, points_to_crs
from analysis.lib.graph.speedups import DirectedGraph
from analysis.lib.io import read_arrow_tables
from analysis.prep.barriers.lib.crossings import get_crossing_code
from analysis.prep.barriers.lib.snap import snap_to_flowlines
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins
from analysis.prep.species.lib.diadromous import get_diadromous_ids

warnings.filterwarnings("ignore", category=UserWarning, message=".*Measured.*")

SNAP_TOLERANCE = 10
DUPLICATE_TOLERANCE = 5

# deduplicate USFS points within this amount of USGS points
USFS_USGS_TOLERANCE = 30


SOURCE_DOMAIN = {
    0: "USGS Database of Stream Crossings in the United States (2022)",
    1: "USFS National Road / Stream Crossings (2024)",
    2: "SARP Southeast 3rd Party Crossings (2025)",
}

# IMPORTANT: this must match analysis/constants.py::CROSSING_TYPE_TO_DOMAIN
USGS_CROSSING_TYPE_TO_DOMAIN = {
    "bridge": 5,
    "culvert": 99,  # assumed culvert
    "tiger2020 road": 99,  # assumed culvert
}

# assume that states are responsible party for interstate / US routes
# other types are unknown re: ownership, so don't bother to map them to codes
# IMPORTANT: this must match api/constants.py::BARRIEROWNERTYPE_DOMAIN
TIGER_RTTYP_TO_DOMAIN = {"C": 4, "I": 3, "S": 3, "U": 3}

# IMPORTANT: this must match api/constants.py::BARRIEROWNERTYPE_DOMAIN
USGS_CROSSING_STRUCTURE_TO_OWNER = {
    "56": 0,
    "57": 0,
    "58": 0,
    "78": 0,
    "79": 0,
    "Air Force": 1,
    "Army": 1,
    "Bureau of Fish and Wildlife": 1,
    "Bureau of Indian Affairs": 1,
    "Bureau of Land Management": 1,
    "Bureau of Reclamation": 1,
    "City or Municipal Highway Agency": 4,
    "Civil Corps of Engineers": 1,
    "County Highway Agency": 4,
    "Indian Tribal Government": 7,
    "Local Park Forest or Reservation Agency": 4,
    "Local Toll Authority": 4,
    "Metropolitan Washington Airports Service": 4,
    "NASA": 1,
    "National Park Service": 1,
    "Navy or Marines": 1,
    "Other Federal Agencies": 1,
    "Other Local Agencies": 4,
    "Other State Agencies": 3,
    "Private other than railroad": 8,
    "Railroad": 8,
    "State Highway Agency": 3,
    "State Park Forest or Reservation Agency": 3,
    "State Toll Authority": 3,
    "Tennessee Valley Authority": 5,
    "Town or Township Highway Agency": 4,
    "U.S. Forest Service": 2,
    "Unknown": 0,
}

# IMPORTANT: this must match api/constants.py::BARRIEROWNERTYPE_DOMAIN
USFS_MAINTAINER_TO_OWNER = {
    "": 0,
    "BIA - BUREAU OF INDIAN AFFAIRS": 1,
    "BLM - BUREAU OF LAND MANAGEMENT": 1,
    "BOR - BUREAU OF RECLAMATION": 1,
    "BPA - BONNEVILLE POWER ADMIN": 5,
    "BR - BUREAU OF RECLAMATION": 1,
    "C - COUNTY, PARISH, BOROUGH": 4,
    "C - FLATHEAD COUNTY": 4,
    "CO - COOPERATOR": 8,
    "CO - COOPERATOR (INDSTRL CST SHARE)": 8,
    "CO - COOPERATOR INDSTRL CST SHARE": 8,
    "CO - PLUM CREEK": 8,
    "COE - CORPS OF ENGINEERS": 1,
    "CU - AMERADA HESS OIL CO": 8,
    "CU - BASIC EARTH SCI.": 8,
    "CU - BTA OIL": 8,
    "CU - CITATION OIL CO": 8,
    "CU - COMMERCIAL USER": 8,
    "CU - CONTINENTAL": 8,
    "CU - CROWN OIL CO": 8,
    "CU - HEADINGTON": 8,
    "CU - MERIT ENERGY COMPANY": 8,
    "CU - MISSOURI BASIN": 8,
    "CU - NANCE PETROLEUM": 8,
    "CU - PETRO HUNT": 8,
    "CU - PRIDE ENERGY": 8,
    "CU - RITTER, LABOR, & ASSOCIATES": 8,
    "CU - SINCLAIR OIL": 8,
    "CU - SLAWSON OIL CO": 8,
    "CU - SUMMIT RESOURCES": 8,
    "CU - TRUE OIL CO": 8,
    "CU - UPTON": 8,
    "CU - WHITING": 8,
    "CU - WINSTON/MARSHALL OIL CO": 8,
    "DOD - DEFENSE DEPARTMENT": 1,
    "DOE - DEPARTMENT OF ENERGY": 1,
    "FAA - FEDERAL AVIATION ADMINISTRATION": 1,
    "FS - FOREST SERVICE": 2,
    "L - LOCAL": 4,
    "NPS - NATIONAL PARK SERVICE": 1,
    "OF - OTHER FEDERAL AGENCIES": 1,
    "OGM - OIL, GAS, MINERAL": 0,
    "P - NORTHERN LIGHTS": 8,
    "P - PRIVATE": 8,
    "P - STIMSON": 8,
    "P - WEYERHAEUSER": 8,
    "PGE - PACIFIC GAS AND ELECTRIC": 5,
    "S - STATE": 3,
    "SCE - SOUTHERN CALIFORNIA EDISON": 5,
    "SH - STATE HIGHWAY": 3,
    "SLR - STATE LANDS ROAD": 3,
    "UNK - UNKNOWN": 0,
}

# IMPORTANT: this must match api/constants.py::BARRIEROWNERTYPE_DOMAIN
THIRD_PARTY_OWNER = 8


start = time()

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
nhd_dir = data_dir / "nhd"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
qa_dir = barriers_dir / "qa"

usgs_gpkg = src_dir / "stream_crossings_united_states_feb_2022.gpkg"
huc2s = sorted(pd.read_feather(boundaries_dir / "huc2.feather", columns=["HUC2"]).HUC2.values)
huc4 = gp.read_feather(boundaries_dir / "huc4.feather", columns=["geometry", "HUC4"])
huc4["HUC2"] = huc4.HUC4.str[:2]


################################################################################
### Read USGS road crossings
################################################################################
print("Reading road crossings")
meta, usgs = read_arrow(
    usgs_gpkg,
    layer="stream_crossing_sites",
    columns=[
        "stream_crossing_id",
        "tiger2020_feature_names",
        "nhdhr_gnis_stream_name",
        "crossing_type",
        "tiger2020_linearids",
    ],
    read_geometry=True,
)
# this includes a number of duplicate records, drop them outright
usgs = usgs.group_by(usgs.column_names).aggregate([])

# coords are in NAD83 geographic
geom = shapely.from_wkb(usgs["geom"])
lon, lat = shapely.get_coordinates(geom).astype("float32").T
usgs_geom = gp.GeoSeries(geom, crs=meta["crs"]).to_crs(CRS)
usgs = pa.Table.from_pydict(
    {
        # index is used as a lookup to take corresponding geometries later;
        # it matches the index of usgs_geom at this point in time
        "index": pa.array(np.arange(len(usgs))),
        "Road": pc.fill_null(pc.utf8_trim(usgs["tiger2020_feature_names"], " "), ""),
        "River": pc.fill_null(pc.utf8_trim(usgs["nhdhr_gnis_stream_name"], " "), ""),
        "lon": pa.array(lon),
        "lat": pa.array(lat),
        "CrossingType": map_values(usgs["crossing_type"], USGS_CROSSING_TYPE_TO_DOMAIN, dtype="uint8"),
        "tiger2020_linearids": pc.split_pattern(pc.replace_substring(usgs["tiger2020_linearids"], " ", ""), ","),
        "stream_crossing_id": usgs["stream_crossing_id"],
    }
)
del lon
del lat

### read observation data to use for barrier ownership information
print("Extracting crossing owner type from USGS observed data")
meta, obs = read_arrow(
    usgs_gpkg,
    layer="observation_data",
    columns=["stream_crossing_id", "observation_year", "crossing_structure_owner"],
    where="crossing_structure_owner != ''",
    read_geometry=True,
)

# drop duplicates
obs = obs.group_by(["stream_crossing_id", "observation_year", "crossing_structure_owner", "geom"]).aggregate([])

obs_geom = gp.GeoSeries(shapely.from_wkb(obs["geom"]), crs=meta["crs"]).to_crs(CRS)
obs = pa.Table.from_pydict(
    {
        "index": pa.array(np.arange(len(obs))),
        "stream_crossing_id": obs["stream_crossing_id"],
        "year": pc.cast(obs["observation_year"], "uint16"),
        "BarrierOwnerType": map_values(
            obs["crossing_structure_owner"], USGS_CROSSING_STRUCTURE_TO_OWNER, dtype="uint8"
        ),
    }
)

# join to crossings on ID and then keep only those within 100m, preferring the
# most recent record
obs = obs.join(
    usgs.select(["stream_crossing_id", "index"]), "stream_crossing_id", join_type="inner", right_suffix="_usgs"
).combine_chunks()
obs = obs.append_column(
    "dist", pa.array(shapely.distance(obs_geom.values.take(obs["index"]), usgs_geom.values.take(obs["index_usgs"])))
)
obs = obs.filter(pc.field("dist") <= 100)
sort_ix = pc.sort_indices(obs, [("stream_crossing_id", "ascending"), ("dist", "descending"), ("year", "ascending")])
obs = (
    obs.take(sort_ix)
    .group_by(["stream_crossing_id"], use_threads=False)
    .aggregate([("BarrierOwnerType", "first")])
    .rename_columns({"BarrierOwnerType_first": "obs_BarrierOwnerType"})
    .combine_chunks()
)


### Use TIGER roads data to try and backfill barrier owner type
# NOTE: we only keep those that evaluated to one of the owner types above
print("Extracting attributes from TIGER roads")
tiger = dataset(src_dir / "tiger_roads_2020.feather", format="feather").to_table(columns=["LINEARID", "RTTYP"])
tiger = (
    tiger.append_column("BarrierOwnerType", map_values(tiger["RTTYP"], TIGER_RTTYP_TO_DOMAIN, dtype="uint8"))
    .drop_columns(["RTTYP"])
    .drop_null()
)

# Explode crossings by tiger line IDs before join
ix = pc.list_parent_indices(usgs["tiger2020_linearids"])
tiger = (
    pa.Table.from_pydict(
        {
            "stream_crossing_id": usgs["stream_crossing_id"].take(ix),
            "tiger2020_linearids": pc.list_flatten(usgs["tiger2020_linearids"]),
        }
    )
    .join(tiger.select(["LINEARID", "BarrierOwnerType"]), "tiger2020_linearids", "LINEARID", join_type="inner")
    .sort_by([("BarrierOwnerType", "ascending")])
    .group_by(["stream_crossing_id"], use_threads=False)
    .aggregate([("BarrierOwnerType", "first")])
    .rename_columns({"BarrierOwnerType_first": "tiger_BarrierOwnerType"})
)

usgs = (
    usgs.drop_columns(["tiger2020_linearids"])
    .join(obs, "stream_crossing_id")
    .join(tiger, "stream_crossing_id")
    .combine_chunks()
)
# sort to realign with usgs_geom
usgs = usgs.sort_by([("index", "ascending")])
del obs
del tiger


usgs = pa.Table.from_pydict(
    {
        **{
            c: usgs[c]
            for c in usgs.column_names
            if c not in {"obs_BarrierOwnerType", "tiger_BarrierOwnerType", "tiger2020_linearids", "stream_crossing_id"}
        },
        "BarrierOwnerType": pc.fill_null(
            pc.if_else(
                pc.is_valid(usgs["obs_BarrierOwnerType"]), usgs["obs_BarrierOwnerType"], usgs["tiger_BarrierOwnerType"]
            ),
            0,
        ),
        "Source": pa.array(np.zeros((len(usgs),), dtype="uint8")),
        "SourceID": pc.cast(usgs["stream_crossing_id"], "str"),
    }
)

# put unknown at the end (250+)
usgs = usgs.append_column(
    "dup_sort",
    pc.if_else(pc.equal(usgs["BarrierOwnerType"], 0), 250, usgs["BarrierOwnerType"]),
)


################################################################################
### Read USFS road crossings
################################################################################
meta, usfs = read_arrow(
    src_dir / "USFS_Crossings_Raw_2024.gdb",
    layer="FS_RdsOnly_Xings_National",
    columns=["FID_National_FS_roads", "NAME", "gnis_name", "PRIMARY_MA"],
    read_geometry=True,
)

usfs_geom = gp.GeoSeries(shapely.force_2d(shapely.from_wkb(usfs["Shape"])), crs=meta["crs"]).to_crs(CRS)
lon, lat = shapely.get_coordinates(usfs_geom.to_crs("EPSG:4326").values).astype("float32").T
usfs = pa.Table.from_pydict(
    {
        "index": np.arange(len(usfs)),
        "Road": pc.fill_null(pc.utf8_title(usfs["NAME"]), ""),
        "River": pc.fill_null(pc.utf8_trim(usfs["gnis_name"], " "), ""),
        "lon": lon,
        "lat": lat,
        "CrossingType": np.repeat(np.uint8(CROSSING_TYPE_TO_DOMAIN["assumed culvert"]), len(usfs)),
        "BarrierOwnerType": pc.fill_null(map_values(usfs["PRIMARY_MA"], USFS_MAINTAINER_TO_OWNER, dtype="uint8"), 0),
        "Source": pa.array(np.ones((len(usfs),), dtype="uint8")),
        # NOTE: no useful source IDs in input
        "SourceID": pa.array(np.repeat("", len(usfs))),
    }
)
del lon
del lat

# per guidance from Kat on 5/16, USFS crossings have lower precedence in dedup
usfs = usfs.append_column(
    "dup_sort",
    pc.if_else(pc.equal(usfs["BarrierOwnerType"], 0), 251, pc.add(usfs["BarrierOwnerType"], 100)),
)


################################################################################
### Read 3rd party road crossings
################################################################################

meta, third_party = read_arrow(
    src_dir / "SARP_3rd_party_crossings/SARP_3rd_party_crossings.shp", columns=["StreamCros"], read_geometry=True
)
third_party_geom = gp.GeoSeries(
    shapely.force_2d(shapely.from_wkb(third_party["wkb_geometry"])), crs=meta["crs"]
).to_crs(CRS)
lon, lat = shapely.get_coordinates(third_party_geom.to_crs("EPSG:4326").values).astype("float32").T
third_party = pa.Table.from_pydict(
    {
        "index": np.arange(len(third_party)),
        "Road": pa.array(np.repeat("", len(third_party))),
        "River": pa.array(np.repeat("", len(third_party))),
        "lon": lon,
        "lat": lat,
        "CrossingType": np.repeat(np.uint8(CROSSING_TYPE_TO_DOMAIN["assumed culvert"]), len(third_party)),
        "BarrierOwnerType": np.ones((len(third_party),), dtype="uint8") * THIRD_PARTY_OWNER,
        "Source": np.ones((len(third_party),), dtype="uint8") * 2,
        "SourceID": pc.cast(third_party["StreamCros"], "str"),
    }
)
del lon
del lat

third_party = third_party.append_column(
    "dup_sort",
    pc.if_else(pc.equal(third_party["BarrierOwnerType"], 0), 251, pc.add(third_party["BarrierOwnerType"], 200)),
)


################################################################################
### Merge crossings
################################################################################

# make sure to select geometries to align with index order
geom = gp.GeoSeries(
    np.concatenate(
        [usgs_geom.take(usgs["index"]), usfs_geom.take(usfs["index"]), third_party_geom.take(third_party["index"])]
    ),
    crs=usgs_geom.crs,
)
del usgs_geom
del usfs_geom
del third_party_geom

# calculate hilbert distance (for sorting geoms)
level = 16
side_length = (2**level) - 1
total_bounds = shapely.total_bounds(geom)
x, y = shapely.get_coordinates(geom).T
x = pc.round(pc.multiply(pc.subtract(x, total_bounds[0]), side_length / (total_bounds[2] - total_bounds[0])))
y = pc.round(pc.multiply(pc.subtract(y, total_bounds[1]), side_length / (total_bounds[3] - total_bounds[1])))

cols = [c for c in usgs.column_names if c != "index"]
df = pa.concat_tables([usgs.select(cols), usfs.select(cols), third_party.select(cols)]).combine_chunks()
df = pa.Table.from_pydict(
    {
        "index": pa.array(np.arange(len(df))),
        "hilbert": encode_hilbert(level, x, y),
        **{c: df[c] for c in df.column_names},
        "CrossingCode": pa.array(get_crossing_code(df["lon"].to_numpy(), df["lat"].to_numpy())),
        "duplicate": pa.array(np.zeros((len(df),), dtype="bool")),
    }
)
del usgs
del usfs
del third_party


# Join to HUC4 (keeping HUC2) and drop any outside of the active HUC4s
tree = shapely.STRtree(geom.values)
left, right = tree.query(huc4.geometry.values, predicate="intersects")
huc2_values = pa.array(huc2s)
huc2_join = pa.Table.from_pydict(
    {
        "index": df["index"].take(right),
        "HUC2": huc4.HUC2.values.take(left),
    }
).sort_by("index")

prev = len(df)
df = df.join(huc2_join, "index", join_type="inner")
print(f"Dropped {prev - len(df):,} crossings that are outside of HUC4s")


# Sort crossings and keep geometry in same order
# TODO: sort by hilbert order within HUC2
df = df.sort_by([("HUC2", "ascending"), ("dup_sort", "ascending"), ("hilbert", "ascending")])
geom = geom.take(df["index"])


# FIXME: remove
# tmp = gp.GeoDataFrame(df.to_pandas(), geometry=geom)


############## TODO: moved from above


# # TODO: can do HUC4 join later after merge
# left, right = shapely.STRtree(df.geometry.values).query(huc4.geometry.values, predicate="intersects")
# huc4_join = (
#     pd.DataFrame({"HUC4": huc4.HUC4.values.take(left)}, index=df.index.values.take(right)).groupby(level=0).HUC4.first()
# )

# df = df.join(huc4_join, how="inner").reset_index(drop=True)
# df["HUC2"] = df.HUC4.str[:2]


# TODO: mark these as duplicates; assign output SARPID
# drop any USFS crossings within tolerance of USGS crossings
# left = np.unique(
#     shapely.STRtree(usgs.geometry.values).query(df.geometry.values, predicate="dwithin", distance=USFS_USGS_TOLERANCE)[
#         0
#     ]
# )
# print(f"Dropping {len(left)} USFS crossings within {USFS_USGS_TOLERANCE}m of USGS crossings")

################

# df = pd.concat([usgs, usfs, sarp_3rd_party], ignore_index=True).sort_values("dup_sort", ascending=True)
# df["id"] = (df.index.values + CROSSINGS_ID_OFFSET).astype("uint64")
# df = df.set_index("id", drop=False)


# There are a bunch of crossings with identical coordinates, remove them
# NOTE: they have different labels, but that seems like it is a result of
# them methods used to identify the crossings (e.g., named highways, roads, etc)
print("Removing duplicate crossings at same location...")
orig_count = len(df)
df = gp.GeoDataFrame(df.groupby("CrossingCode").first().reset_index(), geometry="geometry", crs=df.crs)
print(f"Dropped {orig_count - len(df):,} duplicate road crossings")


# add name field
df["Name"] = ""
df.loc[(df.River != "") & (df.Road != ""), "Name"] = df.River + " / " + df.Road


### Remove crossings that are very close
print("Removing nearby road crossings...")
df = dedup_crossings(df)
print(f"now have {len(df):,} road crossings")


# Snap to flowlines
df["snapped"] = False
df["snap_log"] = "not snapped"
df["lineID"] = np.nan  # line to which crossing was snapped
df["snap_tolerance"] = np.uint8(SNAP_TOLERANCE)

snap_start = time()
to_snap = df.copy()
df, to_snap = snap_to_flowlines(df, to_snap)
print(f"Snapped {df.snapped.sum():,} crossings in {time() - snap_start:.2f}s")

print("---------------------------------")
print("\nSnapping statistics")
print(df.groupby("snap_log").size())
print("---------------------------------\n")

print("Dropping any road crossings that didn't snap")
df = df.loc[df.snapped].copy()


### Remove crossings that are very close after snapping
print("Removing nearby road crossings after snapping...")
df = dedup_crossings(df)
print(f"now have {len(df):,} road crossings")


df = add_spatial_joins(df)

# Cleanup HUC, state, county columns that weren't assigned
for col in [
    "HUC2",
    "HUC4",
    "HUC6",
    "HUC8",
    "HUC10",
    "HUC12",
    "Basin",
    "County",
    "COUNTYFIPS",
    "State",
    "CongressionalDistrict",
]:
    df[col] = df[col].fillna("")


### Drop any that didn't intersect HUCs or states (including those outside analysis region)
df = df.loc[(df.HUC12 != "") & (df.State != "")].copy()

df["CoastalHUC8"] = df.CoastalHUC8.fillna(0).astype("bool")


### Join to line atts
flowlines = (
    read_arrow_tables(
        [nhd_dir / "clean" / huc2 / "flowlines.feather" for huc2 in df.HUC2.unique()],
        columns=[
            "lineID",
            "NHDPlusID",
            "GNIS_Name",
            "sizeclass",
            "StreamOrder",
            "FCode",
            "loop",
            "offnetwork",
            "AnnualFlow",
            "AnnualVelocity",
            "TotDASqKm",
        ],
        filter=pc.is_in(pc.field("lineID"), pa.array(df.lineID.unique())),
    )
    .to_pandas()
    .set_index("lineID")
    .rename(columns={"offnetwork": "offnetwork_flowline"})
)

df = df.join(flowlines, on="lineID")

# NOTE: because these only include snapped crossings here, we don't need to fill
# flowline values with -1
df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("int64")

df["DiadromousHabitat"] = df.NHDPlusID.isin(get_diadromous_ids()).astype("int8")

marine_ids = (
    pa.dataset.dataset(nhd_dir / "clean/all_marine_flowlines.feather", format="feather")
    .to_table(filter=pc.is_in(pc.field("NHDPlusID"), pa.array(flowlines.NHDPlusID.unique())))["NHDPlusID"]
    .to_numpy()
)
df["FlowsToOcean"] = df.NHDPlusID.isin(marine_ids).astype("int8")

great_lake_ids = (
    pa.dataset.dataset(nhd_dir / "clean/all_great_lakes_flowlines.feather", format="feather")
    .to_table(filter=pc.is_in(pc.field("NHDPlusID"), pa.array(flowlines.NHDPlusID.unique())))["NHDPlusID"]
    .to_numpy()
)
df["FlowsToGreatLakes"] = df.NHDPlusID.isin(great_lake_ids).astype("int8")

# Add name from snapped flowline if not already present
df["GNIS_Name"] = df.GNIS_Name.fillna("").str.strip()
ix = (df.River == "") & (df.GNIS_Name != "")
df.loc[ix, "River"] = df.loc[ix].GNIS_Name
df = df.drop(columns=["GNIS_Name"])

# calculate stream type
df["stream_type"] = df.FCode.map(FCODE_TO_STREAMTYPE).fillna(0).astype("uint8")

# calculate intermittent + ephemeral
df["Intermittent"] = df.FCode.isin([46003, 46007]).astype("int8")

# calculate canal / ditch
df["Canal"] = df.FCode.isin([33600, 33601, 33603]).astype("int8")

# Fix missing field values
df.StreamOrder = df.StreamOrder.fillna(-1).astype("int8")
df["loop"] = df.loop.fillna(0).astype("bool")
df["offnetwork_flowline"] = df.offnetwork_flowline.fillna(0).astype("bool")
df["sizeclass"] = df.sizeclass.fillna("")
df["FCode"] = df.FCode.fillna(-1).astype("int32")
# -9998.0 values likely indicate AnnualVelocity data is not available, equivalent to null
df.loc[df.AnnualVelocity < 0, "AnnualVelocity"] = -1
df.loc[df.AnnualFlow <= 0, "AnnualFlow"] = -1

for field in ["AnnualVelocity", "AnnualFlow", "TotDASqKm"]:
    df[field] = df[field].fillna(-1).astype("float32")

df.reset_index(drop=True).to_feather(src_dir / "road_crossings.feather")


print(f"Done in {time() - start:.2f}")
