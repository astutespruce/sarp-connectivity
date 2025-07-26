from pathlib import Path
from time import time
import warnings

import pyarrow as pa
import pyarrow.compute as pc
import geopandas as gp
import pandas as pd
import shapely
from pyogrio import read_dataframe, write_dataframe
import numpy as np

from analysis.constants import (
    CROSSINGS_ID_OFFSET,
    CRS,
    FCODE_TO_STREAMTYPE,
    CROSSING_TYPE_TO_DOMAIN,
)
from analysis.lib.graph.speedups import DirectedGraph
from analysis.lib.io import read_arrow_tables
from analysis.prep.barriers.lib.snap import snap_to_flowlines
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins
from analysis.prep.species.lib.diadromous import get_diadromous_ids

warnings.filterwarnings("ignore", category=UserWarning, message=".*Measured.*")

SNAP_TOLERANCE = 10
DUPLICATE_TOLERANCE = 5

# deduplicate USFS points within this amount of USGS points
USFS_USGS_TOLERANCE = 30


def dedup_crossings(df):
    # we only want to dedup those that are really close, and some may be in chains of
    # crossings, so only dedup by distance not neighborhoods
    tree = shapely.STRtree(df.geometry.values)
    pairs = pd.DataFrame(
        tree.query(df.geometry.values, predicate="dwithin", distance=DUPLICATE_TOLERANCE).T,
        columns=["left", "right"],
    )
    g = DirectedGraph(
        df.id.take(pairs.left.values).values.astype("int64"),
        df.id.take(pairs.right.values).values.astype("int64"),
    )

    # note: components accounts for self-intersections and symmetric pairs
    groups, values = g.flat_components()
    # sort into deterministic order
    groups = (
        pd.DataFrame({"group": groups, "id": values})
        .astype(df.id.dtype)
        .join(df.set_index("id").dup_sort, on="id")
        .sort_values(by=["group", "dup_sort", "id"])
    )

    keep_ids = groups.groupby("group").first().id.values.astype("uint64")

    print(f"Dropping {len(df) - len(keep_ids):,} very close road crossings")
    return df.loc[df.id.isin(keep_ids)].copy()


start = time()

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
nhd_dir = data_dir / "nhd"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
qa_dir = barriers_dir / "qa"

usgs_gpkg = src_dir / "stream_crossings_united_states_feb_2022.gpkg"
huc4 = gp.read_feather(boundaries_dir / "huc4.feather", columns=["geometry", "HUC4"])


################################################################################
### Read USGS road crossings
################################################################################
print("Reading road crossings")

# rename columns to match small barriers
# NOTE: tiger2020_feature_names is a combination of multiple road names
df = read_dataframe(
    usgs_gpkg,
    layer="stream_crossing_sites",
    columns=[
        "stream_crossing_id",
        "tiger2020_feature_names",
        "nhdhr_gnis_stream_name",
        "nhdhr_permanent_identifier",
        "crossing_type",
        "tiger2020_linearids",
    ],
    use_arrow=True,
).rename(
    columns={
        "tiger2020_feature_names": "Road",
        "nhdhr_gnis_stream_name": "River",
        "crossing_type": "CrossingType",
    }
)
print(f"Read {len(df):,} road crossings")

df["Source"] = "USGS Database of Stream Crossings in the United States (2022)"
df["SourceID"] = df.stream_crossing_id.astype("str")


# project HUC4 to match crossings
proj_huc4 = huc4.to_crs(df.crs)
tree = shapely.STRtree(df.geometry.values)
left, right = tree.query(proj_huc4.geometry.values, predicate="intersects")
huc4_join = (
    pd.DataFrame({"HUC4": proj_huc4.HUC4.values.take(left)}, index=df.index.values.take(right))
    .groupby(level=0)
    .HUC4.first()
)

df = df.join(huc4_join, how="inner").reset_index(drop=True)
df["HUC2"] = df.HUC4.str[:2]
print(f"Selected {len(df):,} USGS road crossings in region")

# use original latitude / longitude (NAD83) values
lon, lat = shapely.get_coordinates(df.geometry.values).astype("float32").T
df["lon"] = lon
df["lat"] = lat

# project to match SARP CRS
df = df.to_crs(CRS)


### Cleanup fields
df.River = df.River.str.strip().fillna("")
df.Road = df.Road.str.strip().fillna("")

# update crossingtype and set as domain
df["CrossingType"] = df.CrossingType.fillna("").str.lower()
df.loc[df.CrossingType.isin(["culvert", "tiger2020 road"]), "CrossingType"] = "assumed culvert"
df["CrossingType"] = df.CrossingType.map(CROSSING_TYPE_TO_DOMAIN).astype("uint8")


