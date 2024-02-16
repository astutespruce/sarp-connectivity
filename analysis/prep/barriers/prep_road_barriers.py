"""
Extract road-related barriers from original data source, process for use in network analysis, and convert to feather format.
1. Cleanup data values (as needed)
2. Filter out barriers not to be included in analysis (based on Potential_Project and ManualReview)
3. Snap to USGS road crossings and flowlines
4. Remove duplicate barriers
5. Remove barriers that duplicate dams
6. Mark barriers that co-occur with waterfalls (waterfalls have higher precedence)

NOTE: this must be run AFTER running prep_dams.py and prep_waterfalls.py, because it deduplicates against existing dams and waterfalls.

This creates 2 files for small barriers and 3 for road crossings:
- `barriers/master/small_barriers.feather` - master barriers dataset, including coordinates updated from snapping
- `barriers/snapped/small_barriers.feather` - snapped barriers dataset for network analysis
- `barriers/master/road_crossings.feather` - master road crossings dataset for snapped road crossings
- `barriers/snapped/road_crossings.feather` - snapped road crossings for network analysis
- `data/api/road_crossings.feather` - road crossings data for use in the API

This creates several QA/QC files:
- `barriers/qa/small_barriers_pre_snap_to_post_snap.fgb`: lines between the original coordinate and the snapped coordinate (snapped barriers only)
- `barriers/qa/small_barriers_pre_snap.fgb`: original, unsnapped coordinate (snapped barriers only)
- `barriers/qa/small_barriers_post_snap.fgb`: snapped coordinate (snapped barriers only)
- `barriers/qa/small_barriers_duplicate_areas.fgb`: dissolved buffers around duplicate barriers (duplicates only)
"""

from datetime import datetime
from pathlib import Path
from time import time
import warnings

import geopandas as gp
import shapely
import numpy as np
import pandas as pd
from pyogrio import write_dataframe

from analysis.prep.barriers.lib.snap import snap_to_flowlines, export_snap_dist_lines
from analysis.prep.barriers.lib.duplicates import (
    find_duplicates,
    export_duplicate_areas,
)
from analysis.prep.barriers.lib.spatial_joins import get_huc2, add_spatial_joins
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
from api.constants import ROAD_CROSSING_API_FIELDS, verify_domains

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
api_dir = data_dir / "api"
snapped_dir = barriers_dir / "snapped"
qa_dir = barriers_dir / "qa"

start = time()

print("Reading data")
# TODO: remove rename of Stream / LocalID on next download
df = gp.read_feather(src_dir / "sarp_small_barriers.feather").rename(columns={"Stream": "River", "LocalID": "SourceID"})
df["NearestCrossingID"] = ""
print(f"Read {len(df):,} small barriers")

# TODO: remove rename of Stream on next full run
crossings = (
    gp.read_feather(src_dir / "road_crossings.feather").set_index("id", drop=False).rename(columns={"Stream": "River"})
)
crossings["NearestBarrierID"] = ""
crossings["Surveyed"] = np.uint8(0)
crossings["SourceID"] = crossings.SARPID.str[2:]
crossings["EJTract"] = crossings.EJTract.astype("bool")
crossings["EJTribal"] = crossings.EJTribal.astype("bool")
print(f"Read {len(crossings):,} road crossings")

# only cross-check against dams / waterfalls that break networks
dams = gp.read_feather(snapped_dir / "dams.feather", columns=["geometry"])
waterfalls = gp.read_feather(snapped_dir / "waterfalls.feather", columns=["geometry"])


# remove road crossings that are too close to dams or waterfalls
tree = shapely.STRtree(crossings.geometry.values)
right = tree.query(dams.geometry.values, predicate="dwithin", distance=DUPLICATE_TOLERANCE)[1]
dam_ix = crossings.index.values.take(np.unique(right))
right = tree.query(waterfalls.geometry.values, predicate="dwithin", distance=DUPLICATE_TOLERANCE)[1]
wf_ix = crossings.index.values.take(np.unique(right))
drop_ix = np.unique(np.concatenate([dam_ix, wf_ix]))
crossings = crossings.loc[~crossings.index.isin(drop_ix)].copy()
print(
    f"Found {len(dam_ix):,} road crossings within {DUPLICATE_TOLERANCE}m of dams"
    f" and {len(wf_ix):,} within {DUPLICATE_TOLERANCE}m of waterfalls"
)


