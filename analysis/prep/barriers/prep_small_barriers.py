"""
Extract small barriers from original data source, process for use in network analysis, and convert to feather format.
1. Cleanup data values (as needed)
2. Filter out barriers not to be included in analysis (based on Potential_Project and Snap2018)
3. Remove duplicate barriers
4. Snap to networks by HUC2

This creates 2 files:
`barriers/master/small_barriers.feather` - master barriers dataset, including coordinates updated from snapping
`barriers/snapped/small_barriers.feather` - snapped barriers dataset for network analysis



"""

from pathlib import Path
from time import time
import pandas as pd
import geopandas as gp
import numpy as np

from nhdnet.io import (
    serialize_gdf,
    deserialize_df,
    deserialize_gdf,
    deserialize_sindex,
    to_shp,
)
from nhdnet.geometry.points import mark_duplicates, add_lat_lon
from nhdnet.geometry.lines import snap_to_line

from analysis.constants import (
    REGION_GROUPS,
    REGIONS,
    CRS,
    DUPLICATE_TOLERANCE,
    KEEP_POTENTIAL_PROJECT,
    DROP_POTENTIAL_PROJECT,
    DROP_SNAP2018,
    EXCLUDE_SNAP2018,
    BARRIER_CONDITION_TO_DOMAIN,
    POTENTIAL_TO_SEVERITY,
    ROAD_TYPE_TO_DOMAIN,
    CROSSING_TYPE_TO_DOMAIN,
)

from analysis.prep.barriers.snap import snap_by_region, update_from_snapped

# Snap barriers by 50 meters
SNAP_TOLERANCE = 50

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
master_dir = barriers_dir / "master"
snapped_dir = barriers_dir / "snapped"
qa_dir = barriers_dir / "qa"
barriers_filename = "Road_Related_Barriers_DraftOne_Final08012019.gdb"

start = time()


# Read in authoritative original small barriers data
# drop all columns not necessary later in the stack
keep_cols = [
    "geometry",
    # TODO: GLOBALID
    "AnalysisID",
    "SNAP2018",
    "LocalID",
    "Crossing_Code",
    "StreamName",
    "Road",
    "RoadTypeId",
    "CrossingTypeId",
    "NumberOfStructures",
    "CrossingConditionId",
    "CrossingComment",
    "OnConservationLand",
    "Assessed",
    "SRI_Score",
    "Coffman_Strong",
    "Coffman_Medium",
    "Coffman_Weak",
    "SARP_Score",
    "SE_AOP",
    "Potential_Project",
    "Source",
    "NumberRareSpeciesHUC12",
    # TODO - network metrics only retained for region 8 barriers
    "AbsoluteGainMi",
    "UpstreamMiles",
    "DownstreamMiles",
    "TotalNetworkMiles",
    "PctNatFloodplain",
    "NetworkSinuosity",
    "NumSizeClassesGained",
    "batUSNetID",
    "batDSNetId",
]

df = (
    gp.read_file(src_dir / barriers_filename)
    .rename(columns={"AnalysisId": "AnalysisID"})
    .to_crs(CRS)
)[keep_cols].rename(
    columns={
        "OnConservationLand": "ProtectedLand",
        "NumberRareSpeciesHUC12": "RareSpp",
        # Note re: SARPID - this isn't quite correct but needed for consistency
        "AnalysisID": "SARPID",
        "AbsoluteGainMi": "GainMiles",
        "PctNatFloodplain": "Landcover",
        "NetworkSinuosity": "Sinuosity",
        "NumSizeClassesGained": "SizeClasses",
        "CrossingTypeId": "CrossingType",
        "RoadTypeId": "RoadType",
        "CrossingConditionId": "Condition",
        "StreamName": "Stream",
    }
)


print("Read {} small barriers".format(len(df)))

# Rename all columns that have underscores
df.rename(
    columns={c: c.replace("_", "") for c in df.columns[df.columns.str.count("_") > 0]},
    inplace=True,
)


### Add IDs for internal use
# internal ID
df["id"] = df.index.astype("uint")

# joinID is used for all internal joins in analysis
df["joinID"] = "sb" + df.id.astype("str")


### Add tracking fields
# dropped: records that should not be included in any later analysis
df["dropped"] = False

# excluded: records that should be retained in dataset but not used in analysis
df["excluded"] = False

# duplicate: records that are duplicates of another record that was retained
# NOTE: the first instance of a set of duplicates is NOT marked as a duplicate,
# only following ones are.
df["duplicate"] = False

# snapped: records that snapped to the aquatic network and ready for network analysis
df["snapped"] = False


######### Fix data issues

# Fix mixed casing of values
for column in ("CrossingType", "RoadType", "Stream", "Road"):
    df[column] = df[column].fillna("Unknown").str.title().str.strip()
    df.loc[df[column].str.len() == 0, column] = "Unknown"

# Fix line returns in stream name and road name
df.loc[df.SARPID == "sm7044", "Stream"] = "Unnamed"
df.Road = df.Road.str.replace("\r\n", "")

# Fix issues with RoadType
df.loc[df.RoadType.isin(("No Data", "NoData", "Nodata")), "RoadType"] = "Unknown"

# Fix issues with Condition
df.Condition = df.Condition.fillna("Unknown")
df.loc[
    (df.Condition == "No Data")
    | (df.Condition == "No data")
    | (df.Condition.str.strip().str.len() == 0),
    "Condition",
] = "Unknown"

