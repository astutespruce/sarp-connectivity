"""
Extract waterfalls from original data source, process for use in network analysis, and convert to feather format.
1. Remove records with bad coordinates (one waterfall was represented in wrong projection)
2. Cleanup data values (as needed) and add tracking fields
3. Snap to flowlines
4. Drop duplicates

This creates 2 files:
`barriers/master/waterfalls.feather` - master waterfalls dataset, including coordinates updated from snapping
`barriers/snapped/waterfalls.feather` - snapped waterfalls dataset for network analysis
"""

from pathlib import Path
from time import time

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc

import shapely
import geopandas as gp
import numpy as np
from pyogrio import write_dataframe

from analysis.constants import (
    WATERFALLS_ID_OFFSET,
    FCODE_TO_STREAMTYPE,
    GEO_CRS,
    DROP_RECON,
    DROP_MANUALREVIEW,
    EXCLUDE_RECON,
    EXCLUDE_MANUALREVIEW,
    DAM_BARRIER_SEVERITY_TO_DOMAIN,
    INVASIVE_RECON,
    INVASIVE_MANUALREVIEW,
)

from analysis.lib.io import read_arrow_tables
from analysis.lib.geometry import nearest
from analysis.prep.species.lib.diadromous import get_diadromous_ids
from analysis.prep.barriers.lib.snap import snap_to_flowlines
from analysis.prep.barriers.lib.duplicates import find_duplicates
from analysis.prep.barriers.lib.spatial_joins import get_huc2, add_spatial_joins


# Snap waterfalls by 100 meters
SNAP_TOLERANCE = 100
DUPLICATE_TOLERANCE = 50


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
nhd_dir = data_dir / "nhd"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
master_dir = barriers_dir / "master"
snapped_dir = barriers_dir / "snapped"
qa_dir = barriers_dir / "qa"


start = time()

huc2s = sorted(pd.read_feather(boundaries_dir / "HUC2.feather", columns=["HUC2"]).HUC2.values)


print("\n\n----------------------------------\nReading waterfalls\n---------------------------")

df = gp.read_feather(src_dir / "waterfalls.feather").rename(columns={"fall_type": "FallType"})

# TODO: remove once field is added to ArcGIS service
if "PartnerID" not in df.columns:
    df["PartnerID"] = ""

### drop any that are outside analysis HUC2s
df = df.join(get_huc2(df))
drop_ix = df.HUC2.isnull()
if drop_ix.sum():
    print(f"{drop_ix.sum():,} waterfalls are outside analysis HUC2s; these are dropped from master dataset")
    df = df.loc[~drop_ix].copy()


### Add IDs for internal use
# internal ID
df["id"] = (df.index.values + WATERFALLS_ID_OFFSET).astype("uint64")
df = df.set_index("id", drop=False)


### Cleanup data
df["PartnerID"] = df.PartnerID.fillna("").str.strip()
df.FallType = df.FallType.fillna("").str.strip().str.lower()

df.Source = df.Source.str.strip()
df.loc[df.Source == "Amy Cottrell, Auburn", "Source"] = "Amy Cotrell, Auburn University"

df.Name = df.Name.fillna("").str.strip()
df.loc[df.Name.str.lower().isin(["unknown"]), "Name"] = ""
df.SourceID = df.SourceID.fillna("").str.strip()
df.River = df.River.fillna("").str.strip()

df.GNIS_Name = df.GNIS_Name.fillna("").str.strip()
ix = (df.River == "") & (df.GNIS_Name != "")
df.loc[ix, "River"] = df.loc[ix].GNIS_Name

df = df.drop(columns=["GNIS_Name"])

df["Recon"] = df.Recon.fillna(0).astype("uint8")
df["ManualReview"] = df.ManualReview.fillna(0).astype("uint8")


# convert Private to bool
df["Private"] = (
    df.Private.fillna("").map({"Public": False, "0": False, "Private": True, "1": True, "": False}).astype("bool")
)


### Add tracking fields
# dropped: records that should not be included in any later analysis
df["dropped"] = False

# excluded: records that should be retained in dataset but not used in analysis
# NOTE: no waterfalls are currently excluded from analysis
df["excluded"] = False

# used to flag networks that have invasive barriers, including waterfalls
df["invasive"] = False

df["log"] = ""


