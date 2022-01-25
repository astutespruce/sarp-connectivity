import csv
from pathlib import Path
import subprocess
from time import time

import pandas as pd

from api.constants import (
    DAM_TILE_FILTER_FIELDS,
    DAM_TILE_FIELDS,
    METRIC_FIELDS,
    SB_TILE_FILTER_FIELDS,
    SB_TILE_FIELDS,
    TIER_FIELDS,
    UNIT_FIELDS,
)
from analysis.post.lib.tiles import get_col_types

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


### Create dams tiles
start = time()
df = pd.read_feather(
    results_dir / "dams.feather", columns=["id"] + DAM_TILE_FIELDS,
).rename(columns={"County": "CountyName", "COUNTYFIPS": "County"})

to_lowercase = {
    k: k.lower()
    for k in df.columns
    if k not in UNIT_FIELDS + ["Subbasin", "Subwatershed"]
}

# Set string field nulls to blank strings
str_cols = df.dtypes.loc[df.dtypes == "object"].index
for col in str_cols:
    df[col] = df[col].fillna("").str.replace('"', "'")


# Update boolean fields so that they are output to CSV correctly
# NOTE: these must be manually set for tippecanoe via bool_cols param to get_col_types
# Also NOTE: not of the fields used for filtering can be bool; fails on frontend
for col in ["ProtectedLand", "Excluded", "Estimated", "Trout"]:
    df[col] = df[col].astype("uint8")


### Create tiles for ranked dams with networks
print("Creating tiles for dams with networks")

# Below zoom 8, we only need filter fields
csv_filename = tmp_dir / "dams_lt_z8.csv"
mbtiles_filename = tmp_dir / "dams_lt_z8.mbtiles"
mbtiles_files = [mbtiles_filename]

tmp = df.loc[df.HasNetwork][DAM_TILE_FILTER_FIELDS].rename(columns=to_lowercase)
tmp.to_csv(csv_filename, index=False, quoting=csv.QUOTE_NONNUMERIC)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z2", "-z7", "-r1.5", "-g1.5", "-B7"]
    + ["-l", "dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(tmp)
    + [str(csv_filename)]
)
ret.check_returncode()


csv_filename = tmp_dir / "dams.csv"
mbtiles_filename = tmp_dir / "dams.mbtiles"
mbtiles_files.append(mbtiles_filename)
dams = (
    df.loc[df.HasNetwork]
    .drop(columns=["HasNetwork", "Excluded"])
    .rename(columns=to_lowercase)
)

dams["ranked"] = dams.ranked.astype("uint8")

dams.to_csv(csv_filename, index=False, quoting=csv.QUOTE_NONNUMERIC)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z8", "-z16", "-B8"]
    + ["-l", "dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(dams, bool_cols={"protectedland", "ranked"})
    + [str(csv_filename)]
)
ret.check_returncode()


# Create tiles for dams without networks (these are never ranked)
print("Creating tiles for dams without networks")

# Drop metrics, tiers, and units used only for filtering
other_dams = (
    df.loc[~df.HasNetwork]
    .drop(
        columns=[
            "HUC6",
            "ECO3",
            "ECO4",
            "GainMilesClass",
            "TESppClass",
            "StateSGCNSppClass",
            "StreamOrderClass",
            "PercentAlteredClass",
            "Waterbody",
            "WaterbodyKM2",
            "WaterbodySizeClass",
            "HeightClass",
            "PassageFacilityClass",
        ]
        + METRIC_FIELDS
        + TIER_FIELDS,
        errors="ignore",
    )
    .rename(columns=to_lowercase)
)


