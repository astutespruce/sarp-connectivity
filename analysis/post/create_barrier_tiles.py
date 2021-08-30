import csv
from pathlib import Path
import subprocess
from time import time

import pandas as pd
import geopandas as gp
import pygeos as pg

from api.constants import (
    DAM_CORE_FIELDS,
    DAM_TILE_FIELDS,
    SB_CORE_FIELDS,
    SB_TILE_FIELDS,
    WF_CORE_FIELDS,
    UNIT_FIELDS,
)
from analysis.constants import GEO_CRS
from analysis.post.lib.tiles import get_col_types

api_dir = Path("data/api")
barriers_dir = Path("data/barriers/master")
out_dir = Path("tiles")
tmp_dir = Path("/tmp")


tippecanoe_args = ["tippecanoe", "-f", "-pk", "-pg", "-ai", "--drop-densest-as-needed"]

tilejoin_args = [
    "tile-join",
    "-f",
    "-pg",
    "--no-tile-size-limit",
]


### Create dams tiles
start = time()
df = (
    pd.read_feather(api_dir / "dams.feather", columns=["id"] + DAM_TILE_FIELDS)
    .set_index("id")
    .rename(columns={"County": "CountyName", "COUNTYFIPS": "County"})
)

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
for col in ["HasNetwork", "ProtectedLand", "Excluded"]:
    df[col] = df[col].astype("uint8")


# Create tiles for ranked dams with networks
print("Creating tiles for dams with networks")

csv_filename = tmp_dir / "ranked_dams.csv"
mbtiles_filename = tmp_dir / "ranked_dams.mbtiles"
mbtiles_files = [mbtiles_filename]
ranked_dams = (
    df.loc[df.Ranked]
    .drop(columns=["HasNetwork", "Ranked", "Excluded"])
    .rename(columns=to_lowercase)
)

ranked_dams.to_csv(csv_filename, index_label="id", quoting=csv.QUOTE_NONNUMERIC)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z5", "-z16", "-B6"]
    + ["-l", "dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(ranked_dams, bool_cols={"protectedland"})
    + [str(csv_filename)]
)
ret.check_returncode()


# Create tiles for dams unranked dams
# NOTE: Ranked is HasNetwork + ~unranked (from master)
print("Creating tiles for unranked dams")

unranked_dams = df.loc[~df.Ranked]

# Drop metrics, tiers, and units used only for filtering
# keep HUC8, HUC12 since these are used to get names for those on frontend
keep_fields = unranked_dams.columns.intersection(
    DAM_CORE_FIELDS
    + ["HUC8", "HUC12"]
    + ["CountyName", "State", "HasNetwork", "Excluded"]
)
unranked_dams = unranked_dams[keep_fields].rename(columns=to_lowercase)


