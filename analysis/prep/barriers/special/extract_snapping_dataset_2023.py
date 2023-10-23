import os
from pathlib import Path

import geopandas as gp
from pyogrio import write_dataframe


data_dir = Path("data")
# last run with source data on 10/20/2023
src_dir = data_dir / "barriers/source"
out_dir = Path("/tmp/sarp")

if not out_dir.exists():
    os.makedirs(out_dir)


### Read in source inventory
src = gp.read_feather(
    src_dir / "sarp_dams.feather",
    columns=["geometry", "SARPID", "NIDID", "ManualReview", "Recon"],
).set_index("SARPID")
src.ManualReview = src.ManualReview.fillna(0).astype("uint8")

# Fix Recon value that wasn't assigned to ManualReview
# these are invasive species barriers
src.loc[(src.Recon == 16) & (src.ManualReview == 0), "ManualReview"] = 10

# only keep source points with manual review >= 2 (0,1 not useful; 10,20,21 do not indicate review of coordinates)
src = src.loc[~src.ManualReview.isin([0, 1, 7, 9, 10, 20, 21])].copy()

### read manually snapped dams
snapped_df = gp.read_feather(
    src_dir / "manually_snapped_dams.feather",
    columns=[
        "geometry",
        "SARPID",
        "ManualReview",
        "dropped",
        "excluded",
        "duplicate",
        "snapped",
        "Editor",
        "EditDate",
    ],
)

# Don't pull across those that were not manually snapped or are missing key fields
# 7,9: assumed offstream but attempt to snap
# 0,1,10,20,21: do not indicate review of coordinates
snapped_df = snapped_df.loc[
    ~snapped_df.ManualReview.isin([0, 1, 7, 9, 10, 20, 21])
].set_index("SARPID")

for col in ["dropped", "excluded", "duplicate", "snapped"]:
    snapped_df[col] = (
        snapped_df[col].map({"True": True, "False": False}).astype("bool_")
    )

# Drop any that were marked as in correct location, but were not previously snapped;
# these are errors
ix = (snapped_df.ManualReview == 13) & ~snapped_df.snapped
if ix.sum():
    print(
        f"Dropping {ix.sum():,} dams marked as in correct location but were not previously snapped (errors)"
    )
    snapped_df = snapped_df.loc[~ix].copy()

# Drop any that were marked as duplicates manually and also automatically
ix = (snapped_df.ManualReview == 11) & snapped_df.duplicate
snapped_df = snapped_df.loc[~ix].copy()
print(
    f"Dropping {ix.sum():,} dams that were marked as duplicates both manually and automatically"
)

### extract latest outputs produced by prep_dams.py
df = gp.read_feather(
    data_dir / "barriers/master/dams.feather",
    columns=[
        "geometry",  # this is auto-snapped geometry
        "SARPID",
        "NIDID",
        "State",
        "HUC2",
        "ManualReview",
        "removed",
        "YearRemoved",
        "dropped",
        "excluded",
        "duplicate",
        "snapped",
        "snap_dist",
        "snap_log",
        "loop",
        "offnetwork_flowline",
        "Editor",
        "EditDate",
    ],
).set_index("SARPID")

### Join datasets together
# Merge as follows:
# start from latest results (autosnapped)
# any that were marked as manually reviewed in the source data, use that coordinate instead
# override with coordinates from snapped (reviewed) dataset


df = df.join(
    src[["geometry", "ManualReview"]].rename(
        columns={"geometry": "src_pt", "ManualReview": "src_ManualReview"}
    )
).join(
    snapped_df[["geometry", "ManualReview"]].rename(
        columns={"geometry": "reviewed_pt", "ManualReview": "reviewed_ManualReview"}
    )
)

# mark any as snapped / not
df["cur_pt_src"] = "not snapped"
df.loc[df.snapped, "cur_pt_src"] = "autosnapped pt"

# any that were manually reviewed in source, use that original point and manual review
# (note: these may be overridden again by manually reviewed dams in snapping dataset)
ix = df.src_ManualReview.notnull() & (df.src_ManualReview != 0)
df.loc[ix, "geometry"] = df.loc[ix].src_pt
df.loc[ix, "ManualReview"] = df.loc[ix].src_ManualReview
df.loc[ix, "cur_pt_src"] = "manually reviewed (national dataset)"

# any that were manually reviewed in snapping dataset, use that coordinate and manual review
ix = df.reviewed_ManualReview.notnull() & (df.reviewed_ManualReview != 0)
df.loc[ix, "geometry"] = df.loc[ix].reviewed_pt
df.loc[ix, "ManualReview"] = df.loc[ix].reviewed_ManualReview
df.loc[ix, "cur_pt_src"] = "manually reviewed (snapping dataset)"

df = df.drop(
    columns=["src_pt", "reviewed_pt", "src_ManualReview", "reviewed_ManualReview"]
).reset_index()

df.to_feather("data/barriers/qa/snapping_dataset_2023.feather")

write_dataframe(df, out_dir / "snapping_dataset_2023.gdb", driver="OpenFileGDB")
