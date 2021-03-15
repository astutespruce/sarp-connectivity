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
cols = [c for c in nid.columns if c in DAM_FS_COLS if not c in {"Snap2018"}]
nid = nid[cols + ["geometry"]]

prev_nid = read_dataframe(
    src_dir / "Raw_Featureservice_SARPUniqueID.gdb",
    layer="Dams_Non_SARP_States_09052019",
)
cols = [c for c in prev_nid.columns if c in DAM_FS_COLS if not c in {"Snap2018"}]
prev_nid = prev_nid[cols + ["geometry"]]
prev_nid.NIDID = prev_nid.NIDID.fillna("")
prev_nid = prev_nid.set_index("NIDID")

nabd = (
    read_dataframe(src_dir / "NABD_V2_beta/NABD_V2_beta.shp", columns=["NIDID"])
    .dropna(subset=["NIDID"])
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
keep_prev = prev_nid.loc[prev_nid.index == ""].copy()


# update the location in the NID based on NABD
nid = nid.join(nabd.loc[nabd.index.notnull()].geometry.rename("geometry_nabd"))
ix = nid.geometry_nabd.notnull()
nid.loc[ix, "geometry"] = nid.loc[ix].geometry_nabd
nid = nid.drop(columns=["geometry_nabd"])


# Merge all together
df = (
    nid.reset_index()
    .append(keep_prev.reset_index(), ignore_index=True)
    .rename(
        columns={
            "SARPUniqueID": "SARPID",
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

### add missing fields
df["ManualReview"] = 0

### cleanup fields
for column in ("River", "NIDID", "Source", "SourceDBID", "Name", "OtherName"):
    df[column] = df[column].fillna("").str.strip()

for column in (
    "Construction",
    "Condition",
    "Purpose",
    "Recon",
    "PassageFacility",
    "BarrierStatus",
):
    df[column] = df[column].fillna(0).astype("uint8")

for column in ("Year", "Height", "Length", "Feasibility"):
    df[column] = df[column].fillna(0).astype("uint16")


df.to_feather(src_dir / "dams_outer_huc4.feather")
write_dataframe(df, src_dir / "dams_outer_huc4.gpkg")
