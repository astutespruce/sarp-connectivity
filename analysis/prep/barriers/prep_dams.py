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
from geofeather.pygeos import from_geofeather as from_geofeather_as_pygeos
from pgpkg import to_gpkg
import geopandas as gp
import numpy as np

from nhdnet.io import deserialize_sindex, deserialize_df, to_shp
from nhdnet.geometry.lines import snap_to_line

# from nhdnet.geometry.points import mark_duplicates, find_nearby

from analysis.prep.barriers.lib.points import (
    nearest,
    near,
    neighborhoods,
    connect_points,
)
from analysis.pygeos_compat import to_pygeos, from_pygeos
from analysis.prep.barriers.lib.snap import (
    snap_to_nhd_dams,
    snap_to_waterbodies,
    snap_to_flowlines,
    snap_to_large_waterbodies,
    export_snap_dist_lines,
)

from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins
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


### Custom tolerance values for dams
# Dams within 50 meters are considered duplicates
DUPLICATE_TOLERANCE = 50  # TODO: verify this is producing good results

SNAP_TOLERANCE = {"likely on network": 150, "likely off network": 50}


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
nhd_dir = data_dir / "nhd"
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
df = df.set_index("id", drop=False)


######### Fix data issues
### Set data types
for column in ("River", "NIDID", "Source", "Name", "OtherName"):
    df[column] = df[column].fillna("").str.strip()

for column in ("Construction", "Condition", "Purpose", "Recon"):
    df[column] = df[column].fillna(0).astype("uint8")

for column in ("Year", "Feasibility", "ManualReview"):
    df[column] = df[column].fillna(0).astype("uint16")


# Fix Recon value that wasn't assigned to ManualReview
# these are invasive species barriers
df.loc[df.Recon == 16, "ManualReview"] = 10

# Reset manual review for dams that were previously not snapped, but are not reviewed
df.loc[df.ManualReview.isin([7, 9]), "ManualReview"] = 0


# Round height to nearest foot.  There are no dams between 0 and 1 foot, so fill all
# na as 0
df.Height = df.Height.fillna(0).round().astype("uint16")

# Cleanup names
# Standardize the casing of the name
df.Name = df.Name.str.title()
df.OtherName = df.OtherName.str.title()
df.River = df.River.str.title()

# Fix name issue - 3 dams have duplicate dam names with line breaks, which breaks tippecanoe
ids = df.loc[df.Name.str.count("\r") > 0].index
df.loc[ids, "Name"] = df.loc[ids].Name.apply(lambda v: v.split("\r")[0]).fillna("")


# Identify estimated dams
# these were generated by SARP from analysis of small waterbodies
ix = df.Name.str.count("Estimated Dam") > 0
df.loc[ix, "ManualReview"] = 20  # indicates estimated dam

# Replace estimated dam names if another name is available
ix = ix & (df.OtherName.str.len() > 0)
df.loc[ix, "Name"] = df.loc[ix].OtherName


# Amber Ignatius ACF dams are often features that don't have associated flowlines,
# flag so we don't snap to flowlines that aren't really close
df.loc[df.Source.str.count("Amber Ignatius") > 0, "ManualReview"] = 21


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


### Add tracking fields
# master log field for status
df["log"] = ""
# dropped: records that should not be included in any later analysis
df["dropped"] = False

# excluded: records that should be retained in dataset but not used in analysis
df["excluded"] = False

# duplicate: records that are duplicates of another record that was retained
# NOTE: the first instance of a set of duplicates is NOT marked as a duplicate,
# only following ones are.
df["duplicate"] = False
# duplicate sort will be assigned lower values to find preferred entry w/in dups
df["dup_sort"] = 9999


# Drop any that didn't intersect HUCs or states
drop_idx = df.HUC12.isnull() | df.STATEFIPS.isnull()
print("{:,} dams are outside HUC12 / states".format(len(df.loc[drop_idx])))
# Mark dropped barriers
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: outside HUC12 / states"


### Drop any dams that should be completely dropped from analysis
# based on manual QA/QC and other reivew.

# Drop those where recon shows this as an error
drop_idx = df.Recon.isin(DROP_RECON) & ~df.dropped
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: Recon one of {}".format(DROP_RECON)

# Drop those where recon shows this as an error
drop_idx = df.Feasibility.isin(DROP_FEASIBILITY) & ~df.dropped
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: Feasibility one of {}".format(DROP_FEASIBILITY)