### read observation data to use for barrier ownership information
print("Extracting crossing owner type from USGS observed data")
usgs_obs = read_dataframe(
    usgs_gpkg,
    layer="observation_data",
    columns=["stream_crossing_id", "observation_year", "crossing_structure_owner"],
    use_arrow=True,
).to_crs(CRS)
# only keep those with crossing_owner_type
usgs_obs["crossing_structure_owner"] = usgs_obs.crossing_structure_owner.fillna("").str.strip()
usgs_obs["observation_year"] = usgs_obs.observation_year.fillna(0).astype("uint16")
usgs_obs = usgs_obs.loc[usgs_obs.crossing_structure_owner != ""].set_index("stream_crossing_id")

# only keep those that are within 100m
tmp = df[["stream_crossing_id", "geometry"]].join(usgs_obs, on="stream_crossing_id", how="inner", rsuffix="_obs")
del usgs_obs
tmp["dist"] = shapely.distance(tmp.geometry.values, tmp.geometry_obs.values)
tmp = (
    tmp.loc[tmp.dist <= 100]
    .sort_values(by=["stream_crossing_id", "dist", "observation_year"], ascending=[True, True, False])
    .groupby("stream_crossing_id")[["crossing_structure_owner"]]
    .first()
)

# IMPORTANT: this must match api/constants.py::BARRIEROWNERTYPE_DOMAIN
tmp["BarrierOwnerType"] = (
    tmp.crossing_structure_owner.map(
        {
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
    )
    .fillna(0)
    .astype("uint8")
)

df = df.join(tmp.BarrierOwnerType, on="stream_crossing_id")
df["BarrierOwnerType"] = df.BarrierOwnerType.fillna(0).astype("uint8")


### Use TIGER roads data to try and backfill barrier owner type
print("Extracting attributes from TIGER roads")
tiger = pd.read_feather(src_dir / "tiger_roads_2020.feather", columns=["LINEARID", "RTTYP"]).set_index("LINEARID")
# assume that states are responsible party for interstate / US routes
# other types are unknown re: ownership, so don't bother to map them to codes
# IMPORTANT: this must match api/constants.py::BARRIEROWNERTYPE_DOMAIN
tiger["BarrierOwnerType"] = tiger.RTTYP.map({"C": 4, "I": 3, "S": 3, "U": 3}).fillna(0).astype("uint8")
tiger = tiger.loc[tiger.BarrierOwnerType > 0].copy()

tmp = df[["stream_crossing_id", "tiger2020_linearids"]].copy()
tmp["tiger2020_linearids"] = tmp.tiger2020_linearids.str.replace(" ", "").str.split(",")
tmp = tmp.explode("tiger2020_linearids")
tmp = (
    tmp.join(tiger.BarrierOwnerType, on="tiger2020_linearids", how="inner")
    .sort_values(by=["stream_crossing_id", "BarrierOwnerType"], ascending=True)
    .groupby("stream_crossing_id")[["BarrierOwnerType"]]
    .first()
)
del tiger

df = df.join(tmp.BarrierOwnerType.rename("tiger_BarrierOwnerType"), on="stream_crossing_id")
ix = (df.BarrierOwnerType == 0) & df.tiger_BarrierOwnerType.notnull()
df.loc[ix, "BarrierOwnerType"] = df.loc[ix].tiger_BarrierOwnerType.values.astype("uint8")

df = df.drop(columns=["stream_crossing_id", "tiger_BarrierOwnerType"])

df["dup_sort"] = df.BarrierOwnerType
# put unknown at the end
df.loc[df.BarrierOwnerType == 0, "dup_sort"] = df.BarrierOwnerType.max() + 1

usgs = df


################################################################################
### Read USFS road crossings
################################################################################
df = read_dataframe(
    src_dir / "USFS_Crossings_Raw_2024.gdb",
    layer="FS_RdsOnly_Xings_National",
    columns=["FID_National_FS_roads", "NAME", "gnis_name", "permanent_identifier", "PRIMARY_MA"],
    use_arrow=True,
).rename(
    columns={
        "NAME": "Road",
        "gnis_name": "River",
        "FID_National_FS_roads": "SARPID",
        "permanent_identifier": "nhdhr_permanent_identifier",
        "PRIMARY_MA": "maintainer",
    }
)

df["geometry"] = shapely.force_2d(df.geometry.values)
df = df.to_crs(CRS)

# drop any USFS crossings within tolerance of USGS crossings
left = np.unique(
    shapely.STRtree(usgs.geometry.values).query(df.geometry.values, predicate="dwithin", distance=USFS_USGS_TOLERANCE)[
        0
    ]
)
print(f"Dropping {len(left)} USFS crossings within {USFS_USGS_TOLERANCE}m of USGS crossings")


lon, lat = shapely.get_coordinates(df.to_crs("EPSG:4326").geometry.values).astype("float32").T
df["lon"] = lon
df["lat"] = lat


def capitalizeRoad(road):
    # parts of name after Spur should remain all caps
    spur = " SPUR "
    if spur in road:
        ix = road.index(spur)
        return road[:ix].title() + " Spur " + road[ix + 6 :]
    else:
        return road.title()


df["Road"] = df.Road.fillna("").str.strip().apply(capitalizeRoad)
df["River"] = df.River.fillna("").str.strip()

# assume all are assumed culvert
df["CrossingType"] = np.uint8(CROSSING_TYPE_TO_DOMAIN["assumed culvert"])
df["Source"] = "USFS National Road / Stream Crossings (2024)"
# not applicable
df["SourceID"] = ""

df["maintainer"] = df.maintainer.fillna("").str.strip()
# IMPORTANT: this must match api/constants.py::BARRIEROWNERTYPE_DOMAIN
df["BarrierOwnerType"] = df.maintainer.map(
    {
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
).astype("uint8")

tree = shapely.STRtree(df.geometry.values)
left, right = tree.query(huc4.geometry.values, predicate="intersects")
huc4_join = (
    pd.DataFrame({"HUC4": huc4.HUC4.values.take(left)}, index=df.index.values.take(right)).groupby(level=0).HUC4.first()
)
df = df.join(huc4_join, how="inner").reset_index(drop=True)
df["HUC2"] = df.HUC4.str[:2]
print(f"Selected {len(df):,} USFS road crossings in region")

# per guidance from Kat on 5/16, USFS crossings have lower precedence in dedup
df["dup_sort"] = df.BarrierOwnerType + usgs.dup_sort.max() + 1
df.loc[df.BarrierOwnerType == 0, "dup_sort"] = df.dup_sort + 1

usfs = df


################################################################################
### Read 3rd party road crossings
################################################################################
df = (
    read_dataframe(
        src_dir / "SARP_3rd_party_crossings/SARP_3rd_party_crossings.shp",
        use_arrow=True,
        columns=["StreamCros", "geometry"],
    )
    .to_crs(CRS)
    .rename(columns={"StreamCros": "SourceID"})
)
df["geometry"] = shapely.force_2d(df.geometry.values)
df["SourceID"] = df.SourceID.astype("str")

# IMPORTANT: this must match api/constants.py::BARRIEROWNERTYPE_DOMAIN
df["BarrierOwnerType"] = np.uint8(8)

df["Road"] = ""
df["River"] = ""

# assume all are assumed culvert
df["CrossingType"] = np.uint8(CROSSING_TYPE_TO_DOMAIN["assumed culvert"])
df["Source"] = "SARP Southeast 3rd Party Crossings (2025)"

tree = shapely.STRtree(df.geometry.values)
left, right = tree.query(huc4.geometry.values, predicate="intersects")
huc4_join = (
    pd.DataFrame({"HUC4": huc4.HUC4.values.take(left)}, index=df.index.values.take(right)).groupby(level=0).HUC4.first()
)
df = df.join(huc4_join, how="inner").reset_index(drop=True)
df["HUC2"] = df.HUC4.str[:2]
print(f"Selected {len(df):,} SARP 3rd party road crossings in region")

lon, lat = shapely.get_coordinates(df.to_crs("EPSG:4326").geometry.values).astype("float32").T
df["lon"] = lon
df["lat"] = lat

df["dup_sort"] = df.BarrierOwnerType + usfs.dup_sort.max() + 1

sarp_3rd_party = df


################################################################################
### Merge crossings
################################################################################
df = pd.concat([usgs, usfs, sarp_3rd_party], ignore_index=True).sort_values("dup_sort", ascending=True)
df["id"] = (df.index.values + CROSSINGS_ID_OFFSET).astype("uint64")
df = df.set_index("id", drop=False)

# calculate crossing code to match NAACC scheme
df["CrossingCode"] = (
    "xy"
    + (df.lat * 1e7).round(0).astype("int").abs().astype("str")
    + (df.lon * 1e7).round(0).astype("int").abs().astype("str")
)

# match dtype of SARPID elsewhere
df["SARPID"] = "cr" + df.CrossingCode.str[2:]

# Save snapshot of 3rd party before dedup for Kat
write_dataframe(
    df.loc[
        df.Source == "SARP Southeast 3rd Party Crossings (2025)",
        ["geometry", "SARPID", "CrossingCode", "Source", "SourceID"],
    ].reset_index(drop=True),
    "/tmp/SARP_3rd_party_crossings.gdb",
    driver="OpenFileGDB",
)


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
df["lineID"] = np.nan  # line to which dam was snapped
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