### Make sure there are not duplicates
s = df.groupby("SARPID").size()
if s.max() > 1:
    print(s[s > 1].index)
    warnings.warn(f"Multiple small barriers with same SARPID: {s[s > 1].index.values}")


### drop any that are outside analysis HUC2s
df = df.join(get_huc2(df))
drop_ix = df.HUC2.isnull()
if drop_ix.sum():
    print(f"{drop_ix.sum():,} small barriers are outside analysis HUC2s; these are dropped from master dataset")
    df = df.loc[~drop_ix].copy()


### Add IDs for internal use
# internal ID
df["id"] = (df.index.values + SMALL_BARRIERS_ID_OFFSET).astype("uint64")
df = df.set_index("id", drop=False)


######### Fix data issues
df["ManualReview"] = df.ManualReview.fillna(0).astype("uint8")
df["Recon"] = df.Recon.fillna(0).astype("uint8")
df["SARP_Score"] = df.SARP_Score.fillna(-1).astype("float32")

# fix casing issues of PotentialProject
df["PotentialProject"] = df.PotentialProject.fillna("Unassessed").str.strip().str.replace("barrier", "Barrier")

# TEMP: fix bogus values
df.loc[df.PotentialProject == "1", "PotentialProject"] = ""
# FIXME: remove fix for typo
df.loc[df.PotentialProject == "Insignficant Barrier", "PotentialProject"] = "Insignificant Barrier"

# Recode No => No Barrier per guidance from SARP
df.loc[df.PotentialProject == "No", "PotentialProject"] = "No Barrier"

# mark missing and a few specific codes as unassessed, per guidance from SARP
ix = df.PotentialProject.isin(["", "Unknown", "Small Project", "NA"])
df.loc[ix, "PotentialProject"] = "Unassessed"

# per guidance from Kat, anything where SARP_Score is 0 and potential project is
# not severe barrier is not set correctly, set it to -1 (null)
df.loc[(df.SARP_Score == 0) & (df.PotentialProject != "Severe Barrier"), "SARP_Score"] = -1


# Fix mixed casing of values and discard meaningless unknown values
for column in ("River", "Road"):
    df[column] = df[column].fillna("").str.replace("\r\n", "").str.strip().str.title()
    df.loc[df[column].str.len() == 0, column] = ""
    df.loc[
        df[column].str.lower().isin(["unknown", "unnamed", "no name", "n/a", "na", ""]),
        column,
    ] = ""


# Fill name with road or name, if available
ix = (df.Road != "") & (df.River != "")
df.loc[ix, "Name"] = "Road barrier - " + df.loc[ix].Road + " / " + df.loc[ix].River
df.Name = df.Name.fillna("")

ix = (df.Name == "") & (df.Road != "")
df.loc[ix, "Name"] = "Road barrier - " + df.loc[ix].Road

ix = (df.Name == "") & (df.River != "")
df.loc[ix, "Name"] = "Road barrier - " + df.loc[ix].River

# Fix issues with RoadType
df.loc[df.RoadType.str.lower().isin(("no data", "nodata")), "RoadType"] = "Unknown"
df["RoadType"] = df.RoadType.fillna("").apply(lambda x: f"{x[0].upper()}{x[1:]}" if x else x)

df["YearRemoved"] = df.YearRemoved.fillna(0).astype("uint16")

#########  Fill NaN fields and set data types
for column in ["SourceID", "CrossingCode", "Source", "Link"]:
    df[column] = df[column].fillna("").str.strip()

for column in ["Editor", "EditDate"]:
    df[column] = df[column].fillna("")

for column in ["PassageFacility"]:
    df[column] = df[column].fillna(0).astype("uint8")

