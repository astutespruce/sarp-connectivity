"""
Extract small barriers from original data source, process for use in network analysis, and convert to feather format.
1. Cleanup data values (as needed)
2. Filter out barriers not to be included in analysis (based on Potential_Project and ManualReview)
3. Snap to flowlines
4. Remove duplicate barriers
5. Remove barriers that duplicate dams

NOTE: this must be run AFTER running prep_dams.py, because it deduplicates against existing dams.

This creates 2 files:
`barriers/master/small_barriers.feather` - master barriers dataset, including coordinates updated from snapping
`barriers/snapped/small_barriers.feather` - snapped barriers dataset for network analysis

This creates several QA/QC files:
- `barriers/qa/small_barriers_pre_snap_to_post_snap.gpkg`: lines between the original coordinate and the snapped coordinate (snapped barriers only)
- `barriers/qa/small_barriers_pre_snap.gpkg`: original, unsnapped coordinate (snapped barriers only)
- `barriers/qa/small_barriers_post_snap.gpkg`: snapped coordinate (snapped barriers only)
- `barriers/qa/small_barriers_duplicate_areas.gpkg`: dissolved buffers around duplicate barriers (duplicates only)
"""

from pathlib import Path
from time import time
import warnings

import pandas as pd
import geopandas as gp
import numpy as np
from pyogrio import write_dataframe

from analysis.prep.barriers.lib.snap import snap_to_flowlines, export_snap_dist_lines
from analysis.prep.barriers.lib.duplicates import (
    find_duplicates,
    export_duplicate_areas,
)
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins
from analysis.lib.io import read_feathers
from analysis.lib.pygeos_util import nearest
from analysis.constants import (
    CRS,
    KEEP_POTENTIAL_PROJECT,
    DROP_POTENTIAL_PROJECT,
    DROP_MANUALREVIEW,
    EXCLUDE_MANUALREVIEW,
    BARRIER_CONDITION_TO_DOMAIN,
    POTENTIAL_TO_SEVERITY,
    ROAD_TYPE_TO_DOMAIN,
    CROSSING_TYPE_TO_DOMAIN,
)

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

# Snap barriers by 50 meters
SNAP_TOLERANCE = 50
DUPLICATE_TOLERANCE = 10  # meters


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
nhd_dir = data_dir / "nhd"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
master_dir = barriers_dir / "master"
snapped_dir = barriers_dir / "snapped"
qa_dir = barriers_dir / "qa"

start = time()

df = gp.read_feather(src_dir / "sarp_small_barriers.feather")
print(f"Read {len(df):,} small barriers")


### Make sure there are not duplicates
s = df.groupby("SARPID").size()
if s.max() > 1:
    print(s[s > 1].index)
    raise ValueError("Multiple barriers with same SARPID")


### Add IDs for internal use
# internal ID
df["id"] = df.index.astype("uint32")
df = df.set_index("id", drop=False)

######### Fix data issues

# Fix mixed casing of values
for column in ("CrossingType", "RoadType", "Stream", "Road"):
    df[column] = df[column].fillna("Unknown").str.title().str.strip()
    df.loc[df[column].str.len() == 0, column] = "Unknown"

# Fix line returns in stream name and road name
df.loc[df.Stream.str.contains("\r\n", ""), "Stream"] = "Unnamed"
df.Road = df.Road.str.replace("\r\n", "")

df.loc[
    (~df.Stream.isin(["Unknown", "Unnamed", ""]))
    & (~df.Road.isin(["Unknown", "Unnamed", ""])),
    "Name",
] = (
    df.Stream + " / " + df.Road
)
df.Name = df.Name.fillna("")


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


### Calculate classes
df["ConditionClass"] = df.Condition.map(BARRIER_CONDITION_TO_DOMAIN)
df["SeverityClass"] = df.PotentialProject.map(POTENTIAL_TO_SEVERITY)
df["CrossingTypeClass"] = df.CrossingType.map(CROSSING_TYPE_TO_DOMAIN)
df["RoadTypeClass"] = df.RoadType.map(ROAD_TYPE_TO_DOMAIN)


### Spatial joins
df = add_spatial_joins(df)

# Cleanup HUC, state, county, and ecoregion columns that weren't assigned
for col in [
    "HUC2",
    "HUC6",
    "HUC8",
    "HUC12",
    "Basin",
    "County",
    "COUNTYFIPS",
    "STATEFIPS",
    "State",
    "ECO3",
    "ECO4",
]:
    df[col] = df[col].fillna("")

### Add tracking fields
# master log field for status
df["log"] = ""
# dropped: records that should not be included in any later analysis
df["dropped"] = False

# excluded: records that should be retained in dataset but not used in analysis
df["excluded"] = False

# Drop any that didn't intersect HUCs or states
drop_ix = (df.HUC12 == "") | (df.STATEFIPS == "")
print(f"{drop_ix.sum():,} small barriers are outside HUC12 / states")
# Mark dropped barriers
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = "dropped: outside HUC12 / states"


### Drop any small barriers that should be completely dropped from analysis
# based on manual QA/QC
drop_ix = df.PotentialProject.isin(DROP_POTENTIAL_PROJECT)
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: PotentialProject one of {DROP_POTENTIAL_PROJECT}"
print(
    f"Dropped {drop_ix.sum():,} small barriers from all analysis and mapping based on PotentialProject"
)

