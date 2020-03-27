"""
Extract dams from original data source, process for use in network analysis, and convert to feather format.
1. Cleanup data values (as needed)
2. Filter out dams not to be included in analysis (based on Feasibility and ManualReview)
3. Snap to NHD dams, waterbodies, and flowlines
4. Remove duplicate dams

This creates 2 files:
`barriers/master/dams.feather` - master dams dataset, including coordinates updated from snapping
`barriers/snapped/dams.feather` - snapped dams dataset for network analysis


This creates several QA/QC files:
- `barriers/qa/dams/pre_snap_to_post_snap.gpkg`: lines between the original coordinate and the snapped coordinate (snapped barriers only)
- `barriers/qa/dams/pre_snap.gpkg`: original, unsnapped coordinate (snapped barriers only)
- `barriers/qa/dams/post_snap.gpkg`: snapped coordinate (snapped barriers only)
- `barriers/qa/dams/duplicate_areas.gpkg`: dissolved buffers around duplicate barriers (duplicates only)
"""

from pathlib import Path
from time import time
import pandas as pd
from geofeather.pygeos import from_geofeather, to_geofeather
from pgpkg import to_gpkg
import geopandas as gp
import numpy as np

from nhdnet.io import deserialize_sindex, deserialize_df, deserialize_dfs
from nhdnet.geometry.lines import snap_to_line

from analysis.prep.barriers.lib.points import (
    nearest,
    near,
    neighborhoods,
    connect_points,
)
from analysis.prep.barriers.lib.snap import (
    snap_to_nhd_dams,
    snap_to_waterbodies,
    snap_to_flowlines,
    snap_to_large_waterbodies,
    export_snap_dist_lines,
)
from analysis.prep.barriers.lib.duplicates import (
    find_duplicates,
    export_duplicate_areas,
)

from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins
from analysis.constants import (
    REGION_GROUPS,
    REGIONS,
    CRS,
    DAM_COLS,
    DROP_MANUALREVIEW,
    EXCLUDE_MANUALREVIEW,
    ONSTREAM_MANUALREVIEW,
    DROP_RECON,
    DROP_FEASIBILITY,
    EXCLUDE_RECON,
    RECON_TO_FEASIBILITY,
)


### Custom tolerance values for dams
SNAP_TOLERANCE = {"default": 150, "likely off network": 50}
DUPLICATE_TOLERANCE = {"default": 10, "likely duplicate": 50}


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
nhd_dir = data_dir / "nhd"
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
    # SARPID is Old, use SARPUniqueID for it instead
    .drop(columns=["SARPID"])
    .rename(columns={"SARPUniqueID": "SARPID", "Snap2018": "ManualReview"})[
        DAM_COLS + ["geometry"]
    ]
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
# ONLY keep ManualReview and the location.
print("Reading manually snapped dams...")
snapped_df = from_geofeather(
    src_dir / "manually_snapped_dams.feather",
    columns=["geometry", "ManualReview", "SARPID"],
).set_index("SARPID")

# Don't pull across those that were not manually snapped
snapped_df = snapped_df.loc[~snapped_df.ManualReview.isin([7, 9])]

# Join to snapped and bring across updated geometry and ManualReview
df = df.join(snapped_df, on="SARPID", rsuffix="_snap")

idx = df.loc[df.geometry_snap.notnull()].index
df.loc[idx, "geometry"] = df.loc[idx].geometry_snap

# override with manually snapped assignment
df.loc[idx, "ManualReview"] = df.loc[idx].ManualReview_snap
# drop snap columns

# Reset the index so that we have a clean numbering for all rows
df = df.drop(columns=[c for c in df.columns if c.endswith("_snap")]).reset_index(
    drop=True
)
print("Compiled {:,} dams".format(len(df)))


### Add IDs for internal use
# internal ID
df["id"] = df.index.astype("uint32")
df = df.set_index("id", drop=False)


######### Fix data issues
### Set data types
for column in ("River", "NIDID", "Source", "Name", "OtherName"):
    df[column] = df[column].fillna("").str.strip()

for column in ("Construction", "Condition", "Purpose", "Recon"):
    df[column] = df[column].fillna(0).astype("uint8")

for column in ("Year", "Feasibility", "ManualReview"):
    df[column] = df[column].fillna(0).astype("uint16")


# Fix Recon value that wasn't assigned to ManualReview
# these are invasive species barriers
df.loc[df.Recon == 16, "ManualReview"] = 10

# Reset manual review for dams that were previously not snapped, but are not reviewed
df.loc[df.ManualReview.isin([7, 9]), "ManualReview"] = 0


# Round height to nearest foot.  There are no dams between 0 and 1 foot, so fill all
# na as 0
df.Height = df.Height.fillna(0).round().astype("uint16")

