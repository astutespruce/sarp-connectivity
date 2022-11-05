"""
Extract small barriers from original data source, process for use in network analysis, and convert to feather format.
1. Cleanup data values (as needed)
2. Filter out barriers not to be included in analysis (based on Potential_Project and ManualReview)
3. Snap to flowlines
4. Remove duplicate barriers
5. Remove barriers that duplicate dams
6. Mark barriers that co-occur with waterfalls (waterfalls have higher precedence)

NOTE: this must be run AFTER running prep_dams.py, because it deduplicates against existing dams.

This creates 2 files:
`barriers/master/small_barriers.feather` - master barriers dataset, including coordinates updated from snapping
`barriers/snapped/small_barriers.feather` - snapped barriers dataset for network analysis

This creates several QA/QC files:
- `barriers/qa/small_barriers_pre_snap_to_post_snap.fgb`: lines between the original coordinate and the snapped coordinate (snapped barriers only)
- `barriers/qa/small_barriers_pre_snap.fgb`: original, unsnapped coordinate (snapped barriers only)
- `barriers/qa/small_barriers_post_snap.fgb`: snapped coordinate (snapped barriers only)
- `barriers/qa/small_barriers_duplicate_areas.fgb`: dissolved buffers around duplicate barriers (duplicates only)
"""

from pathlib import Path
from time import time
import warnings

import pandas as pd
import geopandas as gp
import shapely
import numpy as np
from pyogrio import write_dataframe

from analysis.prep.barriers.lib.snap import snap_to_flowlines, export_snap_dist_lines
from analysis.prep.barriers.lib.duplicates import (
    find_duplicates,
    export_duplicate_areas,
)
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins
from analysis.prep.barriers.lib.log import format_log
from analysis.lib.io import read_feathers
from analysis.constants import (
    SMALL_BARRIERS_ID_OFFSET,
    GEO_CRS,
    KEEP_POTENTIAL_PROJECT,
    DROP_POTENTIAL_PROJECT,
    UNRANKED_POTENTIAL_PROJECT,
    REMOVED_POTENTIAL_PROJECT,
    DROP_RECON,
    EXCLUDE_RECON,
    REMOVED_RECON,
    DROP_MANUALREVIEW,
    EXCLUDE_MANUALREVIEW,
    REMOVED_MANUALREVIEW,
    OFFSTREAM_MANUALREVIEW,
    INVASIVE_MANUALREVIEW,
    INVASIVE_RECON,
    BARRIER_CONDITION_TO_DOMAIN,
    POTENTIALPROJECT_TO_SEVERITY,
    ROAD_TYPE_TO_DOMAIN,
    CROSSING_TYPE_TO_DOMAIN,
    FCODE_TO_STREAMTYPE,
    CONSTRICTION_TO_DOMAIN,
    BARRIEROWNERTYPE_TO_DOMAIN,
)

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

### Custom tolerance values for dams
SNAP_TOLERANCE = {
    "default": 50,
    # some of the PNW points are in the correct location but NHD flowlines are
    # less precise, need greater tolerance to line them up
    "pnw": 75,
    # some data sources have coordinates that are less precise; use a larger snapping tolerance
    "bat survey": 100,
}


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
    warnings.warn(f"Multiple small barriers with same SARPID: {s[s > 1].index.values}")


### Add IDs for internal use
# internal ID
df["id"] = (df.index.values + SMALL_BARRIERS_ID_OFFSET).astype("uint64")
df = df.set_index("id", drop=False)


######### Fix data issues
df["ManualReview"] = df.ManualReview.fillna(0).astype("uint8")
df["Recon"] = df.Recon.fillna(0).astype("uint8")
df["SARP_Score"] = df.SARP_Score.fillna(-1).astype("float32")


# fix casing issues of PotentialProject
df["PotentialProject"] = (
    df.PotentialProject.fillna("Unassessed")
    .str.strip()
    .str.replace("barrier", "Barrier")
)

# Recode No => No Barrier per guidance from SARP
df.loc[df.PotentialProject == "No", "PotentialProject"] = "No Barrier"

# mark missing and a few specific codes as unassessed, per guidance from SARP
ix = df.PotentialProject.isin(["", "Unknown", "Small Project", "NA"])
df.loc[ix, "PotentialProject"] = "Unassessed"

