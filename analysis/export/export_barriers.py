"""Helper script to export data in same structure as if downloaded from API
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow as pa
from pyarrow.csv import write_csv

from api.constants import unpack_domains, DAM_EXPORT_FIELDS, SB_EXPORT_FIELDS, unique


EXPORT_FIELDS = {
    "dams": DAM_EXPORT_FIELDS,
    "small_barriers": SB_EXPORT_FIELDS,
    "dams_small_barriers": unique(
        ["BarrierType"] + DAM_EXPORT_FIELDS + SB_EXPORT_FIELDS
    ),
}


data_dir = Path("data/api")
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True)

barrier_type = "dams_small_barriers"  # "dams"  # "small_barriers"
suffix = ""  # use to set a filename suffix if filtering further

df = pd.read_feather(data_dir / f"{barrier_type}.feather")

cols = [c for c in EXPORT_FIELDS[barrier_type] if c in df.columns]

df = unpack_domains(df[cols])

df = pa.Table.from_pandas(df)

write_csv(
    df, out_dir / f"{barrier_type}{suffix}_{datetime.today().strftime('%m_%d_%Y')}.csv"
)