csv_filename = tmp_dir / "other_dams.csv"
mbtiles_filename = tmp_dir / "other_dams.mbtiles"
mbtiles_files.append(mbtiles_filename)
other_dams.to_csv(
    csv_filename, index=False, quoting=csv.QUOTE_NONNUMERIC,
)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z9", "-z16", "-B10"]
    + ["-l", "background"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(other_dams, bool_cols={"protectedland", "excluded"},)
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
df = pd.read_feather(
    results_dir / "small_barriers.feather", columns=["id"] + SB_TILE_FIELDS
).rename(columns={"County": "CountyName", "COUNTYFIPS": "County"})

to_lowercase = {
    k: k.lower()
    for k in df.columns
    if k not in UNIT_FIELDS + ["Subbasin", "Subwatershed"]
}

# Set string field nulls to blank strings
str_cols = df.dtypes.loc[df.dtypes == "object"].index
df[str_cols] = df[str_cols].fillna("")

# Update boolean fields so that they are output to CSV correctly
for col in ["ProtectedLand", "Excluded", "Trout"]:
    df[col] = df[col].astype("uint8")


# Create tiles for small barriers with networks
print("Creating tiles for ranked small barriers with networks")

# Below zoom 8, we only need filter fields
csv_filename = tmp_dir / "small_barriers_lt_z8.csv"
mbtiles_filename = tmp_dir / "small_barriers_lt_z8.mbtiles"
mbtiles_files = [mbtiles_filename]

tmp = df.loc[df.HasNetwork][SB_TILE_FILTER_FIELDS].rename(columns=to_lowercase)
tmp.to_csv(csv_filename, index=False, quoting=csv.QUOTE_NONNUMERIC)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z2", "-z7", "-r1.5", "-g1.5", "-B7"]
    + ["-l", "small_barriers"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(tmp)
    + [str(csv_filename)]
)
ret.check_returncode()


csv_filename = tmp_dir / "small_barriers.csv"
mbtiles_filename = tmp_dir / "small_barriers.mbtiles"
mbtiles_files.append(mbtiles_filename)
barriers = (
    df.loc[df.HasNetwork]
    .drop(columns=["HasNetwork", "Excluded"])
    .rename(columns=to_lowercase)
)

barriers["ranked"] = barriers.ranked.astype("uint8")

barriers.to_csv(csv_filename, index=False, quoting=csv.QUOTE_NONNUMERIC)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z8", "-z16", "-B8"]
    + ["-l", "small_barriers"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(barriers, bool_cols={"protectedland", "ranked"})
    + [str(csv_filename)],
)
ret.check_returncode()


### Combine barriers that don't have networks with road / stream crossings
other_barriers = df.loc[~df.HasNetwork].drop(
    columns=[
        "HUC6",
        "ECO3",
        "ECO4",
        "GainMilesClass",
        "TESppClass",
        "StateSGCNSppClass",
        "StreamOrderClass",
        "PercentAlteredClass",
        "ConditionClass",
        "CrossingTypeClass",
        "RoadTypeClass",
        "SeverityClass",
    ]
    + METRIC_FIELDS
    + TIER_FIELDS,
    errors="ignore",
)

### Read in road crossings to join with small barriers
print("Reading road / stream crossings")
road_crossings = pd.read_feather(barriers_dir / "road_crossings.feather").rename(
    columns={"County": "CountyName"}
)

if road_crossings.id.min() < df.id.max() + 1:
    raise ValueError("Road crossings have overlapping ids with small barriers")

# Standardize other fields before merge
road_crossings["Source"] = "USGS"
road_crossings["Excluded"] = 0


road_crossing_fields = road_crossings.columns.intersection(other_barriers.columns)


combined = (
    other_barriers.append(
        road_crossings[road_crossing_fields], ignore_index=True, sort=False,
    )
    .rename(columns=to_lowercase)
    .reset_index(drop=True)
)
combined["id"] = combined.id.astype("uint")

# Fill in N/A values
cols = [
    "name",
    "sarpid",
    "localid",
    "crossingcode",
    "source",
    "stream",
    "road",
    "roadtype",
    "crossingtype",
    "condition",
    "potentialproject",
    "basin",
    "countyname",
    "State",
]
combined[cols] = combined[cols].fillna("").astype(str)

for col in ["excluded", "protectedland", "ownertype", "trout"]:
    combined[col] = combined[col].fillna(0).astype("uint8")


print("Creating tiles for small barriers and road crossings without networks")

# csv_filename = tmp_dir / "small_barriers_background.csv"
mbtiles_filename = tmp_dir / "small_barriers_background.mbtiles"
mbtiles_files.append(mbtiles_filename)

combined.to_csv(
    tmp_dir / csv_filename, index=False, quoting=csv.QUOTE_NONNUMERIC,
)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z9", "-z16", "-B10"]
    + ["-l", "background"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(combined, bool_cols={"protectedland", "excluded"},)
    + [str(csv_filename)]
)
ret.check_returncode()


# print("Joining small barriers tilesets")
mbtiles_filename = out_dir / "small_barriers.mbtiles"
ret = subprocess.run(
    tilejoin_args + ["-o", str(mbtiles_filename)] + [str(f) for f in mbtiles_files]
)

print(f"Created small barriers tiles in {time() - start:,.2f}s")

#######################################
### Create waterfalls tiles
print("Creating waterfalls tiles")
df = pd.read_feather("data/api/waterfalls.feather")

to_lowercase = {
    k: k.lower()
    for k in df.columns
    if k not in UNIT_FIELDS + ["Subbasin", "Subwatershed"]
}


# Fill N/A values and fix dtypes
str_cols = df.dtypes.loc[df.dtypes == "object"].index
df[str_cols] = df[str_cols].fillna("")

for col in ["HasNetwork", "ProtectedLand", "Excluded", "Trout"]:
    df[col] = df[col].astype("uint8")

df = df.rename(columns=to_lowercase)

csv_filename = tmp_dir / "waterfalls.csv"
mbtiles_filename = out_dir / "waterfalls.mbtiles"
df.to_csv(
    csv_filename, index_label="id", quoting=csv.QUOTE_NONNUMERIC,
)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z9", "-z16", "-B10"]
    + ["-l", "waterfalls"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(df, bool_cols={"protectedland", "excluded", "hasnetwork"})
    + [str(csv_filename)]
)
ret.check_returncode()
