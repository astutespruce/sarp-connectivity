"""Helper script to export data in same structure as if downloaded from API"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import geopandas as gp
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
    STATE_TIER_FIELDS,
    unique,
)
from analysis.export.lib.domains import unpack_domains
from api.lib.tiers import calculate_tiers


EXTRA_FIELDS = ["ActiveList", "KeepOnActiveList"]

EXPORT_FIELDS = {
    "dams": DAM_EXPORT_FIELDS + EXTRA_FIELDS,
    "small_barriers": SB_EXPORT_FIELDS + EXTRA_FIELDS,
    "combined_barriers": unique(["BarrierType"] + DAM_EXPORT_FIELDS + SB_EXPORT_FIELDS + EXTRA_FIELDS),
    "largefish_barriers": unique(["BarrierType"] + DAM_EXPORT_FIELDS + SB_EXPORT_FIELDS + EXTRA_FIELDS),
    "smallfish_barriers": unique(["BarrierType"] + DAM_EXPORT_FIELDS + SB_EXPORT_FIELDS + EXTRA_FIELDS),
    "road_crossings": ROAD_CROSSING_EXPORT_FIELDS,
}

data_dir = Path("data")
master_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True)

#  one of "dams", "small_barriers", "combined_barriers", "road_crossings"
barrier_type = "combined_barriers"
suffix = ""  # use to set a filename suffix if filtering further
rank = False
state_rank = True  # true to calculate state ranks

df = pd.read_feather(api_dir / f"{barrier_type}.feather")

# bring in active list info
if barrier_type != "road_crossings":
    dams = pd.read_feather(master_dir / "dams.feather", columns=["id", "ActiveList", "KeepOnActiveList"])
    small_barriers = pd.read_feather(
        master_dir / "small_barriers.feather", columns=["id", "ActiveList", "KeepOnActiveList"]
    )
    active_list = pd.concat([dams, small_barriers], ignore_index=True).set_index("id")
    df = df.join(active_list, on="id")
    df["ActiveList"] = df.ActiveList.fillna(0).astype("uint8")
    df["KeepOnActiveList"] = df.KeepOnActiveList.fillna(0)


if state_rank or rank:
    table = pa.Table.from_pandas(df)
    to_rank = table.filter(pc.equal(table["Ranked"], True))


if state_rank:
    merged = []
    for state in to_rank["State"].unique():
        subset = to_rank.filter(pc.equal(to_rank["State"], state))
        tiers = calculate_tiers(subset).add_column(0, subset.schema.field("id"), subset["id"])
        merged.append(tiers)

    state_tiers = pa.concat_tables(merged).combine_chunks().to_pandas().set_index("id")
    state_tiers.rename(columns={col: f"State_{col}" for col in state_tiers.columns}, inplace=True)

    # join back to full data frame
    df = df.join(state_tiers, on="id")
    for col in STATE_TIER_FIELDS:
        df[col] = df[col].fillna(-1).astype("int8")

if rank:
    tiers = calculate_tiers(to_rank).add_column(0, to_rank.schema.field("id"), to_rank["id"])

    # join back to full data frame
    df = df.join(tiers.to_pandas().set_index("id"), on="id")
    for col in CUSTOM_TIER_FIELDS:
        df[col] = df[col].fillna(-1).astype("int8")


cols = [c for c in EXPORT_FIELDS[barrier_type] + ["upNetID", "downNetID"] if c in df.columns]

df = unpack_domains(df[cols])


# # to write as csv
# table = pa.Table.from_pandas(df)
# write_csv(table, out_dir / f"{barrier_type}{suffix}__{datetime.today().strftime('%m_%d_%Y')}.csv")


# Kat needs these as FGDB
df = gp.GeoDataFrame(df, geometry=shapely.points(df.lon.values, df.lat.values), crs="EPSG:4326")

write_dataframe(
    df,
    out_dir / f"{barrier_type}{suffix}__{datetime.today().strftime('%m_%d_%Y')}.gdb",
    driver="OpenFileGDB",
    # layer_options={"TARGET_ARCGIS_VERSION": "ARCGIS_PRO_3_2_OR_LATER"},
)