### Convert to domain values
# Recode BarrierOwnerType
df.BarrierOwnerType = df.BarrierOwnerType.fillna(0).map(BARRIEROWNERTYPE_TO_DOMAIN).astype("uint8")

# Calculate BarrierSeverity from PotentialProject
df["BarrierSeverity"] = df.PotentialProject.str.lower().map(POTENTIALPROJECT_TO_SEVERITY).astype("uint8")

# per guidance from Kat, if SARP_Score != -1, assign as likely barrier
df.loc[
    df.PotentialProject.isin(["Potential Project", "Proposed Project"]) & (df.SARP_Score != -1),
    "BarrierSeverity",
] = 6


# Calculate PassageFacility class
df["PassageFacilityClass"] = np.uint8(0)
df.loc[(df.PassageFacility > 0) & (df.PassageFacility != 9), "PassageFacilityClass"] = 1

# Code Condition to use same domain as dams
df["Condition"] = df.Condition.fillna("").str.strip().str.lower().map(BARRIER_CONDITION_TO_DOMAIN).astype("uint8")

df["Constriction"] = df.Constriction.fillna("").str.strip().str.lower().map(CONSTRICTION_TO_DOMAIN).astype("uint8")

# Convert CrossingType to domain
df["CrossingType"] = df.CrossingType.fillna("").str.strip().str.lower().map(CROSSING_TYPE_TO_DOMAIN).astype("uint8")

df["RoadType"] = df.RoadType.fillna("").str.strip().str.lower().map(ROAD_TYPE_TO_DOMAIN).astype("uint8")

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

# nobarrier: barriers that have been assessed and determined not to be a barrier
df["nobarrier"] = df.BarrierSeverity == 8

# invasive: records that are also unranked, but we want to track specfically as invasive for mapping
df["invasive"] = False

### Mark invasive barriers
# NOTE: invasive status is not affected by other statuses
df["invasive"] = df.ManualReview.isin(INVASIVE_MANUALREVIEW) | df.Recon.isin(INVASIVE_RECON)
print(f"Marked {df.invasive.sum()} barriers as invasive barriers")

### Mark any that were removed so that we can show these on the map
# NOTE: we don't mark these as dropped
removed_fields = {
    "PotentialProject": REMOVED_POTENTIAL_PROJECT,
    "Recon": REMOVED_RECON,
    "ManualReview": REMOVED_MANUALREVIEW,
}

# make sure that any with YearRemoved > current year are not marked as removed
for field, values in removed_fields.items():
    ix = df[field].isin(values) & (df.YearRemoved <= datetime.today().year) & (~(df.dropped | df.removed))
    df.loc[ix, "removed"] = True
    df.loc[ix, "log"] = format_log("removed", field, sorted(df.loc[ix][field].unique()))


# for any marked as removed, clear out fields that may now be outdated, per direction from Kat on 1/6/2024
# but don't reset if Feasibility indicates it wasn't completely removed, per direction from Kat on 1/7/2024
ix = df.removed & (~df.Recon.isin([22, 23]))
df.loc[ix, "Passability"] = np.uint8(0)  # unknown
df.loc[ix, "BarrierSeverity"] = np.uint8(0)  # unknown
df.loc[ix, "SARP_Score"] = np.float32(-1)  # unknown


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
    df.loc[ix, "log"] = format_log("excluded", field, sorted(df.loc[ix][field].unique()))


### Mark any barriers that should cut the network but be excluded from ranking
unranked_fields = {"invasive": [True], "PotentialProject": UNRANKED_POTENTIAL_PROJECT}

for field, values in unranked_fields.items():
    ix = df[field].isin(values) & (~(df.dropped | df.excluded | df.removed | df.unranked))
    df.loc[ix, "unranked"] = True
    df.loc[ix, "log"] = format_log("unranked", field, sorted(df.loc[ix][field].unique()))

### Exclude any other PotentialProject values that we don't specfically allow
# IMPORTANT: we now include Minor Barriers, but then exclude them from specific
# network scenarios
exclude_ix = (~df.PotentialProject.isin(KEEP_POTENTIAL_PROJECT)) & (
    ~(df.dropped | df.excluded | df.unranked | df.removed)
)
df.loc[exclude_ix, "excluded"] = True
found_values = sorted(df.loc[exclude_ix].PotentialProject.unique())
df.loc[exclude_ix, "log"] = f"excluded: PotentialProject {found_values}"