# Cleanup names
# Standardize the casing of the name
df.Name = df.Name.str.title()
df.OtherName = df.OtherName.str.title()
df.River = df.River.str.title()

# Fix name issue - 3 dams have duplicate dam names with line breaks, which breaks tippecanoe
ids = df.loc[df.Name.str.count("\r") > 0].index
df.loc[ids, "Name"] = df.loc[ids].Name.apply(lambda v: v.split("\r")[0]).fillna("")


# Identify estimated dams
# these were generated by SARP from analysis of small waterbodies
ix = df.Name.str.count("Estimated Dam") > 0
df.loc[ix, "ManualReview"] = 20  # indicates estimated dam

# Replace estimated dam names if another name is available
ix = ix & (df.OtherName.str.len() > 0)
df.loc[ix, "Name"] = df.loc[ix].OtherName


# Amber Ignatius ACF dams are often features that don't have associated flowlines,
# flag so we don't snap to flowlines that aren't really close
df.loc[df.Source.str.count("Amber Ignatius") > 0, "ManualReview"] = 21


# Fix years between 0 and 100; assume they were in the 1900s
df.loc[(df.Year > 0) & (df.Year < 100), "Year"] = df.Year + 1900
df.loc[df.Year == 20151, "Year"] = 2015
df.loc[df.Year == 9999, "Year"] = 0

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
df = add_spatial_joins(df)


### Add tracking fields
# master log field for status
df["log"] = ""
# dropped: records that should not be included in any later analysis
df["dropped"] = False

# excluded: records that should be retained in dataset but not used in analysis
df["excluded"] = False

# Drop any that didn't intersect HUCs or states
drop_idx = df.HUC12.isnull() | df.STATEFIPS.isnull()
print("{:,} dams are outside HUC12 / states".format(len(df.loc[drop_idx])))
# Mark dropped barriers
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: outside HUC12 / states"


### Drop any dams that should be completely dropped from analysis
# based on manual QA/QC and other reivew.

# Drop those where recon shows this as an error
drop_idx = df.Recon.isin(DROP_RECON) & ~df.dropped
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: Recon one of {}".format(DROP_RECON)

# Drop those where recon shows this as an error
drop_idx = df.Feasibility.isin(DROP_FEASIBILITY) & ~df.dropped
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: Feasibility one of {}".format(DROP_FEASIBILITY)

# Drop those that were manually reviewed off-network or errors
drop_idx = df.ManualReview.isin(DROP_MANUALREVIEW) & ~df.dropped
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: ManualReview one of {}".format(DROP_MANUALREVIEW)

# From Kat: if the dam includes "dike" in the name and not "dam", it is not really a dam
drop_idx = (
    df.Name.str.lower().str.contains(" dike")
    & (~df.Name.str.lower().str.contains(" dam"))
    & ~df.dropped
    & ~df.ManualReview.isin(ONSTREAM_MANUALREVIEW)
)
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: name includes dike and not dam"

print("Dropped {:,} dams from all analysis and mapping".format(len(df.loc[df.dropped])))


### Exclude dams that should not be analyzed or prioritized based on manual QA
exclude_idx = df.Recon.isin(EXCLUDE_RECON) | df.ManualReview.isin(EXCLUDE_MANUALREVIEW)
df.loc[exclude_idx, "excluded"] = True
df.loc[exclude_idx, "log"] = "excluded: Recon one of {}".format(EXCLUDE_RECON)

exclude_idx = df.ManualReview.isin(EXCLUDE_MANUALREVIEW)
df.loc[exclude_idx, "excluded"] = True
df.loc[exclude_idx, "log"] = "excluded: ManualReview one of {}".format(
    EXCLUDE_MANUALREVIEW
)

print(
    "Excluded {:,} dams from analysis and prioritization".format(
        len(df.loc[df.excluded])
    )
)


### Convert to pygeos format for following operations


### Snap dams
# snapped: records that snapped to the aquatic network and ready for network analysis
df["snapped"] = False
df["snap_log"] = "not snapped"
df["snap_ref_id"] = np.nan  # id of feature from snap type this was snapped to
df["snap_dist"] = np.nan
df["lineID"] = np.nan  # line to which dam was snapped
df["wbID"] = np.nan  # waterbody ID where dam is either contained or snapped
df["snap_tolerance"] = SNAP_TOLERANCE["default"]
# Dams likely to be off network get a much smaller tolerance
df.loc[df.ManualReview.isin([20, 21]), "snap_tolerance"] = SNAP_TOLERANCE[
    "likely off network"
]
print(
    "Setting snap tolerance to {}m for {:,} dams likely off network".format(
        SNAP_TOLERANCE["likely off network"],
        len(df.loc[df.ManualReview.isin([20, 21])]),
    )
)

# IMPORTANT: do not snap manually reviewed, off-network dams!
to_snap = df.loc[df.ManualReview != 5].copy()

