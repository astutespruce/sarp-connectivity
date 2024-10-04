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
from datetime import datetime
from time import time
import warnings

import geopandas as gp
import pandas as pd
import shapely
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

from analysis.prep.barriers.lib.spatial_joins import get_huc2, add_spatial_joins
from analysis.prep.barriers.lib.log import format_log
from analysis.constants import (
    KM2_TO_ACRES,
    DAMS_ID_OFFSET,
    GEO_CRS,
    DROP_FEASIBILITY,
    EXCLUDE_FEASIBILITY,
    REMOVED_FEASIBILITY,
    INVASIVE_FEASIBILITY,
    DROP_MANUALREVIEW,
    EXCLUDE_MANUALREVIEW,
    REMOVED_MANUALREVIEW,
    ONSTREAM_MANUALREVIEW,
    OFFSTREAM_MANUALREVIEW,
    INVASIVE_MANUALREVIEW,
    DROP_RECON,
    EXCLUDE_RECON,
    REMOVED_RECON,
    INVASIVE_RECON,
    RECON_TO_FEASIBILITY,
    EXCLUDE_PASSAGEFACILITY,
    DROP_STRUCTURECATEGORY,
    FCODE_TO_STREAMTYPE,
    DAM_BARRIER_SEVERITY_TO_DOMAIN,
    BARRIEROWNERTYPE_TO_DOMAIN,
    EXCLUDE_PASSABILITY,
    FEASIBILITY_TO_FEASIBILITYCLASS_DOMAIN,
    HAZARD_TO_DOMAIN,
    FERCREGULATED_TO_DOMAIN,
)
from analysis.lib.io import read_feathers


### Custom tolerance values for dams
SNAP_TOLERANCE = {"default": 150, "likely off network": 50, "estimated from network": 25}
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


### Read dams for analysis region states states and merge
print("Reading dams in analysis region states")

df = gp.read_feather(src_dir / "sarp_dams.feather")
print(f"Read {len(df):,} dams in region states")

# join in cost columns, but only where height is within tolerance because height
# may have been updated for a given dam after it was run through the analysis
cost = pd.read_feather(src_dir / "sarp_dam_costpred_v2.feather").set_index("SARPID")
df = df.join(cost, on="SARPID")
df["height_m"] = df.Height.fillna(0) * (1 / 3.281)
ix = ~(df.CostMean.notnull() & np.isclose(df.height_m, df.DamHt_m, atol=1))
for col in ["CostMean", "CostUpper", "CostLower"]:
    df.loc[ix, col] = np.nan

df = df.drop(columns=["height_m", "DamHt_m"])


### Read in dams that have been manually reviewed
print("Reading manually snapped dams...")
snapped_df = gp.read_feather(src_dir / "manually_snapped_dams.feather")

# FIXME: temporary fix; there are some with duplicate SARPIDs or missing field values
snapped_df = (
    snapped_df.loc[snapped_df.snapped.notnull() & (~snapped_df.SARPID.isin(["<Null>", "CA"]))]
    .groupby("SARPID")
    .first()
    .reset_index()
)
# groupby loses CRS
snapped_df = snapped_df.set_crs(df.crs, allow_override=True)


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
    print(f"Dropping {ix.sum():,} dams marked as in correct location but were not previously snapped (errors)")
    snapped_df = snapped_df.loc[~ix].copy()

# Drop any that were marked as duplicates manually and also automatically
ix = (snapped_df.ManualReview == 11) & snapped_df.duplicate
if ix.sum():
    snapped_df = snapped_df.loc[~ix].copy()
    print(f"Dropping {ix.sum():,} dams marked as duplicates automatically and manually")

### Read in NABD dams and drop any that are already present in snapping dataset or manually reviewed in master
nabd = gp.read_feather(src_dir / "nabd.feather").set_index("NIDID")
# join through NIDID to get SARPID
nabd = nabd.loc[nabd.index.isin(df.NIDID)].join(df[["SARPID", "NIDID"]].set_index("NIDID"))

# note: 2 (NABD) is excluded because they weren't actually manually reviewed
manually_reviewed_sarpid = df.loc[df.ManualReview.isin([4, 5, 6, 8, 13, 14, 15])].SARPID.unique()

nabd = nabd.loc[(~nabd.SARPID.isin(snapped_df.SARPID)) & (~nabd.SARPID.isin(manually_reviewed_sarpid))].copy()


snapped_df = pd.concat(
    [snapped_df[["SARPID", "geometry", "ManualReview"]], nabd],
    ignore_index=True,
    sort=False,
).set_index("SARPID")

