import os
from pathlib import Path
import warnings

import pygeos as pg
import geopandas as gp
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS, STATES

PREVIOUS_STATES = {
    "AL",
    "AR",
    "AZ",
    "CO",
    "FL",
    "GA",
    "IA",
    "KS",
    "KY",
    "LA",
    "MO",
    "MS",
    "MT",
    "NC",
    "ND",
    "NE",
    "NM",
    "OK",
    "PR",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VA",
    "WY",
}

NEW_STATES = sorted(set(STATES) - PREVIOUS_STATES)


data_dir = Path("data")
src_dir = data_dir / "barriers/source"
out_dir = Path("/tmp/sarp")

if not out_dir.exists():
    os.makedirs(out_dir)


### Create initial version of snapping dataset for states outside previous region (SE + R2 / R6)

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
    prev.SourceState.isin(NEW_STATES) & prev.ManualReview.isin([4, 5, 13])
].copy()


# load latest dams downloaded from state-level feature services
# limited to non-SARP states
df = gp.read_feather(src_dir / "sarp_dams.feather")
df = df.loc[df.SourceState.isin(NEW_STATES)].drop_duplicates(
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

df.to_feather(src_dir / "snapped_outside_prev_v1.feather")
write_dataframe(df, src_dir / "snapped_outside_prev_v1.fgb")
