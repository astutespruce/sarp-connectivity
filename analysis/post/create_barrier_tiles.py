from pathlib import Path
import subprocess
from time import time

import geopandas as gp
import pandas as pd
from pyogrio import write_dataframe

from analysis.lib.compression import pack_bits
from api.constants import (
    DAM_TILE_FILTER_FIELDS,
    DAM_TILE_FIELDS,
    UNIT_FIELDS,
    METRIC_FIELDS,
    UPSTREAM_COUNT_FIELDS,
    DOWNSTREAM_LINEAR_NETWORK_FIELDS,
    SB_TILE_FILTER_FIELDS,
    SB_TILE_FIELDS,
    WF_TILE_FIELDS,
    STATE_TIER_FIELDS,
    STATE_TIER_PACK_BITS,
    ROAD_CROSSING_TILE_FIELDS,
    ROAD_CROSSING_PACK_BITS,
)
from analysis.lib.compression import pack_bits
from analysis.post.lib.tiles import get_col_types, to_lowercase

# unit fields that can be dropped for sets of barriers that are not filtered
DROP_UNIT_FIELDS = [
    f for f in UNIT_FIELDS if not f in {"State", "County", "HUC8", "HUC12"}
]

MAX_ZOOM = 16

barriers_dir = Path("data/barriers/master")
results_dir = Path("data/barriers/networks")
out_dir = Path("tiles")
tmp_dir = Path("/tmp")


# use local clone of github.com/tippecanoe
tippecanoe = "../lib/tippecanoe/tippecanoe"
tile_join = "../lib/tippecanoe/tile-join"


# To determine size of largest tile, query mbtiles file:
# select zoom_level, tile_column, tile_row, length(tile_data) / 1024 as size from tiles order by size desc;
tippecanoe_args = [
    tippecanoe,
    "-f",
    "-pg",
    "--no-tile-size-limit",
    "--drop-densest-as-needed",
    "--coalesce-densest-as-needed",
    "--hilbert",
    "-ai",
]

tilejoin_args = [
    tile_join,
    "-f",
    "-pg",
    "--no-tile-size-limit",
    "--attribution",
    '<a href="https://southeastaquatics.net/">Southeast Aquatic Resources Partnership</>',
]

start = time()

# ####################################################################
# ### Create dams tiles
# ####################################################################
# print("-----------------Creating dam tiles------------------------\n\n")
# df = (
#     gp.read_feather(
#         results_dir / "dams.feather",
#         columns=["geometry", "id"] + DAM_TILE_FIELDS,
#     )
#     .to_crs("EPSG:4326")
#     .rename(columns={"COUNTYFIPS": "County"})
#     .sort_values(by=["TotDASqKm"], ascending=False)
# )

# # Set string field nulls to blank strings
# str_cols = df.dtypes.loc[df.dtypes == "object"].index
# for col in str_cols:
#     df[col] = df[col].fillna("").str.replace('"', "'")


# # Combine string fields
# df["SARPIDName"] = df.SARPID + "|" + df.Name

# df = df.drop(
#     columns=[
#         "SARPID",
#         "Name",
#     ]
# )


# ### Create tiles for ranked dams with networks for low zooms

# # Below zoom 8, we only need filter fields; dams are not selectable so we
# # can't show additional details
# # NOTE: only show dams on flowlines with >= 1 km2 drainage area
# tmp = to_lowercase(
#     df.loc[df.Ranked & (df.TotDASqKm >= 1)][["geometry", "id"] + DAM_TILE_FILTER_FIELDS]
# )

# print(f"Creating tiles for {len(tmp):,} ranked dams with networks for zooms 2-7")

# outfilename = tmp_dir / "dams_lt_z8.fgb"
# mbtiles_filename = tmp_dir / "dams_lt_z8.mbtiles"
# mbtiles_files = [mbtiles_filename]
# write_dataframe(tmp.reset_index(drop=True), outfilename)