# csv_filename = tmp_dir / "unranked_dams.csv"
mbtiles_filename = tmp_dir / "unranked_dams.mbtiles"
mbtiles_files.append(mbtiles_filename)
unranked_dams.to_csv(
    csv_filename, index_label="id", quoting=csv.QUOTE_NONNUMERIC,
)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z9", "-z16", "-B10"]
    + ["-l", "background"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(
        unranked_dams, bool_cols={"protectedland", "excluded", "hasnetwork"}
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


### Create small barrier tiles
start = time()
df = (
    pd.read_feather(api_dir / "small_barriers.feather", columns=["id"] + SB_TILE_FIELDS)
    .set_index("id")
    .rename(columns={"County": "CountyName", "COUNTYFIPS": "County"})
)

to_lowercase = {
    k: k.lower()
    for k in df.columns
    if k not in UNIT_FIELDS + ["Subbasin", "Subwatershed"]
}

# Set string field nulls to blank strings
str_cols = df.dtypes.loc[df.dtypes == "object"].index
df[str_cols] = df[str_cols].fillna("")

# Update boolean fields so that they are output to CSV correctly
for col in ["ProtectedLand", "Excluded"]:
    df[col] = df[col].astype("uint8")


# Create tiles for small barriers with networks
print("Creating tiles for small barriers with networks")

csv_filename = tmp_dir / "ranked_small_barriers.csv"
mbtiles_filename = tmp_dir / "ranked_small_barriers.mbtiles"
mbtiles_files = [mbtiles_filename]
ranked_barriers = (
    df.loc[df.Ranked]
    .drop(columns=["HasNetwork", "Ranked", "Excluded"])
    .rename(columns=to_lowercase)
)

ranked_barriers.to_csv(csv_filename, index_label="id", quoting=csv.QUOTE_NONNUMERIC)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z5", "-z16", "-B6"]
    + ["-l", "dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(ranked_barriers, bool_cols={"protectedland"})
    + [str(csv_filename)],
)
ret.check_returncode()


### Combine barriers that don't have networks with road / stream crossings
unranked_barriers = df.loc[~df.Ranked].copy()

# Drop metrics, tiers, and units used only for filtering
keep_fields = unranked_barriers.columns.intersection(
    SB_CORE_FIELDS
    + ["HUC8", "HUC12"]
    + ["CountyName", "State", "HasNetwork", "Excluded"]
)
unranked_barriers = unranked_barriers[keep_fields].copy()

print("Reading road / stream crossings")
road_crossings = gp.read_feather(barriers_dir / "road_crossings.feather").rename(
    columns={"County": "CountyName"}
)

# bring in Species info
spp_df = (
    pd.read_feather(
        "data/species/derived/spp_HUC12.feather",
        columns=["HUC12", "federal", "sgcn", "regional"],
    )
    .rename(
        columns={
            "federal": "TESpp",
            "sgcn": "StateSGCNSpp",
            "regional": "RegionalSGCNSpp",
        }
    )
    .set_index("HUC12")
)
road_crossings = road_crossings.join(spp_df, on="HUC12")
for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    road_crossings[col] = road_crossings[col].fillna(0).astype("uint8")

# Standardize other fields before merge
road_crossings["Source"] = "USGS"
road_crossings["Excluded"] = 0

road_crossing_fields = road_crossings.columns.intersection(
    SB_CORE_FIELDS + ["HUC8", "HUC12", "CountyName", "State", "HasNetwork", "Excluded"]
)

combined = (
    unranked_barriers.append(
        road_crossings[road_crossing_fields], ignore_index=True, sort=False
    )
    .rename(columns=to_lowercase)
    .reset_index(drop=True)
)

# create a new consolidated ID
combined["id"] = combined.index.values.astype("uint32")

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

for col in [
    "hasnetwork",
    "excluded",
    "protectedland",
    "ownertype",
    "severityclass",
]:
    combined[col] = combined[col].fillna(0).astype("uint8")


print("Creating tiles for small barriers and road crossings without networks")

csv_filename = tmp_dir / "small_barriers_background.csv"
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
    + get_col_types(
        unranked_barriers, bool_cols={"protectedland", "excluded", "hasnetwork"},
    )
    + [str(csv_filename)]
)
ret.check_returncode()


print("Joining small barriers tilesets")
mbtiles_filename = out_dir / "small_barriers.mbtiles"
ret = subprocess.run(
    tilejoin_args + ["-o", str(mbtiles_filename)] + [str(f) for f in mbtiles_files]
)

print(f"Created small barriers tiles in {time() - start:,.2f}s")


### Create waterfalls tiles
print("Creating waterfalls tiles")
df = (
    gp.read_feather(barriers_dir / "waterfalls.feather")
    .set_index("id")
    .drop(
        columns=[
            "level_0",
            "index",
            "dup_group",
            "dup_count",
            "dup_log",
            "snap_dist",
            "snap_tolerance",
            "snap_log",
            "log",
            "lineID",
            "wbID",
        ],
        errors="ignore",
    )
    .rename(columns={"StreamOrde": "StreamOrder",})
)

# set intermittent to -1 where waterfalls were not snapped to networks
df.intermittent = df.intermittent.astype("int8")
df.loc[~df.snapped, "intermittent"] = -1

to_lowercase = {
    k: k.lower()
    for k in df.columns
    if k not in UNIT_FIELDS + ["Subbasin", "Subwatershed"]
}

# drop any that should be DROPPED (dropped or duplicate) from the analysis
# NOTE: excluded ones are retained but don't have networks
df = df.loc[~(df.dropped | df.duplicate)].copy()

### Add lat / lon
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(GEO_CRS)
geo["lat"] = pg.get_y(geo.geometry.values.data).astype("float32")
geo["lon"] = pg.get_x(geo.geometry.values.data).astype("float32")
df = df.join(geo[["lat", "lon"]])

df = df[WF_CORE_FIELDS].copy()

# Fill N/A values and fix dtypes
str_cols = df.dtypes.loc[df.dtypes == "object"].index
df[str_cols] = df[str_cols].fillna("")

df = df.rename(columns=to_lowercase)

csv_filename = tmp_dir / "waterfalls.csv"
mbtiles_filename = out_dir / "waterfalls.mbtiles"
df.to_csv(
    csv_filename, index_label="id", quoting=csv.QUOTE_NONNUMERIC,
)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z5", "-z16", "-B6"]
    + ["-l", "waterfalls"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(df)
    + [str(csv_filename)]
)
ret.check_returncode()