# Join to snapped and bring across updated geometry and ManualReview
df = df.join(snapped_df, on="SARPID", rsuffix="_snap")

# override with manually snapped assignment
ix = df.ManualReview_snap.notnull()
df.loc[ix, "ManualReview"] = df.loc[ix].ManualReview_snap

# Only update geometry from snapped where snapped is likely to be manually moved
# or where validated prior location
ix = df.ManualReview_snap.isin([2, 4, 5, 13, 15])
df.loc[ix, "geometry"] = df.loc[ix].geometry_snap

print(f"Updated {ix.sum():,} dam locations based on snapped / manual review dataset")

# drop snap columns
df = df.drop(columns=[c for c in df.columns if c.endswith("_snap")])

# Reset the index so that we have a clean numbering for all rows
df = df.reset_index(drop=True)
print("-----------------\nCompiled {:,} dams\n-----------------\n".format(len(df)))


### Make sure there are not duplicate SARPIDs
s = df.groupby("SARPID").size()
if s.max() > 1:
    warnings.warn(f"Multiple dams with same SARPID: {s[s > 1].index.values}")


### drop any that are outside analysis HUC2s
df = df.join(get_huc2(df))
drop_ix = df.HUC2.isnull()
if drop_ix.sum():
    print(f"{drop_ix.sum():,} dams are outside analysis HUC2s; these are dropped from master dataset")
    df = df.loc[~drop_ix].copy()


### Add IDs for internal use
# internal ID
df["id"] = (df.index.values + DAMS_ID_OFFSET).astype("uint64")
df = df.set_index("id", drop=False)  # note: this sets index as uint64 dtype

df.to_feather(qa_dir / "dams_raw.feather")

######### Fix data issues

# Calculate feasibility from Recon if not already set
# NOTE: this must be done before backfilling Feasibility with 0
df.Recon = df.Recon.fillna(0).astype("uint8")
ix = df.Feasibility.isnull() | (df.Feasibility == 0)
df.loc[ix, "Feasibility"] = df.loc[ix].Recon.map(RECON_TO_FEASIBILITY)
df["Feasibility"] = df.Feasibility.astype("uint8")

# If either feasibility or recon indicate removal planned, override both to match
ix = (df.Recon == 11) | (df.Feasibility == 12)
df.loc[ix, "Recon"] = 11
df.loc[ix, "Feasibility"] = 12

# If invasive species barrier flag is set, update Recon and Feasibility
ix = (df.InvasiveSpecies == 1) & (df.Recon.isin([0, 3, 4, 6, 13, 15, 17]))
df.loc[ix, "Recon"] = 16
df.loc[ix, "Feasibility"] = 9

# drop invasive species column to prevent later confusion
df = df.drop(columns=["InvasiveSpecies"])

# convert IsPriority to a bool (1 = Yes, Null/0/2 = No / not set)
df["IsPriority"] = df.IsPriority == 1

# convert Private to bool
df["Private"] = (
    df.Private.fillna("").map({"Public": False, "0": False, "Private": True, "1": True, "": False}).astype("bool")
)


### Set data types
for column in (
    "River",
    "NIDID",
    "NIDFederalID",
    "Source",
    "Name",
    "OtherName",
    "SourceID",
    "PartnerID",
    "Editor",
    "EditDate",
    "Link",
    "FedRegulatoryAgency",
):
    df[column] = df[column].fillna("").str.strip()

# If source is Open Street Map, update
df["Source"] = (
    df.Source.replace("Open Street Map", "OpenStreetMap (https://opendatacommons.org/licenses/odbl/)")
    .replace("SEACAP Master", "SEACAP")
    .replace("NID 2023 Mar192023", "NID March19 2023")
    .replace("NID May312023", "NID May 31 2023")
    .replace("Field Assessment", "Field assessment")
    .replace("Field Assessments", "Field assessment")
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
    "Fatality",
):
    df[column] = df[column].fillna(0).astype("uint8")


for column in ("YearCompleted", "YearRemoved", "YearFishPass", "StructureClass"):
    df[column] = df[column].fillna(0).astype("uint16")

# Fix bad values for YearRemoved & YearFishPass
df.loc[(df.YearRemoved > 0) & (df.YearRemoved < 1900), "YearRemoved"] = np.uint16(0)
df.loc[(df.YearFishPass > 0) & (df.YearFishPass < 1900), "YearFishPass"] = np.uint16(0)


# Use float32 instead of float64 (still can hold nulls)
for column in ("ImpoundmentType", "Recon2", "Recon3", "StorageVolume"):
    df[column] = df[column].astype("float32")


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