# per guidance from Kat, make any where potential project is "No Barrier" as -1
df.loc[df.PotentialProject == "No Barrier", "SARP_Score"] = -1


# Fix mixed casing of values
for column in ("CrossingType", "RoadType", "Stream", "Road"):
    df[column] = df[column].fillna("Unknown").str.title().str.strip()
    df.loc[df[column].str.len() == 0, column] = "Unknown"

# Strip unknowns back out for name fields
for column in ("Road", "Stream"):
    df[column] = df[column].str.replace("Unknown", "")


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
df.loc[df.RoadType.str.lower().isin(("no data", "nodata")), "RoadType"] = "Unknown"
df["RoadType"] = df.RoadType.fillna("").apply(
    lambda x: f"{x[0].upper()}{x[1:]}" if x else x
)


df["YearRemoved"] = df.YearRemoved.fillna(0).astype("uint16")

#########  Fill NaN fields and set data types

for column in ["CrossingCode", "LocalID", "Source"]:
    df[column] = df[column].fillna("").str.strip()

for column in ["Editor", "EditDate"]:
    df[column] = df[column].fillna("")


# Recode BarrierOwnerType
df.BarrierOwnerType = (
    df.BarrierOwnerType.fillna(0).map(BARRIEROWNERTYPE_TO_DOMAIN).astype("uint8")
)

# Code BarrierSeverity to use same domain as dams
df["BarrierSeverity"] = (
    df.PotentialProject.fillna("")
    .str.strip()
    .str.lower()
    .map(POTENTIALPROJECT_TO_SEVERITY)
    .astype("uint8")
)

# Code Condition to use same domain as dams
df["Condition"] = (
    df.Condition.fillna("")
    .str.strip()
    .str.lower()
    .map(BARRIER_CONDITION_TO_DOMAIN)
    .astype("uint8")
)


### Calculate classes
df["CrossingTypeClass"] = (
    df.CrossingType.fillna("")
    .str.strip()
    .str.lower()
    .map(CROSSING_TYPE_TO_DOMAIN)
    .astype("uint8")
)
df["RoadTypeClass"] = (
    df.RoadType.fillna("")
    .str.strip()
    .str.lower()
    .map(ROAD_TYPE_TO_DOMAIN)
    .astype("uint8")
)
df["Constriction"] = (
    df.Constriction.fillna("")
    .str.strip()
    .str.lower()
    .map(CONSTRICTION_TO_DOMAIN)
    .astype("uint8")
)


### Spatial joins
df = add_spatial_joins(df)