### Summarize counts
print(f"Dropped {df.dropped.sum():,} small barriers from network analysis and prioritization")
print(f"Excluded {df.excluded.sum():,} small barriers from network analysis and prioritization")
print(f"Marked {df.unranked.sum():,} small barriers to break networks but not be ranked")
print(f"Marked {df.removed.sum()} small barriers that have been removed for conservation")

### Snap barriers
print(f"Snapping {len(df):,} small barriers")
snap_start = time()

df["snapped"] = False
df["snap_log"] = "not snapped"
df["lineID"] = np.nan  # line to which dam was snapped
df["snap_tolerance"] = SNAP_TOLERANCE["default"]

ix = df.Source.str.contains("WDFW Fish Passage Barrier Database") | df.Source.str.contains(
    "ODFW Fish Passage Barrier Database"
)
df.loc[ix, "snap_tolerance"] = SNAP_TOLERANCE["pnw"]

ix = df.Source.str.contains("Bat Surveys") | df.Source.isin(["Coarse Surveys 2020-2021 "])
df.loc[ix, "snap_tolerance"] = SNAP_TOLERANCE["bat survey"]


# Save original locations so we can map the snap line between original and new locations
original_locations = df.copy()

# IMPORTANT: do not snap manually reviewed, off-network small barriers, duplicates, or ones without HUC2!
exclude_snap_ix = False
exclude_snap_fields = {
    "ManualReview": OFFSTREAM_MANUALREVIEW,
}
for field, values in exclude_snap_fields.items():
    ix = df[field].isin(values)
    exclude_snap_ix = exclude_snap_ix | ix
    df.loc[ix, "snap_log"] = format_log("not snapped", field, sorted(df.loc[ix][field].unique()))

to_snap = df.loc[~exclude_snap_ix].copy()

# Snap to nearest crossing (all of which are already snapped to flowlines)
tree = shapely.STRtree(crossings.geometry.values)
for tolerance in to_snap.snap_tolerance.unique():
    tmp = to_snap.loc[to_snap.snap_tolerance == tolerance]
    (left, right), distance = tree.query_nearest(
        tmp.geometry.values,
        max_distance=tolerance,
        return_distance=True,
        all_matches=False,
    )

    matches = pd.DataFrame(
        {
            "crossing_id": crossings.index.values.take(right),
            "crossing_SARPID": crossings.SARPID.values.take(right),
            "geometry": crossings.geometry.values.take(right),
            "lineID": crossings.lineID.values.take(right),
            "barrier_SARPID": tmp.SARPID.values.take(left),
            "snap_dist": distance,
        },
        index=tmp.index.values.take(left),
    )
    if len(matches) == 0:
        continue

    ix = matches.index
    df.loc[ix, "snapped"] = True
    df.loc[ix, "geometry"] = matches.geometry.values
    df.loc[ix, "snap_dist"] = matches.snap_dist.values
    df.loc[ix, "lineID"] = matches.lineID.values
    df.loc[ix, "snap_log"] = f"snapped: within {tolerance}m tolerance of snapped USGS road crossing"
    df.loc[ix, "NearestCrossingID"] = matches.crossing_SARPID.values

    to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

    print(f"{len(ix):,} barriers snapped to USGS road crossings within {tolerance}m")

    # mark the crossing by the closest of any snapped barriers
    nearest_barriers = (
        matches.sort_values(by=["crossing_id", "snap_dist"]).groupby("crossing_id").barrier_SARPID.first()
    )
    ix = nearest_barriers.index
    crossings.loc[ix, "NearestBarrierID"] = nearest_barriers.values
    crossings.loc[ix, "Surveyed"] = np.uint8(1)


# Snap to flowlines
df, to_snap = snap_to_flowlines(df, to_snap)

print(f"Snapped {df.snapped.sum():,} small barriers in {time() - snap_start:.2f}s")