# Cleanup recon vs feasibility (per direction from Kat 9/10/2024)
df.loc[(df.Recon == 5) & (df.Feasibility == 8), "Recon"] = 7


# Round height and width to nearest foot.
# There are no dams between 0 and 1 foot, so fill all na as 0.
df.Height = df.Height.fillna(0).round().clip(0, 1e6).astype("uint16")
# coerce length to width, fix negative values
df.Length = df.Length.fillna(0).round().clip(0, df.Length.max()).astype("uint32")
df.Width = df.Width.fillna(0).round().astype("uint16")


# FIXME: temporarily recode dams that are indicated as errors in lowhead field
# Fix LowheadDam value that should be assigned to Recon / ManualReview instead
ix = df.LowheadDam == 5
df.loc[ix, "Recon"] = 5
df.loc[ix, "Feasibility"] = 7
df.loc[ix, "ManualReview"] = 6

# Recode lowhead dams to align with LOWHEADDAM_DOMAN
df["LowheadDam"] = (
    df.LowheadDam.map(
        {
            0: 3,  # no  # FIXME: longer term these should only come in as 0's
            1: 1,  # yes
            2: 3,  # no
            3: 2,  # needs further review; map these to likely based on direction from Kat on 12/15/2023
            5: 0,  # not a dam but set it to 0 to get it out of the codes
        }
    )
    .fillna(0)
    .astype("uint8")
)

# From Kat: if StructureClass == 916 (lowead dam / weir)
# several are miscoded on Mississippi River and are not lowhead dams
df.loc[
    (df.LowheadDam == 0)
    & (df.StructureClass == 916)
    & (~df.Name.str.lower().str.contains("mississippi river"))
    & (~df.SARPID.isin(["IA19114", "IA19110", "IA19207", "IA19112", "IA19019", "GA29841"]) & (df.Height <= 25)),
    "LowheadDam",
] = 2

# From Kat: many Recon == 14 are lowhead

df.loc[
    (df.LowheadDam == 0)  # TODO: should this include 3?
    & (df.Recon == 14)
    & (df.Height <= 25),
    "LowheadDam",
] = 2

# TODO: from Kat: if in NC and source is Aquatic Obstruction Inventory, also set lowhead dam


### standardize and fix bad values for FedRegulatoryAgency
df.loc[df.FedRegulatoryAgency.isin(["1", "2"]), "FedRegulatoryAgency"] = ""
df.loc[df.FedRegulatoryAgency == "BOR", "FedRegulatoryAgency"] = "Bureau of Reclamation"
df.loc[df.FedRegulatoryAgency == "FERC", "FedRegulatoryAgency"] = "Federal Energy Regulatory Commission"
df.loc[df.FedRegulatoryAgency.isin(["COE", "US Army"]), "FedRegulatoryAgency"] = "US Army Corps of Engineers"
df.loc[df.FedRegulatoryAgency == "COE and FERC", "FedRegulatoryAgency"] = (
    "US Army Corps of Engineers;Federal Energy Regulatory Commission"
)

df.loc[df.FedRegulatoryAgency.isin(["USFS", "Forest Service"]), "FedRegulatoryAgency"] = "USDA Forest Service"
df.loc[df.FedRegulatoryAgency == "TVA", "FedRegulatoryAgency"] = "Tennessee Valley Authority"
df.loc[df.FedRegulatoryAgency.isin(["USFWS", "Fish and Wildlife Service"]), "FedRegulatoryAgency"] = (
    "US Fish and Wildlife Service"
)
df.loc[df.FedRegulatoryAgency == "US Army Corps of Engineers;Fish and Wildlife Service", "FedRegulatoryAgency"] = (
    "US Army Corps of Engineers;US Fish and Wildlife Service"
)
df.loc[df.FedRegulatoryAgency == "Forest Service;Natural Resources Conservation Service", "FedRegulatoryAgency"] = (
    "USDA Forest Service;Natural Resources Conservation Service"
)
df.loc[df.FedRegulatoryAgency == "US Army;Fish and Wildlife Service", "FedRegulatoryAgency"] = (
    "US Army Corps of Engineers;US Fish and Wildlife Service"
)
df["FedRegulatoryAgency"] = df.FedRegulatoryAgency.str.replace(";", ", ")


# if FedRegulatoryAgency is FERC, set FERC_Regulated per direction from Kat (3/7/2024)
ix = df.FedRegulatoryAgency.str.contains("Federal Energy Regulatory Commission")
df.loc[ix, "FERCRegulated"] = 1


