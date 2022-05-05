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
import warnings

import pandas as pd
import pygeos as pg
import geopandas as gp
import numpy as np
from pyogrio import write_dataframe

from analysis.constants import (
    FCODE_TO_STREAMTYPE,
    GEO_CRS,
    DROP_RECON,
    DROP_MANUALREVIEW,
    EXCLUDE_RECON,
    EXCLUDE_MANUALREVIEW,
    DAM_BARRIER_SEVERITY_TO_DOMAIN,
)

from analysis.lib.io import read_feathers
from analysis.lib.geometry import nearest
from analysis.prep.barriers.lib.snap import snap_to_flowlines
from analysis.prep.barriers.lib.duplicates import find_duplicates
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

# Snap waterfalls by 100 meters
SNAP_TOLERANCE = 100
DUPLICATE_TOLERANCE = 50


data_dir = Path("data")
nhd_dir = data_dir / "nhd"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
master_dir = barriers_dir / "master"
snapped_dir = barriers_dir / "snapped"
qa_dir = barriers_dir / "qa"


start = time()


print("Reading waterfalls")

df = gp.read_feather(src_dir / "waterfalls.feather").rename(
    columns={"fall_type": "FallType"}
)

df.FallType = df.FallType.fillna("").str.strip()


### Add IDs for internal use
# internal ID
df["id"] = df.index.astype("uint32")
df = df.set_index("id", drop=False)


### Cleanup data
df.Source = df.Source.str.strip()
df.loc[df.Source == "Amy Cottrell, Auburn", "Source"] = "Amy Cotrell, Auburn University"

df.Name = df.Name.fillna("").str.strip()
df.LocalID = df.LocalID.fillna("").str.strip()
df.Stream = df.Stream.fillna("").str.strip()
df.GNIS_Name = df.GNIS_Name.fillna("").str.strip()
ix = (df.Stream == "") & (df.GNIS_Name != "")
df.loc[ix, "Stream"] = df.loc[ix].GNIS_Name

df = df.drop(columns=["GNIS_Name"])


# Convert BarrierSeverity to a domain
# FIXME: temporary fixes
df.BarrierSeverity = df.fillna("").BarrierSeverity.str.replace(
    "Seasonbly", "Seasonably"
)
df.loc[df.BarrierSeverity.str.startswith("State of UT"), "BarrierSeverity"] = "Unknown"

df["BarrierSeverity"] = (
    df.BarrierSeverity.fillna("")
    .str.strip()
    .map(DAM_BARRIER_SEVERITY_TO_DOMAIN)
    .astype("uint8")
)


### Add persistant sourceID based on original IDs
df["sourceID"] = df.LocalID
ix = ~df.fall_id.isnull()
df.loc[ix, "sourceID"] = df.loc[ix].fall_id.astype("int").astype("str")


### Spatial joins
df = add_spatial_joins(df)


### Add tracking fields
# dropped: records that should not be included in any later analysis
df["dropped"] = False

# excluded: records that should be retained in dataset but not used in analysis
# NOTE: no waterfalls are currently excluded from analysis
df["excluded"] = False

df["log"] = ""


# Remove any that didn't intersect HUCs or states; these are outside the analysis region
drop_ix = df.HUC12.isnull() | df.STATEFIPS.isnull()
if drop_ix.sum():
    print(f"{drop_ix.sum():,} waterfalls are outside HUC12 / states")
    df = df.loc[~drop_ix].copy()


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
    "STATEFIPS",
    "State",
    "ECO3",
    "ECO4",
]:
    df[col] = df[col].fillna("").astype("str")


# Drop those where recon shows this as an error
drop_ix = df.Recon.isin(DROP_RECON) & ~df.dropped
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: Recon one of {DROP_RECON}"

drop_ix = df.ManualReview.isin(DROP_MANUALREVIEW)
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: ManualReview one of {DROP_MANUALREVIEW}"

# Drop manually-identified waterfalls that should be removed
drop_ix = df.SARPID.isin(
    ["f12317", "f13156", "f1557", "f12275", "f92", "f1951", "f7500", "f13457"]
)
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: removed specific ids"

