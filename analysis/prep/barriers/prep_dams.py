"""
Extract dams from original data source, process for use in network analysis, and convert to feather format.
1. Cleanup data values (as needed)
2. Filter out dams not to be included in analysis (based on Feasibility and SNAP2018)
3. Snap to networks by HUC2 and merge into single data frame
4. Remove duplicate dams

This creates 2 files:
`barriers/master/dams.feather` - master dams dataset, including coordinates updated from snapping
`barriers/snapped/dams.feather` - snapped dams dataset for network analysis
"""

from pathlib import Path
from time import time
import pandas as pd
from geofeather import to_geofeather, from_geofeather
import geopandas as gp
import numpy as np

from nhdnet.io import deserialize_sindex, deserialize_df, to_shp
from nhdnet.geometry.lines import snap_to_line
from nhdnet.geometry.points import mark_duplicates

from analysis.constants import (
    REGION_GROUPS,
    REGIONS,
    CRS,
    DAM_COLS,
    DROP_SNAP2018,
    EXCLUDE_SNAP2018,
    DROP_RECON,
    DROP_FEASIBILITY,
    EXCLUDE_RECON,
    RECON_TO_FEASIBILITY,
)

from analysis.prep.barriers.lib.snap import snap_by_region, update_from_snapped


DUPLICATE_TOLERANCE = 30
# Snap barriers by 100 meters
SNAP_TOLERANCE = 100

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
master_dir = barriers_dir / "master"
snapped_dir = barriers_dir / "snapped"
qa_dir = barriers_dir / "qa"
dams_filename = "Raw_Featureservice_SARPUniqueID.gdb"
gdb = src_dir / dams_filename

# dams that fall outside SARP
outside_layer = "Dams_Non_SARP_States_09052019"

start = time()


### Read in SARP states and merge
print("Reading dams in SARP states")
df = from_geofeather(src_dir / "sarp_dams.feather")
print("Read {:,} dams in SARP states".format(len(df)))

### Read in non-SARP states and join in
# these are for states that overlap with HUC4s that overlap with SARP states
print(
    "Reading dams that fall outside SARP states, but within HUC4s that overlap with SARP states..."
)
outside_df = (
    gp.read_file(gdb, layer=outside_layer)
    .rename(columns={"Snap2018": "SNAP2018"})[DAM_COLS + ["geometry"]]
    .to_crs(CRS)
    .rename(
        columns={
            "Barrier_Name": "Name",
            "Other_Barrier_Name": "OtherName",
            "DB_Source": "Source",
            "Year_Completed": "Year",
            "ConstructionMaterial": "Construction",
            "PurposeCategory": "Purpose",
            "StructureCondition": "Condition",
            "Feasibility": "Feasibility",
        }
    )
)
print("Read {:,} dams outside SARP states".format(len(outside_df)))

df = df.append(outside_df, ignore_index=True, sort=False)

### Read in dams that have been manually snapped and join to get latest location
# Join on AnalysisID to merged data above.
# ONLY keep SNAP2018 and the location.
print("Reading manually snapped dams...")
snapped_df = from_geofeather(src_dir / "manually_snapped_dams.feather").set_index(
    "AnalysisID"
)

# Join to snapped and bring across updated geometry and SNAP2018

df = df.join(snapped_df, on="AnalysisID", rsuffix="_snap")

idx = df.loc[df.geometry_snap.notnull()].index
df.loc[idx, "geometry"] = df.loc[idx].geometry_snap
df.loc[idx, "SNAP2018"] = df.loc[idx].SNAP2018_snap
# drop snap columns

# Reset the index so that we have a clean numbering for all rows
df = df.drop(columns=[c for c in df.columns if c.endswith("_snap")]).reset_index(
    drop=True
)
print("Compiled {:,} dams".format(len(df)))


### Add IDs for internal use
# internal ID
df["id"] = df.index.astype("uint32")

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
# Fix Recon value that wasn't assigned to SNAP2018
# these are invasive species barriers
df.loc[df.Recon == 16, "SNAP2018"] = 10


# Round height to nearest foot.  There are no dams between 0 and 1 foot, so fill all
# na as 0
df.Height = df.Height.fillna(0).round().astype("uint16")

# Cleanup names
# Standardize the casing of the name
df.Name = df.Name.fillna("").str.title().str.strip()
df.OtherName = df.OtherName.fillna("").str.title().str.strip()

# Fix name issue - 3 dams have duplicate dam names with line breaks, which breaks tippecanoe
ids = df.loc[df.Name.str.count("\r") > 0].index
df.loc[ids, "Name"] = df.loc[ids].Name.apply(lambda v: v.split("\r")[0])

# Replace estimated dam names if another name is available
ids = (df.Name.str.count("Estimated Dam") > 0) & (df.OtherName.str.len() > 0)
df.loc[ids, "Name"] = df.loc[ids].OtherName


# Fix ProtectedLand: since this was from an intersection, all values should
# either be 1 (intersected) or 0 (did not)
df.loc[df.ProtectedLand != 1, "ProtectedLand"] = 0


# Fix years between 0 and 100; assume they were in the 1900s
df.loc[(df.Year > 0) & (df.Year < 100), "Year"] = df.Year + 1900
df.loc[df.Year == 20151, "Year"] = 2015
df.loc[df.Year == 9999, "Year"] = 0