# ret = subprocess.run(
#     tippecanoe_args
#     + ["-Z2", "-z7", "-r1.5", "-g1.5", "-B5"]
#     + ["-l", "ranked_dams"]
#     + ["-o", f"{str(mbtiles_filename)}"]
#     + get_col_types(tmp)
#     + [str(outfilename)]
# )
# ret.check_returncode()


# df = df.drop(columns=["TotDASqKm"])

# ### Create tiles for ranked dams with networks
# ranked_dams = df.loc[df.Ranked].drop(
#     columns=[
#         "Ranked",
#         "HasNetwork",
#         "symbol",
#         "YearRemoved",
#         "Removed",
#     ]
# )
# print(f"Creating tiles for {len(ranked_dams):,} ranked dams with networks")

# # Pack tier fields; not used for filtering, only display of info in sidebars
# ranked_dams["StateTiers"] = pack_bits(ranked_dams, STATE_TIER_PACK_BITS)
# ranked_dams = ranked_dams.drop(columns=STATE_TIER_FIELDS)
# ranked_dams = to_lowercase(ranked_dams)


# outfilename = tmp_dir / "ranked_dams.fgb"
# mbtiles_filename = tmp_dir / "ranked_dams.mbtiles"
# mbtiles_files.append(mbtiles_filename)

# write_dataframe(ranked_dams.reset_index(drop=True), outfilename)

# ret = subprocess.run(
#     tippecanoe_args
#     + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
#     + ["-l", "ranked_dams"]
#     + ["-o", f"{str(mbtiles_filename)}"]
#     + get_col_types(ranked_dams)
#     + [str(outfilename)]
# )
# ret.check_returncode()


# ### Create tiles for removed dams
# removed_dams = df.loc[df.Removed].drop(
#     columns=[
#         "Removed",
#         "Ranked",
#         "Unranked",
#         "HasNetwork",
#         "symbol",
#         # remove fields only used for filtering
#         "HUC6",
#         "GainMilesClass",
#         "TESppClass",
#         "StateSGCNSppClass",
#         "StreamOrderClass",
#         "CoastalHUC8",
#         "DownstreamOceanMilesClass",
#         "DownstreamOceanBarriersClass",
#         "PassageFacilityClass",
#         "PercentAlteredClass",
#         "SalmonidESUCount",
#     ]
#     + DROP_UNIT_FIELDS
#     + STATE_TIER_FIELDS,
#     errors="ignore",
# )

# # TEMP: eventually removed dams will have network fields; for now, drop them
# removed_dams = removed_dams.drop(
#     columns=[
#         "FlowsToOcean",
#         "MilesToOutlet",
#         "upNetID",
#         "downNetID",
#     ]
#     + [
#         c
#         for c in METRIC_FIELDS
#         if not c
#         in {
#             "Intermittent",
#             "StreamOrder",
#         }
#     ]
#     + UPSTREAM_COUNT_FIELDS
#     + DOWNSTREAM_LINEAR_NETWORK_FIELDS,
#     errors="ignore",
# )


# print(f"Creating tiles for {len(removed_dams):,} removed small barriers")

# removed_dams = to_lowercase(removed_dams)

# outfilename = tmp_dir / "removed_dams.fgb"
# mbtiles_filename = tmp_dir / "removed_dams.mbtiles"
# mbtiles_files.append(mbtiles_filename)
# write_dataframe(removed_dams.reset_index(drop=True), outfilename)

# ret = subprocess.run(
#     tippecanoe_args
#     + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
#     + ["-l", "removed_dams"]
#     + ["-o", f"{str(mbtiles_filename)}"]
#     + get_col_types(removed_dams)
#     + [str(outfilename)]
# )
# ret.check_returncode()