# Cleanup names
# Standardize the casing of the name
df.Name = df.Name.str.strip().str.title()
df.OtherName = df.OtherName.str.strip().str.title()
df.River = df.River.str.strip().str.title()

# strip out meaningless unknown values
df.loc[
    df.Name.str.lower().isin(
        [
            "unknown",
            "unknown dam",
            "unknown barrier",
            "unnamed barrier",
            "unknown ditch",
            "unknown diversion",
            "unknown pond dam",
            "unknown push up dam",
        ]
    ),
    "Name",
] = ""
df.loc[df.Name.str.lower().str.startswith("unknown #"), "Name"] = ""


# Fix name issue - 3 dams have duplicate dam names with line breaks, which breaks tippecanoe
ids = df.loc[df.Name.str.count("\r") > 0].index
df.loc[ids, "Name"] = df.loc[ids].Name.apply(lambda v: v.split("\r")[0]).fillna("")

df.loc[(df.Diversion == 1) & (df.Name == ""), "Name"] = "Water diversion"

# Fix years between 0 and 100; assume they were in the 1900s
df.loc[(df.YearCompleted > 0) & (df.YearCompleted < 100), "YearCompleted"] = df.YearCompleted + 1900
df.loc[df.YearCompleted == 20151, "YearCompleted"] = 2015
df.loc[df.YearCompleted == 9999, "YearCompleted"] = 0


### Calculate classes
# Calculate YearCompleted class based on difference from current year
# NOTE: 0 is reserved for missing data (when combined with small barriers),
# 1: YearCompleted==0
bins = [-1, 10, 30, 50, 70, 100, 1000]
df["YearCompletedClass"] = (
    np.asarray(
        pd.cut(
            datetime.today().year - df.YearCompleted,
            bins,
            right=False,
            labels=np.arange(0, len(bins) - 1),
        )
    )
    + 2
)
df["YearCompletedClass"] = df.YearCompletedClass.fillna(1).astype("uint8")


# Calculate height class
# NOTE: 0 is reserved for missing data
bins = [-1, 1e-6, 5, 10, 25, 50, 100, df.Height.max() + 1]
df["HeightClass"] = (np.asarray(pd.cut(df.Height, bins, right=False, labels=np.arange(0, len(bins) - 1))) + 1).astype(
    "uint8"
)

# Convert PassageFacility to class
df["PassageFacilityClass"] = np.uint8(0)
df.loc[(df.PassageFacility > 0) & (df.PassageFacility != 9), "PassageFacilityClass"] = 1

df["FeasibilityClass"] = df.Feasibility.map(FEASIBILITY_TO_FEASIBILITYCLASS_DOMAIN).astype("uint8")


# Convert BarrierSeverity to a domain and call it Passability
df["Passability"] = (
    df.BarrierSeverity.fillna("unknown").str.strip().str.lower().map(DAM_BARRIER_SEVERITY_TO_DOMAIN).astype("uint8")
)
df = df.drop(columns=["BarrierSeverity"])

# Recode BarrierOwnerType
df.BarrierOwnerType = df.BarrierOwnerType.fillna(0).map(BARRIEROWNERTYPE_TO_DOMAIN).astype("uint8")

# Cleanup FERCRegulated and StateRegulated
df["FERCRegulated"] = df.FERCRegulated.fillna(0).astype("uint8").map(FERCREGULATED_TO_DOMAIN).astype("uint8")

df["StateRegulated"] = df.StateRegulated.fillna("0")
# FIXME: temporary: handle Yes / No values; these should instead be coded using their domain values
ix = df.StateRegulated.isin(["Yes", "No"])
df.loc[ix, "StateRegulated"] = df.loc[ix].StateRegulated.map({"Yes": "1", "No": "2"})
df["StateRegulated"] = df.StateRegulated.astype("uint8")

df["WaterRight"] = df.WaterRight.fillna(0).astype("uint8")

# Recode Hazard (note: original value of 4 = unknown)
df["Hazard"] = df.Hazard.fillna(4).astype("uint8").map(HAZARD_TO_DOMAIN).astype("uint8")


### Add tracking fields
# master log field for status
df["log"] = ""
# dropped: records that should not be included in any later analysis
df["dropped"] = False

# excluded: records that should be retained in dataset but not used in analysis
df["excluded"] = False

# unranked: records that should break the network but not be used for ranking
df["invasive"] = False

# nobarrier: barriers that have been assessed and determined not to be a barrier
df["nobarrier"] = df.Passability == 7

df["unranked"] = False  # combined from above fields

# removed: dam was removed for conservation but we still want to track it
df["removed"] = False

