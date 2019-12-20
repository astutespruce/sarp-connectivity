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

from analysis.prep.barriers.lib.points import nearest, near, neighborhoods, connect_points
from analysis.pygeos_compat import to_pygeos, from_pygeos

pd.options.display.max_rows = 250


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

from analysis.prep.barriers.lib.snap import (
    snap_to_waterbody_points,
    snap_by_region,
    update_from_snapped,
)
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins


### Custom tolerance values for dams
# Dams within 50 meters are considered duplicates
DUPLICATE_TOLERANCE = 50  # TODO: verify this is producing good results
# Snap barriers by 150 meters
SNAP_TOLERANCE = 150  # TODO: verify this is producing good results

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

### Add tracking fields
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

# snapped: records that snapped to the aquatic network and ready for network analysis
df["snapped"] = False
# df["snap_type"] = ""  # TODO: "NHD dam",  etc
df["snap_ref_id"] = np.nan  # id of feature from snap type this was snapped to
df["snap_dist"] = np.nan
df["lineID"] = np.nan
df["wbID"] = np.nan

# save a log of notes about why or how something was dropped, snapped, etc
df["log"] = ""


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
ix = df.Name.str.count("Estimated Dam") > 0
df.loc[ix, "ManualReview"] = 20  # indicates estimated dam

# Replace estimated dam names if another name is available
ix = ix & (df.OtherName.str.len() > 0)
df.loc[ix, "Name"] = df.loc[ix].OtherName


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
df.loc[drop_idx, "log"] = "dropped:  name includes dike and not dam"

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


# FIXME:
# to_geofeather(df.reset_index(drop=True), "/tmp/pre-snap.feather")

### in progress 12/20
# df = from_geofeather("/tmp/pre-snap.feather").set_index("id", drop=False)

# IMPORTANT: do not snap manually reviewed, off-network dams!
to_snap = df.loc[df.ManualReview != 5].copy()
# NOTE: temporary, convert geoms to pygeos
to_snap["geometry"] = to_pygeos(to_snap.geometry)

# Save original locations so we can map the snap line between original and new locations
original_locations = to_snap.copy()

print("Snapping to NHD dams...")
# NOTE: id is not unique for points
nhd_dams_poly = (
    from_geofeather_as_pygeos(nhd_dir / "merged" / "nhd_dams_poly.feather")
    .rename(columns={"id": "damID"})
    .set_index("damID")
    .drop(columns=["index"], errors="ignore")
)
nhd_dams = (
    from_geofeather_as_pygeos(nhd_dir / "merged" / "nhd_dams_pt.feather")
    .rename(columns={"id": "damID"})
    .set_index("damID")
)
# set nulls back to na
nhd_dams.wbID = nhd_dams.wbID.replace(-1, np.nan)


### Find dams that are really close (50m) to NHD dam polygons
# Those that have multiple dams nearby are usually part of a dam complex
snap_start = time()
nhd_dam_distance = 50
near_nhd = nearest(to_snap.geometry, nhd_dams_poly.geometry, nhd_dam_distance)[
    ["damID"]
]

# snap to nearest dam point for that dam (some are > 1 km away)
# NOTE: this will multiple entries for some dams
near_nhd = near_nhd.join(to_snap.geometry.rename("source_pt")).join(
    nhd_dams, on="damID"
)
near_nhd["snap_dist"] = pg.distance(near_nhd.geometry, near_nhd.source_pt)
near_nhd = (
    near_nhd.reset_index().sort_values(by=["id", "snap_dist"]).groupby("id").first()
)

ix = near_nhd.index
df.loc[ix, "snapped"] = True
df.loc[ix, "geometry"] = from_pygeos(near_nhd.geometry)
df.loc[ix, "snap_dist"] = near_nhd.snap_dist
df.loc[ix, "snap_ref_id"] = near_nhd.damID
df.loc[ix, "lineID"] = near_nhd.lineID
df.loc[ix, "wbID"] = near_nhd.wbID
df.loc[ix, "log"] = "snapped: within {}m of NHD dam polygon".format(nhd_dam_distance)

to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()
print(
    "Snapped {:,} dams to NHD dam polygons in {:.2f}s".format(
        len(ix), time() - snap_start
    )
)

