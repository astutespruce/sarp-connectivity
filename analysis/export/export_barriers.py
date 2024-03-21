"""Helper script to export data in same structure as if downloaded from API
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow as pa
from pyarrow.csv import write_csv

from api.constants import (
    DAM_EXPORT_FIELDS,
    SB_EXPORT_FIELDS,
    ROAD_CROSSING_EXPORT_FIELDS,
    unique,
)
from api.lib.tiers import calculate_tiers
from analysis.export.lib.domains import unpack_domains


EXPORT_FIELDS = {
    "dams": DAM_EXPORT_FIELDS,
    "small_barriers": SB_EXPORT_FIELDS,
    "combined_barriers": unique(["BarrierType"] + DAM_EXPORT_FIELDS + SB_EXPORT_FIELDS),
    "largefish_barriers": unique(["BarrierType"] + DAM_EXPORT_FIELDS + SB_EXPORT_FIELDS),
    "smallfish_barriers": unique(["BarrierType"] + DAM_EXPORT_FIELDS + SB_EXPORT_FIELDS),
    "road_crossings": ROAD_CROSSING_EXPORT_FIELDS,
}


data_dir = Path("data/api")
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True)

#  one of "dams", "small_barriers", "combined_barriers", "road_crossings"
barrier_type = "small_barriers"
suffix = ""  # use to set a filename suffix if filtering further

df = pd.read_feather(data_dir / f"{barrier_type}.feather")


cols = [c for c in EXPORT_FIELDS[barrier_type] + ["upNetID", "downNetID"] if c in df.columns]

df = unpack_domains(df[cols])

df = pa.Table.from_pandas(df)

write_csv(df, out_dir / f"{barrier_type}{suffix}__{datetime.today().strftime('%m_%d_%Y')}.csv")
