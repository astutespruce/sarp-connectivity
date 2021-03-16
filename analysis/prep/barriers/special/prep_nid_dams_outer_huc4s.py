from pathlib import Path
import warnings

import pygeos as pg
import geopandas as gp
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import (
    CRS,
    DAM_FS_COLS,
)

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
src_dir = data_dir / "barriers/source"

# note: drop date fields, they have bogus values anyway
nid = (
    read_dataframe(
        src_dir / "NID_2021.gdb",
    )
    .to_crs(CRS)
    .drop(columns=["EditorDate", "NextFollowUpDate"])
    .set_index("NIDID")
)
cols = [c for c in nid.columns if c in DAM_FS_COLS]
nid = nid[cols + ["geometry"]].rename(columns={"SARPUniqueID": "SARPID"})
nid["ManualReview"] = 0


# load previously snapped dams
prev = gp.read_feather(
    src_dir / "manually_snapped_dams.feather",
)
prev.ManualReview = prev.ManualReview.astype("uint8")
prev = prev.loc[prev.ManualReview.isin([4, 5, 13])].set_index("SARPID")


prev_nid = read_dataframe(
    src_dir / "Raw_Featureservice_SARPUniqueID.gdb",
    layer="Dams_Non_SARP_States_09052019",
)
cols = [c for c in prev_nid.columns if c in DAM_FS_COLS]
prev_nid = prev_nid[cols + ["geometry"]]
prev_nid.NIDID = prev_nid.NIDID.fillna("")
prev_nid = prev_nid.rename(
    columns={"Snap2018": "ManualReview", "SARPUniqueID": "SARPID"}
).set_index("NIDID")

# update prev_nid with snap dataset
prev_nid = prev_nid.join(
    prev[["ManualReview", "geometry"]], on="SARPID", rsuffix="_snap"
)
ix = prev_nid.geometry_snap.notnull()

prev_nid.loc[ix, "ManualReview"] = prev_nid.loc[ix].ManualReview_snap
prev_nid.loc[ix, "geometry"] = prev_nid.loc[ix].geometry_snap
prev_nid = prev_nid.drop(columns=["ManualReview_snap", "geometry_snap"])

# note: drop any from NABD that have duplicate NIDID
nabd = (
    read_dataframe(src_dir / "NABD_V2_beta/NABD_V2_beta.shp", columns=["NIDID"])
    .dropna(subset=["NIDID"])
    .drop_duplicates(subset=["NIDID"], keep=False)
    .to_crs(CRS)
    .set_index("NIDID")
)


### Select within outer HUC4s
huc4 = gp.read_feather(boundaries_dir / "outer_huc4.feather")

# select out NID within outer HUC4s
tree = pg.STRtree(nid.geometry.values.data)
left, right = tree.query_bulk(huc4.geometry.values.data, predicate="intersects")
ix = np.unique(right)
nid = nid.iloc[ix].copy()

# select out prev within outer HUC4s
tree = pg.STRtree(prev.geometry.values.data)
left, right = tree.query_bulk(huc4.geometry.values.data, predicate="intersects")
ix = np.unique(right)
prev = prev.iloc[ix].copy()

# select out prev NID within outer HUC4s
tree = pg.STRtree(prev_nid.geometry.values.data)
left, right = tree.query_bulk(huc4.geometry.values.data, predicate="intersects")
ix = np.unique(right)
prev_nid = prev_nid.iloc[ix].copy()


# select out NABD within outer HUC4s
tree = pg.STRtree(nabd.geometry.values.data)
left, right = tree.query_bulk(huc4.geometry.values.data, predicate="intersects")
ix = np.unique(right)
nabd = nabd.iloc[ix].copy()


# Keep records from the previous version that do not have NIDID; these were from
# NE Aquatic Connectivity project  (TODO: these will be updated separately in a future version)
# Also keep any that were manually reviewed
keep_prev = prev_nid.loc[
    (prev_nid.index == "") | (prev_nid.ManualReview.isin([4, 5]))
].copy()

# update the location in the NID based on NABD
nid = nid.join(nabd.loc[nabd.index.notnull()].geometry.rename("geometry_nabd"))
ix = nid.geometry_nabd.notnull()
nid.loc[ix, "geometry"] = nid.loc[ix].geometry_nabd
nid.loc[ix, "ManualReview"] = 2
nid = nid.drop(columns=["geometry_nabd"])

# drop any that were kept above because of manual review
nid = nid.loc[~nid.index.isin(keep_prev.index)].copy()


# Merge all together
df = (
    nid.reset_index()
    .append(keep_prev.reset_index(), ignore_index=True)
    .rename(
        columns={
            "Barrier_Name": "Name",
            "Other_Barrier_Name": "OtherName",
            "DB_Source": "Source",
            "Year_Completed": "Year",
            "ConstructionMaterial": "Construction",
            "PurposeCategory": "Purpose",
            "StructureCondition": "Condition",
            "PotentialFeasibility": "Feasibility",
        }
    )
)


### cleanup fields
df["SourceState"] = df.SARPID.str[:2]

for column in ("River", "NIDID", "Source", "SourceDBID", "Name", "OtherName"):
    df[column] = df[column].fillna("").str.strip()

for column in (
    "Construction",
    "Condition",
    "Purpose",
    "Recon",
    "PassageFacility",
    "BarrierStatus",
    "ManualReview",
):
    df[column] = df[column].fillna(0).astype("uint8")

for column in ("Year", "Height", "Length", "Feasibility"):
    df[column] = df[column].fillna(0).astype("uint16")

s = df.groupby("SARPID").size()
if s.max() > 1:
    raise ValueError(f"Multiple dams with same SARPID: {s[s > 1].index}")


df.to_feather(src_dir / "dams_outer_huc4.feather")
write_dataframe(df, src_dir / "dams_outer_huc4.gpkg")