# Drop records that indicate waterfall is not likely a current fish passage barrier
drop_types = ["dam", "historical rapids", "historical waterfall", "rapids"]
drop_ix = df.FallType.isin(drop_types)
df.loc[drop_ix, "dropped"] = True
df.loc[drop_ix, "log"] = f"dropped: type one of {drop_types}"

print(
    f"Dropped {drop_ix.sum():,} waterfalls from all analysis and mapping based on ManualReview, Recon, type, or ID"
)

### Exclude barriers that should not be analyzed or prioritized based on manual QA
df["excluded"] = df.ManualReview.isin(EXCLUDE_MANUALREVIEW) | df.Recon.isin(
    EXCLUDE_RECON
)

df.loc[df.Recon.isin(EXCLUDE_RECON), "log"] = f"excluded: Recon one of {EXCLUDE_RECON}"
df.loc[
    df.ManualReview.isin(EXCLUDE_MANUALREVIEW), "log"
] = f"excluded: ManualReview one of {EXCLUDE_MANUALREVIEW}"
print(
    f"Excluded {df.excluded.sum():,} waterfalls from network analysis and prioritization"
)

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
df, to_snap = snap_to_flowlines(df, to_snap=df.copy())
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
df, to_dedup = find_duplicates(df, to_dedup=df.copy(), tolerance=DUPLICATE_TOLERANCE)
print(
    f"Found {len(df.loc[df.duplicate]):,} total duplicates in {time() - dedup_start:.2f}s"
)


### Deduplicate by dams
# any that are within duplicate tolerance of dams may be duplicating those dams
# NOTE: these are only the dams that are snapped and not dropped or excluded
dams = gp.read_feather(snapped_dir / "dams.feather", columns=["geometry"])
near_dams = nearest(
    pd.Series(df.geometry.values.data, index=df.index),
    pd.Series(dams.geometry.values.data, index=dams.index),
    DUPLICATE_TOLERANCE,
)

ix = near_dams.index
df.loc[ix, "duplicate"] = True
df.loc[ix, "dup_log"] = f"Within {DUPLICATE_TOLERANCE}m of an existing dam"

print(f"Found {len(ix)} waterfalls within {DUPLICATE_TOLERANCE}m of dams")


### Join to line atts
flowlines = read_feathers(
    [nhd_dir / "clean" / huc2 / "flowlines.feather" for huc2 in df.HUC2.unique()],
    columns=[
        "lineID",
        "NHDPlusID",
        "GNIS_Name",
        "sizeclass",
        "StreamOrder",
        "FCode",
        "loop",
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
df["stream_type"] = df.FCode.map(FCODE_TO_STREAMTYPE)

# calculate intermittent + ephemeral
df["intermittent"] = df.FCode.isin([46003, 46007])


# Fix missing field values
df["loop"] = df.loop.fillna(False)
df["sizeclass"] = df.sizeclass.fillna("")
df["FCode"] = df.FCode.fillna(-1).astype("int32")

print(df.groupby("loop").size())


### Add lat / lon and drop geometry
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(GEO_CRS)
geo["lat"] = pg.get_y(geo.geometry.values.data).astype("float32")
geo["lon"] = pg.get_x(geo.geometry.values.data).astype("float32")
df = df.join(geo[["lat", "lon"]])


### All done processing!
print("\n--------------\n")
df = df.reset_index(drop=True)


df.to_feather(master_dir / "waterfalls.feather")

print("writing GIS for QA/QC")
write_dataframe(df, qa_dir / "waterfalls.fgb")

# Extract out only the snapped ones
df = df.loc[df.snapped & (~(df.duplicate | df.dropped | df.excluded))].reset_index(
    drop=True
)
df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

print("Serializing {0} snapped waterfalls".format(len(df)))
df[
    ["geometry", "id", "HUC2", "lineID", "NHDPlusID", "loop", "intermittent"]
].to_feather(snapped_dir / "waterfalls.feather",)

write_dataframe(df, qa_dir / "snapped_waterfalls.fgb")

print("All done in {:.2f}s".format(time() - start))

