import os
from pathlib import Path
import warnings

import geopandas as gp
import pandas as pd
from pyogrio import read_dataframe, write_dataframe

from analysis.lib.geometry import neighborhoods


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
        pd.Series(raw.geometry.values, index=raw.index),
        tolerance=DUPLICATE_TOLERANCE,
    ).join(raw[["SARPID"]])
)
dup_100m_presnap = raw_groups.SARPID.unique()

groups = pd.DataFrame(
    neighborhoods(
        pd.Series(df.geometry.values, index=df.index),
        tolerance=DUPLICATE_TOLERANCE,
    )
).join(raw[["SARPID"]])
dup_100m_postsnap = groups.SARPID.unique()


df["dup100pre"] = df.SARPID.isin(dup_100m_presnap)
df["dup100post"] = df.SARPID.isin(dup_100m_postsnap)

df["snapped_wb"] = df.wbID.notnull()

qa = df.loc[
    df.dup100pre | df.dup100post | df.loop | (df.snap_dist > 150),
    [
        "geometry",
        "SARPID",
        "NIDID",
        "SourceID",
        "Source",
        "ManualReview",
        "Recon",
        "sizeclass",
        "loop",
        "snap_dist",
        "snapped_wb",
        "snap_log",
        "duplicate",
        "dup_log",
        "dup100pre",
        "dup100post",
    ],
]

write_dataframe(qa, qa_dir / "dams_for_review.fgb")
write_dataframe(qa, out_dir / "dams_for_review.shp")

### Also export snapping lines
snap_lines = read_dataframe(qa_dir / "dams_pre_snap_to_post_snap.fgb")
write_dataframe(snap_lines, out_dir / "dams_pre_snap_to_post_snap.shp")