# ### Create tiles for unranked dams with networks
# unranked_dams = df.loc[df.HasNetwork & (~(df.Ranked | df.Removed))].drop(
#     columns=[
#         "Ranked",
#         "HasNetwork",
#         "YearRemoved",
#         "Removed",
#         "GainMilesClass",
#         "TESppClass",
#         "StateSGCNSppClass",
#         "StreamOrderClass",
#         "StreamSizeClass",
#         "PercentAlteredClass",
#         "WaterbodySizeClass",
#         "HeightClass",
#         "PassageFacilityClass",
#         "SalmonidESUCount",
#         "DownstreamOceanMilesClass",
#         "DownstreamOceanBarriersClass",
#     ]
#     + DROP_UNIT_FIELDS
#     + STATE_TIER_FIELDS,
#     errors="ignore",
# )
# print(f"Creating tiles for {len(unranked_dams):,} unranked dams with networks")

# unranked_dams = to_lowercase(unranked_dams)

# outfilename = tmp_dir / "unranked_dams.fgb"
# mbtiles_filename = tmp_dir / "unranked_dams.mbtiles"
# mbtiles_files.append(mbtiles_filename)
# write_dataframe(unranked_dams.reset_index(drop=True), outfilename)

# ret = subprocess.run(
#     tippecanoe_args
#     + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
#     + ["-l", "unranked_dams"]
#     + ["-o", f"{str(mbtiles_filename)}"]
#     + get_col_types(unranked_dams)
#     + [str(outfilename)]
# )
# ret.check_returncode()


# ### Create tiles for dams without networks (these are never ranked)
# print("Creating tiles for dams without networks")

# # Drop metrics, tiers, and units used only for filtering
# offnetwork_dams = (
#     df.loc[~(df.HasNetwork | df.Removed)]
#     .drop(
#         columns=[
#             "HasNetwork",
#             "Ranked",
#             "YearRemoved",
#             "Removed",
#             "GainMilesClass",
#             "TESppClass",
#             "StateSGCNSppClass",
#             "StreamOrderClass",
#             "StreamSizeClass",
#             "Intermittent",
#             "PercentAlteredClass",
#             "Waterbody",
#             "WaterbodyKM2",
#             "WaterbodySizeClass",
#             "HeightClass",
#             "PassageFacilityClass",
#             "SalmonidESUCount",
#             "FlowsToOcean",
#             "MilesToOutlet",
#             "CoastalHUC8",
#             "DownstreamOceanMilesClass",
#             "DownstreamOceanBarriersClass",
#             "upNetID",
#             "downNetID",
#         ]
#         + DROP_UNIT_FIELDS
#         + METRIC_FIELDS
#         + UPSTREAM_COUNT_FIELDS
#         + DOWNSTREAM_LINEAR_NETWORK_FIELDS
#         + STATE_TIER_FIELDS,
#         errors="ignore",
#     )
#     .reset_index(drop=True)
# )

# offnetwork_dams = to_lowercase(offnetwork_dams)


# outfilename = tmp_dir / "offnetwork_dams.fgb"
# mbtiles_filename = tmp_dir / "offnetwork_dams.mbtiles"
# mbtiles_files.append(mbtiles_filename)
# write_dataframe(offnetwork_dams, outfilename)

# ret = subprocess.run(
#     tippecanoe_args
#     + ["-Z9", f"-z{MAX_ZOOM}", "-B10"]
#     + ["-l", "offnetwork_dams"]
#     + ["-o", f"{str(mbtiles_filename)}"]
#     + get_col_types(
#         offnetwork_dams,
#     )
#     + [str(outfilename)]
# )
# ret.check_returncode()


# print("Joining dams tilesets")
# mbtiles_filename = out_dir / "dams.mbtiles"
# ret = subprocess.run(
#     tilejoin_args + ["-o", str(mbtiles_filename)] + [str(f) for f in mbtiles_files]
# )

# print(f"Created dam tiles in {time() - start:,.2f}s")

# ####################################################################
# ### Create small barrier tiles
# ####################################################################
# print("\n\n-----------------Creating small barrier tiles------------------------\n\n")
# start = time()
# df = (
#     gp.read_feather(
#         results_dir / "small_barriers.feather",
#         columns=["geometry", "id"] + SB_TILE_FIELDS,
#     )
#     .to_crs("EPSG:4326")
#     .rename(columns={"COUNTYFIPS": "County"})
#     .sort_values(by=["TotDASqKm"], ascending=False)
#     .drop(columns=["TotDASqKm"])
# )