### Find dams that are close (within snapping tolerance) of NHD dam points
snap_start = time()
tmp = nhd_dams.reset_index()  # reset index so we have unique index to join on
near_nhd = nearest(to_snap.geometry, tmp.geometry, SNAP_TOLERANCE).rename(
    columns={"distance": "snap_dist"}
)
near_nhd = near_nhd.join(to_snap.geometry.rename("source_pt")).join(
    tmp, on="index_right"
)
near_nhd = (
    near_nhd.reset_index().sort_values(by=["id", "snap_dist"]).groupby("id").first()
)

ix = near_nhd.index
df.loc[ix, "snapped"] = True
df.loc[ix, "geometry"] = from_pygeos(near_nhd.geometry)
df.loc[ix, "snap_dist"] = near_nhd.snap_dist
df.loc[ix, "snap_ref_id"] = near_nhd.damID
df.loc[ix, "lineID"] = near_nhd.lineID
df.loc[ix, "wbID"] = near_nhd.wbID
df.loc[
    ix, "log"
] = "snapped: within {}m of NHD dam point but >{}m from NHD dam polygon".format(
    SNAP_TOLERANCE, nhd_dam_distance
)

to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()
print(
    "Snapped {:,} dams to NHD dam points in {:.2f}s".format(
        len(ix), time() - snap_start
    )
)

### TODO: identify any NHD dam points that didn't get claimed  (need to do this after snapping others)


### Attempt to snap to waterbody drain points for major waterbodies
# Use larger tolerance for larger waterbodies
print("Snapping to waterbodies and drain points..")
wb = from_geofeather_as_pygeos(nhd_dir / "merged" / "waterbodies.feather").set_index(
    "wbID"
)
drains = from_geofeather_as_pygeos(
    nhd_dir / "merged" / "waterbody_drain_points.feather"
).set_index("id")

### First pass - find the dams that are contained by waterbodies
# have to do this in geopandas since it performs better than pygeos
# until pygeos has prepared geoms
d = to_gdf(to_snap, crs=CRS)
wbd = to_gdf(wb, crs=CRS)
d.sindex
wbd.sindex
contained_start = time()
in_wb = gp.sjoin(d, wbd, how="inner").index_right.rename("wbID")
print(
    "Found {:,} dams in waterbodies in {:.2f}s".format(
        len(in_wb), time() - contained_start
    )
)

print("Finding nearest drain points...")
# join back to pygeos geoms and join to drains
# NOTE: this may produce multiple drains for some waterbodies
in_wb = (
    pd.DataFrame(in_wb)
    .join(to_snap.geometry)
    .join(
        drains.reset_index()
        .set_index("wbID")[["geometry", "id", "lineID"]]
        .rename(columns={"id": "drainID", "geometry": "drain"}),
        on="wbID",
    )
    .dropna(subset=["drain"])
)
in_wb["snap_dist"] = pg.distance(in_wb.geometry, in_wb.drain)

# drop any that are > 500 m away, these aren't useful
in_wb = in_wb.loc[in_wb.snap_dist <= 500].copy()

# take the closest drain point
in_wb = (
    in_wb.reset_index().sort_values(by=["index", "snap_dist"]).groupby("index").first()
)

# Any that are within the snap tolerance just snap to that drain
close_enough = in_wb.loc[in_wb.snap_dist <= SNAP_TOLERANCE]
ix = close_enough.index
df.loc[ix, "snapped"] = True
df.loc[ix, "geometry"] = from_pygeos(close_enough.drain)
df.loc[ix, "snap_dist"] = close_enough.snap_dist
df.loc[ix, "snap_ref_id"] = close_enough.drainID
df.loc[ix, "lineID"] = close_enough.lineID
df.loc[ix, "wbID"] = close_enough.wbID
df.loc[
    ix, "log"
] = "snapped: within {}m of drain point for waterbody that contains this dam".format(
    SNAP_TOLERANCE
)

to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

print(
    "Found {:,} dams within {}m of the drain points for their waterbody".format(
        len(ix), SNAP_TOLERANCE
    )
)


# Any that are > 250 m away are suspect if they are close to edges of waterbodies
# (some are clearly well within waterbodies)
# Spot-checked these; above this level things were usually snapping incorrectly
further = in_wb.loc[in_wb.snap_dist > SNAP_TOLERANCE].copy()


### Checkpoint
tmp = df.loc[df.snapped, ["geometry", "Name","snapped", "snap_dist", "log"]].join(
    original_locations.geometry.rename("orig_pt")
)
tmp['new_pt'] = to_pygeos(tmp.geometry)
tmp["geometry"] = connect_points(tmp.new_pt, tmp.orig_pt)

