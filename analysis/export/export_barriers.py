"""Helper script to export data in same structure as if downloaded from API"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import geopandas as gp
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
from pyarrow.csv import write_csv
from pyogrio import write_dataframe
import shapely

from api.constants import (
    DAM_EXPORT_FIELDS,
    SB_EXPORT_FIELDS,
    ROAD_CROSSING_EXPORT_FIELDS,
    CUSTOM_TIER_FIELDS,
    unique,
)
from analysis.export.lib.domains import unpack_domains
from api.lib.tiers import calculate_tiers

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
barrier_type = "dams"
suffix = "_0406"  # use to set a filename suffix if filtering further
rank = True

df = pd.read_feather(data_dir / f"{barrier_type}.feather")

df = df.loc[df.HUC8.str.startswith("0406")].copy()

if rank:
    rank_cols = CUSTOM_TIER_FIELDS

    table = pa.Table.from_pandas(df)
    to_rank = table.filter(pc.equal(table["Ranked"], True))
    tiers = calculate_tiers(to_rank).add_column(0, to_rank.schema.field("id"), to_rank["id"])

    # join back to full data frame
    df = df.join(tiers.to_pandas().set_index("id"), on="id")
    for col in rank_cols:
        df[col] = df[col].fillna(-1).astype("int8")


cols = [c for c in EXPORT_FIELDS[barrier_type] + ["upNetID", "downNetID"] if c in df.columns]

df = unpack_domains(df[cols])

# df = pa.Table.from_pandas(df)
# write_csv(df, out_dir / f"{barrier_type}{suffix}__{datetime.today().strftime('%m_%d_%Y')}.csv")

# Kat needs these as FGDB
df = gp.GeoDataFrame(df, geometry=shapely.points(df.lon.values, df.lat.values), crs="EPSG:4326")


write_dataframe(
    df, out_dir / f"{barrier_type}{suffix}__{datetime.today().strftime('%m_%d_%Y')}.gdb", driver="OpenFileGDB"
)