# # Set string field nulls to blank strings
# str_cols = df.dtypes.loc[df.dtypes == "object"].index
# for col in str_cols:
#     df[col] = df[col].fillna("").str.replace('"', "'")

# # Combine string fields
# df["SARPIDName"] = df.SARPID + "|" + df.Name
# df = df.drop(
#     columns=[
#         "SARPID",
#         "Name",
#     ]
# )


# ### Create tiles for ranked small barriers at low zooms
# # Below zoom 8, we only need filter fields

# outfilename = tmp_dir / "small_barriers_lt_z8.fgb"
# mbtiles_filename = tmp_dir / "small_barriers_lt_z8.mbtiles"
# mbtiles_files = [mbtiles_filename]

# tmp = to_lowercase(df.loc[df.Ranked][["geometry", "id"] + SB_TILE_FILTER_FIELDS])
# print(
#     f"Creating tiles for {len(tmp):,} ranked small barriers with networks for zooms 2-7"
# )
# write_dataframe(tmp.reset_index(drop=True), outfilename)

# ret = subprocess.run(
#     tippecanoe_args
#     + ["-Z2", "-z7", "-r1.5", "-g1.5", "-B5"]
#     + ["-l", "ranked_small_barriers"]
#     + ["-o", f"{str(mbtiles_filename)}"]
#     + get_col_types(tmp)
#     + [str(outfilename)]
# )
# ret.check_returncode()


# ### Create tiles for ranked small barriers
# ranked_barriers = df.loc[df.Ranked].drop(
#     columns=[
#         "Ranked",
#         "HasNetwork",
#         "symbol",
#         "YearRemoved",
#         "Removed",
#     ]
# )
# print(
#     f"Creating tiles for {len(ranked_barriers):,} ranked small barriers with networks"
# )

# # NOTE: small barriers don't have state tier fields
# ranked_barriers = to_lowercase(ranked_barriers)

# outfilename = tmp_dir / "ranked_small_barriers.fgb"

# mbtiles_filename = tmp_dir / "ranked_small_barriers.mbtiles"
# mbtiles_files.append(mbtiles_filename)
# write_dataframe(ranked_barriers.reset_index(drop=True), outfilename)

# ret = subprocess.run(
#     tippecanoe_args
#     + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
#     + ["-l", "ranked_small_barriers"]
#     + ["-o", f"{str(mbtiles_filename)}"]
#     + get_col_types(ranked_barriers)
#     + [str(outfilename)],
# )
# ret.check_returncode()

# ### Create tiles for removed small barriers
# removed_barriers = df.loc[df.Removed].drop(
#     columns=[
#         "Removed",
#         "Ranked",
#         "Unranked",
#         "HasNetwork",
#         "symbol",
#         # remove fields only used for filtering
#         "HUC6",
#         "GainMilesClass",
#         "TESppClass",
#         "StateSGCNSppClass",
#         "StreamOrderClass",
#         "CoastalHUC8",
#         "DownstreamOceanMilesClass",
#         "DownstreamOceanBarriersClass",
#         "PassageFacilityClass",
#         "PercentAlteredClass",
#         "SalmonidESUCount",
#     ]
#     + DROP_UNIT_FIELDS
#     + STATE_TIER_FIELDS,
#     errors="ignore",
# )

# # TEMP: eventually removed barriers will have network fields; for now, drop them
# removed_barriers = removed_barriers.drop(
#     columns=[
#         "FlowsToOcean",
#         "MilesToOutlet",
#         "upNetID",
#         "downNetID",
#     ]
#     + DROP_UNIT_FIELDS
#     + [
#         c
#         for c in METRIC_FIELDS
#         if not c
#         in {
#             "Intermittent",
#             "StreamOrder",
#         }
#     ]
#     + UPSTREAM_COUNT_FIELDS
#     + DOWNSTREAM_LINEAR_NETWORK_FIELDS,
#     errors="ignore",
# )