# nostructure: diversion point without associated structure
df["nostructure"] = False


### Mark invasive barriers
# NOTE: invasive status is not affected by other statuses
invasive_fields = {
    "Recon": INVASIVE_RECON,
    "Feasibility": INVASIVE_FEASIBILITY,
    "ManualReview": INVASIVE_MANUALREVIEW,
}

for field, values in invasive_fields.items():
    ix = df[field].isin(values)
    df.loc[ix, "invasive"] = True


### Drop any dams that should be completely dropped from analysis
dropped_fields = {
    "Recon": DROP_RECON,
    "Feasibility": DROP_FEASIBILITY,
    "ManualReview": DROP_MANUALREVIEW,
    "StructureCategory": DROP_STRUCTURECATEGORY,
}

for field, values in dropped_fields.items():
    ix = df[field].isin(values) & (~df.dropped)
    df.loc[ix, "dropped"] = True
    df.loc[ix, "log"] = format_log("dropped", field, sorted(df.loc[ix][field].unique()))

# per direction from Kat on 12/8/2023, drop if:
# structure category == 3 and structureclass is not 916 or 917 and barrierseverity is null
# structure category == 3 and barrier severity is no barrier
# snap if:
# if structure category == 3 and structure class == 916 or 917 and barrier severity is null or not no barrier
# structure category == 3 and barrier severity is not null or is not no barrier
df["nostructure"] = (df.StructureCategory == 3) & (
    # no barrrier: always exclude
    (df.Passability == 7)
    # unknown severity and not a dam structure class
    | ((df.Passability == 0) & (~df.StructureClass.isin([916, 917])))
)
ix = df.nostructure & ~df.dropped
df.loc[ix, "dropped"] = True
df.loc[ix, "log"] = "dropped: StructureCategory==3 and not identified as dam by other fields"


### Mark any that were removed so that we can show these on the map
# NOTE: we don't mark these as dropped
removed_fields = {
    "Recon": REMOVED_RECON,
    "Feasibility": REMOVED_FEASIBILITY,
    "ManualReview": REMOVED_MANUALREVIEW,
}

# make sure that any with YearRemoved > current year are not marked as removed
for field, values in removed_fields.items():
    ix = df[field].isin(values) & (df.YearRemoved <= datetime.today().year) & (~(df.dropped | df.removed))
    df.loc[ix, "removed"] = True
    df.loc[ix, "log"] = format_log("removed", field, sorted(df.loc[ix][field].unique()))


# if YearRemoved is set, mark it as removed (per direction from Kat 3/11/2024)
ix = (df.YearRemoved > 0) & (df.YearRemoved <= datetime.today().year) & ~(df.dropped | df.removed)
df.loc[ix, "removed"] = True
df.loc[ix, "log"] = f"removed: YearRemoved is set and <= {datetime.today().year}"

# clear out cost columns for removed dams since they are no longer applicable
for col in ["CostMean", "CostUpper", "CostLower"]:
    df.loc[df.removed, col] = np.nan


# if YearFishPass is set and Passability indicates no barrier, mark as removed (fully mitigated)
# (per direction from Kat 3/12/2024)
ix = (
    (df.YearFishPass > 0)
    & (df.YearFishPass <= datetime.today().year)
    & ~(df.dropped | df.removed)
    & (df.Passability == 7)
)
df.loc[ix, "removed"] = True
df.loc[ix, "log"] = f"removed: YearFishPass is set and <= {datetime.today().year} and Passability indicates no barrier"


# use YearFishPass to set YearRemoved
# IMPORTANT: this must be done after using YearRemoved above
ix = (df.YearRemoved == 0) & (df.YearFishPass > 0)
df.loc[ix, "YearRemoved"] = df.loc[ix].YearFishPass


# for any marked as removed, clear out fields that may now be outdated, per direction from Kat on 1/6/2024
# but don't reset if Feasibility indicates it wasn't completely removed, per direction from Kat on 1/7/2024
ix = df.removed & (~(df.Feasibility.isin([11, 14]) | df.Recon.isin([22, 23])))
df.loc[ix, "Passability"] = np.uint8(0)  # unknown


### Exclude dams that should not be analyzed or prioritized based on manual QA
excluded_fields = {
    "Recon": EXCLUDE_RECON,
    "Feasibility": EXCLUDE_FEASIBILITY,
    "ManualReview": EXCLUDE_MANUALREVIEW,
    "PassageFacility": EXCLUDE_PASSAGEFACILITY,
    "Passability": EXCLUDE_PASSABILITY,
}

