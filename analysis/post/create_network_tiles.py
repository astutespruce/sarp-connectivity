from pathlib import Path
import subprocess
from time import time

import numpy as np
import pandas as pd
import geopandas as gp
import pyarrow as pa
import pyarrow.compute as pc
import shapely
from pyogrio import write_dataframe

from analysis.constants import GEO_CRS, NETWORK_TYPES, CRS
from analysis.lib.io import read_arrow_tables
from analysis.lib.geometry.lines import merge_lines

src_dir = Path("data/networks")
intermediate_dir = Path("data/tiles")
out_dir = Path("tiles")
tmp_dir = Path("/tmp")

# map sizeclasses
sizeclasses = [2, 5, 25, 100, 250, 500, 5000, 25000, 50000, 500000, 2000000]


def classify_size(series):
    bins = sizeclasses + [max(series.max(), 2000000) + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(1, len(bins)))
    ).astype("uint8")


zoom_config = [
    {
        "zoom": [3, 4],
        "sizeclass": 8,
        "streamlevel": 3,
        "simplification": 1000,
        "scope": "national",
    },
    {
        "zoom": [5, 5],
        "sizeclass": 7,
        "streamlevel": 5,
        "simplification": 1000,
        "scope": "national",
    },
    {
        "zoom": [6, 6],
        "sizeclass": 5,
        "simplification": 500,
        "scope": "national",
    },
    {
        "zoom": [7, 7],
        "sizeclass": 4,
        "simplification": 250,
        "scope": "national",
    },
    {
        "zoom": [8, 8],
        "sizeclass": 3,
        "simplification": 100,
        "scope": "national",
    },
    {
        "zoom": [9, 9],
        "sizeclass": 2,
        "simplification": 50,
        "scope": "national",
    },
    {
        "zoom": [10, 10],
        "sizeclass": 1,
        "simplification": 10,
        "scope": "national",
    },
    {"zoom": [11, 16], "sizeclass": 0, "simplification": 0},
]


tippecanoe = "tippecanoe"
tile_join = "tile-join"

col_types = [
    "-T",
    "dams:int",
    "-T",
    "small_barriers:int",
    "-T",
    "sizeclass:int",
    "-T",
    "mapcode:int",
]

tippecanoe_args = [
    tippecanoe,
    "-f",
    "-l",
    "networks",
    "-pg",
    "--visvalingam",
] + col_types


start = time()

network_cols = list(NETWORK_TYPES.keys())
merge_cols = network_cols + ["sizeclass", "mapcode"]


print("Loading data")

groups_df = pd.read_feather(src_dir / "connected_huc2s.feather")
huc2s = sorted(groups_df.HUC2.unique())

segments = (
    read_arrow_tables(
        [src_dir / "clean" / huc2 / "network_segments.feather" for huc2 in huc2s],
        columns=["lineID"] + network_cols,
    )
    .combine_chunks()
    .sort_by("lineID")
)


flowline_paths = [src_dir / "raw" / huc2 / "flowlines.feather" for huc2 in huc2s]
flowlines = (
    read_arrow_tables(
        flowline_paths,
        columns=[
            "lineID",
            "intermittent",
            "altered",
            "TotDASqKm",
        ],
    )
    .combine_chunks()
    .sort_by("lineID")
)

# combine intermittent and altered into a single uint value
# codes are:
# 0: regular flowline
# 1: intermittent flowline
# 2: altered flowline
# 3: altered intermittent flowline
mapcode = np.zeros((len(flowlines),), dtype="uint8")
mapcode[flowlines["intermittent"]] = 1
mapcode[pc.and_not(flowlines["altered"], flowlines["intermittent"])] = 2
mapcode[pc.and_(flowlines["altered"], flowlines["intermittent"])] = 3

flowlines = pa.Table.from_pydict(
    {
        "lineID": flowlines["lineID"],
        "sizeclass": classify_size(flowlines["TotDASqKm"].to_numpy()),
        "mapcode": mapcode,
    }
).join(segments, "lineID")


################## Create tiles #######################
mbtiles_files = []

### For lower zooms, build tiles across all regions for efficiency
national_levels = [l for l in zoom_config if l.get("scope") == "national"]

# read in the highest level of detail for national level and aggregate
level = national_levels[-1]
lines = (
    read_arrow_tables(
        flowline_paths,
        columns=["lineID", "geometry", "StreamLevel"],
        filter=pc.field("TotDASqKm") >= sizeclasses[level["sizeclass"]],
    )
    .join(
        flowlines.filter(pc.field("sizeclass") >= level["sizeclass"]),
        "lineID",
    )
    .to_pandas()
)
lines["geometry"] = shapely.from_wkb(lines.geometry.values)
lines = gp.GeoDataFrame(lines, crs=CRS)

