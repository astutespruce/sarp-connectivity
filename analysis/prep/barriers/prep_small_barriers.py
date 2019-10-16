"""
Extract small barriers from original data source, process for use in network analysis, and convert to feather format.
1. Cleanup data values (as needed)
2. Filter out barriers not to be included in analysis (based on Potential_Project and Snap2018)
3. Snap to networks by HUC2
4. Remove duplicate barriers

This creates 2 files:
`barriers/master/small_barriers.feather` - master barriers dataset, including coordinates updated from snapping
`barriers/snapped/small_barriers.feather` - snapped barriers dataset for network analysis
"""

from pathlib import Path
from time import time
import pandas as pd
from geofeather import to_geofeather, from_geofeather
import geopandas as gp
import numpy as np

from nhdnet.io import deserialize_df, deserialize_sindex, to_shp
from nhdnet.geometry.points import mark_duplicates, add_lat_lon
from nhdnet.geometry.lines import snap_to_line

from analysis.constants import (
    REGION_GROUPS,
    REGIONS,
    CRS,
    DUPLICATE_TOLERANCE,
    KEEP_POTENTIAL_PROJECT,
    DROP_POTENTIAL_PROJECT,
    DROP_SNAP2018,
    EXCLUDE_SNAP2018,
    BARRIER_CONDITION_TO_DOMAIN,
    POTENTIAL_TO_SEVERITY,
    ROAD_TYPE_TO_DOMAIN,
    CROSSING_TYPE_TO_DOMAIN,
)

from analysis.prep.barriers.lib.snap import snap_by_region, update_from_snapped
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins

# Snap barriers by 50 meters
SNAP_TOLERANCE = 50

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
master_dir = barriers_dir / "master"
snapped_dir = barriers_dir / "snapped"
qa_dir = barriers_dir / "qa"

start = time()


df = from_geofeather(src_dir / "sarp_small_barriers.feather")
print("Read {:,} small barriers".format(len(df)))

# Rename all columns that have underscores


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
] = (df.Stream + " / " + df.Road)
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

# Drop any that didn't intersect HUCs or states
drop_idx = df.HUC12.isnull() | df.STATEFIPS.isnull()
print("{:,} small barriers are outside HUC12 / states".format(len(df.loc[drop_idx])))
# Mark dropped barriers
df.loc[drop_idx, "dropped"] = True


### Drop any small barriers that should be completely dropped from analysis
# based on manual QA/QC
# NOTE: small barriers currently do not have any values set for SNAP2018
drop_idx = df.PotentialProject.isin(DROP_POTENTIAL_PROJECT) | df.SNAP2018.isin(
    DROP_SNAP2018
)
print(
    "Dropped {:,} small barriers from all analysis and mapping".format(
        len(df.loc[drop_idx])
    )
)
df.loc[drop_idx, "dropped"] = True

### Exclude barriers that should not be analyzed or prioritized based on manual QA
# NOTE: small barriers currently do not have any values set for SNAP2018
exclude_idx = ~df.PotentialProject.isin(KEEP_POTENTIAL_PROJECT) | df.SNAP2018.isin(
    EXCLUDE_SNAP2018
)

print(
    "Excluded {:,} small barriers from network analysis and prioritization".format(
        len(df.loc[exclude_idx])
    )
)
df.loc[exclude_idx, "excluded"] = True

### Snap by region group
to_snap = df.loc[~(df.dropped | df.excluded), ["geometry", "HUC2", "id"]].copy()
print("Attempting to snap {:,} small barriers".format(len(to_snap)))

snapped = snap_by_region(to_snap, REGION_GROUPS, SNAP_TOLERANCE)

# join back to master
df = update_from_snapped(df, snapped)


# Remove duplicates after snapping, in case any snapped to the same position
# These are completely dropped from the analysis from here on out
# Sort by descending severity before deduplication so that most severe barrier is retained
df = mark_duplicates(
    df.sort_values("SeverityClass", ascending=False), DUPLICATE_TOLERANCE
)
df = df.sort_values("id")
print(
    "{} duplicate small barriers removed after snapping".format(
        len(df.loc[df.duplicate])
    )
)

print("\n--------------\n")

df = df.reset_index(drop=True)

print("Serializing {:,} small barriers".format(len(df)))
to_geofeather(df, master_dir / "small_barriers.feather")


print("writing shapefiles for QA/QC")
to_shp(df, qa_dir / "small_barriers.shp")


# Extract out only the snapped ones
df = df.loc[df.snapped & ~df.duplicate].reset_index(drop=True)
df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

print("Serializing {:,} snapped small barriers".format(len(df)))
to_geofeather(
    df[["geometry", "id", "HUC2", "lineID", "NHDPlusID"]],
    snapped_dir / "small_barriers.feather",
)

print("All done in {:.2f}s".format(time() - start))