drop_ix = df.ManualReview.isin(DROP_MANUALREVIEW)
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: ManualReview one of {DROP_MANUALREVIEW}"
print(
    f"Dropped {drop_ix.sum():,} small barriers from all analysis and mapping based on ManualReview"
)

### Exclude barriers that should not be analyzed or prioritized based on manual QA
exclude_ix = ~df.PotentialProject.isin(KEEP_POTENTIAL_PROJECT)
df.loc[exclude_ix, "excluded"] = True
df.loc[
    exclude_ix, "log"
] = f"excluded: PotentialProject not one of retained types {KEEP_POTENTIAL_PROJECT}"
print(
    f"Excluded {exclude_ix.sum():,} small barriers from network analysis and prioritization based on PotentialProject"
)


exclude_ix = df.ManualReview.isin(EXCLUDE_MANUALREVIEW)
df.loc[exclude_ix, "excluded"] = True
df.loc[exclude_ix, "log"] = f"excluded: ManualReview one of {EXCLUDE_MANUALREVIEW}"
print(
    f"Excluded {exclude_ix.sum():,} small barriers from network analysis and prioritization based on ManualReview"
)


### Snap barriers
print(f"Snapping {len(df):,} small barriers")

df["snapped"] = False
df["snap_log"] = "not snapped"
df["lineID"] = np.nan  # line to which dam was snapped
df["snap_tolerance"] = SNAP_TOLERANCE

# Save original locations so we can map the snap line between original and new locations
original_locations = df.copy()

# Only snap those that have HUC2 assigned
to_snap = df.loc[df.HUC2 != ""].copy()

# Snap to flowlines
snap_start = time()
df, to_snap = snap_to_flowlines(df, to_snap)

print(f"Snapped {df.snapped.sum():,} small barriers in {time() - snap_start:.2f}s")

print("---------------------------------")
print("\nSnapping statistics")
print(df.groupby("snap_log").size())
print("---------------------------------\n")


### Save results from snapping for QA
export_snap_dist_lines(
    df.loc[df.snapped], original_locations, qa_dir, prefix="small_barriers_"
)


print("\n--------------\n")

### Remove duplicates after snapping, in case any snapped to the same position
print("Removing duplicates...")

df["duplicate"] = False
df["dup_group"] = np.nan
df["dup_count"] = np.nan
df["dup_log"] = "not a duplicate"

# Duplicate sort is opposite of SeverityClass
df["dup_sort"] = df.SeverityClass.map(
    {np.nan: 9999, 0: 9999, 1: 3, 2: 2, 3: 1}  # highest sort, highest severity
)

dedup_start = time()
df, to_dedup = find_duplicates(df, to_dedup=df.copy(), tolerance=DUPLICATE_TOLERANCE)
print(f"Found {df.duplicate.sum():,} total duplicates in {time() - dedup_start:.2f}s")

print("---------------------------------")
print("\nDe-duplication statistics")
print(df.groupby("dup_log").size())
print("---------------------------------\n")

# Export duplicate areas for QA
dups = df.loc[df.dup_group.notnull()].copy()
dups.dup_group = dups.dup_group.astype("uint16")
dups["dup_tolerance"] = DUPLICATE_TOLERANCE
export_duplicate_areas(dups, qa_dir / "small_barriers_duplicate_areas.gpkg")


### Deduplicate by dams
# any that are within duplicate tolerance of dams may be duplicating those dams
dams = gp.read_feather(master_dir / "dams.feather").set_index("id")
near_dams = nearest(
    pd.Series(df.geometry.values.data, index=df.index),
    pd.Series(dams.geometry.values.data, index=dams.index),
    DUPLICATE_TOLERANCE,
)

ix = near_dams.index
df.loc[ix, "duplicate"] = True
df.loc[ix, "dup_log"] = f"Within {DUPLICATE_TOLERANCE}m of an existing dam"

print(f"Found {len(ix)} small barriers within {DUPLICATE_TOLERANCE}m of dams")

### Join to line atts
flowlines = read_feathers(
    [
        nhd_dir / "clean" / huc2 / "flowlines.feather"
        for huc2 in df.HUC2.unique()
        if huc2
    ],
    columns=["lineID", "NHDPlusID", "sizeclass", "StreamOrde", "loop"],
).set_index("lineID")

df = df.join(flowlines, on="lineID")

# Fix missing field values
df["loop"] = df.loop.fillna(False)
df["sizeclass"] = df.sizeclass.fillna("")

print(df.groupby("loop").size())

print("\n--------------\n")

df = df.reset_index(drop=True)

print("Serializing {:,} small barriers".format(len(df)))
df.to_feather(master_dir / "small_barriers.feather")
write_dataframe(df, qa_dir / "small_barriers.gpkg")


# Extract out only the snapped ones
df = df.loc[df.snapped & ~(df.duplicate | df.dropped | df.excluded)].reset_index(
    drop=True
)
df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

print("Serializing {:,} snapped small barriers".format(len(df)))
df[["geometry", "id", "HUC2", "lineID", "NHDPlusID", "loop"]].to_feather(
    snapped_dir / "small_barriers.feather",
)
write_dataframe(df, qa_dir / "snapped_small_barriers.gpkg")

print("All done in {:.2f}s".format(time() - start))