# Cleanup HUC, state, county, and ecoregion columns that weren't assigned
for col in [
    "HUC2",
    "HUC4",
    "HUC6",
    "HUC8",
    "HUC10",
    "HUC12",
    "Basin",
    "Subbasin",
    "Subwatershed",
    "County",
    "COUNTYFIPS",
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

# unranked: records that should break the network but not be used for ranking
df["unranked"] = False  # includes invasive and barriers with no upstream

# removed: barriers was removed for conservation but we still want to track it
df["removed"] = False

# invasive: records that are also unranked, but we want to track specfically as invasive for mapping
df["invasive"] = False

### Mark invasive barriers
# NOTE: invasive status is not affected by other statuses
df["invasive"] = df.ManualReview.isin(INVASIVE_MANUALREVIEW) | df.Recon.isin(
    INVASIVE_RECON
)
print(f"Marked {df.invasive.sum()} barriers as invasive barriers")


### Drop any that didn't intersect HUCs or states (including those outside analysis region)
drop_ix = (df.HUC12 == "") | (df.State == "")
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = "dropped: outside HUC12 / states"


### Mark any that were removed so that we can show these on the map
# NOTE: we don't mark these as dropped
removed_fields = {
    "PotentialProject": REMOVED_POTENTIAL_PROJECT,
    "Recon": REMOVED_RECON,
    "ManualReview": REMOVED_MANUALREVIEW,
}

for field, values in removed_fields.items():
    ix = df[field].isin(values) & (~(df.dropped | df.removed))
    df.loc[ix, "removed"] = True
    df.loc[ix, "log"] = format_log("removed", field, sorted(df.loc[ix][field].unique()))


### Drop any small barriers that should be completely dropped from analysis
dropped_fields = {
    "PotentialProject": DROP_POTENTIAL_PROJECT,
    "Recon": DROP_RECON,
    "ManualReview": DROP_MANUALREVIEW,
}

for field, values in dropped_fields.items():
    ix = df[field].isin(values) & (~(df.dropped | df.removed))
    df.loc[ix, "dropped"] = True
    df.loc[ix, "log"] = format_log("dropped", field, sorted(df.loc[ix][field].unique()))


### Exclude barriers that should not be analyzed or prioritized based on Recon or ManualReview
# NOTE: other barriers are excluded based on potential project after marking unranked / removed ones
exclude_fields = {"Recon": EXCLUDE_RECON, "ManualReview": EXCLUDE_MANUALREVIEW}

for field, values in exclude_fields.items():
    ix = df[field].isin(values) & (~(df.dropped | df.removed | df.excluded))
    df.loc[ix, "excluded"] = True
    df.loc[ix, "log"] = format_log(
        "excluded", field, sorted(df.loc[ix][field].unique())
    )


### Mark any barriers that should cut the network but be excluded from ranking
unranked_fields = {"invasive": [True], "PotentialProject": UNRANKED_POTENTIAL_PROJECT}

for field, values in unranked_fields.items():
    ix = df[field].isin(values) & (
        ~(df.dropped | df.excluded | df.removed | df.unranked)
    )
    df.loc[ix, "unranked"] = True
    df.loc[ix, "log"] = format_log(
        "unranked", field, sorted(df.loc[ix][field].unique())
    )

### Exclude any other PotentialProject values that we don't specfically allow
exclude_ix = (~df.PotentialProject.isin(KEEP_POTENTIAL_PROJECT)) & (
    ~(df.dropped | df.excluded | df.unranked | df.removed)
)
df.loc[exclude_ix, "excluded"] = True
found_values = sorted(df.loc[exclude_ix].PotentialProject.unique())
df.loc[exclude_ix, "log"] = f"excluded: PotentialProject {found_values}"


### Summarize counts
print(
    f"Dropped {df.dropped.sum():,} small barriers from network analysis and prioritization"
)
print(
    f"Excluded {df.excluded.sum():,} small barriers from network analysis and prioritization"
)
print(
    f"Marked {df.unranked.sum():,} small barriers to break networks but not be ranked"
)
print(
    f"Marked {df.removed.sum()} small barriers that have been removed for conservation"
)

### Snap barriers
print(f"Snapping {len(df):,} small barriers")

df["snapped"] = False
df["snap_log"] = "not snapped"
df["lineID"] = np.nan  # line to which dam was snapped
df["snap_tolerance"] = SNAP_TOLERANCE["default"]

ix = df.Source.str.contains(
    "WDFW Fish Passage Barrier Database"
) | df.Source.str.contains("ODFW Fish Passage Barrier Database")
df.loc[ix, "snap_tolerance"] = SNAP_TOLERANCE["pnw"]

ix = df.Source.str.contains("Bat Surveys") | df.Source.isin(
    ["Coarse Surveys 2020-2021 "]
)
df.loc[ix, "snap_tolerance"] = SNAP_TOLERANCE["bat survey"]


# Save original locations so we can map the snap line between original and new locations
original_locations = df.copy()

# Only snap those that have HUC2 assigned
# IMPORTANT: do not snap manually reviewed, off-network small barriers, duplicates, or ones without HUC2!
exclude_snap_ix = False
exclude_snap_fields = {
    "HUC2": [""],
    "State": [""],
    "ManualReview": OFFSTREAM_MANUALREVIEW,
}
for field, values in exclude_snap_fields.items():
    ix = df[field].isin(values)
    exclude_snap_ix = exclude_snap_ix | ix
    df.loc[ix, "snap_log"] = format_log(
        "not snapped", field, sorted(df.loc[ix][field].unique())
    )

to_snap = df.loc[~exclude_snap_ix].copy()


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

# Set dup_sort from BarrierSeverity, but put unknown at the end
df["dup_sort"] = np.where(df.BarrierSeverity == 0, 9999, df.BarrierSeverity)

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
export_duplicate_areas(dups, qa_dir / "small_barriers_duplicate_areas.fgb")


### Deduplicate by dams
# any that are within duplicate tolerance of dams may be duplicating those dams
# NOTE: these are only the dams that are snapped and not dropped or excluded
dams = gp.read_feather(snapped_dir / "dams.feather", columns=["geometry"])
tree = shapely.STRtree(df.geometry.values.data)
left, right = tree.query(
    dams.geometry.values.data, predicate="dwithin", distance=DUPLICATE_TOLERANCE
)
ix = df.index.values.take(np.unique(right))

df.loc[ix, "duplicate"] = True
df.loc[ix, "dup_log"] = f"Within {DUPLICATE_TOLERANCE}m of an existing dam"

print(f"Found {len(ix)} small barriers within {DUPLICATE_TOLERANCE}m of dams")

### Exclude those that co-occur with waterfalls
waterfalls = gp.read_feather(snapped_dir / "waterfalls.feather", columns=["geometry"])

tree = shapely.STRtree(df.geometry.values.data)
left, right = tree.query(
    waterfalls.geometry.values.data, predicate="dwithin", distance=DUPLICATE_TOLERANCE
)
near_wf = df.index.values.take(np.unique(right))

# only update those that are not already dropped / excluded / removed
ix = df.index.isin(near_wf) & (~(df.excluded | df.dropped | df.removed))
df.loc[ix, "excluded"] = True
df.loc[ix, "log"] = "excluded: co-occurs with a waterfall"


### update data types
df["dup_sort"] = df.dup_sort.astype("uint8")
df["snap_tolerance"] = df.snap_tolerance.astype("uint16")

for field in ("snap_ref_id", "snap_dist", "dup_group", "dup_count"):
    df[field] = df[field].astype("float32")


### Join to line atts
flowlines = read_feathers(
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
        "StreamOrder",
        "FCode",
        "loop",
        "AnnualFlow",
        "AnnualVelocity",
        "TotDASqKm",
    ],
).set_index("lineID")