# Drop those that were manually reviewed off-network or errors
drop_idx = df.ManualReview.isin(DROP_MANUALREVIEW) & ~df.dropped
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: ManualReview one of {}".format(DROP_MANUALREVIEW)

# From Kat: if the dam includes "dike" in the name and not "dam", it is not really a dam
drop_idx = (
    df.Name.str.lower().str.contains(" dike")
    & (~df.Name.str.lower().str.contains(" dam"))
    & ~df.dropped
)
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: name includes dike and not dam"

print("Dropped {:,} dams from all analysis and mapping".format(len(df.loc[df.dropped])))


### Exclude dams that should not be analyzed or prioritized based on manual QA
exclude_idx = df.Recon.isin(EXCLUDE_RECON) | df.ManualReview.isin(EXCLUDE_MANUALREVIEW)
df.loc[exclude_idx, "excluded"] = True
df.loc[exclude_idx, "log"] = "excluded: Recon one of {}".format(EXCLUDE_RECON)

exclude_idx = df.ManualReview.isin(EXCLUDE_MANUALREVIEW)
df.loc[exclude_idx, "excluded"] = True
df.loc[exclude_idx, "log"] = "excluded: ManualReview one of {}".format(
    EXCLUDE_MANUALREVIEW
)

print(
    "Excluded {:,} dams from analysis and prioritization".format(
        len(df.loc[df.excluded])
    )
)


# FIXME:
# to_geofeather(df.reset_index(drop=True), "/tmp/pre-snap.feather")
# raise ("FOO")

### Snap dams
# snapped: records that snapped to the aquatic network and ready for network analysis
df["snapped"] = False
df["snap_log"] = ""
df["snap_ref_id"] = np.nan  # id of feature from snap type this was snapped to
df["snap_dist"] = np.nan
df["lineID"] = np.nan  # line to which dam was snapped
df["wbID"] = np.nan  # waterbody ID where dam is either contained or snapped
df["snap_tolerance"] = SNAP_TOLERANCE["likely on network"]
# Dams likely to be off network get a much smaller tolerance
df.loc[df.ManualReview.isin([20, 21]), "snap_tolerance"] = SNAP_TOLERANCE[
    "likely off network"
]
print(
    "Setting snap tolerance to {}m for {:,} dams likely off network".format(
        SNAP_TOLERANCE["likely off network"],
        len(df.loc[df.ManualReview.isin([20, 21])]),
    )
)

# IMPORTANT: do not snap manually reviewed, off-network dams!
to_snap = df.loc[df.ManualReview != 5].copy()

# NOTE: temporary, convert geoms to pygeos
to_snap["geometry"] = to_pygeos(to_snap.geometry)

# Save original locations so we can map the snap line between original and new locations
original_locations = to_snap.copy()

snap_start = time()

# Snap to NHD dams
df, to_snap = snap_to_nhd_dams(df, to_snap)

# Snap to waterbodies
df, to_snap = snap_to_waterbodies(df, to_snap)

# Snap to flowlines
df, to_snap = snap_to_flowlines(df, to_snap)

# Last ditch effort to snap major waterbody-related dams
df, to_snap = snap_to_large_waterbodies(df, to_snap)

print(
    "Snapped {:,} dams in {:.2f}s".format(len(df.loc[df.snapped]), time() - snap_start)
)
print("\nSnapping statistics")
print(df.groupby("snap_log").size())
print("---------------------------------\n")

### Save results from snapping for QA
tmp = pd.DataFrame(df.copy())
tmp["geometry"] = to_pygeos(tmp.geometry)
export_snap_dist_lines(df.loc[df.snapped], original_locations, qa_dir, prefix="dams_")

### TODO: dedup and assign new flowline IDs to members of dup group


# ### First pass deduplication - TODO: re-enable
# # Assign dup_sort, lower numbers = higher priority to keep from duplicate group
# # Start from lower priorities and override with lower values

# # Prefer dams with River to those that do not
# df.loc[df.River != "", "dup_sort"] = 5

# # Prefer dams that have been reconned to those that haven't
# df.loc[df.Recon > 0, "dup_sort"] = 4

# # Prefer dams with height or year to those that do not
# df.loc[(df.Year > 0) | (df.Height > 0), "dup_sort"] = 3

# # NABD dams should be reasonably high priority
# df.loc[df.ManualReview == 2, "dup_sort"] = 2

