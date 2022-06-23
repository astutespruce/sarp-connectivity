from pathlib import Path
import subprocess
from time import time

import numpy as np
import pandas as pd
import geopandas as gp
import pygeos as pg
from pyogrio import write_dataframe

from analysis.constants import GEO_CRS
from analysis.lib.io import read_feathers
from analysis.lib.geometry.lines import merge_lines
from analysis.post.lib.tiles import get_col_types

src_dir = Path("data/networks")
intermediate_dir = Path("data/tiles")
out_dir = Path("tiles")
tmp_dir = Path("/tmp")


def classify_size(series):
    # map sizeclasses are 0-2, 3-4, 5-9, 10-99, 100-499, 500-9999, 10000 - 24999, >25000 km2
    bins = [-1, 0, 2, 5, 10, 50, 100, 500, 10000, 25000] + [
        max(series.max(), 25000) + 1
    ]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(-1, len(bins) - 2))
    ).astype("uint8")


# Simplification level in meters
simplification = {5: 1000, 4: 500, 3: 250, 2: 100, 1: 100}


zoom_config = [
    {"zoom": [5, 5], "size": 6, "simplification": 1000},
    {"zoom": [6, 6], "size": 5, "simplification": 500},
    {"zoom": [7, 7], "size": 4, "simplification": 250},
    {"zoom": [8, 8], "size": 3, "simplification": 100},
    {"zoom": [9, 9], "size": 2, "simplification": 50},
    {"zoom": [10, 10], "size": 1, "simplification": 10},
    {"zoom": [11, 16], "size": 0, "simplification": 0},
]


zoom_levels = {
    5: [5, 5],
    4: [6, 6],
    3: [6, 8],
    2: [9, 9],
    1: [10, 10],
    0: [11, 16],
}


tippecanoe_args = [
    "tippecanoe",
    "-f",
    "-l",
    "networks",
    "-P",
    "-pg",
]

start = time()


groups_df = pd.read_feather(src_dir / "connected_huc2s.feather")

region_tiles = []

for group in groups_df.groupby("group").HUC2.apply(set).values:
    group = sorted(group)

    print(f"\n\n===========================\nProcessing group {group}")
    segments = read_feathers(
        [src_dir / "clean" / huc2 / "network_segments.feather" for huc2 in group],
        columns=[
            "lineID",
            "dams",
            "small_barriers",
        ],
    ).set_index("lineID")

    # create output files by HUC2 based on where the segments occur
    for huc2 in group:
        print(f"----------------------\nProcessing {huc2}")

        huc2_start = time()

        huc2_mbtiles_filename = intermediate_dir / f"region{huc2}_networks.mbtiles"
        region_tiles.append(huc2_mbtiles_filename)

        if huc2_mbtiles_filename.exists():
            print("already exists, skipping")
            continue

        flowlines = gp.read_feather(
            src_dir / "raw" / huc2 / "flowlines.feather",
            columns=[
                "lineID",
                "geometry",
                "intermittent",
                "altered",
                "TotDASqKm",
            ],
        ).set_index("lineID")
        flowlines = flowlines.join(segments)

        # set custom size class for mapping
        flowlines["sizeclass"] = classify_size(flowlines.TotDASqKm)

        # combine intermittent and altered into a single uint value
        flowlines["mapcode"] = 0
        flowlines.loc[flowlines.intermittent, "mapcode"] = 1
        flowlines.loc[(~flowlines.intermittent) & flowlines.altered, "mapcode"] = 2
        flowlines.loc[flowlines.intermittent & flowlines.altered, "mapcode"] = 3
        flowlines.mapcode = flowlines.mapcode.astype("uint8")
        flowlines = flowlines.drop(columns=["intermittent", "altered"])

        # aggregate to MultiLineStrings for smaller outputs
        print("Aggregating flowlines to networks")
        flowlines = merge_lines(
            flowlines,
            by=["dams", "small_barriers", "sizeclass", "mapcode"],
        ).sort_values(by="dams")

        mbtiles_files = []
        col_types = get_col_types(
            flowlines[["dams", "small_barriers", "sizeclass", "mapcode"]]
        )

        for level in zoom_config:
            minzoom, maxzoom = level["zoom"]
            simplification = level["simplification"]
            size_threshold = level["size"]

            print(
                f"Extracting size class >= {size_threshold} for zooms {minzoom} - {maxzoom} (simplifying to {simplification})"
            )
            subset = flowlines.loc[flowlines.sizeclass >= size_threshold].copy()

            if maxzoom < 8:
                # exclude altered flowlines at low zooms
                subset = subset.loc[subset.mapcode < 2].copy()

            if simplification:
                subset["geometry"] = pg.simplify(
                    subset.geometry.values.data, simplification
                )

            json_filename = tmp_dir / f"region{huc2}_{minzoom}_{maxzoom}_flowlines.json"
            mbtiles_filename = (
                tmp_dir / f"region{huc2}_{minzoom}_{maxzoom}_flowlines.mbtiles"
            )
            mbtiles_files.append(mbtiles_filename)

            write_dataframe(
                subset.to_crs(GEO_CRS),
                json_filename,
                driver="GeoJSONSeq",
            )

            del subset

            ret = subprocess.run(
                tippecanoe_args
                + ["-Z", str(minzoom), "-z", str(maxzoom)]
                + ["-o", f"{str(mbtiles_filename)}", str(json_filename)]
                + col_types
            )
            ret.check_returncode()

            # remove JSON file
            json_filename.unlink()

        print("Combining tilesets")
        ret = subprocess.run(
            [
                "tile-join",
                "-f",
                "-pg",
                "-o",
                str(huc2_mbtiles_filename),
            ]
            + [str(f) for f in mbtiles_files],
        )
        ret.check_returncode()

        # remove temporary tilesets
        for f in mbtiles_files:
            f.unlink()

        print(f"Region done in {(time() - huc2_start) / 60:,.2f}m")


print("\n\n============================\nCombining tiles for all regions")
mbtiles_filename = out_dir / "networks.mbtiles"
ret = subprocess.run(
    [
        "tile-join",
        "-f",
        "-pg",
        "-o",
        str(mbtiles_filename),
    ]
    + [str(f) for f in region_tiles],
)
ret.check_returncode()

print(f"\n\n======================\nAll done in {(time() - start) / 60:,.2f}m")
