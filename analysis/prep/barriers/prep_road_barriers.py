"""
Extract road-related barriers from original data source, process for use in network analysis, and convert to feather format.
1. Cleanup data values (as needed)
2. Filter out barriers not to be included in analysis (based on Potential_Project and ManualReview)
3. Snap to USGS and USFS road crossings and flowlines
4. Remove duplicate barriers
5. Remove barriers that duplicate dams
6. Mark barriers that co-occur with waterfalls (waterfalls have higher precedence)

NOTE: this must be run AFTER running prep_dams.py and prep_waterfalls.py, because it deduplicates against existing dams and waterfalls.

This creates 2 files for small barriers and 2 for road crossings:
- `barriers/master/small_barriers.feather` - master barriers dataset, including coordinates updated from snapping
- `barriers/snapped/small_barriers.feather` - snapped barriers dataset for network analysis
- `barriers/master/road_crossings.feather` - master road crossings dataset for snapped road crossings
- `barriers/snapped/road_crossings.feather` - snapped road crossings for network analysis

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
import pyarrow as pa
import pyarrow.compute as pc

from analysis.prep.barriers.lib.snap import snap_to_flowlines, export_snap_dist_lines
from analysis.prep.barriers.lib.duplicates import find_duplicates, export_duplicate_areas
from analysis.prep.barriers.lib.spatial_joins import get_huc2, add_spatial_joins
from analysis.prep.barriers.lib.log import format_log
from analysis.prep.species.lib.diadromous import get_diadromous_ids
from analysis.lib.io import read_arrow_tables
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

### Custom tolerance values for dams
SNAP_TOLERANCE = {
    "default": 50,
    # some of the PNW points are in the correct location but NHD flowlines are
    # less precise, need greater tolerance to line them up
    "pnw": 75,
    # some data sources have coordinates that are less precise; use a larger snapping tolerance
    "bat survey": 100,
    # barriers manually moved during snapping should be very close to correct location
    "manually snapped": 25,
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
df = gp.read_feather(src_dir / "sarp_small_barriers.feather")
print(f"Read {len(df):,} small barriers")

### Read in photo attachments, have to join on location
urls = gp.read_feather(
    src_dir / "sarp_small_barrier_survey_urls.feather",
    columns=["geometry", "attachments"],
)
tree = shapely.STRtree(df.geometry.values)
left, right = tree.query_nearest(urls.geometry.values, max_distance=50)
urls = (
    pd.DataFrame(
        {
            "attachments": urls.attachments.values.take(left),
        },
        index=df.index.values.take(right),
    )
    .groupby(level=0)
    .first()
)

df = df.join(urls)

crossings = (
    gp.read_feather(src_dir / "road_crossings.feather")
    .set_index("id", drop=False)
    .drop(columns=["maintainer", "tiger2020_linearids", "nhdhr_permanent_identifier"])
)

# save original USGS ID because SourceID gets overwritten on match with road barrier
crossings["USGSCrossingID"] = crossings.SourceID.values
crossings["Surveyed"] = np.uint8(0)
crossings["excluded"] = False
crossings["removed"] = False
crossings["invasive"] = False
crossings["YearRemoved"] = np.uint16(0)
crossings["EJTract"] = crossings.EJTract.astype("bool")
crossings["EJTribal"] = crossings.EJTribal.astype("bool")
# fill road barrier fields to match schema
crossings["BarrierSeverity"] = np.uint8(0)
crossings["PotentialProject"] = ""
crossings["Constriction"] = np.uint8(0)
crossings["SARP_Score"] = np.float32(-1.0)
crossings["ProtocolUsed"] = ""
crossings["PartnerID"] = ""
# add join field to join surveyed barriers to the older version of the IDs used for crossings
crossings["USGSJoinID"] = "cr" + crossings.USGSCrossingID.values

print(f"Read {len(crossings):,} road crossings")

# if assumed culvert crossings are on larger stream orders (except loops), assume
# they are bridges
ix = (crossings.CrossingType == 99) & (crossings.StreamOrder >= 7) & ~crossings.loop
crossings.loc[ix, "CrossingType"] = 98


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


### Make sure there are not any duplicates
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

# fix typo and bogus value (1)
df["PotentialProject"] = df.PotentialProject.replace("Insignficant Barrier", "Insignificant Barrier").replace("1", "")

# Recode No => No Barrier per guidance from SARP
df.loc[df.PotentialProject == "No", "PotentialProject"] = "No Barrier"

# mark missing and a few specific codes as unassessed, per guidance from SARP
ix = df.PotentialProject.isin(["", "Unknown", "Small Project"])
df.loc[ix, "PotentialProject"] = "Unassessed"

# per guidance from Kat, anything where SARP_Score is 0 and potential project is
# not severe barrier is not set correctly, set it to -1 (null)
df.loc[(df.SARP_Score == 0) & (df.PotentialProject != "Severe Barrier"), "SARP_Score"] = -1

# convert IsPriority to 0 vs 1  (1 = Yes, Null/0/2 = No / not set)
df["IsPriority"] = df.IsPriority.map({1: 1, 0: 0, np.nan: 0, 2: 0}).fillna(0).astype("uint8")

# convert Private to bool
df["Private"] = (
    df.Private.fillna("").map({"Public": False, "0": False, "Private": True, "1": True, "": False}).astype("bool")
)


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

for column in ("YearRemoved", "YearFishPass"):
    df[column] = df[column].fillna(0).astype("uint16")

# Fix bad values for YearRemoved
df.loc[(df.YearRemoved > 0) & (df.YearRemoved < 1900), "YearRemoved"] = np.uint16(0)
df.loc[(df.YearFishPass > 0) & (df.YearFishPass < 1900), "YearFishPass"] = np.uint16(0)


#########  Fill NaN fields and set data types
for column in ["SourceID", "PartnerID", "CrossingCode", "Source", "SourceLink", "ProtocolUsed"]:
    df[column] = df[column].fillna("").str.strip().replace("<Null>", "")


# if SourceID is negative, assume it is null (per guidance from Kat on 2/16/2024)
df.loc[df.SourceID.str.startswith("-"), "SourceID"] = ""

for column in ["Editor", "EditDate"]:
    df[column] = df[column].fillna("")

for column in ["PassageFacility"]:
    df[column] = df[column].fillna(0).astype("uint8")

### Convert to domain values
# Recode BarrierOwnerType
df.BarrierOwnerType = df.BarrierOwnerType.fillna(0).map(BARRIEROWNERTYPE_TO_DOMAIN).astype("uint8")

# Calculate BarrierSeverity from PotentialProject
df["BarrierSeverity"] = (
    df.PotentialProject.str.replace("  ", " ").str.lower().map(POTENTIALPROJECT_TO_SEVERITY).astype("uint8")
)

# per guidance from Kat, if SARP_Score != -1, assign as likely barrier
df.loc[
    df.PotentialProject.isin(["Potential Project", "Proposed Project"]) & (df.SARP_Score != -1),
    "BarrierSeverity",
] = 6


# Cleanup ProtocolUsed
df["ProtocolUsed"] = (
    df.ProtocolUsed.str.strip(".")
    .str.replace("  ", "")
    .str.replace("Protocol", "", case=False)
    .str.replace("Judgement", "judgement")
    .str.replace(" 2009", " (2009)")
    .str.replace(" 2001", " (2001)")
    .str.replace("Crossings2003", "Crossings (2003)")
    .str.replace(" (PAD)", "")
    .replace("SARP NAACC", "NAACC/SARP")
    .replace("SARP/NAACC", "NAACC/SARP")
    .replace("NAACC / SARP", "NAACC/SARP")
    .replace("NAACC/SARP Coarse Protocol", "NAACC/SARP Coarse")
    .replace("GLSCI", "Great Lakes Stream Crossing Inventory")
    .replace("San Dimas AOP Inventory", "San Dimas")
    .replace(
        "Road-Stream Crossing Inventory and AOP Assessment - WMNF",
        "WMNF Road-Stream Crossing Inventory and AOP Assessment",
    )
    .str.strip(" ")
)

# per guidance from Kat (7/25/2024), when protocol used isn't SARP, set SARP score to -1
df.loc[~df.ProtocolUsed.str.contains("SARP"), "SARP_Score"] = -1


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
print(f"Marked {df.invasive.sum():,} barriers as invasive barriers")

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
    df.loc[ix, "log"] = format_log("removed", field, sorted(df.loc[ix][field].unique().tolist()))


# if YearFishPass is set and BarrierSeverity indicates no barrier, mark as removed (fully mitigated)
# (per direction from Kat 3/12/2024)
ix = (
    (df.YearFishPass > 0)
    & (df.YearFishPass <= datetime.today().year)
    & ~(df.dropped | df.removed)
    & (df.BarrierSeverity == 8)
)
df.loc[ix, "removed"] = True
df.loc[ix, "log"] = f"removed: YearFishPass is set and <= {datetime.today().year} and Passability indicates no barrier"


# use YearFishPass to set YearRemoved
# IMPORTANT: this must be done after using YearRemoved above
ix = (df.YearRemoved == 0) & (df.YearFishPass > 0)
df.loc[ix, "YearRemoved"] = df.loc[ix].YearFishPass


# for any marked as removed, clear out fields that may now be outdated, per direction from Kat on 1/6/2024
# but don't reset if Feasibility indicates it wasn't completely removed, per direction from Kat on 1/7/2024
ix = df.removed & (~df.Recon.isin([22, 23]))
df.loc[ix, "Passability"] = np.uint8(0)  # unknown
df.loc[ix, "BarrierSeverity"] = np.uint8(0)  # unknown
df.loc[ix, "SARP_Score"] = np.float32(-1)  # unknown


# recode ActiveList and KeepOnActiveList
df["ActiveList"] = df.ActiveList.fillna(0).astype("uint8")
df["KeepOnActiveList"] = df.KeepOnActiveList.map({1: 1, 2: 0}).fillna(0).astype("bool")


### Drop any small barriers that should be completely dropped from analysis
dropped_fields = {
    "PotentialProject": DROP_POTENTIAL_PROJECT,
    "Recon": DROP_RECON,
    "ManualReview": DROP_MANUALREVIEW,
}

for field, values in dropped_fields.items():
    ix = df[field].isin(values) & (~(df.dropped | df.removed))
    df.loc[ix, "dropped"] = True
    df.loc[ix, "log"] = format_log("dropped", field, sorted(df.loc[ix][field].unique().tolist()))


### Exclude barriers that should not be analyzed or prioritized based on Recon or ManualReview
# NOTE: other barriers are excluded based on potential project after marking unranked / removed ones
exclude_fields = {"Recon": EXCLUDE_RECON, "ManualReview": EXCLUDE_MANUALREVIEW}

for field, values in exclude_fields.items():
    ix = df[field].isin(values) & (~(df.dropped | df.removed | df.excluded))
    df.loc[ix, "excluded"] = True
    df.loc[ix, "log"] = format_log("excluded", field, sorted(df.loc[ix][field].unique().tolist()))


### Mark any barriers that should cut the network but be excluded from ranking
unranked_fields = {"invasive": [True], "PotentialProject": UNRANKED_POTENTIAL_PROJECT}

for field, values in unranked_fields.items():
    ix = df[field].isin(values) & (~(df.dropped | df.excluded | df.removed | df.unranked))
    df.loc[ix, "unranked"] = True
    df.loc[ix, "log"] = format_log("unranked", field, sorted(df.loc[ix][field].unique().tolist()))

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
print(f"Marked {df.removed.sum():,} small barriers that have been removed for conservation")


################################################################################
### Join barrier owner type from TIGER
################################################################################
print("Joining barriers to TIGER roads to determine BarrierOwnerType")
# use road owner type of nearest road within 50m
tiger = gp.read_feather(src_dir / "tiger_roads_2020.feather", columns=["geometry", "RTTYP"]).to_crs(df.crs)
tiger["BarrierOwnerType"] = tiger.RTTYP.map({"C": 3, "I": 2, "S": 2, "U": 2}).fillna(0).astype("uint8")
left, right = shapely.STRtree(tiger.geometry.values).query_nearest(
    df.geometry.values, max_distance=50, all_matches=True
)
owner_type = (
    pd.DataFrame({"id": df.id.values.take(left), "BarrierOwnerType": tiger.BarrierOwnerType.values.take(right)})
    .sort_values(by=["id", "BarrierOwnerType"])
    .groupby("id")
    .BarrierOwnerType.first()
    .rename("BarrierOwnerType_tiger")
)
# only keep matches with known barrier owner type
owner_type = owner_type[owner_type > 0]
df = df.join(owner_type)

# only override if unknown, federal, state, local, or private
ix = df.BarrierOwnerType_tiger.notnull() & df.BarrierOwnerType.isin([0, 1, 2, 3, 7])
df.loc[ix, "BarrierOwnerType"] = df.loc[ix].BarrierOwnerType_tiger.values.astype("uint8")
df = df.drop(columns=["BarrierOwnerType_tiger"])

################################################################################
### Snap barriers
################################################################################
print(f"Snapping {len(df):,} small barriers")
snap_start = time()

df["snapped"] = False
df["snap_log"] = "not snapped"
df["lineID"] = np.nan  # line to which barrier was snapped
df["snap_tolerance"] = SNAP_TOLERANCE["default"]

ix = df.Source.str.contains("WDFW Fish Passage Barrier Database") | df.Source.str.contains(
    "ODFW Fish Passage Barrier Database"
)
df.loc[ix, "snap_tolerance"] = SNAP_TOLERANCE["pnw"]

ix = df.Source.str.contains("Bat Surveys") | df.Source.isin(["Coarse Surveys 2020-2021 "])
df.loc[ix, "snap_tolerance"] = SNAP_TOLERANCE["bat survey"]

# use tight tolerance for barriers manually moved in snapping dataset
ix = df.ManualReview == 15
df.loc[ix, "snap_tolerance"] = SNAP_TOLERANCE["manually snapped"]

# Save original locations so we can map the snap line between original and new locations
original_locations = df.copy()

# IMPORTANT: do not snap manually reviewed off-network small barriers, or ones without HUC2!
# do not snapped dropped  barriers
exclude_snap_ix = np.zeros((len(df),)).astype("bool")
exclude_snap_fields = {
    "dropped": [True],
    "ManualReview": OFFSTREAM_MANUALREVIEW,
}
for field, values in exclude_snap_fields.items():
    ix = df[field].isin(values)
    exclude_snap_ix = exclude_snap_ix | ix
    df.loc[ix, "snap_log"] = format_log("not snapped", field, sorted(df.loc[ix][field].unique().tolist()))

to_snap = df.loc[~exclude_snap_ix].copy()


# # DEBUG
# df.to_feather("/tmp/small_barriers.feather")
# to_snap.to_feather("/tmp/to_snap.feather")
# crossings.to_feather("/tmp/crossings.feather")

### Snap to crossing joined on USGS ID
# NOTE: this snaps the surveyed barrier to the crossing identified by SourceID
# when that was set from an older version of the crossings ("cr" prefix in USGS ID)
matches = (
    df.loc[df.SourceID.str.startswith("cr"), ["SARPID", "SourceID", "geometry"]]
    .rename(columns={"geometry": "barrier_geometry"})
    .join(
        crossings[["id", "USGSJoinID", "geometry", "lineID"]]
        .rename(columns={"id": "crossing_id"})
        .set_index("USGSJoinID"),
        on="SourceID",
        how="inner",
    )
)
if len(matches):
    matches["snap_dist"] = shapely.distance(matches.barrier_geometry.values, matches.geometry.values)
    # NOTE: some of these are too far away to be reasonable, discard them
    matches = matches.loc[matches.snap_dist < 250].copy()

    ix = matches.index
    df.loc[ix, "snapped"] = True
    df.loc[ix, "geometry"] = matches.geometry.values
    df.loc[ix, "snap_dist"] = matches.snap_dist.values
    df.loc[ix, "lineID"] = matches.lineID.values
    df.loc[ix, "snap_log"] = "snapped: matched to USGS road crossing on SourceID"
    df.loc[ix, "crossing_id"] = matches.crossing_id.values

    to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

    # link the corresponding crossings to the closest barrier
    # NOTE: multiple barriers may be linked to the same crossing
    nearest_barriers = (
        matches.sort_values(by=["crossing_id", "snap_dist"]).reset_index().groupby("crossing_id").id.first()
    )
    crossings.loc[nearest_barriers.index, "barrier_id"] = nearest_barriers.values
    # mark these as known surveyed
    crossings.loc[nearest_barriers.index, "Surveyed"] = np.uint8(1)


### Snap to nearest crossing (all of which are already snapped to flowlines)
# NOTE: we previously were trying to prevent snapping unrelated crossing types
# to each other (e.g., bridge to culvert and vice-versa), but due to differences
# in coding of crossing type in inventoried barriers vs road crossings, that
# excluded seemingly valid matches.

tree = shapely.STRtree(crossings.geometry.values)
(left, right), distance = tree.query_nearest(
    to_snap.geometry.values,
    max_distance=SNAP_TOLERANCE["default"],
    return_distance=True,
    all_matches=False,
)

matches = pd.DataFrame(
    {
        "crossing_id": crossings.index.values.take(right),
        "crossing_USGSCrossingID": crossings.USGSCrossingID.values.take(right),
        "crossing_CrossingType": crossings.CrossingType.values.take(right),
        "geometry": crossings.geometry.values.take(right),
        "lineID": crossings.lineID.values.take(right),
        # intentionally using id instead of SARPID to avoid issues when there are
        # duplicate SARPIDs
        "barrier_id": to_snap.id.values.take(left),
        "barrier_CrossingType": to_snap.CrossingType.values.take(left),
        "snap_dist": distance,
    },
    index=to_snap.index.values.take(left),
)


ix = matches.index
df.loc[ix, "snapped"] = True
df.loc[ix, "geometry"] = matches.geometry.values
df.loc[ix, "snap_dist"] = matches.snap_dist.values
df.loc[ix, "lineID"] = matches.lineID.values
df.loc[ix, "snap_log"] = f"snapped: within {SNAP_TOLERANCE['default']}m tolerance of snapped USGS/USFS road crossing"
df.loc[ix, "crossing_id"] = matches.crossing_id.values

to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

print(f"{len(ix):,} barriers snapped to USGS/USFS road crossings within {SNAP_TOLERANCE['default']}m")

# mark the crossing by the closest of any snapped barriers
# this will be updated after barrier deduplication below
nearest_barriers = matches.sort_values(by=["crossing_id", "snap_dist"]).groupby("crossing_id").barrier_id.first()
ix = nearest_barriers.index
crossings.loc[ix, "barrier_id"] = nearest_barriers.values


### Snap to flowlines
# snap culverts to smaller stream orders or loops
# (loops are allowed because they are often side channels with much smaller width)
print("Snapping culverts")
df = snap_to_flowlines(
    df,
    to_snap.loc[to_snap.CrossingType == 8].copy(),
    find_nearest_nonloop=False,
    filter=(pc.field("StreamOrder") < 7) | (pc.field("loop") == True),  # noqa
)[0]


# snap everything else to all flowlines
print("Snapping non-culverts")
df = snap_to_flowlines(df, to_snap.loc[to_snap.CrossingType != 8].copy(), find_nearest_nonloop=False)[0]

print(f"Snapped {df.snapped.sum():,} small barriers in {time() - snap_start:.2f}s")


print("\n--------------\n")


################################################################################
### Remove duplicates after snapping, in case any snapped to the same position
################################################################################
print("Marking duplicates...")
dedup_start = time()

df["duplicate"] = False
df["dup_group"] = np.nan
df["dup_count"] = np.nan
df["dup_log"] = "not a duplicate"
# Set dup_sort from BarrierSeverity, but put unknown at the end
df["dup_sort"] = np.where(df.BarrierSeverity == 0, 9999, df.BarrierSeverity)
# give removed barriers highest priority to retain them during deduplication
df.loc[df.removed, "dup_sort"] = np.uint8(0)
# make private barriers lower priority relative to public barriers
df.loc[df.Private, "dup_sort"] += 100

# for any barriers that snapped to crossings, deduplicate those at the same crossing
multiple_per_crossing = df.loc[df.crossing_id.notnull()].groupby("crossing_id").size().rename("dup_count")
multiple_per_crossing = multiple_per_crossing[multiple_per_crossing > 1].reset_index()
multiple_per_crossing["dup_group"] = multiple_per_crossing.index.values
# assign dup_group so these behave like those deduplicated in reuglar way
multiple_per_crossing = multiple_per_crossing.set_index("crossing_id")
ix = df.crossing_id.isin(multiple_per_crossing.index.values)
df.loc[ix, "dup_group"] = df.loc[ix].crossing_id.map(multiple_per_crossing.dup_group)
df.loc[ix, "dup_count"] = df.loc[ix].crossing_id.map(multiple_per_crossing.dup_count)

grouped = df.loc[ix].sort_values(by=["dup_sort", "SARPID"]).groupby("dup_group").agg({"id": "first", "excluded": "max"})
keep_ids = grouped.id
drop_ix = ix & ~df.id.isin(keep_ids)
df.loc[drop_ix, "duplicate"] = True
df.loc[drop_ix, "dup_log"] = "duplicate: other barriers snapped to same road crossing point"
df.loc[df.id.isin(keep_ids), "dup_log"] = "kept: other barriers snapped to same road crossing point"

# Exclude all records from groups that have an excluded record unless the retained one is trusted because it has a barrier severity set
trusted_keepers = df.loc[
    df.id.isin(keep_ids) & ~(df.dropped | df.excluded) & (df.BarrierSeverity > 0) & (df.BarrierSeverity <= 7)
].id.values

exclude_groups = grouped.loc[grouped.excluded & ~(grouped.id.isin(trusted_keepers))].index

count_excluded = len(df.loc[df.dup_group.isin(exclude_groups) & ~df.excluded])
print(f"Excluded {count_excluded:,} barriers that were in duplicate groups with barriers that were excluded")

ix = df.dup_group.isin(exclude_groups)
df.loc[ix, "excluded"] = True
df.loc[ix, "dup_log"] = "excluded: at least one of duplicates marked to exclude"


# fix road crossing side for any deduplicated above
mapping = df.loc[drop_ix, ["dup_group"]].join(keep_ids, on="dup_group").id
ix = crossings.barrier_id.isin(mapping.index.values)
crossings.loc[ix, "barrier_id"] = crossings.loc[ix].barrier_id.map(mapping).values


# only use full dedup methods those not already deduplicated above by crossing.
df, to_dedup = find_duplicates(
    df,
    to_dedup=df.loc[df.snapped & df.crossing_id.isnull() & ~df.dropped].copy(),
    tolerance=DUPLICATE_TOLERANCE,
    next_group_id=df.dup_group.max() + 1,
)
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

################################################################################
### Sync attributes between non-private barriers and road crossings they snapped to
################################################################################

# Per direction from Kat on 7/30/2024, copy across several of the fields from the nearest barrier to the crossing
# NOTE: CrossingCode of the crossing is intentionally retained
copy_cols = [
    "SARPID",
    "CrossingCode",
    "CrossingType",
    "Source",
    "SourceID",
    "Road",
    "River",
    "Name",
    "excluded",
    "invasive",
    "removed",
    "YearRemoved",
    "BarrierSeverity",
    "PotentialProject",
    "Constriction",
    "SARP_Score",
    "ProtocolUsed",
    "PartnerID",
]
crossings = crossings.join(
    df.loc[~df.Private, copy_cols].rename(columns={c: f"{c}_barrier" for c in copy_cols}),
    on="barrier_id",
)

# NOTE: surveyed status can only be set for non-private barriers
surveyed = crossings.SARPID_barrier.notnull()
crossings.loc[surveyed & (crossings.Surveyed == 0), "Surveyed"] = np.uint8(2)

# override CrossingCode if present in inventoried barrier
ix = surveyed & (crossings.CrossingCode_barrier != "")
crossings.loc[ix, "CrossingCode"] = crossings.loc[ix].CrossingCode_barrier

# always override with values from inventoried barrier
for col in [
    "SARPID",
    "Source",
    "SourceID",
    "excluded",
    "invasive",
    "removed",
    "YearRemoved",
    "BarrierSeverity",
    "PotentialProject",
    "Constriction",
    "SARP_Score",
    "ProtocolUsed",
    "PartnerID",
]:
    crossings.loc[surveyed, col] = crossings.loc[surveyed, f"{col}_barrier"].astype(crossings[col].dtype)

# only override if value is not unknown from inventoried barrier
for col in ["CrossingType"]:
    ix = surveyed & (crossings[col] != 0)
    crossings.loc[ix, col] = crossings.loc[ix, f"{col}_barrier"]

# override only if blank
for col in ["Road", "River", "Name"]:
    ix = surveyed & (crossings[col] == "") & (crossings[f"{col}_barrier"] != "")
    crossings.loc[ix, col] = crossings.loc[ix, f"{col}_barrier"]

crossings = crossings.drop(
    columns=[f"{c}_barrier" for c in copy_cols],
)

# now update the corresponding fields on the inventoried barriers side to match
df = df.join(
    crossings[["SARPID", "USGSCrossingID"]].rename(
        columns={"SARPID": "NearestCrossingID", "USGSCrossingID": "NearestUSGSCrossingID"}
    ),
    on="crossing_id",
)

for col in ["NearestCrossingID", "NearestUSGSCrossingID"]:
    df[col] = df[col].fillna("")

# set BarrierOwnerType from crossing to barrier
ix = df.crossing_id.notnull() & df.BarrierOwnerType.isin([0, 1, 2, 3, 7])
df.loc[ix, "BarrierOwnerType"] = df.loc[ix].crossing_id.map(
    crossings.loc[crossings.id.isin(df.crossing_id.values)].BarrierOwnerType
)


################################################################################
### Cleanup for export
################################################################################

print("---------------------------------")
print("\nSnapping statistics")
print(df.groupby("snap_log").size())
print("---------------------------------\n")


### Save results from snapping for QA
export_snap_dist_lines(df.loc[df.snapped], original_locations, qa_dir, prefix="small_barriers_")


################################################################################
### Cleanup for export
################################################################################

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
    "CongressionalDistrict",
]:
    df[col] = df[col].fillna("").astype("str")

df["CoastalHUC8"] = df.CoastalHUC8.fillna(0).astype("bool")

### Drop any that didn't intersect HUCs or states (including those outside analysis region)
drop_ix = (df.HUC12 == "") | (df.State == "")
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = "dropped: outside HUC12 / states"

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

df["NHDPlusID"] = df.NHDPlusID.fillna(-1).astype("int64")
df.StreamOrder = df.StreamOrder.fillna(-1).astype("int8")

df["DiadromousHabitat"] = df.NHDPlusID.isin(get_diadromous_ids()).astype("int8")
df.loc[~df.snapped, "DiadromousHabitat"] = -1

marine_ids = (
    pa.dataset.dataset(nhd_dir / "clean/all_marine_flowlines.feather", format="feather")
    .to_table(filter=pc.is_in(pc.field("NHDPlusID"), pa.array(flowlines.NHDPlusID.unique())))["NHDPlusID"]
    .to_numpy()
)
df["FlowsToOcean"] = df.NHDPlusID.isin(marine_ids).astype("int8")
df.loc[~df.snapped, "FlowsToOcean"] = -1

great_lake_ids = (
    pa.dataset.dataset(nhd_dir / "clean/all_great_lakes_flowlines.feather", format="feather")
    .to_table(filter=pc.is_in(pc.field("NHDPlusID"), pa.array(flowlines.NHDPlusID.unique())))["NHDPlusID"]
    .to_numpy()
)
df["FlowsToGreatLakes"] = df.NHDPlusID.isin(great_lake_ids).astype("int8")
df.loc[~df.snapped, "FlowsToGreatLakes"] = -1


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
df["Intermittent"] = df.FCode.isin([46003, 46007]).astype("int8")
df.loc[~df.snapped, "Intermittent"] = -1

# calculate canal / ditch
df["Canal"] = df.FCode.isin([33600, 33601, 33603]).astype("int8")
df.loc[~df.snapped, "Canal"] = 1

# Fix missing field values
df["loop"] = df.loop.fillna(0).astype("bool")
df["offnetwork_flowline"] = df.offnetwork_flowline.fillna(0).astype("bool")
df["sizeclass"] = df.sizeclass.fillna("")
df["FCode"] = df.FCode.fillna(-1).astype("int32")
# -9998.0 values likely indicate AnnualVelocity data is not available, equivalent to null
df.loc[df.AnnualVelocity < 0, "AnnualVelocity"] = -1
df.loc[df.AnnualFlow <= 0, "AnnualFlow"] = -1

for field in ["AnnualVelocity", "AnnualFlow", "TotDASqKm"]:
    df[field] = df[field].fillna(-1).astype("float32")

print(df.groupby("loop").size())

################################################################################
### Fill remaining fields and export
################################################################################
print("-----------------")


### Add lat / lon
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(GEO_CRS)
geo["lat"] = shapely.get_y(geo.geometry.values).astype("float32")
geo["lon"] = shapely.get_x(geo.geometry.values).astype("float32")
df = df.join(geo[["lat", "lon"]])


### Assign map symbol for use in (some) tiles
df["symbol"] = 0
df.loc[df.invasive, "symbol"] = 4
# BarrierSeverity = 4 => minor barrier (only breaks networks in small-bodied fish scenario and displayed separately on map otherwise)
df.loc[df.BarrierSeverity == 4, "symbol"] = 3
# BarrierSeverity = 8 => not a barrier
df.loc[df.BarrierSeverity == 8, "symbol"] = 2
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

### Extract out only the snapped ones not on loops
to_analyze = df.loc[df.primary_network | df.largefish_network | df.smallfish_network].reset_index(drop=True)
to_analyze.lineID = to_analyze.lineID.astype("uint32")
to_analyze.NHDPlusID = to_analyze.NHDPlusID.astype("uint64")

print("Serializing {:,} snapped small barriers".format(len(to_analyze)))
to_analyze[
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
        "invasive",
    ]
].to_feather(
    snapped_dir / "small_barriers.feather",
)
write_dataframe(to_analyze, qa_dir / "snapped_small_barriers.fgb")

################################################################################
### Output road crossings
################################################################################

crossings = crossings.drop(columns=["USGSJoinID"])

### Merge in non-private road barriers that have no associated crossing
tmp = df.loc[
    (~(df.dropped | df.duplicate | df.Private))
    # exclude any that had their SARPIDs merged into crossings
    & (~df.SARPID.isin(crossings.SARPID.values))
    # exclude any that have an associated crossing
    & (df.crossing_id.isnull()),
    list(set(crossings.columns).intersection(df.columns)),
].reset_index(drop=True)
# mark these as known surveyed
tmp["Surveyed"] = np.uint8(1)
print(f"Merging {len(tmp):,} inventoried barriers into crossings that have no associated crossing point")

crossings = pd.concat([crossings.reset_index(drop=True), tmp], ignore_index=True, sort=True)

# sanity check
if crossings.groupby("SARPID").size().max() > 1:
    raise ValueError("ERROR: multiple SARPIDs now present for crossings")


# NOTE: road crossings are always excluded from network analysis but cut networks
# so they can be counted within networks
crossings["primary_network"] = False
crossings["largefish_network"] = False
crossings["smallfish_network"] = False

# Assign map symbol for use in tiles
crossings["symbol"] = 0
crossings.loc[crossings.invasive, "symbol"] = 4
crossings.loc[crossings.BarrierSeverity == 4, "symbol"] = 3
crossings.loc[crossings.BarrierSeverity == 8, "symbol"] = 2
crossings.loc[~crossings.snapped, "symbol"] = 1
# intentionally give removed barriers higher precedence
crossings.loc[crossings.removed, "symbol"] = 5
crossings.symbol = crossings.symbol.astype("uint8")


print(f"Serializing {len(crossings):,} road crossings")
crossings.to_feather(master_dir / "road_crossings.feather")
write_dataframe(crossings, qa_dir / "road_crossings.fgb")

### Extract out only the snapped crossings not on loops / off-network flowlines
# for use in network analysis; also exclude any that duplicate inventoried barriers
# NOTE: any that were not snapped were dropped in earlier processing
print(f"Serializing {crossings.snapped.sum():,} snapped road crossings")
snapped_crossings = crossings.loc[
    crossings.snapped
    & (
        ~(crossings.loop | crossings.offnetwork_flowline)
        # exclude any known to be surveyed
        & (crossings.Surveyed == 0)
        # exclude any that are linked to private barriers not marked as surveyed
        & (crossings.barrier_id.isnull())
    ),
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

print("All done in {:.2f}s".format(time() - start))
