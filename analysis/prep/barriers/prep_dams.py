"""
Extract dams from original data source, process for use in network analysis, and convert to feather format.
1. Cleanup data values (as needed)
2. Filter out dams not to be included in analysis (based on Feasibility and ManualReview)
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
from nhdnet.geometry.lines import snap_to_line, snap_to_waterbody_points
from nhdnet.geometry.points import mark_duplicates

pd.options.display.max_rows = 250


from analysis.constants import (
    REGION_GROUPS,
    REGIONS,
    CRS,
    DAM_COLS,
    DROP_MANUALREVIEW,
    EXCLUDE_MANUALREVIEW,
    DROP_RECON,
    DROP_FEASIBILITY,
    EXCLUDE_RECON,
    RECON_TO_FEASIBILITY,
)

from analysis.prep.barriers.lib.snap import (
    snap_to_waterbody_points,
    snap_by_region,
    update_from_snapped,
)
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins


DUPLICATE_TOLERANCE = 30
# Snap barriers by 150 meters
SNAP_TOLERANCE = 150

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
# Join on AnalysisID to merged data above.
# ONLY keep ManualReview and the location.
print("Reading manually snapped dams...")
snapped_df = from_geofeather(
    src_dir / "manually_snapped_dams.feather",
    columns=["geometry", "ManualReview", "AnalysisID"],
).set_index("AnalysisID")

# Don't pull across those that were not manually snapped
snapped_df = snapped_df.loc[~snapped_df.ManualReview.isin([7, 9])]

# Join to snapped and bring across updated geometry and ManualReview

df = df.join(snapped_df, on="AnalysisID", rsuffix="_snap")

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
### Set data types
for column in ("River", "NIDID", "Source"):
    df[column] = df[column].fillna("").str.strip()

for column in ("Construction", "Condition", "Purpose", "Recon"):
    df[column] = df[column].fillna(0).astype("uint8")

for column in ("Year", "Feasibility", "ManualReview"):
    df[column] = df[column].fillna(0).astype("uint16")


# Fix Recon value that wasn't assigned to ManualReview
# these are invasive species barriers
df.loc[df.Recon == 16, "ManualReview"] = 10


# Round height to nearest foot.  There are no dams between 0 and 1 foot, so fill all
# na as 0
df.Height = df.Height.fillna(0).round().astype("uint16")

# Cleanup names
# Standardize the casing of the name
df.Name = df.Name.fillna("").str.title().str.strip()
df.OtherName = df.OtherName.fillna("").str.title().str.strip()

df.River = df.River.str.title()

# Fix name issue - 3 dams have duplicate dam names with line breaks, which breaks tippecanoe
ids = df.loc[df.Name.str.count("\r") > 0].index
df.loc[ids, "Name"] = df.loc[ids].Name.apply(lambda v: v.split("\r")[0])

# Replace estimated dam names if another name is available
ids = (df.Name.str.count("Estimated Dam") > 0) & (df.OtherName.str.len() > 0)
df.loc[ids, "Name"] = df.loc[ids].OtherName


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


# Drop any that didn't intersect HUCs or states
drop_idx = df.HUC12.isnull() | df.STATEFIPS.isnull()
print("{:,} dams are outside HUC12 / states".format(len(df.loc[drop_idx])))
# Mark dropped barriers
df.loc[drop_idx, "dropped"] = True


### Drop any dams that should be completely dropped from analysis
# based on manual QA/QC
drop_idx = (
    df.Recon.isin(DROP_RECON)
    | df.Feasibility.isin(DROP_FEASIBILITY)
    | df.ManualReview.isin(DROP_MANUALREVIEW)
)

df.loc[drop_idx, "dropped"] = True


### Drop duplicate NIDID records
# TODO: WIP!

# Find any where one of the duplicates for an NIDID was dropped;
# we may need to drop the others too if they are close
# by_nidid = df.loc[(df.NIDID != "")].groupby("NIDID")
# count_by_nidid = by_nidid.size()
# dup_nidid = count_by_nidid.loc[count_by_nidid > 1].index
# maybe_dropped = df.loc[
#     (df.NIDID.isin(dup_nidid)) & (df.NIDID.isin(df.loc[df.dropped].NIDID))
# ].copy()


# by_nidid = df.loc[(df.NIDID != "") & (~df.dropped)].groupby("NIDID")
# count_by_nidid = by_nidid.size()
# dup_nidid = count_by_nidid.loc[count_by_nidid > 1].index
# dups = df.loc[df.NIDID.isin(dup_nidid)].copy()

# # Assign empty ManualReview to high value
# dups.loc[dups.ManualReview == 0, "ManualReview"] = 999
# dups = dups.sort_values(by="ManualReview")


### Drop dams with "dike" in the name (but not "dam")
# these were manually checked by Kat, and either off network or otherwise not dams.
# This must be done AFTER deduplicating NIDID
df.loc[
    (df.Name.str.lower().str.contains(" dike"))
    & (~df.Name.str.lower().str.contains(" dam")),
    "dropped",
] = True


# NOTE: these have varying attributes, so try to take the non-zero values where available
# ManualReview 7,9 are not meaningful,
# For any given duplicate set, if there is a ManualReview == 1 available, use that

# If one that is dropped has same NIDID and is very close to one that has missing or blah ManualReview, consider dropping those too


print("Dropped {:,} dams from all analysis and mapping".format(len(df.loc[df.dropped])))


### Exclude dams that should not be analyzed or prioritized based on manual QA
exclude_idx = df.Recon.isin(EXCLUDE_RECON) | df.ManualReview.isin(EXCLUDE_MANUALREVIEW)
print(
    "Excluded {:,} dams from network analysis and prioritization".format(
        len(df.loc[exclude_idx])
    )
)
df.loc[exclude_idx, "excluded"] = True
print("Excluded {:,} dams from analysis".format(len(df.loc[df.excluded])))


# FIXME:
to_geofeather(df.reset_index(drop=True), "/tmp/pre-snap.feather")


### Snap to waterbody drain points and flowlines

# If ManualReview==2, these are NABD dams and potentially large, but not immediately on the network.
# If ManualReview==4, these were visually verified by SARP as being on network, but may
# be larger dams and > 100 m off channel.  Snap up to 250 meters for these.

to_snap = df.loc[
    ~(df.dropped | df.excluded), ["geometry", "HUC2", "id", "ManualReview"]
].copy()
to_snap["tolerance"] = SNAP_TOLERANCE
to_snap.loc[to_snap.ManualReview.isin([2, 4]), "tolerance"] = 250

print("Attempting to snap {:,} dams".format(len(to_snap)))

# Snap to waterbody drain points
snapped = snap_to_waterbody_points(to_snap)


### TODO: points that snap to within-waterbody segments are suspect, watch for duplicates


# Snap to flowlines
snapped = snap_by_region(to_snap, REGION_GROUPS)


# join back to master
df = update_from_snapped(df, snapped)


# Remove duplicates after snapping, in case any snapped to the same position
# These are completely dropped from the analysis from here on out
# Sort by ascending order of the boolean attributes that indicate barriers are to be dropped / excluded
# so that if one of a duplicate cluster was dropped / excluded, the rest are too.
df = mark_duplicates(
    df.sort_values(by=["dropped", "excluded", "snapped"]), DUPLICATE_TOLERANCE
)
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
