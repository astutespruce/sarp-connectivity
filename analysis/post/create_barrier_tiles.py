from pathlib import Path
import subprocess
from time import time

import pandas as pd
import pyarrow as pa
from pyarrow.csv import write_csv

from analysis.lib.util import pack_bits
from api.constants import (
    DAM_TILE_FILTER_FIELDS,
    DAM_TILE_FIELDS,
    UNIT_FIELDS,
    METRIC_FIELDS,
    SB_TILE_FILTER_FIELDS,
    SB_TILE_FIELDS,
    WF_TILE_FIELDS,
    TIER_FIELDS,
    STATE_TIER_PACK_BITS,
    UNIT_FIELDS,
    SB_PACK_BITS,
)
from analysis.lib.util import pack_bits
from analysis.post.lib.tiles import get_col_types

# unit fields that can be dropped for sets of barriers that are not filtered
DROP_UNIT_FIELDS = [
    f for f in UNIT_FIELDS if not f in {"State", "County", "HUC8", "HUC12"}
]

# FIXME:
MAX_ZOOM = 10  # 16


def to_lowercase(df):
    return df.rename(
        columns={
            k: k.lower()
            for k in df.columns
            if k not in UNIT_FIELDS + ["Subbasin", "Subwatershed"]
        }
    )


barriers_dir = Path("data/barriers/master")
results_dir = Path("data/barriers/networks")
out_dir = Path("tiles")
tmp_dir = Path("/tmp")

# select zoom_level, tile_column, tile_row, length(tile_data) / 1024 as size from tiles order by size desc;
tippecanoe_args = [
    "tippecanoe",
    "-f",
    "-pg",
    "--no-tile-size-limit",
    "--drop-densest-as-needed",
    "--coalesce-densest-as-needed",
    "--hilbert",
    "-ai",
]

tilejoin_args = [
    "tile-join",
    "-f",
    "-pg",
    "--no-tile-size-limit",
    "--attribution",
    '<a href="https://southeastaquatics.net/">Southeast Aquatic Resources Partnership</>',
]

start = time()

### Create dams tiles
df = (
    pd.read_feather(
        results_dir / "dams.feather",
        columns=["id"] + DAM_TILE_FIELDS,
    )
    .rename(columns={"COUNTYFIPS": "County"})
    .sort_values(by=["TotDASqKm"], ascending=False)
)


# Set string field nulls to blank strings
str_cols = df.dtypes.loc[df.dtypes == "object"].index
for col in str_cols:
    df[col] = df[col].fillna("").str.replace('"', "'")


# Update boolean fields so that they are output to CSV correctly
# NOTE: these must be manually set for tippecanoe via bool_cols param to get_col_types
# NOTE: none of the fields used for filtering can be bool; fails on frontend
for col in ["Trout"]:
    df[col] = df[col].astype("uint8")

# Combine string fields
df["SARPIDName"] = df.SARPID + "|" + df.Name

df = df.drop(
    columns=[
        "SARPID",
        "Name",
    ]
)


### Create tiles for ranked dams with networks for low zooms

# Below zoom 8, we only need filter fields; dams are not selectable so we
# can't show additional details
# NOTE: only show dams on flowlines with >= 1 km2 drainage area
tmp = to_lowercase(
    df.loc[df.Ranked & (df.TotDASqKm >= 1)][["id"] + DAM_TILE_FILTER_FIELDS]
)

print(f"Creating tiles for {len(tmp):,} ranked dams with networks for zooms 2-7")