print("---------------------------------")
print("\nSnapping statistics")
print(df.groupby("snap_log").size())
print("---------------------------------\n")


### Save results from snapping for QA
export_snap_dist_lines(df.loc[df.snapped], original_locations, qa_dir, prefix="small_barriers_")


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
tree = shapely.STRtree(df.geometry.values)
left, right = tree.query(dams.geometry.values, predicate="dwithin", distance=DUPLICATE_TOLERANCE)
ix = df.index.values.take(np.unique(right))

df.loc[ix, "duplicate"] = True
df.loc[ix, "dup_log"] = f"Within {DUPLICATE_TOLERANCE}m of an existing dam"

print(f"Found {len(ix)} small barriers within {DUPLICATE_TOLERANCE}m of dams")

### Exclude those that co-occur with waterfalls
tree = shapely.STRtree(df.geometry.values)
left, right = tree.query(waterfalls.geometry.values, predicate="dwithin", distance=DUPLICATE_TOLERANCE)
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


### Spatial joins
df = add_spatial_joins(df.drop(columns=["HUC2"]))

print("-----------------")

# Cleanup HUC, state, county columns that weren't assigned
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
]:
    df[col] = df[col].fillna("").astype("str")

df["CoastalHUC8"] = df.CoastalHUC8.fillna(False)

### Drop any that didn't intersect HUCs or states (including those outside analysis region)
drop_ix = (df.HUC12 == "") | (df.State == "")
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = "dropped: outside HUC12 / states"

### Join to line atts
flowlines = (
    read_feathers(
        [nhd_dir / "clean" / huc2 / "flowlines.feather" for huc2 in df.HUC2.unique() if huc2],
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
    )
    .set_index("lineID")
    .rename(columns={"offnetwork": "offnetwork_flowline"})
)

df = df.join(flowlines, on="lineID")

df.StreamOrder = df.StreamOrder.fillna(-1).astype("int8")

# Add name from snapped flowline if not already present
df["GNIS_Name"] = df.GNIS_Name.fillna("").str.strip()
ix = (df.River == "") & (df.GNIS_Name != "")
df.loc[ix, "River"] = df.loc[ix].GNIS_Name
df = df.drop(columns=["GNIS_Name"])

ix = (df.Name == "") & (df.River != "")
df.loc[ix, "Name"] = "Road barrier - " + df.loc[ix].River

# calculate stream type
df["stream_type"] = df.FCode.map(FCODE_TO_STREAMTYPE).fillna(0).astype("uint8")

# calculate intermittent + ephemeral
df["intermittent"] = df.FCode.isin([46003, 46007])

# Fix missing field values
df["loop"] = df.loop.fillna(False)
df["offnetwork_flowline"] = df.offnetwork_flowline.fillna(False)
df["sizeclass"] = df.sizeclass.fillna("")
df["FCode"] = df.FCode.fillna(-1).astype("int32")
# -9998.0 values likely indicate AnnualVelocity data is not available, equivalent to null
df.loc[df.AnnualVelocity < 0, "AnnualVelocity"] = np.nan

for field in ["AnnualVelocity", "AnnualFlow", "TotDASqKm"]:
    df[field] = df[field].astype("float32")

print(df.groupby("loop").size())

################################################################################
### prepare road crossings
################################################################################
print("-----------------")

# for any road crossings that didn't have an inventoried barrier snap to them
# and are within DUPLICATE_TOLERANCE, mark them with the nearest barrier SARPID
# NOTE: all barriers selected here will already be marked with NearestCrossingID
tmp = crossings.loc[crossings.NearestBarrierID == ""]
tree = shapely.STRtree(df.geometry.values)

# find nearest inventoried barrier
left, right = tree.query_nearest(tmp.geometry.values, max_distance=DUPLICATE_TOLERANCE, all_matches=False)

ix = tmp.index.values.take(left)
barriers_ix = df.index.values.take(right)
crossings.loc[ix, "NearestBarrierID"] = df.loc[barriers_ix].SARPID.values


