"""
Extract NHD File Geodatabases (FGDB) for all HUC4s within each HUC2.

Data are downloaded using `nhd/download.py::download_huc4`.

Only the flowlines, joins between flowlines, and specific attributes are extracted for analysis.

Due to data limitations of the FGDB / Shapefile format, NHDPlus IDs are represented natively as float64 data.
However, float64 data are not ideal for indexing, so all IDs are converted to uint64 within this package, and
converted back to float64 only for export to GIS.

These are output as 3 files:
* flowlines.feather: serialized flowline geometry and attributes
* flowline_joins.feather: serialized joins between adjacent flowlines, with the upstream and downstream IDs of a join
* waterbodies.feather: serialized waterbody geometry and attributes
"""

from pathlib import Path
import os
from time import time
import warnings

import pandas as pd
import pygeos as pg
import numpy as np
from pyogrio import write_dataframe

from analysis.prep.network.lib.nhd import (
    extract_flowlines,
    extract_waterbodies,
    extract_barrier_points,
    extract_barrier_lines,
    extract_barrier_polygons,
)

from analysis.constants import (
    CRS,
    WATERBODY_EXCLUDE_FTYPES,
    WATERBODY_MIN_SIZE,
)
from analysis.lib.pygeos_util import sjoin_geometry
from analysis.lib.util import append


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")
warnings.filterwarnings("ignore", message=".*M values are stripped during reading.*")