# # manually reviewed dams should be highest priority (4=onstream, 5=offstream)
# df.loc[df.ManualReview.isin([4, 5]), "dup_sort"] = 1


### TODO: re-enable AFTER snapping
### Remove duplicates within 10 m;
# from those that were hand-checked on the map, they are duplicates of each other
# drop any duplicate clusters that have one or among them that was dropped
# groups = (
#     find_neighborhoods(df, 10)
#     .join(df[["dropped", "excluded", "ManualReview", "dup_sort"]])
#     .sort_values(by="dup_sort")
# )
# grouped = groups.groupby("group")
# count = grouped.size().rename("dup_count")
# groups = groups.join(count, on="group")
# keep = groups.reset_index().rename(columns={"index": "id"}).groupby("group").first()

# dups = groups.loc[~groups.index.isin(keep.id.unique())].index

# print("Found {:,} duplicates before snapping".format(len(dups)))

# # mark duplicates and combine in dup group info
# df.loc[df.index.isin(dups), "duplicate"] = True
# df = df.join(groups.rename(columns={"group": "dup_group"})[["dup_group", "dup_count"]])

# # Drop all records from any groups that have a dropped record
# # UNLESS the one being kept is manually reviewed and not dropped
# trusted_keepers = keep.loc[(keep.ManualReview == 4) & ~keep.dropped]
# drop_groups = grouped.dropped.max()
# drop_groups = drop_groups.loc[
#     drop_groups & ~drop_groups.index.isin(trusted_keepers.index)
# ].index

# print(
#     "Dropped {:,} dams that were in duplicate groups with dams that were dropped".format(
#         len(df.loc[df.dup_group.isin(drop_groups) & ~df.dropped])
#     )
# )

# df.loc[df.dup_group.isin(drop_groups), "dropped"] = True


# # Exclude all records from groups that have an excluded record
# exclude_groups = grouped.excluded.max()
# exclude_groups = exclude_groups.loc[
#     exclude_groups & ~exclude_groups.index.isin(trusted_keepers.index)
# ].index

# print(
#     "Excluded {:,} dams that were in duplicate groups with dams that were excluded".format(
#         len(df.loc[df.dup_group.isin(exclude_groups) & ~df.excluded])
#     )
# )

# df.loc[df.dup_group.isin(exclude_groups), "excluded"] = True


# # TODO: (LONG TERM) check distance from kept point to all the others

# print(
#     "First stage deduplication complete, now have {:,} dropped, {:,} excluded, {:,} duplicates, {:,} kept".format(
#         df.dropped.sum(),
#         df.excluded.sum(),
#         df.duplicate.sum(),
#         len(df.loc[~(df.dropped | df.excluded | df.duplicate)]),
#     )
# )

#### End TODO: re-enable dedup stage 1


### TODO: join to line atts


### Deduplicate manually snapped dams and snap nearby ones to them
# NABD dams (ManualReview == 2) should probably snap to bigger reservoirs, if possible
# TODO: exclude estimated ones that were dropped
# trusted = df.loc[df.ManualReview == 4]
# estimated = df.loc[df.ManualReview == 20]


### Snap based on NHD Lines and Areas that identify dams

# print("Loading large waterbodies...")
# large_wb = from_geofeather(nhd_dir / "merged" / "large_waterbodies.feather")
# large_drains = from_geofeather(
#     nhd_dir / "merged" / "large_waterbody_drain_points.feather"
# ).rename(columns={"id": "drainID"})
# large_drains.sindex

# print("Loading NHD dam areas...")
# nhd_lines = from_geofeather(nhd_dir / "extra" / "nhd_lines.feather")
# nhd_areas = from_geofeather(nhd_dir / "extra" / "nhd_areas.feather")

# # extract dams and drop missing geoms
# nhd_lines = nhd_lines.loc[(nhd_lines.FType == 343) & nhd_lines.geometry.notnull()].copy()
# nhd_areas = nhd_areas.loc[(nhd_areas.FType == 343) & nhd_areas.geometry.notnull()].copy()

# # TODO: intersect the lines with flowlines; these represent real dams that may not be captured in the inventory


# # buffer lines by 30m, buffer areas by 30m, merge, and dissolve
# buffered = np.append(pg.buffer(to_pygeos(nhd_lines.geometry), 30), pg.buffer(to_pygeos(nhd_areas.geometry), 30))
# buffered = pg.union_all(buffered)