# Save original locations so we can map the snap line between original and new locations
original_locations = to_snap.copy()

snap_start = time()

# Snap to NHD dams
df, to_snap = snap_to_nhd_dams(df, to_snap)

# Snap to waterbodies
df, to_snap = snap_to_waterbodies(df, to_snap)

# Snap to flowlines
df, to_snap = snap_to_flowlines(df, to_snap)

# Last ditch effort to snap major waterbody-related dams
df, to_snap = snap_to_large_waterbodies(df, to_snap)

print(
    "Snapped {:,} dams in {:.2f}s".format(len(df.loc[df.snapped]), time() - snap_start)
)

print("---------------------------------")
print("\nSnapping statistics")
print(df.groupby("snap_log").size())
print("---------------------------------\n")


### Save results from snapping for QA
export_snap_dist_lines(df.loc[df.snapped], original_locations, qa_dir, prefix="dams_")

### De-duplicate dams that are very close
# duplicate: records that are duplicates of another record that was retained
# NOTE: the first instance of a set of duplicates is NOT marked as a duplicate,
# only following ones are.
df["duplicate"] = False
df["dup_group"] = np.nan
df["dup_count"] = np.nan
# duplicate sort will be assigned lower values to find preferred entry w/in dups
df["dup_sort"] = 9999
df["dup_log"] = "not a duplicate"

# Assign dup_sort, lower numbers = higher priority to keep from duplicate group
# Start from lower priorities and override with lower values

# Prefer dams with River to those that do not
df.loc[df.River != "", "dup_sort"] = 5

# Prefer dams that have been reconned to those that haven't
df.loc[df.Recon > 0, "dup_sort"] = 4

# Prefer dams with height or year to those that do not
df.loc[(df.Year > 0) | (df.Height > 0), "dup_sort"] = 3

# NABD dams should be reasonably high priority
df.loc[df.ManualReview == 2, "dup_sort"] = 2

# manually reviewed dams should be highest priority (both on and off stream)
df.loc[df.ManualReview.isin(ONSTREAM_MANUALREVIEW + [5]), "dup_sort"] = 1


dedup_start = time()
# Dams within 10 meters are very likely duplicates of each other
# from those that were hand-checked on the map, they are duplicates of each other
df, to_dedup = find_duplicates(
    df, to_dedup=df.copy(), tolerance=DUPLICATE_TOLERANCE["default"]
)

# Search a bit further for duplicates from estimated dams that snapped
# hand-checked these on the map, these look very likely to be real duplicates
next_group_id = df.dup_group.max() + 1
to_dedup = to_dedup.loc[to_dedup.snapped & df.ManualReview.isin([20, 21])].copy()
df, to_dedup = find_duplicates(
    df,
    to_dedup,
    tolerance=DUPLICATE_TOLERANCE["likely duplicate"],
    next_group_id=next_group_id,
)

print(
    "Found {:,} total duplicates in {:.2f}s".format(
        len(df.loc[df.duplicate]), time() - dedup_start
    )
)
print("---------------------------------")
print("\nDe-duplication statistics")
print(df.groupby("dup_log").size())
print("---------------------------------\n")

# Export duplicate areas for QA
dups = df.loc[df.dup_group.notnull()].copy()
dups.dup_group = dups.dup_group.astype("uint16")
dups["dup_tolerance"] = DUPLICATE_TOLERANCE["default"]
ix = dups.snapped & dups.ManualReview.isin([20, 21])
dups.loc[ix, "dup_tolerance"] = DUPLICATE_TOLERANCE["likely duplicate"]

export_duplicate_areas(dups, qa_dir / "dams_duplicate_areas")


### Join to line atts
flowlines = deserialize_dfs(
    [nhd_dir / "clean" / region / "flowlines.feather" for region in REGION_GROUPS],
    columns=["lineID", "NHDPlusID", "sizeclass", "streamorder", "loop", "waterbody"],
).set_index("lineID")

df = df.join(flowlines, on="lineID")
df["loop"] = df.loop.fillna(False)

print(df.groupby("loop").size())

### All done processing!

print("\n--------------\n")
df = df.reset_index(drop=True)

print("Serializing {:,} dams to master file".format(len(df)))
to_geofeather(df, master_dir / "dams.feather", crs=CRS)

print("writing GIS for QA/QC")
to_gpkg(df, qa_dir / "dams", crs=CRS)


# Extract out only the snapped ones
df = df.loc[df.snapped & ~(df.duplicate | df.dropped | df.excluded)].reset_index(
    drop=True
)
df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

print("Serializing {:,} snapped dams".format(len(df)))
to_geofeather(
    df[["geometry", "id", "HUC2", "lineID", "NHDPlusID", "loop", "waterbody"]],
    snapped_dir / "dams.feather",
    crs=CRS,
)

print("All done in {:.2f}s".format(time() - start))