to_gpkg(tmp.drop(columns=['new_pt', 'orig_pt']).reset_index(drop=True), '/tmp/snap_lines', crs=CRS)
to_gpgk(tmp.drop(columns=['geometry', 'new_pt']).rename(columns={'orig_pt': 'geometry'}).reset_index(drop=True), '/tmp/pre_snap', crs=CRS)
to_gpgk(tmp.drop(columns=['geometry', 'orig_pt']).rename(columns={'new_pt': 'geometry'}).reset_index(drop=True), '/tmp/post_snap', crs=CRS)


# check for any that have drain points for other waterbodies that are closer (within 100m)
# sometimes there are dams between adjacent waterbodies, and the dam point is in a
# waterbody when it should be between them.
ix = in_wb.snap_dist > 250

print("Found {:,} dams > 250m away from their waterbody's drain".format(ix.sum()))

# Find that are close to the edge of their waterbody
tmp = in_wb.loc[ix].join(pg.get_exterior_ring(wb.geometry).rename("wb_bnd"), on="wbID")
tmp["bnd_dist"] = pg.distance(tmp.geometry, tmp.wb_bnd)

# If within 30m of an edge of a waterbody but far away from a drain
# these points are suspicious; see if there is an adjacent drain closer
ix = tmp.bnd_dist <= 30
print(
    "Of these, {:,} dams are <= 30m from the edge of their waterbody".format(ix.sum())
)
nearest_drain = find_nearest(tmp.loc[ix].geometry, drains.geometry, 100)

print(
    "Found {:,} of these that are closer to the drain of an adjacent waterbody".format(
        len(nearest_drain)
    )
)

# Still in progress
# TODO: if found nearest in suspect ones, snap to nearby
# otherwise drop suspect ones


ids = in_wb.loc[nearest_drain.index].wbID.unique()
t = in_wb.loc[nearest_drain.index].join(wb.geometry.rename("wb"), on="wbID")


# TODO: may need to do a mini-network analysis for these to make sure we don't jump networks?


### TODO: only for those that don't have a closer drain point
ix = in_wb.index
df.loc[ix, "geometry"] = in_wb.drain
df.loc[ix, "snapped"] = True
df.loc[ix, "snap_dist"] = in_wb.snap_dist
df.loc[ix, "snap_type"] = "in waterbody, snapped drain"
df.loc[ix, "snap_ref_id"] = in_wb.drainID
df.loc[ix, "wbID"] = in_wb.wbID


# first pass filter, find all combos of buffers around waterbody drains and dams
# buffer the drains, there are fewer of them
wb_start = time()
buffered = pg.buffer(drains.geometry, 1000)
joined = sjoin(buffered, to_snap.geometry.head())
print("Elapsed {:.2f}s".format(time() - wb_start))


contained_start = time()
# in_wb = (
#     sjoin(wb.geometry, to_snap.geometry, how="left")
#     .rename("id")
#     .reset_index()
#     .drop_duplicates()
#     .dropna(subset=["id"])
#     .astype("uint32")
#     .set_index("id")
# )
print("Elapsed {:.2f}s".format(time() - contained_start))


# Find nearest waterbodies - if the dam is in the waterbody it should be the closest waterbody


# NOTE: have to do this from the waterbody side and invert
buffered = pg.buffer(to_snap.geometry, 30)
nearest_wb = (
    sjoin(wb.geometry, buffered, how="left")
    .rename("id")
    .reset_index()
    .drop_duplicates()
    .dropna(subset=["id"])
    .astype("uint32")
    .set_index("id")
)


# nearest_wb = to_snap[["geometry"]].join(nearest_wb, how="left")
print("Elapsed {:.2f}s".format(time() - snap_start))


# nearest_wb = (
#     sjoin(wb.geometry.head(100), buffered.head(100), how="left")
#     .rename("id")
#     .reset_index()
#     .drop_duplicates()
#     .dropna(subset=["id"])
#     .astype("uint32")
#     .set_index("id")
# )


# nearest_wb = find_nearest(wb.geometry, df.geometry, 30, how="left").rename()
print("Elapsed {:.2f}s".format(time() - snap_start))
# print(
#     "Snapped {:,} dams to NHD dams in {:.2f}s".format(
#         len(nearest_dams), time() - snap_start
#     )
# )

### end in progress 12/15


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
