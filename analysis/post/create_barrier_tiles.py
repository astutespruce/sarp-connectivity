from pathlib import Path
import subprocess
from time import time

import geopandas as gp
from pyogrio import write_dataframe

from api.constants import (
    DAM_TILE_FILTER_FIELDS,
    SB_TILE_FILTER_FIELDS,
    COMBINED_TILE_FILTER_FIELDS,
    unique,
)

from analysis.post.lib.tiles import (
    get_col_types,
    to_lowercase,
    combine_sarpid_name,
    fill_na_fields,
)


MAX_ZOOM = 16

barriers_dir = Path("data/barriers/master")
results_dir = Path("data/barriers/networks")
out_dir = Path("tiles")
tmp_dir = Path("/tmp")


tippecanoe = "tippecanoe"
tile_join = "tile-join"


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

####################################################################
### Create dams tiles
####################################################################
print("-----------------Creating dam tiles------------------------\n\n")
df = (
    gp.read_feather(
        results_dir / "dams.feather",
        columns=unique(
            [
                "geometry",
                "id",
                "SARPID",
                "Name",
                "symbol",
                "upNetID",
                "HasNetwork",
                "Ranked",
                "Removed",
                "TotDASqKm",
            ]
            + DAM_TILE_FILTER_FIELDS
        ),
    )
    .to_crs("EPSG:4326")
    .rename(columns={"COUNTYFIPS": "County"})
    .sort_values(by=["TotDASqKm"], ascending=False)
)
df = combine_sarpid_name(df)
fill_na_fields(df)


### Create tiles for ranked dams with networks for low zooms

ranked_dams = df.loc[
    df.Ranked,
    ["geometry", "id", "SARPIDName", "upNetID", "TotDASqKm"] + DAM_TILE_FILTER_FIELDS,
]


# Below zoom 8, we only need filter fields; dams are not selectable so we
# can't show additional details including name
# NOTE: only show dams on flowlines with >= 1 km2 drainage area
tmp = ranked_dams.loc[df.TotDASqKm >= 1, ["geometry", "id"] + DAM_TILE_FILTER_FIELDS]

print(f"Creating tiles for {len(tmp):,} ranked dams with networks for zooms 2-7")

outfilename = tmp_dir / "dams_lt_z8.fgb"
mbtiles_filename = tmp_dir / "dams_lt_z8.mbtiles"
mbtiles_files = [mbtiles_filename]