df = df.join(flowlines, on="lineID")

df.StreamOrder = df.StreamOrder.fillna(-1).astype("int8")

# Add name from snapped flowline if not already present
df["GNIS_Name"] = df.GNIS_Name.fillna("").str.strip()
ix = (df.Stream == "") & (df.GNIS_Name != "")
df.loc[ix, "Stream"] = df.loc[ix].GNIS_Name
df = df.drop(columns=["GNIS_Name"])


# calculate stream type
df["stream_type"] = df.FCode.map(FCODE_TO_STREAMTYPE).fillna(0).astype("uint8")

# calculate intermittent + ephemeral
df["intermittent"] = df.FCode.isin([46003, 46007])


# Fix missing field values
df["loop"] = df.loop.fillna(False)
df["sizeclass"] = df.sizeclass.fillna("")
df["FCode"] = df.FCode.fillna(-1).astype("int32")
# -9998.0 values likely indicate AnnualVelocity data is not available, equivalent to null
df.loc[df.AnnualVelocity < 0, "AnnualVelocity"] = np.nan

for field in ["AnnualVelocity", "AnnualFlow", "TotDASqKm"]:
    df[field] = df[field].astype("float32")

print(df.groupby("loop").size())

### Add lat / lon
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(GEO_CRS)
geo["lat"] = shapely.get_y(geo.geometry.values.data).astype("float32")
geo["lon"] = shapely.get_x(geo.geometry.values.data).astype("float32")
df = df.join(geo[["lat", "lon"]])

print("\n--------------\n")
df = df.reset_index(drop=True)

print("Serializing {:,} small barriers".format(len(df)))
df.to_feather(master_dir / "small_barriers.feather")
write_dataframe(df, qa_dir / "small_barriers.fgb")


# Extract out only the snapped ones not on loops
df = df.loc[
    df.snapped & (~(df.duplicate | df.dropped | df.excluded | df.loop))
].reset_index(drop=True)
df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

print("Serializing {:,} snapped small barriers".format(len(df)))
df[
    ["geometry", "id", "HUC2", "lineID", "NHDPlusID", "loop", "intermittent", "removed"]
].to_feather(
    snapped_dir / "small_barriers.feather",
)
write_dataframe(df, qa_dir / "snapped_small_barriers.fgb")

print("All done in {:.2f}s".format(time() - start))
