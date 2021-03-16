from pathlib import Path
import warnings

import pygeos as pg
import geopandas as gp
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS, DAM_FS_COLS, STATES, SARP_STATES

NONSARP_STATES = list(set(STATES) - set(SARP_STATES))

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
src_dir = data_dir / "barriers/source"

# load NABD dams (drop any that have duplicate NIDID)
nabd = (
    read_dataframe(src_dir / "NABD_V2_beta/NABD_V2_beta.shp", columns=["NIDID"])
    .dropna(subset=["NIDID"])
    .to_crs(CRS)
    .dropna(subset=["NIDID"])
    .drop_duplicates(subset=["NIDID"], keep=False)
    .set_index("NIDID")
)

# load previously snapped dams
prev = gp.read_feather(
    src_dir / "manually_snapped_dams.feather",
)
prev["SourceState"] = prev.SARPID.str[:2]
prev.ManualReview = prev.ManualReview.astype("uint8")
prev = prev.loc[
    prev.SourceState.isin(NONSARP_STATES) & prev.ManualReview.isin([4, 5, 13])
].copy()


# join prev to previous dataset outside SARP states to get SARP NIDID
# since SARPID is different for these same dams in the new dataset below
prev_nid = (
    read_dataframe(
        src_dir / "Raw_Featureservice_SARPUniqueID.gdb",
        layer="Dams_Non_SARP_States_09052019",
        columns=["NIDID", "SARPUniqueID"],
        read_geometry=False,
    )
    .rename(columns={"SARPUniqueID": "SARPID"})
    .dropna(subset=["NIDID"])
    .drop_duplicates(subset=["NIDID"], keep=False)
    .set_index("SARPID")
)

prev = prev.join(prev_nid, on="SARPID", how="inner").set_index("NIDID")


# load latest dams downloaded from state-level feature services
# limited to non-SARP states
df = gp.read_feather(src_dir / "sarp_dams.feather")
df = df.loc[df.SourceState.isin(NONSARP_STATES)].drop_duplicates(
    subset=["NIDID"], keep=False
)
df.ManualReview = df.ManualReview.fillna(0).astype("uint8")


df = df.join(
    prev[["ManualReview", "geometry"]],
    on="NIDID",
    rsuffix="_prev",
).join(nabd.geometry.rename("nabd_geometry"), on="NIDID")

# if previously reviewed, use that directly
ix = (df.ManualReview == 0) & df.geometry_prev.notnull()
df.loc[ix, "ManualReview"] = df.loc[ix].ManualReview_prev
df.loc[ix, "geometry"] = df.loc[ix].geometry_prev

# update location from NABD if within 5,000 meters
ix = (df.ManualReview == 0) & (
    pg.distance(df.geometry.values.data, df.nabd_geometry.values.data) <= 5000
)

df.loc[ix, "ManualReview"] = 2
df.loc[ix, "geometry"] = df.loc[ix].nabd_geometry

df = df.drop(columns=["ManualReview_prev", "geometry_prev", "nabd_geometry"])

# drop anything that wasn't snapped
df = df.loc[df.ManualReview > 0].copy()
df.ManualReview = df.ManualReview.astype("uint8")

df.to_feather(src_dir / "snapped_outside_sarp_2021.feather")
write_dataframe(df, src_dir / "snapped_outside_sarp_2021.gpkg")