for field, values in excluded_fields.items():
    ix = df[field].isin(values) & (~(df.dropped | df.removed | df.excluded))
    df.loc[ix, "excluded"] = True
    df.loc[ix, "log"] = format_log("excluded", field, sorted(df.loc[ix][field].unique()))

# If Recon / Feasibility indicates fish passage installed and Barrier Severity
# does not indicate passability issue, exclude (per guidance from SARP)
ix = (
    (df.Recon.isin([22, 23]) | (df.Feasibility == 11))
    & df.Passability.isin([0, 7])
    & (~(df.dropped | df.removed | df.excluded))
)
df.loc[ix, "excluded"] = True
df.loc[ix, "log"] = "excluded: Recon/Feasibility indicate fish passage installed but Passability marked as passable"
df.loc[ix, "nobarrier"] = True

### Mark any dams that should cut the network but be excluded from ranking
unranked_fields = {
    "invasive": [True],
}
for field, values in unranked_fields.items():
    ix = df[field].isin(values) & (~(df.dropped | df.excluded | df.removed | df.unranked))
    df.loc[ix, "unranked"] = True
    df.loc[ix, "log"] = format_log("unranked", field, sorted(df.loc[ix][field].unique()))

### Mark estimated dams
# these were generated by SARP from analysis of small waterbodies or in this
# data pipeline from NHD waterbody drain points
# NOTE: this MUST be done AFTER dropping / excluding barriers
# NOTE: Estimated Dams <datestamp> are estimated using methods here; others were done in other ways
df["is_estimated"] = (
    df.Name.str.lower().str.contains("estimated dam")
    | df.Source.str.lower().str.contains("estimated dam")
    | df.Source.str.lower().str.contains("nhdplus high resolution watebodies instersecting")
)
# Replace estimated dam names if another name is available
ix = df.is_estimated & (df.OtherName.str.len() > 0)
df.loc[ix, "Name"] = df.loc[ix].OtherName


### Mark dams for de-duplication
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
# Prefer dams with River to those that do not
df.loc[(df.River != "") | (df.Name != ""), "dup_sort"] = 7
# Prefer dams with key fields present
df.loc[(df.YearCompleted > 0) | (df.Height > 0) | (df.Condition > 0) | (df.BarrierStatus > 0), "dup_sort"] = 6
# Prefer NID dams
df.loc[df.NIDID != "", "dup_sort"] = 5
# Prefer NABD dams
df.loc[df.ManualReview == 2, "dup_sort"] = 4
# Prefer dams with recon / feasibility
df.loc[
    ((df.Recon > 0) & ~df.Recon.isin([5, 19])) | ((df.Feasibility > 0) & ~df.Feasibility.isin([6, 7, 10])), "dup_sort"
] = 3
# Prefer dams with manual review (onstream or off)
df.loc[df.ManualReview.isin(ONSTREAM_MANUALREVIEW + [5]), "dup_sort"] = 2
# Prefer removed dams
df.loc[df.removed, "dup_sort"] = 1


### De-duplicate dams before snapping if possible (duplicates are not snapped since they may snap other places)

# Dams within 10 meters are very likely duplicates of each other
# from those that were hand-checked on the map, they are duplicates of each other
# Important: remove dropped barriers before dedup
to_dedup = df.loc[~(df.duplicate | df.dropped)].copy()
df, to_dedup = find_duplicates(df, to_dedup, tolerance=DUPLICATE_TOLERANCE["default"])

print(f"Found {df.duplicate.sum():,} total duplicates before snapping (duplicates are not snapped)")
print("---------------------------------")
print("\nDe-duplication statistics")
print(df.groupby("dup_log").size())
print("---------------------------------\n")


### Snap dams
# snapped: records that snapped to the aquatic network and ready for network analysis
df["snapped"] = False
# 0 = default, 1 = estimated (old methods), 2 = Amber Ignatius ACF dams, 3 = estimated from waterbodies (current version)
df["snap_group"] = 0
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

df.loc[ix, "snap_tolerance"] = np.max([df.loc[ix].snap_tolerance.values, length_tolerance], axis=0)

### Mark dam snapping groups

# Identify dams estimated from waterbodies
ix = df.Source.str.lower().isin(["estimated dams oct 2021", "estimated dams summer 2022", "estimated dams jan 2023"])
df.loc[ix, "snap_group"] = 3
df.loc[ix, "Name"] = "Estimated dam"
df.loc[ix, "snap_tolerance"] = SNAP_TOLERANCE["estimated from network"]
print(
    f"Setting snap tolerance to {SNAP_TOLERANCE['estimated from network']}m for {ix.sum():,} dams estimated from waterbodies"
)