# preliminary merge to reduce complexity
lines = merge_lines(
    lines,
    by=network_cols + ["sizeclass", "mapcode", "StreamLevel"],
).sort_values(by=network_cols)

# fix dtypes after merge
lines["sizeclass"] = lines.sizeclass.astype("uint8")
lines["mapcode"] = lines.mapcode.astype("uint8")

for level in national_levels:
    minzoom, maxzoom = level["zoom"]
    ix = lines.sizeclass >= level["sizeclass"]
    if "streamlevel" in level:
        ix = ix & (lines.StreamLevel <= level["streamlevel"])
    subset = lines.loc[ix].copy()

    print(f"Processing zooms {minzoom}-{maxzoom} ({len(subset):,} flowlines)")

    # suppress styling of intermittent / altered at low zooms
    if maxzoom < 8:
        subset["mapcode"] = 0

    subset = merge_lines(
        subset.explode(ignore_index=True),
        by=network_cols + ["sizeclass", "mapcode"],
    ).sort_values(by=network_cols)

    # fix dtypes after merge
    subset["sizeclass"] = subset.sizeclass.astype("uint8")
    subset["mapcode"] = subset.mapcode.astype("uint8")

    subset["geometry"] = shapely.simplify(subset["geometry"], level["simplification"])

    outfilename = tmp_dir / f"flowlines_{minzoom}_{maxzoom}.fgb"
    mbtiles_filename = tmp_dir / f"flowlines_{minzoom}_{maxzoom}.mbtiles"
    mbtiles_files.append(mbtiles_filename)

    write_dataframe(
        subset.to_crs(GEO_CRS),
        outfilename,
    )

    del subset  # free up memory

    ret = subprocess.run(
        tippecanoe_args
        + ["-Z", str(minzoom), "-z", str(maxzoom)]
        + ["-o", f"{str(mbtiles_filename)}", str(outfilename)]
    )
    ret.check_returncode()

    # remove FGB file
    outfilename.unlink()


######################


regional_levels = [l for l in zoom_config if l.get("scope") != "national"]

for group in groups_df.groupby("group").HUC2.apply(set).values:
    group = sorted(group)

    print(f"\n\n===========================\nProcessing group {group}")

    # create output files by HUC2 based on where the segments occur
    for huc2 in group:
        print(f"----------------------\nProcessing {huc2}")

        huc2_start = time()

        lines = (
            pa.dataset.dataset(
                src_dir / "raw" / huc2 / "flowlines.feather", format="feather"
            )
            .to_table(
                columns=["lineID", "geometry"],
            )
            .join(flowlines, "lineID")
            .to_pandas()
        )
        lines["geometry"] = shapely.from_wkb(lines.geometry.values)

        # aggregate by sizeclass / map code
        lines = merge_lines(
            gp.GeoDataFrame(lines, crs=CRS),
            by=network_cols + ["sizeclass", "mapcode"],
        ).sort_values(by=network_cols)

        # fix dtypes after merge
        lines["sizeclass"] = lines.sizeclass.astype("uint8")
        lines["mapcode"] = lines.mapcode.astype("uint8")

        for level in regional_levels:
            minzoom, maxzoom = level["zoom"]
            simplification = level["simplification"]
            sizeclass = level["sizeclass"]

            print(
                f"Extracting size class >= {sizeclass} for zooms {minzoom} - {maxzoom}"
            )
            subset = lines.loc[lines.sizeclass >= sizeclass].copy()

            if simplification:
                print(f"simplifying to {simplification} m")
                subset["geometry"] = shapely.simplify(
                    subset.geometry.values.data, simplification
                )

            outfilename = tmp_dir / f"region{huc2}_flowlines_{minzoom}_{maxzoom}.fgb"
            mbtiles_filename = (
                tmp_dir / f"region{huc2}_flowlines_{minzoom}_{maxzoom}.mbtiles"
            )
            mbtiles_files.append(mbtiles_filename)

            write_dataframe(
                subset.to_crs(GEO_CRS),
                outfilename,
            )

            del subset

            ret = subprocess.run(
                tippecanoe_args
                + ["-Z", str(minzoom), "-z", str(maxzoom)]
                + ["-o", f"{str(mbtiles_filename)}", str(outfilename)]
            )
            ret.check_returncode()

            # remove FGB file
            outfilename.unlink()

        print(f"Region done in {(time() - huc2_start) / 60:,.2f}m")


print("\n\n============================\nCombining tiles")
mbtiles_filename = out_dir / "networks.mbtiles"
ret = subprocess.run(
    [
        tile_join,
        "-f",
        "-pg",
        "-o",
        str(mbtiles_filename),
    ]
    + [str(f) for f in mbtiles_files],
)
ret.check_returncode()


# Cleanup intermediate tiles
for filename in mbtiles_files:
    filename.unlink()


print(f"\n\n======================\nAll done in {(time() - start) / 60:,.2f}m")
