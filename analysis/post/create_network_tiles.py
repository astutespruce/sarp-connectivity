from pathlib import Path
import subprocess
from time import time

import pandas as pd
import geopandas as gp
import pygeos as pg
from pyogrio import write_dataframe

from analysis.constants import GEO_CRS
from analysis.lib.io import read_feathers
from analysis.lib.geometry.lines import aggregate_lines

src_dir = Path("data/networks")
intermediate_dir = Path("data/tiles")
out_dir = Path("tiles")
tmp_dir = Path("/tmp")


# map sizeclass string to uint for smaller files
sizeclasses = {"1a": 0, "1b": 1, "2": 2, "3a": 3, "3b": 4, "4": 4, "5": 5}


tippecanoe_args = [
    "tippecanoe",
    "-f",
    "-l",
    "networks",
    "-P",
    "-pg",
    "-T",
    "intermittent:bool",
]

start = time()


groups_df = pd.read_feather(src_dir / "connected_huc2s.feather")

region_tiles = []

for group in groups_df.groupby("group").HUC2.apply(set).values:
    group = sorted(group)

    print(f"\n\n===========================\nProcessing group {group}")
    segments = read_feathers(
        [src_dir / "clean" / huc2 / "network_segments.feather" for huc2 in group],
        columns=["lineID", "dams", "small_barriers",],
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
            columns=["lineID", "geometry", "intermittent", "sizeclass", "altered"],
        ).set_index("lineID")
        flowlines = flowlines.join(segments)

        # remap sizeclass to uint8
        flowlines["sizeclass"] = flowlines.sizeclass.map(sizeclasses).astype("uint8")

        # aggregate to MultiLineStrings for smaller outputs
        print("Aggregating flowlines to networks")
        flowlines = aggregate_lines(
            flowlines,
            by=["dams", "small_barriers", "sizeclass", "intermittent", "altered"],
        ).sort_values(by="dams")

        mbtiles_files = []

        ### Zoom 6: simplify
        print("Extracting largest flowlines")
        largest = flowlines.loc[flowlines.sizeclass >= 3].copy()
        largest["geometry"] = pg.simplify(
            largest.geometry.values.data, 100, preserve_topology=True
        )

        json_filename = tmp_dir / f"region{huc2}_largest_flowlines.json"
        mbtiles_filename = tmp_dir / f"region{huc2}_largest_flowlines.mbtiles"
        mbtiles_files.append(mbtiles_filename)

        write_dataframe(
            largest.to_crs(GEO_CRS), json_filename, driver="GeoJSONSeq",
        )

        print("Creating tiles for largest flowlines")
        ret = subprocess.run(
            tippecanoe_args
            + ["-Z", "6", "-z", "6"]
            + ["-o", f"{str(mbtiles_filename)}", str(json_filename)]
        )
        ret.check_returncode()

        # remove JSON file
        json_filename.unlink()

        ### Zoom 7-9: simplify and dissolve
        print("Extracting large flowlines")
        large = flowlines.loc[flowlines.sizeclass >= 1].copy()
        large["geometry"] = pg.simplify(
            large.geometry.values.data, 100, preserve_topology=True
        )

        json_filename = tmp_dir / f"region{huc2}_large_flowlines.json"
        mbtiles_filename = tmp_dir / f"region{huc2}_large_flowlines.mbtiles"
        mbtiles_files.append(mbtiles_filename)

        write_dataframe(
            large.to_crs(GEO_CRS), json_filename, driver="GeoJSONSeq",
        )

        print("Creating tiles for large flowlines")
        ret = subprocess.run(
            tippecanoe_args
            + ["-Z", "7", "-z", " 9"]
            + ["-o", f"{str(mbtiles_filename)}", str(json_filename)]
        )
        ret.check_returncode()
        json_filename.unlink()

        ### ~ Zoom 10 - 16
        json_filename = tmp_dir / f"region{huc2}_flowlines.json"
        mbtiles_filename = tmp_dir / f"region{huc2}_flowlines.mbtiles"
        mbtiles_files.append(mbtiles_filename)

        print("Reprojecting all flowlines")
        flowlines = flowlines.to_crs(GEO_CRS)

        print("Serializing all flowlines")
        write_dataframe(
            flowlines, json_filename, driver="GeoJSONSeq",
        )

        print("Creating tiles for all flowlines")
        ret = subprocess.run(
            tippecanoe_args
            + ["-Z", "10", "-z", " 16"]
            + ["-o", f"{str(mbtiles_filename)}", str(json_filename)]
        )
        ret.check_returncode()
        json_filename.unlink()

        print("Combining tilesets")
        ret = subprocess.run(
            ["tile-join", "-f", "-pg", "-o", str(huc2_mbtiles_filename),]
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
    ["tile-join", "-f", "-pg", "-o", str(mbtiles_filename),]
    + [str(f) for f in region_tiles],
)
ret.check_returncode()

print(f"\n\n======================\nAll done in {(time() - start) / 60:,.2f}m")