# print(f"Creating tiles for {len(removed_barriers):,} removed small barriers")

# removed_barriers = to_lowercase(removed_barriers)

# outfilename = tmp_dir / "removed_small_barriers.fgb"
# mbtiles_filename = tmp_dir / "removed_small_barriers.mbtiles"
# mbtiles_files.append(mbtiles_filename)
# write_dataframe(removed_barriers.reset_index(drop=True), outfilename)

# ret = subprocess.run(
#     tippecanoe_args
#     + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
#     + ["-l", "removed_small_barriers"]
#     + ["-o", f"{str(mbtiles_filename)}"]
#     + get_col_types(removed_barriers)
#     + [str(outfilename)]
# )
# ret.check_returncode()


# ### Create tiles for unranked barriers with networks
# unranked_barriers = df.loc[df.HasNetwork & (~(df.Ranked | df.Removed))].drop(
#     columns=[
#         "Ranked",
#         "HasNetwork",
#         "Removed",
#         "YearRemoved",
#         "GainMilesClass",
#         "TESppClass",
#         "StateSGCNSppClass",
#         "StreamOrderClass",
#         "StreamSizeClass",
#         "PercentAlteredClass",
#         "SalmonidESUCount",
#         "DownstreamOceanMilesClass",
#         "DownstreamOceanBarriersClass",
#         "PassageFacilityClass",
#     ]
#     + DROP_UNIT_FIELDS,
#     errors="ignore",
# )

# print(
#     f"Creating tiles for {len(unranked_barriers):,} unranked small barriers with networks"
# )

# unranked_barriers = to_lowercase(unranked_barriers)

# outfilename = tmp_dir / "unranked_barriers.fgb"
# mbtiles_filename = tmp_dir / "unranked_barriers.mbtiles"
# mbtiles_files.append(mbtiles_filename)
# write_dataframe(unranked_barriers.reset_index(drop=True), outfilename)

# ret = subprocess.run(
#     tippecanoe_args
#     + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
#     + ["-l", "unranked_small_barriers"]
#     + ["-o", f"{str(mbtiles_filename)}"]
#     + get_col_types(unranked_barriers)
#     + [str(outfilename)]
# )
# ret.check_returncode()


# ### Create tiles for small barriers without networks (these are never ranked)
# offnetwork_barriers = df.loc[~(df.HasNetwork | df.Removed)].drop(
#     columns=[
#         "HasNetwork",
#         "Ranked",
#         "Removed",
#         "YearRemoved",
#         # remove fields only used for filtering and general network fields
#         "HUC6",
#         "GainMilesClass",
#         "TESppClass",
#         "StateSGCNSppClass",
#         "StreamOrderClass",
#         "StreamSizeClass",
#         "Intermittent",
#         "PercentAlteredClass",
#         "SalmonidESUCount",
#         "FlowsToOcean",
#         "MilesToOutlet",
#         "CoastalHUC8",
#         "DownstreamOceanMilesClass",
#         "DownstreamOceanBarriersClass",
#         "upNetID",
#         "downNetID",
#     ]
#     + DROP_UNIT_FIELDS
#     + METRIC_FIELDS
#     + UPSTREAM_COUNT_FIELDS
#     + DOWNSTREAM_LINEAR_NETWORK_FIELDS
#     + STATE_TIER_FIELDS,
#     errors="ignore",
# )

# offnetwork_barriers = to_lowercase(offnetwork_barriers)

# outfilename = tmp_dir / "offnetwork_small_barriers.fgb"
# mbtiles_filename = tmp_dir / "offnetwork_small_barriers.mbtiles"
# mbtiles_files.append(mbtiles_filename)
# write_dataframe(offnetwork_barriers, outfilename)