def process_huc4s(src_dir, out_dir, huc4s):
    merged_flowlines = None
    merged_joins = None
    merged_waterbodies = None
    merged_points = None
    merged_lines = None
    merged_poly = None

    for huc4 in huc4s:
        print(f"------------------- Reading {huc4} -------------------")

        huc_id = int(huc4) * 1000000

        gdb = src_dir / huc4 / f"NHDPLUS_H_{huc4}_HU4_GDB.gdb"

        ### Read flowlines and joins
        read_start = time()
        flowlines, joins = extract_flowlines(gdb, target_crs=CRS)
        print(
            "Read {:,} flowlines in {:.2f} seconds".format(
                len(flowlines), time() - read_start
            )
        )

        flowlines["HUC4"] = huc4
        joins["HUC4"] = huc4

        # Calculate lineIDs to be unique across all HUC2s
        flowlines["lineID"] += huc_id
        # Set updated lineIDs with the HUC4 prefix
        joins.loc[joins.upstream_id != 0, "upstream_id"] += huc_id
        joins.loc[joins.downstream_id != 0, "downstream_id"] += huc_id

        merged_flowlines = append(merged_flowlines, flowlines)
        merged_joins = append(merged_joins, joins)

        ### Read waterbodies
        read_start = time()
        waterbodies = extract_waterbodies(
            gdb,
            target_crs=CRS,
            exclude_ftypes=WATERBODY_EXCLUDE_FTYPES,
            min_area=WATERBODY_MIN_SIZE,
        )
        print(
            "Read {:,} waterbodies in  {:.2f} seconds".format(
                len(waterbodies), time() - read_start
            )
        )

        waterbodies["HUC4"] = huc4

        # calculate ids to be unique across region
        waterbodies["wbID"] += huc_id

        ### Only retain waterbodies that intersect flowlines
        print("Intersecting waterbodies and flowlines")
        # use waterbodies to query flowlines since there are many more flowlines
        tree = pg.STRtree(flowlines.geometry.values.data)
        left, right = tree.query_bulk(
            waterbodies.geometry.values.data, predicate="intersects"
        )
        waterbodies = waterbodies.iloc[np.unique(left)].copy()
        print(
            "Retained {:,} waterbodies that intersect flowlines".format(
                len(waterbodies)
            )
        )

        merged_waterbodies = append(merged_waterbodies, waterbodies)

        ### Extract barrier points, lines, polygons
        points = extract_barrier_points(gdb, target_crs=CRS)
        points.HUC4 = huc4
        points["id"] += huc_id
        merged_points = append(merged_points, points)

        lines = extract_barrier_lines(gdb, target_crs=CRS)
        lines.HUC4 = huc4
        lines["id"] += huc_id
        merged_lines = append(merged_lines, lines)

        poly = extract_barrier_polygons(gdb, target_crs=CRS)
        poly.HUC4 = huc4
        poly["id"] += huc_id
        merged_poly = append(merged_poly, poly)

    print("--------------------")

    flowlines = merged_flowlines.reset_index(drop=True)
    joins = merged_joins.reset_index(drop=True)
    waterbodies = merged_waterbodies.reset_index(drop=True)
    points = merged_points.reset_index(drop=True)
    lines = merged_lines.reset_index(drop=True)
    poly = merged_poly.reset_index(drop=True)

    ### Deduplicate waterbodies that are duplicated between adjacent HUC4s
    print("Removing duplicate waterbodies, starting with {:,}".format(len(waterbodies)))
    # Calculate a hash of the WKB bytes of the polygon.
    # This correctly catches polygons that are EXACTLY the same.
    # It will miss those that are NEARLY the same.

    waterbodies["hash"] = pd.util.hash_array(
        pg.to_wkb(waterbodies.geometry.values.data)
    )

    id_map = (
        waterbodies.set_index("wbID")[["hash"]]
        .join(waterbodies.groupby("hash").wbID.first(), on="hash")
        .wbID
    )
    # extract out where they are not equal; these are the ones to drop
    waterbodies = (
        waterbodies.loc[waterbodies.wbID.isin(id_map)]
        .drop(columns=["hash"])
        .reset_index(drop=True)
    )
    print("{:,} waterbodies remain after removing duplicates".format(len(waterbodies)))

    ### Update the missing upstream_ids at the joins between HUCs.
    # These are the segments that are immediately DOWNSTREAM of segments that flow into this HUC4
    # We set a new UPSTREAM id for them based on the segment that is next upstream

    huc_in_idx = joins.loc[joins.type == "huc_in"].index
    cross_huc_joins = joins.loc[huc_in_idx]

    new_upstreams = (
        cross_huc_joins.join(
            joins.set_index("downstream").downstream_id.rename("new_upstream"),
            on="upstream",
        )
        .new_upstream.fillna(0)
        .astype("uint32")
    )
    joins.loc[new_upstreams.index, "upstream_id"] = new_upstreams

    # update new internal joins
    joins.loc[(joins.type == "huc_in") & (joins.upstream_id != 0), "type"] = "internal"

    # remove the duplicate downstreams that used to be terminals for their respective HUCs
    joins = joins.loc[
        ~(joins.upstream.isin(cross_huc_joins.upstream) & (joins.type == "terminal"))
    ]

    # remove dead ends
    joins = joins.loc[~((joins.downstream == 0) & (joins.upstream == 0))].reset_index(
        drop=True
    )

    print("\n--------------------")

    print(f"serializing {len(flowlines):,} flowlines")
    flowlines.to_feather(out_dir / "flowlines.feather")
    joins.to_feather(out_dir / "flowline_joins.feather")

    print(f"serializing {len(waterbodies):,} waterbodies")
    waterbodies.to_feather(out_dir / "waterbodies.feather")

    # DEBUG:
    # write_dataframe(flowlines, out_dir / "flowlines.gpkg")
    # write_dataframe(waterbodies, out_dir / "waterbodies.gpkg")

    if len(points):
        print(f"serializing {len(points):,} NHD barrier points")
        points.to_feather(out_dir / "nhd_points.feather")
        # DEBUG:
        # write_dataframe(points, out_dir / 'nhd_points.gpkg')

    if len(lines):
        print(f"serializing {len(lines):,} NHD barrier lines")
        lines.to_feather(out_dir / "nhd_lines.feather")
        # DEBUG:
        # write_dataframe(lines, out_dir / 'nhd_lines.gpkg')

    if len(poly):
        print(f"serializing {len(poly):,} NHD barrier polygons")
        poly.to_feather(out_dir / "nhd_poly.feather")
        # DEBUG:
        # write_dataframe(poly, out_dir / 'nhd_poly.gpkg')


data_dir = Path("data")
src_dir = data_dir / "nhd/source/huc4"
out_dir = data_dir / "nhd/raw"

if not out_dir.exists():
    os.makedirs(out_dir)

start = time()

huc4_df = pd.read_feather(
    data_dir / "boundaries/huc4.feather", columns=["HUC2", "HUC4"]
)
# Convert to dict of sorted HUC4s per HUC2
units = huc4_df.groupby("HUC2").HUC4.unique().apply(sorted).to_dict()

# manually subset keys from above for processing
huc2s = [
    # "02",
    # "03",
    # "05",
    # "06",
    # "07",
    # "08",
    # "09",
    # "10",
    # "11",
    "12",
    "13",
    # "14",
    "15",
    "16",
    "17",
    "21",
]


for huc2 in huc2s:
    huc2_start = time()
    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2
    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    process_huc4s(src_dir, huc2_dir, units[huc2])

    print("--------------------")
    print("HUC2: {} done in {:.0f}s\n\n".format(huc2, time() - huc2_start))

print("Done in {:.2f}s\n============================".format(time() - start))