#########  Fill NaN fields and set data types

for column in ("CrossingCode", "LocalID", "Source"):
    df[column] = df[column].fillna("").str.strip()

for column in ("RareSpp", "ProtectedLand"):
    df[column] = df[column].fillna(0).astype("uint8")


### Calculate classes
df["ConditionClass"] = df.Condition.map(BARRIER_CONDITION_TO_DOMAIN)
df["SeverityClass"] = df.PotentialProject.map(POTENTIAL_TO_SEVERITY)
df["CrossingTypeClass"] = df.CrossingType.map(CROSSING_TYPE_TO_DOMAIN)
df["RoadTypeClass"] = df.RoadType.map(ROAD_TYPE_TO_DOMAIN)


### Spatial joins
# Join against HUC12 and then derive HUC2
print("Reading HUC2 boundaries and joining to small barriers")
huc12 = deserialize_gdf(boundaries_dir / "HUC12.feather")
huc12.sindex

df.sindex
df = gp.sjoin(df, huc12, how="left").drop(columns=["index_right"])

# Calculate HUC codes for other levels from HUC12
df["HUC2"] = df["HUC12"].str.slice(0, 2)  # region
df["HUC6"] = df["HUC12"].str.slice(0, 6)  # basin
df["HUC8"] = df["HUC12"].str.slice(0, 8)  # subbasin

# Read in HUC6 and join in basin name
huc6 = (
    deserialize_gdf(boundaries_dir / "HUC6.feather")[["HUC6", "NAME"]]
    .rename(columns={"NAME": "Basin"})
    .set_index("HUC6")
)
df = df.join(huc6, on="HUC6")


print("Joining to counties")
counties = deserialize_gdf(boundaries_dir / "counties.feather")[
    ["geometry", "County", "COUNTYFIPS", "STATEFIPS"]
]
counties.sindex
df.sindex
df = gp.sjoin(df, counties, how="left").drop(columns=["index_right"])

# Join in state name based on STATEFIPS from county
states = deserialize_df(boundaries_dir / "states.feather")[
    ["STATEFIPS", "State"]
].set_index("STATEFIPS")
df = df.join(states, on="STATEFIPS")


print("Joining to ecoregions")
# Only need to join in ECO4 dataset since it has both ECO3 and ECO4 codes
eco4 = deserialize_gdf(boundaries_dir / "eco4.feather")[["geometry", "ECO3", "ECO4"]]
eco4.sindex
df.sindex
df = gp.sjoin(df, eco4, how="left").drop(columns=["index_right"])


# Drop any that didn't intersect HUCs or states
drop_idx = df.HUC12.isnull() | df.STATEFIPS.isnull()
print("{} small barriers are outside HUC12 / states".format(len(df.loc[drop_idx])))
# Mark dropped barriers
df.loc[drop_idx, "dropped"] = True


### Drop any small barriers that should be completely dropped from analysis
# based on manual QA/QC
# NOTE: small barriers currently do not have any values set for SNAP2018
drop_idx = df.PotentialProject.isin(DROP_POTENTIAL_PROJECT) | df.SNAP2018.isin(
    DROP_SNAP2018
)
print(
    "Dropped {} small barriers from all analysis and mapping".format(
        len(df.loc[drop_idx])
    )
)
df.loc[drop_idx, "dropped"] = True

### Exclude barriers that should not be analyzed or prioritized based on manual QA
# NOTE: small barriers currently do not have any values set for SNAP2018
exclude_idx = ~df.PotentialProject.isin(KEEP_POTENTIAL_PROJECT) & df.SNAP2018.isin(
    EXCLUDE_SNAP2018
)
print(
    "Excluded {} small barriers from network analysis and prioritization".format(
        len(df.loc[exclude_idx])
    )
)
df.loc[exclude_idx, "excluded"] = True


### Snap by region group
to_snap = df.loc[
    ~(df.dropped | df.excluded), ["geometry", "HUC2", "id", "joinID"]
].copy()
snapped = snap_by_region(to_snap, REGION_GROUPS, SNAP_TOLERANCE)
print("\n--------------\n")

# join back to master
df = update_from_snapped(df, snapped)

### Add lat / lon
print("Adding lat / lon fields")
df = add_lat_lon(df)


# Remove duplicates after snapping, in case any snapped to the same position
# These are completely dropped from the analysis from here on out
# Sort by descending severity before deduplication so that most severe barrier is retained
df = mark_duplicates(
    df.sort_values("SeverityClass", ascending=False), DUPLICATE_TOLERANCE
)
df = df.sort_values("id")
print(
    "{} duplicate small barriers removed after snapping".format(
        len(df.loc[df.duplicate])
    )
)

print("Serializing {} small barriers".format(len(df)))
serialize_gdf(df, master_dir / "small_barriers.feather", index=False)


print(
    "Serializing {0} snapped small barriers".format(
        len(df.loc[df.snapped & ~df.duplicate])
    )
)
serialize_gdf(
    df.loc[
        df.snapped & ~df.duplicate,
        ["geometry", "id", "joinID", "HUC2", "lineID", "NHDPlusID"],
    ],
    snapped_dir / "small_barriers.feather",
    index=False,
)

print("writing shapefiles for QA/QC")
to_shp(df, qa_dir / "small_barriers.shp")