csv_filename = tmp_dir / "dams_lt_z8.csv"
mbtiles_filename = tmp_dir / "dams_lt_z8.mbtiles"
mbtiles_files = [mbtiles_filename]
write_csv(pa.Table.from_pandas(tmp.reset_index(drop=True)), csv_filename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z2", "-z7", "-r1.5", "-g1.5", "-B5"]
    + ["-l", "ranked_dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(tmp)
    + [str(csv_filename)]
)
ret.check_returncode()


### Create tiles for ranked dams with networks
df = df.drop(columns=["TotDASqKm"])

ranked_dams = df.loc[df.Ranked].drop(columns=["Ranked", "HasNetwork"])
print(f"Creating tiles for {len(ranked_dams):,} ranked dams with networks")


# Pack tier fields
ranked_dams["StateTiers"] = pack_bits(ranked_dams, STATE_TIER_PACK_BITS)
ranked_dams = ranked_dams.drop(columns=TIER_FIELDS)
ranked_dams = to_lowercase(ranked_dams)


csv_filename = tmp_dir / "ranked_dams.csv"
mbtiles_filename = tmp_dir / "ranked_dams.mbtiles"
mbtiles_files.append(mbtiles_filename)
write_csv(pa.Table.from_pandas(ranked_dams.reset_index(drop=True)), csv_filename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
    + ["-l", "ranked_dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(ranked_dams)
    + [str(csv_filename)]
)
ret.check_returncode()


### Create tiles for unranked dams with networks
unranked_dams = df.loc[df.HasNetwork & (~df.Ranked)].drop(
    columns=[
        "Ranked",
        "HasNetwork",
        "GainMilesClass",
        "TESppClass",
        "StateSGCNSppClass",
        "StreamOrderClass",
        "StreamSizeClass",
        "PercentAlteredClass",
        "WaterbodySizeClass",
        "HeightClass",
        "PassageFacilityClass",
    ]
    + DROP_UNIT_FIELDS
    + TIER_FIELDS,
    errors="ignore",
)
print(f"Creating tiles for {len(unranked_dams):,} unranked dams with networks")

unranked_dams = to_lowercase(unranked_dams)

csv_filename = tmp_dir / "unranked_dams.csv"
mbtiles_filename = tmp_dir / "unranked_dams.mbtiles"
mbtiles_files.append(mbtiles_filename)
write_csv(pa.Table.from_pandas(unranked_dams.reset_index(drop=True)), csv_filename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
    + ["-l", "unranked_dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(unranked_dams)
    + [str(csv_filename)]
)
ret.check_returncode()


### Create tiles for dams without networks (these are never ranked)
print("Creating tiles for dams without networks")

# Drop metrics, tiers, and units used only for filtering
offnetwork_dams = (
    df.loc[~df.HasNetwork]
    .drop(
        columns=[
            "HasNetwork",
            "Ranked",
            "GainMilesClass",
            "TESppClass",
            "StateSGCNSppClass",
            "StreamOrderClass",
            "StreamSizeClass",
            "Intermittent",
            "PercentAlteredClass",
            "Waterbody",
            "WaterbodyKM2",
            "WaterbodySizeClass",
            "HeightClass",
            "PassageFacilityClass",
            "NHDPlusID",
            "upNetID",
            "downNetID",
        ]
        + DROP_UNIT_FIELDS
        + METRIC_FIELDS
        + TIER_FIELDS,
        errors="ignore",
    )
    .reset_index(drop=True)
)

offnetwork_dams = to_lowercase(offnetwork_dams)


csv_filename = tmp_dir / "offnetwork_dams.csv"
mbtiles_filename = tmp_dir / "offnetwork_dams.mbtiles"
mbtiles_files.append(mbtiles_filename)
write_csv(pa.Table.from_pandas(offnetwork_dams), csv_filename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z9", f"-z{MAX_ZOOM}", "-B10"]
    + ["-l", "offnetwork_dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(
        offnetwork_dams,
    )
    + [str(csv_filename)]
)
ret.check_returncode()


print("Joining dams tilesets")
mbtiles_filename = out_dir / "dams.mbtiles"
ret = subprocess.run(
    tilejoin_args + ["-o", str(mbtiles_filename)] + [str(f) for f in mbtiles_files]
)

print(f"Created dam tiles in {time() - start:,.2f}s")

####################################################################
### Create small barrier tiles
start = time()
df = (
    pd.read_feather(
        results_dir / "small_barriers.feather", columns=["id"] + SB_TILE_FIELDS
    )
    .rename(columns={"COUNTYFIPS": "County"})
    .sort_values(by=["TotDASqKm"], ascending=False)
    .drop(columns=["TotDASqKm"])
)


# Set string field nulls to blank strings
str_cols = df.dtypes.loc[df.dtypes == "object"].index
for col in str_cols:
    df[col] = df[col].fillna("").str.replace('"', "'")


# Update boolean fields so that they are output to CSV correctly
for col in ["Trout"]:
    df[col] = df[col].astype("uint8")


df["SARPIDName"] = df.SARPID + "|" + df.Name
df = df.drop(
    columns=[
        "SARPID",
        "Name",
    ]
)


### Create tiles for ranked small barriers at low zooms
# Below zoom 8, we only need filter fields

mbtiles_filename = tmp_dir / "small_barriers_lt_z8.mbtiles"
mbtiles_files = [mbtiles_filename]

tmp = to_lowercase(df.loc[df.Ranked][["id"] + SB_TILE_FILTER_FIELDS])
print(
    f"Creating tiles for {len(tmp):,} ranked small barriers with networks for zooms 2-7"
)
csv_filename = tmp_dir / "small_barriers_lt_z8.csv"
write_csv(pa.Table.from_pandas(tmp.reset_index(drop=True)), csv_filename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z2", "-z7", "-r1.5", "-g1.5", "-B5"]
    + ["-l", "ranked_small_barriers"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(tmp)
    + [str(csv_filename)]
)
ret.check_returncode()


### Create tiles for ranked small barriers

ranked_barriers = df.loc[df.Ranked].drop(columns=["Ranked", "HasNetwork"])
print(
    f"Creating tiles for {len(ranked_barriers):,} ranked small barriers with networks"
)

# Pack tier fields
ranked_barriers["StateTiers"] = pack_bits(ranked_barriers, STATE_TIER_PACK_BITS)
ranked_barriers = ranked_barriers.drop(columns=TIER_FIELDS)
ranked_barriers = to_lowercase(ranked_barriers)


mbtiles_filename = tmp_dir / "ranked_small_barriers.mbtiles"
mbtiles_files.append(mbtiles_filename)

csv_filename = tmp_dir / "ranked_small_barriers.csv"
write_csv(pa.Table.from_pandas(ranked_barriers.reset_index(drop=True)), csv_filename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
    + ["-l", "ranked_small_barriers"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(ranked_barriers)
    + [str(csv_filename)],
)
ret.check_returncode()

### Create tiles for unranked barriers with networks
unranked_barriers = df.loc[df.HasNetwork & (~df.Ranked)].drop(
    columns=[
        "Ranked",
        "HasNetwork",
        "GainMilesClass",
        "TESppClass",
        "StateSGCNSppClass",
        "StreamOrderClass",
        "StreamSizeClass",
        "PercentAlteredClass",
    ]
    + DROP_UNIT_FIELDS
    + TIER_FIELDS,
    errors="ignore",
)

print(
    f"Creating tiles for {len(unranked_barriers):,} unranked small barriers with networks"
)

unranked_barriers = to_lowercase(unranked_barriers)

mbtiles_filename = tmp_dir / "unranked_barriers.mbtiles"
mbtiles_files.append(mbtiles_filename)

csv_filename = tmp_dir / "unranked_barriers.csv"
write_csv(pa.Table.from_pandas(unranked_barriers.reset_index(drop=True)), csv_filename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
    + ["-l", "unranked_small_barriers"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(unranked_barriers)
    + [str(csv_filename)]
)
ret.check_returncode()


# ### Combine barriers that don't have networks with road / stream crossings
other_barriers = df.loc[~df.HasNetwork].drop(
    columns=[
        "HasNetwork",
        "Ranked",
        "HUC6",
        "ECO3",
        "ECO4",
        "GainMilesClass",
        "TESppClass",
        "StateSGCNSppClass",
        "StreamOrderClass",
        "StreamSizeClass",
        "Intermittent",
        "PercentAlteredClass",
        "NHDPlusID",
        "upNetID",
        "downNetID",
    ]
    + DROP_UNIT_FIELDS
    + METRIC_FIELDS
    + TIER_FIELDS,
    errors="ignore",
)

# ### Read in road crossings to join with small barriers
# print("Reading road / stream crossings")
road_crossings = pd.read_feather(
    barriers_dir / "road_crossings.feather",
    columns=[
        "id",
        "lat",
        "lon",
        "SARPID",
        "Name",
        "County",
        "HUC8",
        "HUC12",
        "HUC8_COA",
        "HUC8_SGCN",
        "HUC8_USFS",
        "OwnerType",
        "Road",
        "State",
        "Stream",
        "TESpp",
        "RegionalSGCNSpp",
        "StateSGCNSpp",
        "Trout",
        "StreamOrder",
        "loop",
    ],
).rename(columns={"COUNTYFIPS": "County", "loop": "OnLoop"})

if road_crossings.id.min() < df.id.max() + 1:
    raise ValueError("Road crossings have overlapping ids with small barriers")

# Standardize other fields before merge
road_crossings[
    "Source"
] = "USGS Database of Stream Crossings in the United States (2022)"

road_crossings["SARPIDName"] = road_crossings.SARPID + "|" + road_crossings.Name

# Note: OnLoop and StreamOrder are currently ignored because HasNetwork is always False
road_crossings["HasNetwork"] = False
road_crossings["Excluded"] = False
road_crossings["Invasive"] = False
road_crossings["Unranked"] = False
road_crossings["Recon"] = 0

pack_cols = [e["field"] for e in SB_PACK_BITS]
tmp = road_crossings[pack_cols].copy()
# recode streamorder -1 to 0 for packing
tmp.loc[tmp.StreamOrder == -1, "StreamOrder"] = 0

# add packed field
road_crossings["packed"] = pack_bits(tmp, SB_PACK_BITS)
road_crossings = road_crossings.drop(
    columns=pack_cols
    + [
        "SARPID",
        "Name",
    ]
)

combined = pd.concat(
    [other_barriers, road_crossings], ignore_index=True, sort=False
).reset_index(drop=True)

combined["id"] = combined.id.astype("uint")

# Fill in N/A values
cols = [
    "SARPIDName",
    "LocalID",
    "CrossingCode",
    "Source",
    "Stream",
    "Road",
    "State",
    "County",
]
for col in cols:
    combined[col] = combined[col].fillna("").astype(str)

for col in [
    "ConditionClass",
    "CrossingTypeClass",
    "RoadTypeClass",
    "SeverityClass",
    "Constriction",
    "OwnerType",
    "Trout",
]:
    combined[col] = combined[col].fillna(0).astype("uint8")

combined["SARP_Score"] = combined["SARP_Score"].fillna(-1).astype("float32")

combined = to_lowercase(combined)


print(
    f"Creating tiles for {len(combined):,} small barriers and road crossings without networks"
)

mbtiles_filename = tmp_dir / "offnetwork_small_barriers.mbtiles"
mbtiles_files.append(mbtiles_filename)

csv_filename = tmp_dir / "offnetwork_small_barriers.csv"
write_csv(pa.Table.from_pandas(combined.reset_index(drop=True)), csv_filename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z9", f"-z{MAX_ZOOM}", "-B10"]
    + ["-l", "offnetwork_small_barriers"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(combined)
    + [str(csv_filename)]
)
ret.check_returncode()


print("Joining small barriers tilesets")
mbtiles_filename = out_dir / "small_barriers.mbtiles"
ret = subprocess.run(
    tilejoin_args + ["-o", str(mbtiles_filename)] + [str(f) for f in mbtiles_files]
)

print(f"Created small barriers tiles in {time() - start:,.2f}s")

#######################################
### Create waterfalls tiles
print("Creating waterfalls tiles")
df = (
    pd.read_feather("data/api/waterfalls.feather", columns=["id"] + WF_TILE_FIELDS)
    .rename(columns={"COUNTYFIPS": "County"})
    .sort_values(by=["TotDASqKm"], ascending=False)
)

# Fill N/A values and fix dtypes
str_cols = df.dtypes.loc[df.dtypes == "object"].index
df[str_cols] = df[str_cols].fillna("")

# Update boolean fields so that they are output to CSV correctly
for col in ["Trout"]:
    df[col] = df[col].astype("uint8")


# Combine string fields
df["SARPIDName"] = df.SARPID + "|" + df.Name
df = df.drop(
    columns=[
        "SARPID",
        "Name",
    ]
)


df = to_lowercase(df)

csv_filename = tmp_dir / "waterfalls.csv"
mbtiles_filename = out_dir / "waterfalls.mbtiles"
write_csv(pa.Table.from_pandas(df.reset_index(drop=True)), csv_filename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z9", f"-z{MAX_ZOOM}", "-B10"]
    + ["-l", "waterfalls"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(df, bool_cols={"excluded", "hasnetwork"})
    + [str(csv_filename)]
)
ret.check_returncode()
