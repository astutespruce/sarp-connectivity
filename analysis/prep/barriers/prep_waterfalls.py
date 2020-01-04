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
import pandas as pd
from time import time
from geofeather import from_geofeather
from geofeather.pygeos import to_geofeather
from pgpkg import to_gpkg
import geopandas as gp
import numpy as np
from nhdnet.io import deserialize_dfs


from analysis.constants import REGION_GROUPS, REGIONS, CRS
from analysis.pygeos_compat import to_pygeos
from analysis.prep.barriers.lib.snap import snap_to_flowlines
from analysis.prep.barriers.lib.duplicates import find_duplicates
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins

# Snap waterfalls by 100 meters
SNAP_TOLERANCE = 100
DUPLICATE_TOLERANCE = 10

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
nhd_dir = data_dir / "nhd"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
master_dir = barriers_dir / "master"
snapped_dir = barriers_dir / "snapped"
qa_dir = barriers_dir / "qa"
gdb_filename = "Waterfalls.gdb"


start = time()

print("Reading waterfalls")

df = gp.read_file(src_dir / gdb_filename)

### Drop records with bad coordinates
# must be done before projecting coordinates
print(
    "Dropping {} waterfalls with bad coordinates".format(
        len(df.loc[df.geometry.y > 90])
    )
)
df = df.loc[df.geometry.y.abs() <= 90]

### Reproject to CONUS Albers
df = df.to_crs(CRS)


### Add IDs for internal use
# internal ID
df["id"] = df.index.astype("uint32")
df = df.set_index("id", drop=False)


### Cleanup data
df.Source = df.Source.str.strip()
amy_idx = df.Source == "Amy Cottrell, Auburn"
df.loc[amy_idx, "Source"] = "Amy Cotrell, Auburn University"

### Add persistant sourceID based on original IDs
df["sourceID"] = df.LocalID
usgs_idx = ~df.fall_id.isnull()
df.loc[usgs_idx, "sourceID"] = df.loc[usgs_idx].fall_id.astype("int").astype("str")


### Spatial joins
df = add_spatial_joins(df)


### Add tracking fields
# dropped: records that should not be included in any later analysis
df["dropped"] = False

# excluded: records that should be retained in dataset but not used in analysis
# NOTE: no waterfalls are currently excluded from analysis
df["excluded"] = False


# Drop any that didn't intersect HUCs or states
drop_idx = df.HUC12.isnull() | df.STATEFIPS.isnull()
print("{} waterfalls are outside HUC12 / states".format(len(df.loc[drop_idx])))
df.loc[drop_idx, "dropped"] = True

### Convert to pygeos format for following operations
df = pd.DataFrame(df.copy())
df["geometry"] = to_pygeos(df.geometry)


### Snap waterfalls
print("Snapping {:,} waterfalls".format(len(df)))

# snapped: records that snapped to the aquatic network and ready for network analysis
df["snapped"] = False
df["snap_log"] = "not snapped"
df["lineID"] = np.nan  # line to which dam was snapped
df["snap_tolerance"] = SNAP_TOLERANCE

# Snap to flowlines
snap_start = time()
df, to_snap = snap_to_flowlines(df, to_snap=df.copy())
df["loop"] = df.loop.fillna(False)
print(
    "Snapped {:,} waterfalls in {:.2f}s".format(
        len(df.loc[df.snapped]), time() - snap_start
    )
)
print("---------------------------------")
print("\nSnapping statistics")
print(df.groupby("snap_log").size())
print(df.groupby("loop").size())
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
    "Found {:,} total duplicates in {:.2f}s".format(
        len(df.loc[df.duplicate]), time() - dedup_start
    )
)

### Join to line atts
flowlines = deserialize_dfs(
    [nhd_dir / "clean" / region / "flowlines.feather" for region in REGION_GROUPS],
    columns=["lineID", "NHDPlusID", "sizeclass", "streamorder", "loop", "waterbody"],
).set_index("lineID")

df = df.join(flowlines, on="lineID")

### All done processing!
print("\n--------------\n")
df = df.reset_index(drop=True)


to_geofeather(df, master_dir / "waterfalls.feather")

print("writing GIS for QA/QC")
to_gpkg(df, qa_dir / "waterfalls")
# to_shp(df, qa_dir / "waterfalls.shp")

# Extract out only the snapped ones
df = df.loc[df.snapped & ~(df.duplicate | df.dropped | df.excluded)].reset_index(
    drop=True
)
df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

print("Serializing {0} snapped waterfalls".format(len(df)))
to_geofeather(
    df[["geometry", "id", "HUC2", "lineID", "NHDPlusID", "loop", "waterbody"]],
    snapped_dir / "waterfalls.feather",
)

print("All done in {:.2f}s".format(time() - start))