### Add lat / lon
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(GEO_CRS)
geo["lat"] = shapely.get_y(geo.geometry.values).astype("float32")
geo["lon"] = shapely.get_x(geo.geometry.values).astype("float32")
df = df.join(geo[["lat", "lon"]])


### Assign map symbol for use in (some) tiles
df["symbol"] = 0
df.loc[df.invasive, "symbol"] = 4
df.loc[df.BarrierSeverity == 4, "symbol"] = 3
df.loc[df.nobarrier, "symbol"] = 2
df.loc[~df.snapped, "symbol"] = 1
# intentionally give removed barriers higher precedence
df.loc[df.removed, "symbol"] = 5
df.symbol = df.symbol.astype("uint8")


### Assign to network analysis scenario
# omit any that are not snapped or are duplicate / dropped / excluded or on loops / off-network flowlines
can_break_networks = df.snapped & (~(df.duplicate | df.dropped | df.excluded | df.loop | df.offnetwork_flowline))
df["primary_network"] = can_break_networks & (df.PotentialProject != "Minor Barrier")
# salmonid / large fish: only keep significant and severe barriers
# added Potential Project, Proposed Project per direction from Kat on 8/18/2023 due to insufficient data re: actual passability
df["largefish_network"] = can_break_networks & (
    df.PotentialProject.isin(
        [
            "Severe Barrier",
            "Significant Barrier",
            "Potential Project",
            "Proposed Project",
        ]
    )
)
df["smallfish_network"] = can_break_networks  # includes minor barriers


print("\n--------------\n")
df = df.reset_index(drop=True)

print("Serializing {:,} small barriers".format(len(df)))
df.to_feather(master_dir / "small_barriers.feather")
write_dataframe(df, qa_dir / "small_barriers.fgb")


# Extract out only the snapped ones not on loops
df = df.loc[df.primary_network | df.largefish_network | df.smallfish_network].reset_index(drop=True)
df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

print("Serializing {:,} snapped small barriers".format(len(df)))
df[
    [
        "geometry",
        "id",
        "HUC2",
        "lineID",
        "NHDPlusID",
        "primary_network",
        "largefish_network",
        "smallfish_network",
        "removed",
        "YearRemoved",
    ]
].to_feather(
    snapped_dir / "small_barriers.feather",
)
write_dataframe(df, qa_dir / "snapped_small_barriers.fgb")


### Output road crossings

# NOTE: road crossings are always excluded from network analysis but cut networks
# so they can be counted within networks
crossings["primary_network"] = False
crossings["largefish_network"] = False
crossings["smallfish_network"] = False

print(f"Serializing {len(crossings):,} road crossings")

crossings = crossings.reset_index(drop=True)
crossings.to_feather(master_dir / "road_crossings.feather")
write_dataframe(crossings, qa_dir / "road_crossings.fgb")

### Extract out only the snapped crossings not on loops / off-network flowlines
# for use in network analysis; also exclude any that duplicate inventoried barriers
# NOTE: any that were not snapped were dropped in earlier processing
print(f"Serializing {crossings.snapped.sum():,} snapped road crossings")
snapped_crossings = crossings.loc[
    crossings.snapped & (~(crossings.loop | crossings.offnetwork_flowline | (crossings.NearestBarrierID != ""))),
    [
        "geometry",
        "id",
        "HUC2",
        "lineID",
        "NHDPlusID",
        "primary_network",
        "largefish_network",
        "smallfish_network",
    ],
].reset_index(drop=True)

snapped_crossings.to_feather(barriers_dir / "snapped/road_crossings.feather")


### Export for use in API to avoid reading the data again later
crossings = crossings.rename(
    columns={
        "snapped": "Snapped",
        "intermittent": "Intermittent",
        "loop": "OnLoop",
        "sizeclass": "StreamSizeClass",
        "crossingtype": "CrossingType",
    }
)[["id"] + ROAD_CROSSING_API_FIELDS]

# cast intermittent to int to match other types
crossings["Intermittent"] = crossings.Intermittent.astype("int8")

verify_domains(crossings)

crossings.to_feather(api_dir / "road_crossings.feather")

print("All done in {:.2f}s".format(time() - start))
