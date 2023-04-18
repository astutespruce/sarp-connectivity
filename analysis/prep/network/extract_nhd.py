"""
Extract NHD File Geodatabases (FGDB) for all HUC4s within each HUC2.
"""

from pathlib import Path
import os
from time import time
import warnings

import numpy as np
import pandas as pd
import shapely

from analysis.prep.network.lib.nhd import (
    extract_flowlines,
    extract_waterbodies,
    extract_barrier_points,
    extract_barrier_lines,
    extract_barrier_polygons,
    extract_altered_rivers,
    extract_marine,
)

from analysis.constants import CRS
from analysis.lib.util import append


warnings.filterwarnings("ignore", message=".*geometry types are not supported*")


def process_gdbs(huc2, src_dir, out_dir):
    merged_flowlines = None
    merged_joins = None
    merged_waterbodies = None
    merged_points = None
    merged_lines = None
    merged_poly = None
    merged_altered_rivers = None
    merged_marine = None

    # There are up to 4.1M flowlines after cutting by waterbodies and all barriers
    # in the largest HUC2, so assign each HUC2 a contiguous range of 5M to ensure
    # ids are globally unique
    huc2_offset = np.uint32(int(huc2) * 5000000)
    flowlines_offset = huc2_offset.copy()
    waterbodies_offset = huc2_offset.copy()
    nhd_points_offset = huc2_offset.copy()
    nhd_lines_offset = huc2_offset.copy()
    nhd_polygons_offset = huc2_offset.copy()
    altered_rivers_offset = huc2_offset.copy()

    gdbs = sorted(
        [gdb for gdb in src_dir.glob(f"{huc2}*/*.gdb")],
        key=lambda p: p.parent.name,
    )
    if len(gdbs) == 0:
        raise ValueError(
            f"No GDBs available for {huc2} within {src_dir}; did you forget to unzip them?"
        )

    for gdb in gdbs:
        print(f"------------------- Reading {gdb.name} -------------------")

        huc4 = gdb.parent.name[:4]

        ### Read flowlines and joins
        read_start = time()
        flowlines, joins = extract_flowlines(gdb, target_crs=CRS)
        print(f"Read {len(flowlines):,} flowlines in {time() - read_start:.2f} seconds")

        flowlines = flowlines.reset_index(drop=True)
        joins = joins.reset_index(drop=True)

        flowlines["HUC4"] = huc4
        joins["HUC4"] = huc4

        # set lineID range
        flowlines["lineID"] = flowlines.lineID + flowlines_offset
        joins.loc[joins.upstream_id != 0, "upstream_id"] += flowlines_offset
        joins.loc[joins.downstream_id != 0, "downstream_id"] += flowlines_offset
        flowlines_offset = flowlines.lineID.max() + np.uint32(1)

        merged_flowlines = append(merged_flowlines, flowlines)
        merged_joins = append(merged_joins, joins)

        ### Read waterbodies
        read_start = time()
        waterbodies = extract_waterbodies(gdb, target_crs=CRS)
        print(
            "Read {:,} waterbodies in  {:.2f} seconds".format(
                len(waterbodies), time() - read_start
            )
        )

        ### Only retain waterbodies that intersect flowlines
        print("Intersecting waterbodies and flowlines")
        # use waterbodies to query flowlines since there are many more flowlines
        tree = shapely.STRtree(flowlines.geometry.values.data)
        ix = tree.query(waterbodies.geometry.values.data, predicate="intersects")[0]
        waterbodies = waterbodies.iloc[np.unique(ix)].copy()
        print(f"Retained {len(waterbodies):,} waterbodies that intersect flowlines")

        waterbodies["HUC4"] = huc4

        # calculate ids to be unique across region
        waterbodies["wbID"] = (
            np.arange(1, len(waterbodies) + 1, dtype="uint32") + waterbodies_offset
        )
        waterbodies_offset = waterbodies.wbID.max() + np.uint32(1)

        merged_waterbodies = append(merged_waterbodies, waterbodies)

        ### Extract barrier points, lines, polygons
        points = extract_barrier_points(gdb, target_crs=CRS)
        if len(points):
            points["HUC4"] = huc4
            points["id"] = (
                np.arange(1, len(points) + 1, dtype="uint32") + nhd_points_offset
            )
            nhd_points_offset = points.id.max() + np.uint32(1)
            merged_points = append(merged_points, points)

        lines = extract_barrier_lines(gdb, target_crs=CRS)
        if len(lines):
            lines["HUC4"] = huc4
            lines["id"] = (
                np.arange(1, len(lines) + 1, dtype="uint32") + nhd_lines_offset
            )
            nhd_lines_offset = lines.id.max() + np.uint32(1)
            merged_lines = append(merged_lines, lines)

        poly = extract_barrier_polygons(gdb, target_crs=CRS)
        if len(poly):
            poly["HUC4"] = huc4
            poly["id"] = (
                np.arange(1, len(poly) + 1, dtype="uint32") + nhd_polygons_offset
            )
            nhd_polygons_offset = poly.id.max() + np.uint32(1)
            merged_poly = append(merged_poly, poly)

        ### Extract altered rivers
        altered_rivers = extract_altered_rivers(gdb, target_crs=CRS)
        if len(altered_rivers):
            altered_rivers["HUC4"] = huc4
            altered_rivers["id"] = (
                np.arange(len(altered_rivers), dtype="uint32") + altered_rivers_offset
            )
            altered_rivers_offset = altered_rivers.id.max() + np.uint32(1)
            merged_altered_rivers = append(merged_altered_rivers, altered_rivers)

        ### Extract marine
        marine = extract_marine(gdb, target_crs=CRS)
        if len(marine):
            marine["HUC4"] = huc4
            merged_marine = append(merged_marine, marine)

    print("--------------------")

    flowlines = merged_flowlines.reset_index(drop=True)
    joins = merged_joins.reset_index(drop=True)
    waterbodies = merged_waterbodies.reset_index(drop=True)

    if merged_points is not None and len(merged_points):
        points = merged_points.reset_index(drop=True)
    else:
        points = None

    if merged_lines is not None and len(merged_lines):
        lines = merged_lines.reset_index(drop=True)
    else:
        lines = None

    if merged_poly is not None and len(merged_poly):
        poly = merged_poly.reset_index(drop=True)
    else:
        poly = None

    if merged_altered_rivers is not None and len(merged_altered_rivers):
        altered_rivers = merged_altered_rivers.reset_index(drop=True)
    else:
        altered_rivers = None

    if merged_marine is not None and len(merged_marine):
        marine = merged_marine.reset_index(drop=True)
    else:
        marine = None

    ### Deduplicate waterbodies that are duplicated between adjacent HUC4s
    print("Removing duplicate waterbodies, starting with {:,}".format(len(waterbodies)))
    # Calculate a hash of the WKB bytes of the polygon.
    # This correctly catches polygons that are EXACTLY the same.
    # It will miss those that are NEARLY the same.

    waterbodies["hash"] = pd.util.hash_array(
        shapely.to_wkb(waterbodies.geometry.values.data)
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

    # remove the duplicate downstreams that were functionally terminals for their HUC2s but
    # not marked as such (they had an NHDPlusID downstream but no flowlines in their HUC2)
    ix = joins.loc[
        (joins.downstream != 0) & (joins.downstream_id == 0)
    ].upstream.unique()
    joins = joins.loc[~(joins.upstream.isin(ix) & (joins.downstream_id == 0))]

    # remove dead ends
    joins = joins.loc[~((joins.downstream == 0) & (joins.upstream == 0))].reset_index(
        drop=True
    )

    missing_downstream = joins.loc[
        (joins.downstream != 0) & (~joins.downstream.isin(flowlines.NHDPlusID))
    ]
    if len(missing_downstream):
        print("WARNING: downstream side of join is not present in flowlines")
        print("This may be a valid HUC2 exit, or it may be an error in the data")
        print(missing_downstream)

    missing_upstream = joins.loc[
        (joins.upstream != 0) & (~joins.upstream.isin(flowlines.NHDPlusID))
    ]
    if len(missing_upstream):
        print("WARNING: upstream side of join is not present in flowlines")
        print("This may be a valid HUC2 inlet, or it may be an error in the data")
        print(missing_upstream)

    print("\n--------------------")

    print(f"serializing {len(flowlines):,} flowlines")
    flowlines.to_feather(out_dir / "flowlines.feather")
    joins.to_feather(out_dir / "flowline_joins.feather")

    print(f"serializing {len(waterbodies):,} waterbodies")
    waterbodies.to_feather(out_dir / "waterbodies.feather")

    if points is not None and len(points):
        print(f"serializing {len(points):,} NHD barrier points")
        points.to_feather(out_dir / "nhd_points.feather")

    if lines is not None and len(lines):
        print(f"serializing {len(lines):,} NHD barrier lines")
        lines.to_feather(out_dir / "nhd_lines.feather")

    if poly is not None and len(poly):
        print(f"serializing {len(poly):,} NHD barrier polygons")
        poly.to_feather(out_dir / "nhd_poly.feather")

    if altered_rivers is not None and len(altered_rivers):
        print(f"serializing {len(altered_rivers):,} NHD altered rivers")
        altered_rivers.to_feather(out_dir / "nhd_altered_rivers.feather")

    if marine is not None and len(marine):
        print(f"serializing {len(marine):,} NHD marine areas")
        marine.to_feather(out_dir / "nhd_marine.feather")


data_dir = Path("data")
huc4_dir = data_dir / "nhd/source/huc4"
huc8_dir = data_dir / "nhd/source/huc8"
out_dir = data_dir / "nhd/raw"

if not out_dir.exists():
    os.makedirs(out_dir)

start = time()

huc2s = [
    # "01",
    # "02",
    # "03",
    # "04"
    "05",
    # "06",
    "07",
    # "08",
    "09",
    # "10",
    # "11",
    # "12",
    # "13",
    # "14",
    # "15",
    "16",
    # "17",
    "18",
    # "19",
    # "21",
]


for huc2 in huc2s:
    huc2_start = time()
    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2
    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    src_dir = huc8_dir if huc2 == "19" else huc4_dir
    process_gdbs(huc2, src_dir, huc2_dir)

    print("--------------------")
    print("HUC2: {} done in {:.0f}s\n\n".format(huc2, time() - huc2_start))

print("Done in {:.2f}s\n============================".format(time() - start))
