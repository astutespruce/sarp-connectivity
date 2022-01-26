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
- `barriers/qa/dams/pre_snap_to_post_snap.fgb`: lines between the original coordinate and the snapped coordinate (snapped barriers only)
- `barriers/qa/dams/pre_snap.fgb`: original, unsnapped coordinate (snapped barriers only)
- `barriers/qa/dams/post_snap.fgb`: snapped coordinate (snapped barriers only)
- `barriers/qa/dams/duplicate_areas.fgb`: dissolved buffers around duplicate barriers (duplicates only)
"""

from pathlib import Path
from time import time
import warnings

import geopandas as gp
import pygeos as pg
import numpy as np
from pyogrio import write_dataframe

from analysis.prep.barriers.lib.snap import (
    snap_estimated_dams_to_drains,
    snap_to_nhd_dams,
    snap_to_waterbodies,
    snap_to_flowlines,
    export_snap_dist_lines,
)
from analysis.prep.barriers.lib.duplicates import (
    find_duplicates,
    export_duplicate_areas,
)
from analysis.lib.waterbodies import classify_waterbody_size

from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins
from analysis.constants import (
    GEO_CRS,
    DROP_FEASIBILITY,
    DROP_MANUALREVIEW,
    DROP_RECON,
    DROP_STRUCTURECATEGORY,
    EXCLUDE_FEASIBILITY,
    EXCLUDE_MANUALREVIEW,
    EXCLUDE_RECON,
    EXCLUDE_PASSAGEFACILITY,
    ONSTREAM_MANUALREVIEW,
    OFFSTREAM_MANUALREVIEW,
    RECON_TO_FEASIBILITY,
    UNRANKED_FEASIBILITY,
    UNRANKED_MANUALREVIEW,
    UNRANKED_RECON,
    FCODE_TO_STREAMTYPE,
    DAM_BARRIER_SEVERITY_TO_DOMAIN,
    EXCLUDE_BARRIER_SEVERITY,
)
from analysis.lib.io import read_feathers


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

### Custom tolerance values for dams
SNAP_TOLERANCE = {
    "default": 150,
    "likely off network": 50,
    "estimated from network": 10,
}
DUPLICATE_TOLERANCE = {"default": 10, "likely duplicate": 50}


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
nhd_dir = data_dir / "nhd"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
master_dir = barriers_dir / "master"
snapped_dir = barriers_dir / "snapped"
qa_dir = barriers_dir / "qa"


start = time()


### Read in SARP states and merge
print("Reading dams in SARP states")
df = gp.read_feather(src_dir / "sarp_dams.feather")
print(f"Read {len(df):,} dams in region states")

### Read in non-SARP states and join in
# these are for states that overlap with HUC4s that overlap with SARP states
print(
    "Reading dams that fall outside region states, but within HUC4s that overlap with region states..."
)

outside_df = gp.read_feather(src_dir / "dams_outer_huc4.feather")
# drop any that are in the main dataset, since there are several dams at state lines
outside_df = outside_df.loc[~outside_df.SARPID.isin(df.SARPID.unique())].copy()
print(f"Read {len(outside_df):,} dams outer HUC4s")

df = df.append(outside_df, ignore_index=True, sort=False)

### Read in dams that have been manually reviewed within SARP states
print("Reading manually snapped dams...")
snapped_df = gp.read_feather(src_dir / "manually_snapped_dams.feather",)

# Don't pull across those that were not manually snapped or are missing key fields
# 0,1: not reviewed,
# 7,9: assumed offstream but attempt to snap
# 20,21: dams with lower confidence assigned automatically in previous run
snapped_df = snapped_df.loc[~snapped_df.ManualReview.isin([0, 1, 7, 9, 20, 21])].copy()

for col in ["dropped", "excluded", "duplicate", "snapped"]:
    snapped_df[col] = snapped_df[col].map({"True": True, "False": False}).astype(bool)

# Drop any that were marked as in correct location, but were not previously snapped;
# these are errors
ix = (snapped_df.ManualReview == 13) & ~snapped_df.snapped
if ix.sum():
    print(
        f"Dropping {ix.sum():,} dams marked as in correct location but were not previously snapped (errors)"
    )
    snapped_df = snapped_df.loc[~ix].copy()

# Drop any that were marked as duplicates manually and also automatically
ix = (snapped_df.ManualReview == 11) & snapped_df.duplicate
if ix.sum():
    snapped_df = snapped_df.loc[~ix].copy()
    print(f"Dropping {ix.sum():,} dams marked as duplicates automatically and manually")

# temporary: splice in local snap dataset for non-SARP states until it is available online
other_df = gp.read_feather(
    src_dir / "snapped_outside_sarp_v1.feather",
    columns=["SARPID", "geometry", "ManualReview"],
)
snapped_df = (
    snapped_df[["SARPID", "geometry", "ManualReview"]]
    .append(other_df, ignore_index=True)
    .set_index("SARPID")
)

# Join to snapped and bring across updated geometry and ManualReview
df = df.join(snapped_df, on="SARPID", rsuffix="_snap")

# override with manually snapped assignment
ix = df.ManualReview_snap.notnull()
df.loc[ix, "ManualReview"] = df.loc[ix].ManualReview_snap

# Only update geometry from snapped where snapped is likely to be manually moved
# or where validated prior location
ix = df.ManualReview_snap.isin([4, 5, 13, 15])
df.loc[ix, "geometry"] = df.loc[ix].geometry_snap

print(f"Updated {ix.sum():,} dam locations based on snapped / manual review dataset")

# drop snap columns
df = df.drop(columns=[c for c in df.columns if c.endswith("_snap")])

# Reset the index so that we have a clean numbering for all rows
df = df.reset_index(drop=True)
print("-----------------\nCompiled {:,} dams\n-----------------\n".format(len(df)))

### Make sure there are not duplicates
s = df.groupby("SARPID").size()
if s.max() > 1:
    warnings.warn(f"Multiple dams with same SARPID: {s[s > 1].index.values}")


### Add IDs for internal use
# internal ID
df["id"] = df.index.astype("uint32")
df = df.set_index("id", drop=False)


######### Fix data issues

# Calculate feasibility from Recon if not already set
# NOTE: this must be done before backfilling Feasibility with 0
df.Recon = df.Recon.fillna(0).astype("uint8")
ix = df.Feasibility.isnull() | (df.Feasibility == 0)
df.loc[ix, "Feasibility"] = df.loc[ix].Recon.map(RECON_TO_FEASIBILITY)
df["Feasibility"] = df.Feasibility.astype("uint8")


### Set data types
for column in (
    "River",
    "NIDID",
    "Source",
    "Name",
    "OtherName",
    "SourceDBID",
    "Editor",
    "EditDate",
):
    df[column] = df[column].fillna("").str.strip()

df["BarrierSeverity"] = df.BarrierSeverity.fillna("Unknown").str.strip()
df.loc[df.BarrierSeverity == "Complete Barrier", "BarrierSeverity"] = "Complete"
# temporary fixes
df.BarrierSeverity = df.BarrierSeverity.str.replace(
    "Seasonbly", "Seasonably"
).str.replace(
    "Partial Passibility - Non Salmonid", "Partial Passability - Non Salmonid"
)

for column in (
    "Construction",
    "Condition",
    "Purpose",
    "ManualReview",
    "PassageFacility",
    "BarrierStatus",
    "Diversion",
    "FishScreen",
    "ScreenType",
    "StructureCategory",
):
    df[column] = df[column].fillna(0).astype("uint8")

for column in ("Year", "YearRemoved"):
    df[column] = df[column].fillna(0).astype("uint16")


# Fix Recon value that wasn't assigned to ManualReview
# these are invasive species barriers
df.loc[df.Recon == 16, "ManualReview"] = 10

# Reset manual review for dams that were previously not snapped, but are not reviewed
df.loc[df.ManualReview.isin([7, 9]), "ManualReview"] = 0

# Update dam condition based on BarrierStatus and Recon
# dam failed
df.loc[df.Recon == 18, "Condition"] = 5
# dam breached (but we don't know if this was on purpose)
df.loc[df.BarrierStatus.isin([2, 3]), "Condition"] = 6


# Round height and width to nearest foot.
# There are no dams between 0 and 1 foot, so fill all na as 0.
df.Height = df.Height.fillna(0).round().astype("uint16")
# coerce length to width
df.Length = df.Length.fillna(0).round().astype("uint16")
df.Width = df.Width.fillna(0).round().astype("uint16")

df.LowheadDam = df.LowheadDam.fillna(-1).astype("int8")

# manually reviewed dams > 5ft that are highly likely to be lowhead dams
df.loc[
    df.SARPID.isin(
        [
            "NC3047",
            "NC248",
            "VA1999",
            "NC01012",
            "NC00446",
            "NC01637",
            "NC6267",
            "NC6283",
            "NC01218",
            "TN1752",
            "AL00919",
        ]
    ),
    "LowheadDam",
] = 1


# TODO: from Kat: if in NC and source is Aquatic Obstruction Inventory, also set lowhead dam


# Cleanup names
# Standardize the casing of the name
df.Name = df.Name.str.title()
df.OtherName = df.OtherName.str.title()
df.River = df.River.str.title()

# Fix name issue - 3 dams have duplicate dam names with line breaks, which breaks tippecanoe
ids = df.loc[df.Name.str.count("\r") > 0].index
df.loc[ids, "Name"] = df.loc[ids].Name.apply(lambda v: v.split("\r")[0]).fillna("")


# Fix years between 0 and 100; assume they were in the 1900s
df.loc[(df.Year > 0) & (df.Year < 100), "Year"] = df.Year + 1900
df.loc[df.Year == 20151, "Year"] = 2015
df.loc[df.Year == 9999, "Year"] = 0

### Calculate classes


# Calculate height class
df["HeightClass"] = 0  # Unknown
df.loc[(df.Height > 0) & (df.Height < 5), "HeightClass"] = 1
df.loc[(df.Height >= 5) & (df.Height < 10), "HeightClass"] = 2
df.loc[(df.Height >= 10) & (df.Height < 25), "HeightClass"] = 3
df.loc[(df.Height >= 25) & (df.Height < 50), "HeightClass"] = 4
df.loc[(df.Height >= 50) & (df.Height < 100), "HeightClass"] = 5
df.loc[df.Height >= 100, "HeightClass"] = 6
df.HeightClass = df.HeightClass.astype("uint8")

# Convert PassageFacility to a boolean for filtering
df["PassageFacilityClass"] = (
    (df.PassageFacility > 0) & (df.PassageFacility != 9)
).astype("uint8")

# Convert BarrierSeverity to a domain
df.BarrierSeverity = df.BarrierSeverity.map(DAM_BARRIER_SEVERITY_TO_DOMAIN).astype(
    "uint8"
)


### Spatial joins
df = add_spatial_joins(df)

print("-----------------")

# Cleanup HUC, state, county, and ecoregion columns that weren't assigned
for col in [
    "HUC2",
    "HUC6",
    "HUC8",
    "HUC12",
    "Basin",
    "Subbasin",
    "Subwatershed",
    "County",
    "COUNTYFIPS",
    "STATEFIPS",
    "State",
    "ECO3",
    "ECO4",
]:
    df[col] = df[col].fillna("").astype("str")

### Add tracking fields
# master log field for status
df["log"] = ""
# dropped: records that should not be included in any later analysis
df["dropped"] = False

# excluded: records that should be retained in dataset but not used in analysis
df["excluded"] = False

# unranked: records that should break the network but not be used for ranking
df["unranked"] = False

# removed: dam was removed for conservation but we still want to track it
df["removed"] = False

# Drop any that didn't intersect HUCs or states
drop_ix = (df.HUC12 == "") | (df.STATEFIPS == "")
if drop_ix.sum():
    print(f"{drop_ix.sum():,} dams are outside HUC12 / states")
    # Mark dropped barriers
    df.loc[drop_ix, "dropped"] = True
    df.loc[drop_ix, "log"] = "dropped: outside HUC12 / states"

### Drop any dams that should be completely dropped from analysis
# based on manual QA/QC and other reivew.

# Drop those where recon shows this as an error
drop_ix = df.Recon.isin(DROP_RECON) & ~df.dropped
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: Recon one of {DROP_RECON}"

# Drop those where recon shows this as an error
drop_ix = df.Feasibility.isin(DROP_FEASIBILITY) & ~df.dropped
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: Feasibility one of {DROP_FEASIBILITY}"

# Drop those that were manually reviewed off-network or errors
drop_ix = df.ManualReview.isin(DROP_MANUALREVIEW) & ~df.dropped
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: ManualReview one of {DROP_MANUALREVIEW}"

# From Kat: if the dam includes "dike" in the name and not "dam", it is not really a dam
drop_ix = (
    df.Name.str.lower().str.contains(" dike")
    & (~df.Name.str.lower().str.contains(" dam"))
    & ~df.dropped
    & ~df.ManualReview.isin(ONSTREAM_MANUALREVIEW)
)
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = "dropped: name includes dike and not dam"

# Drop any that are diversions (irrigation ditches) without an associated structure
# from Kat: anything that is partial or complete barrier should cut the network; others
# should be dropped
drop_ix = (
    (df.StructureCategory.isin(DROP_STRUCTURECATEGORY))
    & (df.BarrierSeverity.isin([0, 7]))
    & (~df.dropped)
)
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: StructureCategory one of {DROP_STRUCTURECATEGORY}"

print(f"Dropped {df.dropped.sum():,} dams from all analysis and mapping")

### Exclude dams that should not be analyzed or prioritized based on manual QA
df["excluded"] = (
    df.ManualReview.isin(EXCLUDE_MANUALREVIEW)
    | df.Recon.isin(EXCLUDE_RECON)
    | df.Feasibility.isin(EXCLUDE_FEASIBILITY)
    | df.PassageFacility.isin(EXCLUDE_PASSAGEFACILITY)
    | df.BarrierSeverity.isin(EXCLUDE_BARRIER_SEVERITY)
)

df.loc[
    df.PassageFacility.isin(EXCLUDE_PASSAGEFACILITY), "log"
] = f"excluded: PassageFacility one of {EXCLUDE_PASSAGEFACILITY}"
df.loc[
    df.Feasibility.isin(EXCLUDE_FEASIBILITY), "log"
] = f"excluded: Feasibility one of {EXCLUDE_FEASIBILITY}"
df.loc[
    df.BarrierSeverity.isin(EXCLUDE_BARRIER_SEVERITY), "log"
] = f"excluded: BarrierSeverity one of {EXCLUDE_BARRIER_SEVERITY}"
df.loc[df.Recon.isin(EXCLUDE_RECON), "log"] = f"excluded: Recon one of {EXCLUDE_RECON}"
df.loc[
    df.ManualReview.isin(EXCLUDE_MANUALREVIEW), "log"
] = f"excluded: ManualReview one of {EXCLUDE_MANUALREVIEW}"
print(f"Excluded {df.excluded.sum():,} dams from analysis and prioritization")


### Mark any dams that should cut the network but be excluded from ranking
unranked_idx = ()
df["unranked"] = (
    df.ManualReview.isin(UNRANKED_MANUALREVIEW)
    | df.Recon.isin(UNRANKED_RECON)
    | df.Feasibility.isin(UNRANKED_FEASIBILITY)
)
df.loc[
    df.Feasibility.isin(UNRANKED_FEASIBILITY), "log"
] = f"unranked: Feasibility one of {UNRANKED_FEASIBILITY}"
df.loc[
    df.Recon.isin(UNRANKED_RECON), "log"
] = f"unranked: Recon one of {UNRANKED_RECON}"
df.loc[
    df.ManualReview.isin(UNRANKED_MANUALREVIEW), "log"
] = f"unranked: ManualReview one of {UNRANKED_MANUALREVIEW}"

### Mark any that were removed so that we can show these on the map
df["removed"] = (df.ManualReview == 8) | (df.Recon == 7) | (df.Feasibility == 8)
df.loc[df.removed, "log"] = f"removed: dam was removed for conservation"
print(
    f"Marked {df.unranked.sum():,} dams beneficial to containing invasives to omit from ranking"
)


### Snap dams
# snapped: records that snapped to the aquatic network and ready for network analysis
df["snapped"] = False
df[
    "snap_group"
] = 0  # 0 = default, 1 = estimated (previous), 2 = Amber Ignatius ACF dams, 3 = estimated from waterbodies
df["snap_tolerance"] = SNAP_TOLERANCE["default"]
df["snap_log"] = "not snapped"
df["snap_ref_id"] = np.nan  # id of feature from snap type this was snapped to
df["snap_dist"] = np.nan
df["lineID"] = np.nan  # line to which dam was snapped
df["wbID"] = np.nan  # waterbody ID where dam is either contained or snapped


# for dams that are marked as on network or from NABD that have a length (across the stream),
# use their length to determine snap tolerance (convert feet to meters, rounded up to nearest 100m)
# limited to 1000m
ix = df.ManualReview.isin([2, 4]) & (df.Length > 0)
length_tolerance = np.clip(
    (np.ceil((df.loc[ix].Length.values * 0.3048) / 100) * 100).round().astype("int64"),
    0,
    1000,
)

df.loc[ix, "snap_tolerance"] = np.max(
    [df.loc[ix].snap_tolerance.values, length_tolerance], axis=0
)


# log dams excluded from snapping
df.loc[
    df.ManualReview.isin(OFFSTREAM_MANUALREVIEW), "snap_log"
] = f"excluded from snapping (manual review one of {OFFSTREAM_MANUALREVIEW})"

### Mark dam snapping groups
# estimated dams or likely off-network dams will get lower snapping tolerance


# these were generated by SARP from analysis of small waterbodies
# NOTE: this MUST be done AFTER dropping / excluding barriers
ix = (
    (df.Name.str.count("Estimated Dam") > 0)
    | df.Source.str.lower().str.count("estimated")
    | (df.SourceDBID.str.startswith("e"))
)

df.loc[ix, "snap_group"] = 1  # indicates estimated dam
df["is_estimated"] = ix

# Replace estimated dam names if another name is available
ix = ix & (df.OtherName.str.len() > 0)
df.loc[ix, "Name"] = df.loc[ix].OtherName


# Amber Ignatius ACF dams are often features that don't have associated flowlines,
# flag so we don't snap to flowlines that aren't really close
# NOTE: this MUST be done AFTER dropping / excluding barriers
df.loc[df.Source.str.count("Amber Ignatius") > 0, "snap_group"] = 2

# Identify dams estimated from waterbodies
ix = df.Source.isin(["Estimated Dams OCT 2021"])
df.loc[ix, "snap_group"] = 3
df.loc[ix, "Name"] = "Estimated (" + df.loc[ix].SARPID + ")"

# Dams likely to be off network get a much smaller tolerance
df.loc[df.snap_group.isin([1, 2]), "snap_tolerance"] = SNAP_TOLERANCE[
    "likely off network"
]
print(
    f"Setting snap tolerance to {SNAP_TOLERANCE['likely off network']}m for {df.snap_group.isin([1,2]).sum():,} dams likely off network"
)

df.loc[df.snap_group == 3, "snap_tolerance"] = SNAP_TOLERANCE["estimated from network"]
print(
    f"Setting snap tolerance to {SNAP_TOLERANCE['estimated from network']}m for {(df.snap_group == 3).sum():,} dams estimated from waterbodies"
)


# IMPORTANT: do not snap manually reviewed, off-network dams, duplicates, or ones without HUC2!
to_snap = df.loc[
    (~df.ManualReview.isin(OFFSTREAM_MANUALREVIEW))
    & (df.HUC2 != "")
    & (df.STATEFIPS != "")
].copy()

# Save original locations so we can map the snap line between original and new locations
original_locations = to_snap.copy()

snap_start = time()

print("-----------------")

# Snap estimated dams to the drain point of the waterbody that contains them, if possible
df, to_snap = snap_estimated_dams_to_drains(df, to_snap)

# # Snap to NHD dams
df, to_snap = snap_to_nhd_dams(df, to_snap)

# Snap to waterbodies
df, to_snap = snap_to_waterbodies(df, to_snap)

# Snap to flowlines
df, to_snap = snap_to_flowlines(df, to_snap)

print(f"Snapped {df.snapped.sum():,} dams in {time() - snap_start:.2f}s")

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
df["dup_log"] = "not a duplicate"
df["dup_group"] = np.nan
df["dup_count"] = np.nan
# duplicate sort will be assigned lower values to find preferred entry w/in dups
df["dup_sort"] = 9999

# assign duplicate status for any that were manually reviewed as such
ix = df.ManualReview == 11
df.loc[ix, "duplicate"] = True
df.loc[ix, "dup_log"] = "Manually reviewed as duplicate"


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

# Exclude those where ManualReview indicated duplicate (these are also dropped),
# otherwise this cascades to drop other barriers in this group; at least one of
# which should be kept
to_dedup = df.loc[~df.duplicate].copy()


# Dams within 10 meters are very likely duplicates of each other
# from those that were hand-checked on the map, they are duplicates of each other
df, to_dedup = find_duplicates(df, to_dedup, tolerance=DUPLICATE_TOLERANCE["default"])

# Search a bit further for duplicates from estimated dams that snapped
# hand-checked these on the map, these look very likely to be real duplicates
next_group_id = df.dup_group.max() + 1
to_dedup = to_dedup.loc[to_dedup.snapped & df.snap_group.isin([1, 2])].copy()
df, to_dedup = find_duplicates(
    df,
    to_dedup,
    tolerance=DUPLICATE_TOLERANCE["likely duplicate"],
    next_group_id=next_group_id,
)

print(f"Found {df.duplicate.sum():,} total duplicates in {time() - dedup_start:.2f}s")
print("---------------------------------")
print("\nDe-duplication statistics")
print(df.groupby("dup_log").size())
print("---------------------------------\n")

# Export duplicate areas for QA
dups = df.loc[df.dup_group.notnull()].copy()
dups.dup_group = dups.dup_group.astype("uint16")
dups["dup_tolerance"] = DUPLICATE_TOLERANCE["default"]
ix = dups.snapped & dups.snap_group.isin([1, 2])
dups.loc[ix, "dup_tolerance"] = DUPLICATE_TOLERANCE["likely duplicate"]

export_duplicate_areas(dups, qa_dir / "dams_duplicate_areas.fgb")


### Join to line atts
flowlines = (
    read_feathers(
        [
            nhd_dir / "clean" / huc2 / "flowlines.feather"
            for huc2 in df.HUC2.unique()
            if huc2
        ],
        columns=[
            "lineID",
            "NHDPlusID",
            "GNIS_Name",
            "sizeclass",
            "StreamOrde",
            "FCode",
            "loop",
        ],
    )
    .rename(columns={"StreamOrde": "StreamOrder"})
    .set_index("lineID")
)

df = df.join(flowlines, on="lineID")

df.StreamOrder = df.StreamOrder.fillna(-1).astype("int8")

# Add name from snapped flowline if not already present
df["GNIS_Name"] = df.GNIS_Name.fillna("").str.strip()
ix = (df.River == "") & (df.GNIS_Name != "")
df.loc[ix, "River"] = df.loc[ix].GNIS_Name
df = df.drop(columns=["GNIS_Name"])

# calculate stream type
df["stream_type"] = df.FCode.map(FCODE_TO_STREAMTYPE)

# calculate intermittent + ephemeral
df["intermittent"] = df.FCode.isin([46003, 46007])


# Fix missing field values
df["loop"] = df.loop.fillna(False)
df["sizeclass"] = df.sizeclass.fillna("")
df["FCode"] = df.FCode.fillna(-1).astype("int32")

print("dams on loops:\n", df.groupby("loop").size())


### Join waterbody properties
wb = (
    read_feathers(
        [
            nhd_dir / "clean" / huc2 / "waterbodies.feather"
            for huc2 in df.HUC2.unique()
            if huc2
        ],
        columns=["wbID", "km2"],
    )
    .rename(columns={"km2": "WaterbodyKM2"})
    .set_index("wbID")
)

wb["WaterbodySizeClass"] = classify_waterbody_size(wb.WaterbodyKM2)

df = df.join(wb, on="wbID")
df.WaterbodyKM2 = df.WaterbodyKM2.fillna(-1).astype("float32")
df.WaterbodySizeClass = df.WaterbodySizeClass.fillna(-1).astype("int8")


### Update lowhead dam status with estimated lowhead dams
# from Kat: if ImpoundmentType==1 (run of the river), it is likely a lowhead dam;
# limit this to <= 15 feet based on review against aerial imagery (very few over 15 feet are lowhead)
# ignore estimated dams or ones on very small streams
df.loc[
    (df.LowheadDam == -1)
    & (df.ImpoundmentType == 1)
    & (df.Height <= 25)
    & (~df.is_estimated)
    & (df.snapped)
    & (df.sizeclass != "1a"),
    "LowheadDam",
] = 2


### Add lat / lon (must be done after snapping!)
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(GEO_CRS)
geo["lat"] = pg.get_y(geo.geometry.values.data).astype("float32")
geo["lon"] = pg.get_x(geo.geometry.values.data).astype("float32")
df = df.join(geo[["lat", "lon"]])


### All done processing!

print("\n--------------\n")
df = df.reset_index(drop=True)

print("Serializing {:,} dams to master file".format(len(df)))
df.to_feather(master_dir / "dams.feather")
write_dataframe(df, qa_dir / "dams.fgb")


# Extract out only the snapped ones
df = df.loc[df.snapped & (~(df.duplicate | df.dropped | df.excluded))].reset_index(
    drop=True
)
df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

print("Serializing {:,} snapped dams".format(len(df)))
df[
    ["geometry", "id", "HUC2", "lineID", "NHDPlusID", "loop", "intermittent"]
].to_feather(snapped_dir / "dams.feather",)
write_dataframe(df, qa_dir / "snapped_dams.fgb")


print("All done in {:.2f}s".format(time() - start))