# use tight tolerance for dams estimated by older methods
ix = df.is_estimated & (df.snap_group != 3)
df.loc[ix, "snap_group"] = 1  # indicates estimated dam
df.loc[ix, "snap_tolerance"] = SNAP_TOLERANCE["likely off network"]
print(
    f"Setting snap tolerance to {SNAP_TOLERANCE['likely off network']}m for {ix.sum():,} estimated dams (old methods)"
)

# Amber Ignatius ACF dams are often features that don't have associated flowlines,
# flag so we don't snap to flowlines that aren't really close
# NOTE: this MUST be done AFTER dropping / excluding barriers
ix = df.Source.str.count("Amber Ignatius") > 0
df.loc[ix, "snap_group"] = 2
df.loc[ix, "snap_tolerance"] = SNAP_TOLERANCE["likely off network"]
print(f"Setting snap tolerance to {SNAP_TOLERANCE['likely off network']}m for {ix.sum():,} dams likely off network")


# IMPORTANT: do not snap manually reviewed off-network dams, duplicates, or dropped dams
# duplicates are excluded here because they may snap to different locations due
# to different snap tolerances, so don't snap them at all
# dropped dams don't need to be snapped (includes no-structure diversions)
exclude_snap_ix = False
exclude_snap_fields = {
    "duplicate": [True],
    "dropped": [True],
    "ManualReview": OFFSTREAM_MANUALREVIEW,
}
for field, values in exclude_snap_fields.items():
    ix = df[field].isin(values)
    exclude_snap_ix = exclude_snap_ix | ix
    df.loc[ix, "snap_log"] = format_log("not snapped", field, sorted(df.loc[ix][field].unique()))

to_snap = df.loc[~exclude_snap_ix].copy()


# Save original locations so we can map the snap line between original and new locations
original_locations = to_snap.copy()

snap_start = time()

print("-----------------")

# DEBUG
# df.reset_index(drop=True).to_feather("/tmp/dams.feather")
# to_snap.reset_index(drop=True).to_feather("/tmp/to_snap.feather")


# Snap estimated dams to the drain point of the waterbody that contains them, if possible
df, to_snap = snap_estimated_dams_to_drains(df, to_snap)

# Snap to NHD dams
df, to_snap = snap_to_nhd_dams(df, to_snap)

# Snap to waterbodies
df, to_snap = snap_to_waterbodies(df, to_snap)

# Snap to flowlines
df, to_snap = snap_to_flowlines(df, to_snap, find_nearest_nonloop=True)

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

dedup_start = time()

# Exclude those where ManualReview indicated duplicate (these are also dropped),
# and those identified as duplicates before snapping, otherwise this cascades to
# drop other barriers in this group; at least one of which should be kept
to_dedup = df.loc[df.snapped & ~(df.duplicate | df.dropped)].copy()

# Dams within 10 meters are very likely duplicates of each other
# from those that were hand-checked on the map, they are duplicates of each other
next_group_id = df.dup_group.max() + 1
df, to_dedup = find_duplicates(df, to_dedup, tolerance=DUPLICATE_TOLERANCE["default"], next_group_id=next_group_id)

# Search a bit further for duplicates from estimated dams that snapped
# hand-checked these on the map, these look very likely to be real duplicates
next_group_id = df.dup_group.max() + 1
to_dedup = to_dedup.loc[df.snap_group.isin([1, 2])].copy()
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


# update data types
for field in (
    "snap_group",
    "dup_sort",
):
    df[field] = df[field].astype("uint8")

df["snap_tolerance"] = df.snap_tolerance.astype("uint16")

# intentionally not casting snap_ref_id, wbID as it changes values
for field in ("snap_dist", "dup_group", "dup_count"):
    df[field] = df[field].astype("float32")

print("-----------------")


### Spatial joins
df = add_spatial_joins(df.drop(columns=["HUC2"]))

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

# calculate stream type
df["stream_type"] = df.FCode.map(FCODE_TO_STREAMTYPE).fillna(0).astype("uint8")

# calculate intermittent + ephemeral
df["intermittent"] = df.FCode.isin([46003, 46007])


# Fix missing field values
df["loop"] = df.loop.fillna(0).astype("bool")
df["offnetwork_flowline"] = df.offnetwork_flowline.fillna(0).astype("bool")
df["sizeclass"] = df.sizeclass.fillna("")
df["FCode"] = df.FCode.fillna(-1).astype("int32")
# -9998.0 - 0 values likely indicate AnnualVelocity / AnnualFlow data is not available, equivalent to null
df.loc[df.AnnualVelocity < 0, "AnnualVelocity"] = np.nan
df.loc[df.AnnualFlow <= 0, "AnnualFlow"] = np.nan