for column in ("River", "NIDID", "Source"):
    df[column] = df[column].fillna("").str.strip()

df.River = df.River.str.title()


for column in (
    # "RareSpp",
    "ProtectedLand",
    "Construction",
    "Condition",
    "Purpose",
    "Recon",
):
    df[column] = df[column].fillna(0).astype("uint8")


for column in ("Year", "Feasibility", "SNAP2018"):
    df[column] = df[column].fillna(0).astype("uint16")


### Calculate classes
# Calculate feasibility
df["Feasibility"] = df.Recon.map(RECON_TO_FEASIBILITY).astype("uint8")

# Calculate height class
df["HeightClass"] = 0  # Unknown
df.loc[(df.Height > 0) & (df.Height < 5), "HeightClass"] = 1
df.loc[(df.Height >= 5) & (df.Height < 10), "HeightClass"] = 2
df.loc[(df.Height >= 10) & (df.Height < 25), "HeightClass"] = 3
df.loc[(df.Height >= 25) & (df.Height < 50), "HeightClass"] = 4
df.loc[(df.Height >= 50) & (df.Height < 100), "HeightClass"] = 5
df.loc[df.Height >= 100, "HeightClass"] = 6
df.HeightClass = df.HeightClass.astype("uint8")


### Spatial joins
# Join against HUC12 and then derive HUC2
print("Reading HUC12 boundaries and joining to dams")
huc12 = from_geofeather(boundaries_dir / "HUC12.feather")
huc12.sindex

df.sindex
df = gp.sjoin(df, huc12, how="left").drop(columns=["index_right"])

# Calculate HUC codes for other levels from HUC12
df["HUC2"] = df["HUC12"].str.slice(0, 2)  # region
df["HUC6"] = df["HUC12"].str.slice(0, 6)  # basin
df["HUC8"] = df["HUC12"].str.slice(0, 8)  # subbasin

# Read in HUC6 and join in basin name
huc6 = (
    from_geofeather(boundaries_dir / "HUC6.feather")[["HUC6", "NAME"]]
    .rename(columns={"NAME": "Basin"})
    .set_index("HUC6")
)
df = df.join(huc6, on="HUC6")


print("Joining to counties")
counties = from_geofeather(boundaries_dir / "counties.feather")[
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


# TODO: remove, moved to post
# print("Joining to ecoregions")
# # Only need to join in ECO4 dataset since it has both ECO3 and ECO4 codes
# eco4 = from_geofeather(boundaries_dir / "eco4.feather")[["geometry", "ECO3", "ECO4"]]
# eco4.sindex
# df.sindex
# df = gp.sjoin(df, eco4, how="left").drop(columns=["index_right"])


# Drop any that didn't intersect HUCs or states
drop_idx = df.HUC12.isnull() | df.STATEFIPS.isnull()
print("{:,} dams are outside HUC12 / states".format(len(df.loc[drop_idx])))
# Mark dropped barriers
df.loc[drop_idx, "dropped"] = True


### Drop any dams that should be completely dropped from analysis
# based on manual QA/QC
# NOTE: small barriers currently do not have any values set for SNAP2018
drop_idx = (
    df.Recon.isin(DROP_RECON)
    | df.Feasibility.isin(DROP_FEASIBILITY)
    | df.SNAP2018.isin(DROP_SNAP2018)
)
print("Dropped {:,} dams from all analysis and mapping".format(len(df.loc[drop_idx])))
df.loc[drop_idx, "dropped"] = True


### Exclude dams that should not be analyzed or prioritized based on manual QA
exclude_idx = df.Recon.isin(EXCLUDE_RECON) | df.SNAP2018.isin(EXCLUDE_SNAP2018)
print(
    "Excluded {:,} dams from network analysis and prioritization".format(
        len(df.loc[exclude_idx])
    )
)
df.loc[exclude_idx, "excluded"] = True


### Snap by region group
to_snap = df.loc[~(df.dropped | df.excluded), ["geometry", "HUC2", "id"]].copy()
print("Attempting to snap {:,} dams".format(len(to_snap)))

snapped = snap_by_region(to_snap, REGION_GROUPS, SNAP_TOLERANCE)


# join back to master
df = update_from_snapped(df, snapped)


# Remove duplicates after snapping, in case any snapped to the same position
# These are completely dropped from the analysis from here on out
df = mark_duplicates(df, DUPLICATE_TOLERANCE)
df = df.sort_values("id")
print("{:,} duplicate dams removed after snapping".format(len(df.loc[df.duplicate])))

print("\n--------------\n")
df = df.reset_index(drop=True)

print("Serializing {:,} dams to master file".format(len(df)))
to_geofeather(df, master_dir / "dams.feather")

print("writing shapefiles for QA/QC")
to_shp(df, qa_dir / "dams.shp")


# Extract out only the snapped ones
df = df.loc[df.snapped & ~df.duplicate].reset_index(drop=True)
df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

print("Serializing {:,} snapped dams".format(len(df)))
to_geofeather(
    df[["geometry", "id", "HUC2", "lineID", "NHDPlusID"]], snapped_dir / "dams.feather"
)

print("All done in {:.2f}s".format(time() - start))