# ret = subprocess.run(
#     tippecanoe_args
#     + ["-Z9", f"-z{MAX_ZOOM}", "-B10"]
#     + ["-l", "offnetwork_small_barriers"]
#     + ["-o", f"{str(mbtiles_filename)}"]
#     + get_col_types(
#         offnetwork_barriers,
#     )
#     + [str(outfilename)]
# )
# ret.check_returncode()

# print("Joining small barriers tilesets")
# mbtiles_filename = out_dir / "small_barriers.mbtiles"
# ret = subprocess.run(
#     tilejoin_args + ["-o", str(mbtiles_filename)] + [str(f) for f in mbtiles_files]
# )

# print(f"Created small barrier tiles in {time() - start:,.2f}s")


####################################################################
### Create road crossing tiles
####################################################################
print("\n\n-----------------Creating road crossing tiles------------------------\n\n")

df = (
    gp.read_feather(
        barriers_dir / "road_crossings.feather",
    )
    .to_crs("EPSG:4326")
    .drop(columns=["County"])
    .rename(
        columns={
            "COUNTYFIPS": "County",
            "intermittent": "Intermittent",
            "loop": "OnLoop",
            "sizeclass": "StreamSizeClass",
        }
    )
)

# Set string field nulls to blank strings
str_cols = df.dtypes.loc[df.dtypes == "object"].index
for col in str_cols:
    df[col] = df[col].fillna("").str.replace('"', "'")

bool_cols = df.dtypes.loc[df.dtypes == "bool"].index
for col in bool_cols:
    df[col] = df[col].fillna(False).astype("uint8")

# Combine string fields
df["SARPIDName"] = df.SARPID + "|" + df.Name

df = df.drop(
    columns=[
        "SARPID",
        "Name",
    ]
)

pack_cols = [e["field"] for e in ROAD_CROSSING_PACK_BITS]
tmp = df[pack_cols].copy()
tmp.loc[tmp.StreamOrder == -1, "StreamOrder"] = 0
df["packed"] = pack_bits(tmp, ROAD_CROSSING_PACK_BITS)
df = df.drop(columns=pack_cols)

df = to_lowercase(df[ROAD_CROSSING_TILE_FIELDS + ["geometry"]])

outfilename = tmp_dir / "road_crossings.fgb"
mbtiles_filename = out_dir / "road_crossings.mbtiles"

write_dataframe(df.reset_index(drop=True), outfilename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z9", f"-z{MAX_ZOOM}", "-B10"]
    + ["-l", "road_crossings"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(df)
    + [str(outfilename)]
)
ret.check_returncode()


print(f"Created road crossing tiles in {time() - start:,.2f}s")

# ###################################################################
# ## Create waterfalls tiles
# ###################################################################
# print("\n\n-----------------Creating waterfalls tiles------------------------\n\n")
# print("Creating waterfalls tiles")
# df = (
#     gp.read_feather(
#         results_dir / "waterfalls.feather", columns=["geometry", "id"] + WF_TILE_FIELDS
#     )
#     .to_crs("EPSG:4326")
#     .rename(columns={"COUNTYFIPS": "County"})
#     .sort_values(by=["TotDASqKm"], ascending=False)
# ).drop(columns=["TotDASqKm"])

# # Fill N/A values and fix dtypes
# str_cols = df.dtypes.loc[df.dtypes == "object"].index
# df[str_cols] = df[str_cols].fillna("")


# # Combine string fields
# df["SARPIDName"] = df.SARPID + "|" + df.Name
# df = df.drop(
#     columns=[
#         "SARPID",
#         "Name",
#     ]
# )


# df = to_lowercase(df)

# outfilename = tmp_dir / "waterfalls.fgb"
# mbtiles_filename = out_dir / "waterfalls.mbtiles"
# write_dataframe(df.reset_index(drop=True), outfilename)

# ret = subprocess.run(
#     tippecanoe_args
#     + ["-Z9", f"-z{MAX_ZOOM}", "-B10"]
#     + ["-l", "waterfalls"]
#     + ["-o", f"{str(mbtiles_filename)}"]
#     + get_col_types(df)
#     + [str(outfilename)]
# )
# ret.check_returncode()