# cast fields with missing values to float32
for field in ["AnnualVelocity", "AnnualFlow", "TotDASqKm"]:
    df[field] = df[field].astype("float32")

print("dams on loops:\n", df.groupby("loop").size())
print("dams on offnetwork flowlines: \n", df.groupby("offnetwork_flowline").size())


### Join waterbody properties
wb = (
    read_feathers(
        [nhd_dir / "clean" / huc2 / "waterbodies.feather" for huc2 in df.HUC2.unique() if huc2],
        columns=["wbID", "km2"],
    ).set_index("wbID")
    * KM2_TO_ACRES
).rename(columns={"km2": "WaterbodyAcres"})


# classify waterbody size class (see WATERBODY_SIZECLASS_DOMAIN)
# Note: 0 is reserved for missing data
bins = [-1, 0, 2.5, 25, 250, 2500] + [wb.WaterbodyAcres.max() + 1]
wb["WaterbodySizeClass"] = np.asarray(pd.cut(wb.WaterbodyAcres, bins, right=False, labels=np.arange(0, len(bins) - 1)))

df = df.join(wb, on="wbID")
df.WaterbodyAcres = df.WaterbodyAcres.fillna(-1).astype("float32")
df.WaterbodySizeClass = df.WaterbodySizeClass.fillna(0).astype("uint8")


### Update lowhead dam status with estimated lowhead dams
# from Kat: if ImpoundmentType==1 (run of the river), it is likely a lowhead dam;
# limit this to <= 15 feet based on review against aerial imagery (very few over 15 feet are lowhead)
# or if height is not present.  Ignore estimated dams or ones on very small streams
df.loc[
    (df.LowheadDam == 0)  # TODO: should this include 3
    & (df.ImpoundmentType == 1)
    & (df.Height <= 25)
    & (~df.is_estimated)
    & (df.snapped)
    & (df.sizeclass != "1a"),
    "LowheadDam",
] = 2

print(f"Lowhead dams: {df.groupby('LowheadDam').size()}")


### Add lat / lon (must be done after snapping!)
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(GEO_CRS)
geo["lat"] = shapely.get_y(geo.geometry.values).astype("float32")
geo["lon"] = shapely.get_x(geo.geometry.values).astype("float32")
df = df.join(geo[["lat", "lon"]])

### Pack small categorical fields not used for filtering in UI into an integer
print("Calculating packed categorical fields")
# NOTE: packing only includes fields not used for filtering in UI

# validate value ranges
if df.Recon.max() >= 32:
    raise ValueError("Update categorical packing, too many Recon values")

if df.PassageFacility.max() >= 32:
    raise ValueError("Update categorical packing, too many PassageFacility values")


### Assign map symbol for use in (some) tiles
df["symbol"] = 0
df.loc[df.invasive, "symbol"] = 4
# value 3 is minor road-related barrier, not used for dams
df.loc[df.nobarrier, "symbol"] = 2
df.loc[~df.snapped, "symbol"] = 1
# intentionally give removed barriers higher precedence
df.loc[df.removed, "symbol"] = 5
df.symbol = df.symbol.astype("uint8")


### Assign to network analysis scenario
# omit any that are not snapped or are duplicate / dropped / excluded or on loops / off-network flowlines
can_break_networks = df.snapped & (~(df.duplicate | df.dropped | df.excluded | df.loop | df.offnetwork_flowline))
df["primary_network"] = can_break_networks
# salmonid / large fish: exclude barriers that are passable to salmonids
# based on direction from Kat, exclude any with partial or seasonal passability
df["largefish_network"] = can_break_networks & (~(df.Passability.isin([2, 3, 4, 5, 6])))
df["smallfish_network"] = can_break_networks


### All done processing!

print("\n--------------\n")
df = df.reset_index(drop=True)

print("Serializing {:,} dams to master file".format(len(df)))
df.to_feather(master_dir / "dams.feather")
write_dataframe(df, qa_dir / "dams.fgb")


# Extract out only the snapped ones that are not on loops
df = df.loc[df.primary_network | df.largefish_network | df.smallfish_network].reset_index(drop=True)
df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

print("Serializing {:,} snapped dams".format(len(df)))
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
        "invasive",
    ]
].to_feather(
    snapped_dir / "dams.feather",
)
write_dataframe(df, qa_dir / "snapped_dams.fgb")


print("All done in {:.2f}s".format(time() - start))
