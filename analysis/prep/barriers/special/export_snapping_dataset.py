import os
from pathlib import Path
import warnings

import pygeos as pg
import geopandas as gp
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS, DAM_FS_COLS, STATES, SARP_STATES

NONSARP_STATES = list(set(STATES) - set(SARP_STATES))

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


src_dir = Path("data/barriers/master")
out_dir = Path("/tmp/sarp")

if not out_dir.exists():
    os.makedirs(out_dir)

df = gp.read_feather(src_dir / "dams.feather")
df = df.loc[df.SourceState.isin(NONSARP_STATES)].copy()

df = df[
    [
        "geometry",
        "SARPID",
        "ManualReview",
        "NIDID",
        "Source",
        "Name",
        "OtherName",
        "River",
        "Purpose",
        "Construction",
        "Condition",
        "BarrierStatus",
        "Height",
        "Length",
        "dropped",
        "excluded",
        "duplicate",
        "log",
        "snap_log",
        "snap_dist",
        "snap_tolerance",
        "NHDPlusID",
        "StreamOrde",
        "sizeclass",
        "loop",
        "waterbody",
        "wbID",
    ]
]
