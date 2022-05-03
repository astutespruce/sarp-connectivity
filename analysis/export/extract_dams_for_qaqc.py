import os
from pathlib import Path
from time import time
import warnings

import geopandas as gp
import pandas as pd
import pygeos as pg
import numpy as np
from pyogrio import write_dataframe

from analysis.lib.geometry import neighborhoods


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

# Per guidance from Kat: this is set intentionally to 100m instead of 10m, to guide
# QAQC
DUPLICATE_TOLERANCE = 100

qa_dir = Path("data/barriers/qa")
out_dir = Path("/tmp/sarp")

if not out_dir.exists():
    os.makedirs(out_dir)

raw = gp.read_feather("data/barriers/qa/dams_raw.feather").set_index("id")
df = gp.read_feather("data/barriers/master/dams.feather").set_index("id")


### Identify any that are duplicates within 100m before or after snapping
raw_groups = pd.DataFrame(
    neighborhoods(
        pd.Series(raw.geometry.values.data, index=raw.index),
        tolerance=DUPLICATE_TOLERANCE,
    ).join(raw[["SARPID"]])
)
dup_100m_presnap = raw_groups.SARPID.unique()

groups = pd.DataFrame(
    neighborhoods(
        pd.Series(df.geometry.values.data, index=df.index),
        tolerance=DUPLICATE_TOLERANCE,
    )
).join(raw[["SARPID"]])
dup_100m_postsnap = groups.SARPID.unique()


df["dup100mpre"] = df.SARPID.isin(dup_100m_presnap)
df["dup100mpost"] = df.SARPID.isin(dup_100m_postsnap)

df["snapped_wb"] = df.wbID.notnull()

qa = df.loc[
    df.dup100mpre | df.dup100mpost | df.loop | (df.snap_dist > 150),
    [
        "geometry",
        "SARPID",
        "NIDID",
        "SourceDBID",
        "Source",
        "ManualReview",
        "Recon",
        "sizeclass",
        "snap_dist",
        "snapped_wb",
        "snap_log",
        "duplicate",
        "dup_log",
        "dup100mpre",
        "dup100mpost",
    ],
]

write_dataframe(qa, qa_dir / "dams_for_review.fgb")
write_dataframe(qa, out_dir / "dams_for_review.shp")