# Drop those where recon shows this as an error
drop_ix = df.Recon.isin(DROP_RECON) & ~df.dropped
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: Recon one of {DROP_RECON}"

drop_ix = df.ManualReview.isin(DROP_MANUALREVIEW)
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: ManualReview one of {DROP_MANUALREVIEW}"

# Drop manually-identified waterfalls that should be removed
drop_ix = df.SARPID.isin(
    [
        # Celilo Falls are drowned by backwaters of Dalles dam
        "f720",
        "f5117",
        "f9785",
        "f9827",
        "f10666",
        "f10925",
    ]
)
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = "dropped: removed specific ids"

# Drop records that indicate waterfall is not likely a current fish passage barrier
drop_types = ["dam", "historical rapids", "historical waterfall", "rapids"]
drop_ix = df.FallType.isin(drop_types)
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: type one of {drop_types}"

print(f"Dropped {drop_ix.sum():,} waterfalls from all analysis and mapping based on ManualReview, Recon, type, or ID")

### Exclude barriers based on BarrierSeverity

df.BarrierSeverity = df.BarrierSeverity.fillna("").str.strip().str.lower()

# FIXME: temporary fixes
df.loc[df.BarrierSeverity.str.lower().str.startswith("state of ut"), "BarrierSeverity"] = "unknown"
df.loc[df.BarrierSeverity == "complete barriar", "BarrierSeverity"] = "Complete Barrier"

# mark as excluded if barrier severity is no barrier
exclude_severities = ["no barrier"]
ix = df.BarrierSeverity.isin(exclude_severities)
df.loc[ix, "excluded"] = True
df.loc[ix, "log"] = f"excluded: BarrierSeverity one of {', '.join(exclude_severities)}"

# Convert to domain and call it Passability
df["Passability"] = (
    df.BarrierSeverity.fillna("unknown").str.strip().str.lower().map(DAM_BARRIER_SEVERITY_TO_DOMAIN).astype("uint8")
)

df = df.drop(columns=["BarrierSeverity"])

### Exclude barriers that should not be analyzed based on manual QA
ix = df.Recon.isin(EXCLUDE_RECON)
df.loc[ix, "excluded"] = True
df.loc[ix, "log"] = f"excluded: Recon one of {EXCLUDE_RECON}"

ix = df.ManualReview.isin(EXCLUDE_MANUALREVIEW)
df.loc[ix, "excluded"] = True
df.loc[ix, "log"] = f"excluded: ManualReview one of {EXCLUDE_MANUALREVIEW}"
print(f"Excluded {df.excluded.sum():,} waterfalls from network analysis")

### Mark invasive barriers
# for waterfalls, these indicate that the waterfall is a barrier to flow of invasive species
invasive_fields = {
    "Recon": INVASIVE_RECON,
    "ManualReview": INVASIVE_MANUALREVIEW,
}

for field, values in invasive_fields.items():
    ix = df[field].isin(values)
    df.loc[ix, "invasive"] = True


### Snap waterfalls
print(f"Snapping {len(df):,} waterfalls")
write_dataframe(df.reset_index(drop=True), qa_dir / "waterfalls_pre_snap.fgb")

# snapped: records that snapped to the aquatic network and ready for network analysis
df["snapped"] = False
df["snap_log"] = "not snapped"
df["lineID"] = np.nan  # line to which dam was snapped
df["snap_tolerance"] = SNAP_TOLERANCE

# Snap to flowlines
snap_start = time()

df, to_snap = snap_to_flowlines(df, to_snap=df.loc[~df.dropped].copy(), allow_offnetwork_flowlines=False)
print(f"Snapped {len(df.loc[df.snapped]):,} waterfalls in {time() - snap_start:.2f}s")
print("---------------------------------")
print("\nSnapping statistics")
print(df.groupby("snap_log").size())
print("---------------------------------\n")


print("\n--------------\n")

### Remove duplicates after snapping, in case any snapped to the same position
print("Removing duplicates...")

df["duplicate"] = False
df["dup_group"] = np.nan
df["dup_count"] = np.nan
df["dup_log"] = "not a duplicate"
df["dup_sort"] = 0  # not meaningful for waterfalls
df["ManualReview"] = 0  # not meaningful for waterfalls

dedup_start = time()
df, to_dedup = find_duplicates(df, to_dedup=df.loc[~df.dropped].copy(), tolerance=DUPLICATE_TOLERANCE)
print(f"Found {len(df.loc[df.duplicate]):,} total duplicates in {time() - dedup_start:.2f}s")

