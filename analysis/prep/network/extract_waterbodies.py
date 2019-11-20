"""Extract waterbodies to use for the network analysis.

These are used to determine the distance of stream segments that are through waterbodies, and thus
have a different character than free-running stream segments.

Reservoir types listing: https://prd-wret.s3-us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/NHDv2.2.1_poster_081216.pdf
"""
from pathlib import Path
import os
from time import time

import geopandas as gp
import numpy as np
from shapely.geometry import Point
from geofeather import to_geofeather, from_geofeather
from nhdnet.geometry.polygons import to2D
from nhdnet.io import serialize_df, deserialize_df, serialize_sindex, to_shp


from analysis.constants import REGIONS, REGION_GROUPS, CRS, EXCLUDE_IDs

MIN_SQ_KM = 0.001
RESERVOIR_COLS = ["wbID", "NHDPlusID", "FType", "AreaSqKm", "geometry"]


src_dir = Path("data/nhd/source/huc4")
out_dir = Path("data/nhd/flowlines")

start = time()

for region, HUC2s in REGION_GROUPS.items():
    print("\n----- {} ------\n".format(region))

    region_dir = out_dir / region

    if os.path.exists(region_dir / "reservoir.feather"):
        print("Skipping existing region {}".format(region))
        continue

    region_start = time()

    merged = None
    for HUC2 in HUC2s:
        for i in REGIONS[HUC2]:
            HUC4 = "{0}{1:02d}".format(HUC2, i)

            read_start = time()
            print("\n\n------------------- Reading {} -------------------".format(HUC4))
            gdb = src_dir / HUC4 / "NHDPLUS_H_{HUC4}_HU4_GDB.gdb".format(HUC4=HUC4)

            df = gp.read_file(gdb, layer="NHDWaterbody")
            df.NHDPlusID = df.NHDPlusID.astype("uint64")

            # add our own ID
            df["wbID"] = df.index.values.astype("uint32") + 1

            df = df.loc[df.AreaSqKm >= MIN_SQ_KM][RESERVOIR_COLS].copy()

            df.geometry = df.geometry.apply(to2D)
            df = df.to_crs(CRS)

            if merged is None:
                merged = df
            else:
                merged = merged.append(df, ignore_index=True)

    print("--------------------")
    print("Extracted {:,} waterbodies in this region".format(len(merged)))
    df = merged

    ### Join waterbodies to flowlines
    # Keep only the waterbodies that intersect flowlines
    print("Reading flowlines...")
    flowlines = from_geofeather(region_dir / "flowline.feather")[
        ["geometry", "lineID", "length"]
    ]
    joins = deserialize_df(region_dir / "flowline_joins.feather")

    print(
        "Creating spatial index on waterbodies and flowlines, this might take a while..."
    )
    df.sindex
    flowlines.sindex

    print("Joining waterbodies to flowines")
    joined = gp.sjoin(
        df[["wbID", "geometry"]],
        flowlines[["lineID", "length", "geometry"]],
        how="left",
        op="contains",
    )
    joined = joined.loc[joined.lineID.notnull(), ["wbID", "lineID", "length"]]
    joined.lineID = joined.lineID.astype("uint32")

    serialize_df(
        joined[["wbID", "lineID"]].reset_index(drop=True),
        region_dir / "waterbody_flowline_joins.feather",
    )

    wb_stats = (
        joined.groupby("wbID")
        .agg({"length": "sum", "lineID": "count"})
        .rename(columns={"lineID": "numSegments", "length": "flowlineLength"})
    )

    print("Dropping all waterbodies that do not intersect flowlines")
    df = df.join(wb_stats, on="wbID", how="inner")

    print("serializing {:,} waterbodies to feather".format(len(df)))
    to_geofeather(df.reset_index(drop=True), region_dir / "waterbodies.feather")

    # Find the downstream most point(s) on the flowline for each waterbody
    in_wb = flowlines.loc[flowlines.lineID.isin(joined.lineID)]
    drain_ids = joins.loc[
        joins.upstream_id.isin(in_wb.lineID) & (~joins.downstream_id.isin(in_wb.lineID))
    ].upstream_id

    drain_pts = (
        in_wb.loc[in_wb.lineID.isin(drain_ids), ["lineID", "geometry"]]
        .join(joined.set_index("lineID")[["wbID"]], on="lineID")
        .join(wb_stats, on="wbID")
        .join(df.set_index("wbID")[["AreaSqKm"]], on="wbID")
    )

    # create a point from the last coordinate, which is the furthest one downstream
    drain_pts.geometry = drain_pts.geometry.apply(
        lambda g: Point(np.column_stack(g.xy)[-1])
    )

    to_geofeather(
        drain_pts.reset_index(drop=True), region_dir / "waterbody_drain_points.feather"
    )

    print("serializing to shp")
    serialize_start = time()
    to_shp(df.reset_index(drop=True), region_dir / "waterbodies.shp")

    to_shp(drain_pts.reset_index(drop=True), region_dir / "waterbody_drain_points.shp")

    print("serialize done in {:.0f}s".format(time() - serialize_start))

    print("Region done in {:.0f}s".format(time() - region_start))


print("Done in {:.2f}s\n============================".format(time() - start))
