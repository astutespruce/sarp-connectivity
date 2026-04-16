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
    CUSTOM_TIER_FIELDS,
    STATE_TIER_FIELDS,
    HUC8_TIER_FIELDS,
    SB_EXPORT_FIELDS,
    ROAD_CROSSING_EXPORT_FIELDS,
    verify_domains,
)
from analysis.constants import CRS
from api.lib.tiers import calculate_tiers
from analysis.lib.util import get_signed_dtype
from analysis.export.lib.domains import unpack_domains
from analysis.rank.lib.networks import get_network_results

data_dir = Path("data")
src_dir = data_dir / "barriers/source"
master_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True)

rename_cols = {
    "snapped": "Snapped",
    "excluded": "Excluded",
    "removed": "Removed",
    "invasive": "Invasive",
    "unranked": "Unranked",
    "loop": "OnLoop",
    "sizeclass": "StreamSizeClass",
    "CrossingCode_src": "CrossingCode_join",
}


states = ["ID"]
suffix = "_ID"


# NOTE: this only includes crossings that were snapped to the network
df = (
    pa.dataset.dataset(master_dir / "road_crossings.feather", format="feather")
    .to_table(filter=pc.is_in(pc.field("State"), pa.array(states)))
    .to_pandas()
    .rename(columns=rename_cols)
    .set_index("id")
)

df["geometry"] = shapely.from_wkb(df.geometry.values)
df = gp.GeoDataFrame(df, geometry="geometry", crs=CRS)

# fix missing unranked column
sb = (
    pd.read_feather(master_dir / "small_barriers.feather", columns=["SARPID", "unranked"])
    .set_index("SARPID")
    .unranked.rename("Unranked")
)
df = df.join(sb, on="SARPID")
df["Unranked"] = df.Unranked.fillna(0).astype("bool")


### Extract networks
crossing_networks = get_network_results(df, "road_crossings", state_ranks=True, huc8_ranks=True)
df = df.join(crossing_networks)

for col in ["HasNetwork", "Ranked"]:
    df[col] = df[col].fillna(0).astype("bool")

table = pa.Table.from_pandas(df.drop(columns=["geometry"]))
to_rank = table.filter(pc.equal(table["Ranked"], True))
tiers = calculate_tiers(to_rank).add_column(0, to_rank.schema.field("id"), to_rank["id"])

# join back to full data frame
df = df.join(tiers.to_pandas().set_index("id"), on="id")
for col in CUSTOM_TIER_FIELDS + STATE_TIER_FIELDS + HUC8_TIER_FIELDS:
    df[col] = df[col].fillna(-1).astype("int8")

# backfill missing values with 0 for classes and -1 for other network metrics
for col in crossing_networks.columns:
    if df[col].dtype == bool:
        continue

    orig_dtype = crossing_networks[col].dtype
    if col.endswith("Class"):
        df[col] = df[col].fillna(0).astype(orig_dtype)
    elif orig_dtype.name == "category":
        df[col] = df[col].fillna("")
    elif orig_dtype == "str":
        df[col] = df[col].fillna("")
    else:
        df[col] = df[col].fillna(-1).astype(get_signed_dtype(orig_dtype))


cols = [
    c
    for c in df.columns
    if c
    in set(
        SB_EXPORT_FIELDS
        + ROAD_CROSSING_EXPORT_FIELDS
        + CUSTOM_TIER_FIELDS
        + STATE_TIER_FIELDS
        + HUC8_TIER_FIELDS
        + ["geometry"]
    )
]

df = df[cols].copy()

df = gp.GeoDataFrame(df, geometry="geometry", crs=CRS)

verify_domains(df)
df = unpack_domains(df)

# to write as csv
table = pa.Table.from_pandas(df.drop(columns=["geometry"]))
write_csv(table, out_dir / f"W_road_crossings_{suffix}__{datetime.today().strftime('%m_%d_%Y')}.csv")

print("Exporting to FGDB")
filename = out_dir / f"road_crossings_{suffix}__{datetime.today().strftime('%m_%d_%Y')}.gdb"
write_dataframe(df, filename, layer="road_crossings", driver="OpenFileGDB")