# # explode parts
# buffered = np.array([pg.get_geometry(buffered, i) for i in range(0, pg.get_num_geometries(buffered))])
# nhd_dams = gp.GeoDataFrame(from_pygeos(buffered).rename('geometry'), crs=df.crs)
# nhd_dams['nhdid'] = nhd_dams.index.copy().astype('uint16')

# ### Intersect with waterbody drains
# nhd_dams.sindex
# large_drains.sindex
# dam_drains = gp.sjoin(nhd_dams, large_drains, how='inner')
# # NOTE: there are duplicate drains for some dams

# # sort by waterbody size and take largest waterbody
# dam_drains = dam_drains.sort_values(by='AreaSqKm', ascending=False).groupby('nhdid').first().reset_index()

# # join in drain geometry
# dam_drains = dam_drains.join(large_drains.set_index('drainID').geometry.rename('drain'), on='drainID')
# dam_drains = gp.GeoDataFrame(dam_drains[['nhdid', 'geometry', 'lineID', 'wbID', 'drainID', 'drain']], crs=large_drains.crs)

# # This will be the larger set
# dams_no_drains = nhd_dams.loc[~nhd_dams.nhdid.isin(dam_drains.nhdid.unique())].copy()
# # TODO: figure out how to bring flowlines in here

# # now intersect with dams and find closest drain

# df.sindex
# dam_drains.sindex
# dams = gp.sjoin(df[['geometry']], dam_drains, how='inner')
# print("Found {:,} dams associated with NHD dams that have waterbody drains".format(len(dams)))


# for any that don't have drains, need to intersect with flowlines


### Intersect with NHD dams
# Dams that are close to NHD dams are trusted
# nhd_dams.sindex
# df.sindex
# dams = gp.sjoin(df[['geometry']], nhd_dams, how='inner')
# # introducing dups?
# dams = dams.join(nhd_dams.geometry.rename('nhd_dam'), on='index_right').drop(columns=['index_right'])
# print("Found {:,} dams overlapping NHD dams".format(len(dams)))

# NOTE: there are duplicate dams at some of these; once we find appropriate point for each we'll snap and reduce dups


# # Find the nearest waterbody drain within tolerance distance of nhd_areas
# large_drains.sindex
# dam_drains = gp.sjoin(dams.set_geometry('nhd_dam'), large_drains, how='inner')

# print("Found {:,} waterbody drains overlapping with NHD dams".format(len(dam_drains)))
# # if there isn't one close by, snap to the closest flowline that intersects the nhd area


### Snap to waterbody drain points and flowlines


# Find all dams within large waterbodies
# There are some that are just randomly within large waterbodies
# others are at the fringes and are valid dams (there are multiple waterbodies but NHD only has one, or we merged them)

# to_snap.sindex

# for those that are within large waterbodies,
# attempt to snap to the nearest drain if within 1 km (arbitrary limit)
# FIXME: This is producing dups, where there are multiple drains per WB, need to find the closest for each

# Analyze dams that are completely within waterbodies or within 30m of their edge
print("Analyzing dams completely within large waterbodies or within 30m of them...")
buffered = to_snap.copy()
buffered["geometry"] = buffered.geometry.buffer(30)

large_wb.sindex
buffered.sindex
in_wb = gp.sjoin(buffered, large_wb, how="inner").join(
    large_drains.set_index("wbID").geometry.rename("drain"), on="wbID"
)
in_wb["snap_dist"] = in_wb.geometry.distance(gp.GeoSeries(in_wb.drain))

print(
    "Found {:,} dams within large waterbodies, snapped {:,} to drain points of those waterbodies".format(
        len(in_wb)
    )
)


# If ManualReview==2, these are NABD dams and potentially large, but not always correctly located on the network.
# If ManualReview==4, these were visually verified by SARP as being on network, but may
# be larger dams and > 100 m off channel.  Snap up to 250 meters for these.

to_snap = df.loc[
    ~(df.dropped | df.excluded), ["geometry", "HUC2", "id", "ManualReview"]
].copy()
to_snap["tolerance"] = SNAP_TOLERANCE
to_snap.loc[to_snap.ManualReview.isin([2, 4]), "tolerance"] = 250

print("Attempting to snap {:,} dams".format(len(to_snap)))

# # Snap to waterbody drain points
# snapped = snap_to_waterbody_points(to_snap)


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