tmp = to_lowercase(tmp)
write_dataframe(tmp.reset_index(drop=True), outfilename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z0", "-z7", "-r1.5", "-g1.5", "-B5"]
    + ["-l", "ranked_dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(tmp)
    + [str(outfilename)]
)
ret.check_returncode()


### Create tiles for ranked dams with networks
print(f"Creating tiles for {len(ranked_dams):,} ranked dams with networks")

# drainage area only used for selecting dams for low zooms; drop it
ranked_dams = ranked_dams.drop(columns=["TotDASqKm"])

outfilename = tmp_dir / "ranked_dams.fgb"
mbtiles_filename = tmp_dir / "ranked_dams.mbtiles"
mbtiles_files.append(mbtiles_filename)

ranked_dams = to_lowercase(ranked_dams)
write_dataframe(ranked_dams.reset_index(drop=True), outfilename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
    + ["-l", "ranked_dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(ranked_dams)
    + [str(outfilename)]
)
ret.check_returncode()


### Create tiles for unranked dams
# these are invasive barriers that have networks but are not filtered or ranked
unranked_dams = df.loc[
    df.HasNetwork & (~(df.Ranked | df.Removed)),
    ["geometry", "id", "SARPIDName", "upNetID", "symbol"],
]

print(f"Creating tiles for {len(unranked_dams):,} unranked dams with networks")

outfilename = tmp_dir / "unranked_dams.fgb"
mbtiles_filename = tmp_dir / "unranked_dams.mbtiles"
mbtiles_files.append(mbtiles_filename)
unranked_dams = to_lowercase(unranked_dams)
write_dataframe(unranked_dams.reset_index(drop=True), outfilename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
    + ["-l", "unranked_dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(unranked_dams)
    + [str(outfilename)]
)
ret.check_returncode()


### Create tiles for removed dams (including off-network)
# these are not filtered
# TODO: network IDs
removed_dams = df.loc[df.Removed, ["geometry", "id", "SARPIDName"]]
print(f"Creating tiles for {len(removed_dams):,} removed dams")

outfilename = tmp_dir / "removed_dams.fgb"
mbtiles_filename = tmp_dir / "removed_dams.mbtiles"
mbtiles_files.append(mbtiles_filename)
removed_dams = to_lowercase(removed_dams)
write_dataframe(removed_dams.reset_index(drop=True), outfilename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z6", f"-z{MAX_ZOOM}", "-B6"]
    + ["-l", "removed_dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(removed_dams)
    + [str(outfilename)]
)
ret.check_returncode()


### Create tiles for all other dams
# these include remaining off-network / excluded dams; these are not filtered
other_dams = df.loc[(~df.HasNetwork) & (~df.Removed), ["geometry", "id", "SARPIDName", "symbol"]]

print(f"Creating tiles for {len(other_dams):,} other dams")

outfilename = tmp_dir / "other_dams.fgb"
mbtiles_filename = tmp_dir / "other_dams.mbtiles"
mbtiles_files.append(mbtiles_filename)
other_dams = to_lowercase(other_dams)
write_dataframe(other_dams.reset_index(drop=True), outfilename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z6", f"-z{MAX_ZOOM}", "-B8"]
    + ["-l", "other_dams"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(other_dams)
    + [str(outfilename)]
)
ret.check_returncode()


print("Joining dams tilesets")
mbtiles_filename = out_dir / "dams.mbtiles"
ret = subprocess.run(tilejoin_args + ["-o", str(mbtiles_filename)] + [str(f) for f in mbtiles_files])

# remove intermediates
# FIXME:
# for mbtiles_file in mbtiles_files:
#     mbtiles_file.unlink()


print(f"Created dam tiles in {time() - start:,.2f}s")

####################################################################
### Create small barrier tiles
####################################################################
# NOTE: small barriers don't have state tier fields

print("\n\n-----------------Creating small barrier tiles------------------------\n\n")
start = time()
df = (
    gp.read_feather(
        results_dir / "small_barriers.feather",
        columns=[
            "geometry",
            "id",
            "SARPID",
            "Name",
            "symbol",
            "upNetID",
            "HasNetwork",
            "Ranked",
            "Removed",
            "TotDASqKm",
        ]
        + SB_TILE_FILTER_FIELDS,
    )
    .to_crs("EPSG:4326")
    .rename(columns={"COUNTYFIPS": "County"})
    .sort_values(by=["TotDASqKm"], ascending=False)
    .drop(columns=["TotDASqKm"])
)
df = combine_sarpid_name(df)
fill_na_fields(df)

### Create tiles for ranked small barriers at low zooms

ranked_barriers = df.loc[df.Ranked, ["geometry", "id", "SARPIDName", "upNetID"] + SB_TILE_FILTER_FIELDS]


# Below zoom 8, we only need filter fields
outfilename = tmp_dir / "small_barriers_lt_z8.fgb"
mbtiles_filename = tmp_dir / "small_barriers_lt_z8.mbtiles"
mbtiles_files = [mbtiles_filename]

tmp = ranked_barriers[["geometry", "id"] + SB_TILE_FILTER_FIELDS]
print(f"Creating tiles for {len(tmp):,} ranked small barriers with networks for zooms 2-7")

tmp = to_lowercase(ranked_barriers)
write_dataframe(tmp.reset_index(drop=True), outfilename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z0", "-z7", "-r1.5", "-g1.5", "-B5"]
    + ["-l", "ranked_small_barriers"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(tmp)
    + [str(outfilename)]
)
ret.check_returncode()

### Create tiles for ranked small barriers
print(f"Creating tiles for {len(ranked_barriers):,} ranked small barriers with networks")

outfilename = tmp_dir / "ranked_small_barriers.fgb"
mbtiles_filename = tmp_dir / "ranked_small_barriers.mbtiles"
mbtiles_files.append(mbtiles_filename)
ranked_barriers = to_lowercase(ranked_barriers)
write_dataframe(ranked_barriers.reset_index(drop=True), outfilename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
    + ["-l", "ranked_small_barriers"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(ranked_barriers)
    + [str(outfilename)],
)
ret.check_returncode()


### Create tiles for unranked barriers with networks
# these are invasive barriers that have networks but are not filtered or ranked
unranked_barriers = df.loc[
    df.HasNetwork & (~(df.Ranked | df.Removed)),
    ["geometry", "id", "SARPIDName", "upNetID", "symbol"],
]

print(f"Creating tiles for {len(unranked_barriers):,} unranked small barriers with networks")

outfilename = tmp_dir / "unranked_barriers.fgb"
mbtiles_filename = tmp_dir / "unranked_barriers.mbtiles"
mbtiles_files.append(mbtiles_filename)
unranked_barriers = to_lowercase(unranked_barriers)
write_dataframe(unranked_barriers.reset_index(drop=True), outfilename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
    + ["-l", "unranked_small_barriers"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(unranked_barriers)
    + [str(outfilename)]
)
ret.check_returncode()


### Create tiles for removed small barriers
# TODO: network IDs
removed_barriers = df.loc[df.Removed, ["geometry", "id", "SARPIDName"]]

print(f"Creating tiles for {len(removed_barriers):,} removed small barriers")

outfilename = tmp_dir / "removed_small_barriers.fgb"
mbtiles_filename = tmp_dir / "removed_small_barriers.mbtiles"
mbtiles_files.append(mbtiles_filename)
removed_barriers = to_lowercase(removed_barriers)
write_dataframe(removed_barriers, outfilename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z6", f"-z{MAX_ZOOM}", "-B6"]
    + ["-l", "removed_small_barriers"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(
        removed_barriers,
    )
    + [str(outfilename)]
)
ret.check_returncode()

### Create tiles all other small barriers
other_barriers = df.loc[(~df.HasNetwork) & (~df.Removed), ["geometry", "id", "SARPIDName", "symbol"]]

print(f"Creating tiles for {len(other_barriers):,} other small barriers")

outfilename = tmp_dir / "other_small_barriers.fgb"
mbtiles_filename = tmp_dir / "other_small_barriers.mbtiles"
mbtiles_files.append(mbtiles_filename)
other_barriers = to_lowercase(other_barriers)
write_dataframe(other_barriers, outfilename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z6", f"-z{MAX_ZOOM}", "-B10"]
    + ["-l", "other_small_barriers"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(
        other_barriers,
    )
    + [str(outfilename)]
)
ret.check_returncode()

print("Joining small barriers tilesets")
mbtiles_filename = out_dir / "small_barriers.mbtiles"
ret = subprocess.run(tilejoin_args + ["-o", str(mbtiles_filename)] + [str(f) for f in mbtiles_files])

# remove intermediates
# FIXME:
# for mbtiles_file in mbtiles_files:
#     mbtiles_file.unlink()

print(f"Created small barrier tiles in {time() - start:,.2f}s")


####################################################################
### Create barrier tiles for other network_types
####################################################################
for network_type in ["combined_barriers", "largefish_barriers", "smallfish_barriers"]:
    print(f"-----------------Creating {network_type} tiles------------------------\n\n")
    df = (
        gp.read_feather(
            results_dir / f"{network_type}.feather",
            columns=[
                "geometry",
                "BarrierType",
                "id",
                "SARPID",
                "Name",
                "symbol",
                "upNetID",
                "HasNetwork",
                "Ranked",
                "Removed",
                "TotDASqKm",
            ]
            + COMBINED_TILE_FILTER_FIELDS,
        )
        .to_crs("EPSG:4326")
        .rename(columns={"COUNTYFIPS": "County"})
        .sort_values(by=["TotDASqKm"], ascending=False)
    )
    df = combine_sarpid_name(df)
    fill_na_fields(df)

    ### Create tiles for ranked combined barriers
    ranked_barriers = df.loc[
        df.Ranked,
        ["geometry", "BarrierType", "id", "SARPIDName", "upNetID", "TotDASqKm"] + COMBINED_TILE_FILTER_FIELDS,
    ]

    # create tiles for low zooms
    tmp = ranked_barriers.loc[ranked_barriers.TotDASqKm >= 1][
        ["geometry", "id", "BarrierType"] + COMBINED_TILE_FILTER_FIELDS
    ]

    print(f"Creating tiles for {len(tmp):,} ranked {network_type} with networks for zooms 2-7")

    outfilename = tmp_dir / "combined_barriers_lt_z8.fgb"
    mbtiles_filename = tmp_dir / "combined_barriers_lt_z8.mbtiles"
    mbtiles_files = [mbtiles_filename]
    tmp = to_lowercase(tmp)
    write_dataframe(tmp.reset_index(drop=True), outfilename)

    ret = subprocess.run(
        tippecanoe_args
        + ["-Z0", "-z7", "-r1.5", "-g1.5", "-B5"]
        + ["-l", f"ranked_{network_type}"]
        + ["-o", f"{str(mbtiles_filename)}"]
        + get_col_types(tmp)
        + [str(outfilename)]
    )
    ret.check_returncode()

    ranked_barriers = ranked_barriers.drop(columns=["TotDASqKm"])

    ### Create tiles for ranked combined barriers with networks
    print(f"Creating tiles for {len(ranked_barriers):,} {network_type} barriers with networks")

    outfilename = tmp_dir / f"ranked_{network_type}.fgb"
    mbtiles_filename = tmp_dir / f"ranked_{network_type}.mbtiles"
    mbtiles_files.append(mbtiles_filename)
    ranked_barriers = to_lowercase(ranked_barriers)
    write_dataframe(ranked_barriers.reset_index(drop=True), outfilename)

    ret = subprocess.run(
        tippecanoe_args
        + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
        + ["-l", f"ranked_{network_type}"]
        + ["-o", f"{str(mbtiles_filename)}"]
        + get_col_types(ranked_barriers)
        + [str(outfilename)]
    )
    ret.check_returncode()

    ### Create tiles for unranked combined barriers with networks
    unranked_barriers = df.loc[
        df.HasNetwork & (~(df.Ranked | df.Removed)),
        ["geometry", "id", "SARPIDName", "BarrierType", "upNetID", "symbol"],
    ]

    print(f"Creating tiles for {len(unranked_barriers):,} unranked {network_type} barriers with networks")

    outfilename = tmp_dir / f"unranked_{network_type}.fgb"
    mbtiles_filename = tmp_dir / f"unranked_{network_type}.mbtiles"
    mbtiles_files.append(mbtiles_filename)
    unranked_barriers = to_lowercase(unranked_barriers)
    write_dataframe(unranked_barriers.reset_index(drop=True), outfilename)

    ret = subprocess.run(
        tippecanoe_args
        + ["-Z8", f"-z{MAX_ZOOM}", "-B8"]
        + ["-l", f"unranked_{network_type}"]
        + ["-o", f"{str(mbtiles_filename)}"]
        + get_col_types(unranked_barriers)
        + [str(outfilename)]
    )
    ret.check_returncode()

    ### Create tiles for removed barriers
    removed_barriers = df.loc[
        df.Removed,
        # TODO: network IDs
        ["geometry", "id", "SARPIDName", "BarrierType"],
    ]
    print(f"Creating tiles for {len(removed_barriers)} removed barriers")

    outfilename = tmp_dir / f"removed_{network_type}.fgb"
    mbtiles_filename = tmp_dir / f"removed_{network_type}.mbtiles"
    mbtiles_files.append(mbtiles_filename)
    removedr_barriers = to_lowercase(removed_barriers)
    write_dataframe(removed_barriers, outfilename)

    ret = subprocess.run(
        tippecanoe_args
        + ["-Z6", f"-z{MAX_ZOOM}", "-B6"]
        + ["-l", f"removed_{network_type}"]
        + ["-o", f"{str(mbtiles_filename)}"]
        + get_col_types(other_barriers)
        + [str(outfilename)]
    )
    ret.check_returncode()

    ### Create tiles for all other barriers; these don't have network info
    other_barriers = df.loc[
        (~df.HasNetwork) & (~df.Removed),
        ["geometry", "id", "SARPIDName", "BarrierType", "symbol"],
    ]
    print(f"Creating tiles for {len(other_barriers)} other barriers")

    outfilename = tmp_dir / f"other_{network_type}.fgb"
    mbtiles_filename = tmp_dir / f"other_{network_type}.mbtiles"
    mbtiles_files.append(mbtiles_filename)
    other_barriers = to_lowercase(other_barriers)
    write_dataframe(other_barriers, outfilename)

    ret = subprocess.run(
        tippecanoe_args
        + ["-Z6", f"-z{MAX_ZOOM}", "-B10"]
        + ["-l", f"other_{network_type}"]
        + ["-o", f"{str(mbtiles_filename)}"]
        + get_col_types(other_barriers)
        + [str(outfilename)]
    )
    ret.check_returncode()

    print(f"Joining {network_type} tilesets")
    mbtiles_filename = out_dir / f"{network_type}.mbtiles"
    ret = subprocess.run(tilejoin_args + ["-o", str(mbtiles_filename)] + [str(f) for f in mbtiles_files])

    # remove intermediates
    # FIXME:
    # for mbtiles_file in mbtiles_files:
    #     mbtiles_file.unlink()

    print(f"Created {network_type} tiles in {time() - start:,.2f}s")


####################################################################
### Create road crossing tiles
####################################################################
print("\n\n-----------------Creating road crossing tiles------------------------\n\n")

df = (
    gp.read_feather(
        barriers_dir / "road_crossings.feather",
        columns=[
            "geometry",
            "id",
            "SARPID",
            "Name",
            "TotDASqKm",
            "loop",
            "offnetwork_flowline",
            "NearestBarrierID",
        ],
    )
    .to_crs("EPSG:4326")
    .sort_values(by="TotDASqKm", ascending=False)
    .drop(columns=["TotDASqKm"])
)

# drop any on loops or off-network flowlines; these are not useful to show
# drop any that have a nearest barrier ID; these duplicate barriers in the analysis
df = df.loc[~(df.loop | df.offnetwork_flowline | (df.NearestBarrierID != ""))].drop(
    columns=["loop", "offnetwork_flowline", "NearestBarrierID"]
)

df = combine_sarpid_name(df)
fill_na_fields(df)

outfilename = tmp_dir / "road_crossings.fgb"
mbtiles_filename = out_dir / "road_crossings.mbtiles"
df = to_lowercase(df)
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

###################################################################
## Create waterfalls tiles
###################################################################
print("\n\n-----------------Creating waterfalls tiles------------------------\n\n")
print("Creating waterfalls tiles")
df = gp.read_feather(
    results_dir / "waterfalls.feather",
    columns=[
        "geometry",
        "id",
        "SARPID",
        "Name",
        "network_type",
        "upNetID",
        "TotDASqKm",
    ],
)

# pivot network IDs into one column per network type for tiles, then join back to single record
network_ids = (
    df[["id", "network_type", "upNetID"]].pivot(columns=["network_type"], index="id").fillna(-1).astype("int64")
)
network_ids.columns = [f"{network}_{col}" for col, network in network_ids.columns]

df = (
    df.drop(columns=["network_type", "upNetID"])
    .groupby("id")
    .first()
    .join(network_ids)
    .reset_index()
    .sort_values(by=["TotDASqKm"], ascending=False)
    .drop(columns=["TotDASqKm"])
    .set_crs(df.crs)
    .to_crs("EPSG:4326")
)

df = combine_sarpid_name(df)
fill_na_fields(df)

outfilename = tmp_dir / "waterfalls.fgb"
mbtiles_filename = out_dir / "waterfalls.mbtiles"
df = to_lowercase(df)
write_dataframe(df.reset_index(drop=True), outfilename)

ret = subprocess.run(
    tippecanoe_args
    + ["-Z9", f"-z{MAX_ZOOM}", "-B10"]
    + ["-l", "waterfalls"]
    + ["-o", f"{str(mbtiles_filename)}"]
    + get_col_types(df)
    + [str(outfilename)]
)
ret.check_returncode()