### Deduplicate by dams
# any that are within duplicate tolerance of dams may be duplicating those dams
# NOTE: these are only the dams that are snapped and not dropped or excluded
dams = gp.read_feather(snapped_dir / "dams.feather", columns=["geometry"])
near_dams = nearest(
    pd.Series(df.geometry.values, index=df.index),
    pd.Series(dams.geometry.values, index=dams.index),
    DUPLICATE_TOLERANCE,
)

ix = near_dams.index
df.loc[ix, "duplicate"] = True
df.loc[ix, "dup_log"] = f"Within {DUPLICATE_TOLERANCE}m of an existing dam"

print(f"Found {len(ix)} waterfalls within {DUPLICATE_TOLERANCE}m of dams")


# update data types
df["dup_sort"] = df.dup_sort.astype("uint8")
df["snap_tolerance"] = df.snap_tolerance.astype("uint16")

for field in ("snap_ref_id", "snap_dist", "dup_group", "dup_count"):
    df[field] = df[field].astype("float32")


### Spatial joins
df = add_spatial_joins(df.drop(columns=["HUC2"]))

drop_ix = df.HUC12.isnull()
if drop_ix.sum():
    print(f"{drop_ix.sum():,} waterfalls are outside analysis HUC12s")
    df = df.loc[~drop_ix].copy()

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
            "AnnualFlow",
            "AnnualVelocity",
            "TotDASqKm",
        ],
        filter=pc.is_in(pc.field("lineID"), pa.array(df.lineID.unique())),
    )
    .to_pandas()
    .set_index("lineID")
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
df["sizeclass"] = df.sizeclass.fillna("")
df["FCode"] = df.FCode.fillna(-1).astype("int32")
# -9998.0 values likely indicate AnnualVelocity data is not available, equivalent to null
df.loc[df.AnnualVelocity < 0, "AnnualVelocity"] = -1
df.loc[df.AnnualFlow <= 0, "AnnualFlow"] = -1

for field in ["AnnualVelocity", "AnnualFlow", "TotDASqKm"]:
    df[field] = df[field].fillna(-1).astype("float32")

print(df.groupby("loop").size())


### Add lat / lon and drop geometry
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(GEO_CRS)
geo["lat"] = shapely.get_y(geo.geometry.values).astype("float32")
geo["lon"] = shapely.get_x(geo.geometry.values).astype("float32")
df = df.join(geo[["lat", "lon"]])


### Assign to network analysis scenario
# omit any that are not snapped or are duplicate / dropped / excluded or on loops
can_break_networks = df.snapped & (~(df.duplicate | df.dropped | df.excluded | df.loop))
df["primary_network"] = can_break_networks
# salmonid / large fish: exclude barriers that are passable to salmonids
# based on direction from Kat, exclude any with partial or seasonal passability
df["largefish_network"] = can_break_networks & (~(df.Passability.isin([2, 3, 4, 5, 6])))
df["smallfish_network"] = can_break_networks


### All done processing!
print("\n--------------\n")
df = df.reset_index(drop=True)


df.to_feather(master_dir / "waterfalls.feather")

print("writing GIS for QA/QC")
write_dataframe(df, qa_dir / "waterfalls.fgb")

# Extract out only the snapped ones not on loops
snapped_waterfalls = df.loc[
    df.primary_network | df.largefish_network | df.smallfish_network,
    [
        "geometry",
        "id",
        "SARPID",
        "HUC2",
        "lineID",
        "NHDPlusID",
        "primary_network",
        "largefish_network",
        "smallfish_network",
        "invasive",
    ],
].reset_index(drop=True)
snapped_waterfalls.lineID = snapped_waterfalls.lineID.astype("uint32")
snapped_waterfalls.NHDPlusID = snapped_waterfalls.NHDPlusID.astype("uint64")
snapped_waterfalls["HUC2"] = snapped_waterfalls.HUC2.astype(pd.CategoricalDtype(categories=huc2s, ordered=True))

print(f"Serializing {len(snapped_waterfalls)} snapped waterfalls")
snapped_waterfalls.to_feather(snapped_dir / "waterfalls.feather")
write_dataframe(df, qa_dir / "snapped_waterfalls.fgb")

print("All done in {:.2f}s".format(time() - start))
