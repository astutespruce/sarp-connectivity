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
RESERVOIR_COLS = ["NHDPlusID", "FType", "AreaSqKm", "geometry"]

# Exclude swamp/marsh (466), estuaries (493), playas (361).
# NOTE: they do not cut the flowlines in the same
# way as other waterbodies, so they will cause issues.
EXCLUDE_FTYPE = [361, 466, 493]

src_dir = Path("data/nhd/source/huc4")
nhd_dir = Path("data/nhd")

start = time()

for region, HUC2s in REGION_GROUPS.items():
    print("\n----- {} ------\n".format(region))

    out_dir = nhd_dir / "waterbodies" / region

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if os.path.exists(out_dir / "waterbodies.feather"):
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

            df = df.loc[(df.AreaSqKm >= MIN_SQ_KM) & (~df.FType.isin(EXCLUDE_FTYPE))][
                RESERVOIR_COLS
            ].copy()

            df.geometry = df.geometry.apply(to2D)
            df = df.to_crs(CRS)

            df.AreaSqKm = df.AreaSqKm.astype("float32")
            df.FType = df.FType.astype("uint16")

            if merged is None:
                merged = df
            else:
                merged = merged.append(df, ignore_index=True)

    print("--------------------")
    print("Extracted {:,} waterbodies in this region".format(len(merged)))
    df = merged.reset_index(drop=True)

    # add our own ID
    df["wbID"] = df.index.values.copy()
    df.wbID = (df.wbID + 1).astype("uint32")

    ### Join waterbodies to flowlines
    # Keep only the waterbodies that intersect flowlines
    print("Reading flowlines...")
    flowlines = from_geofeather(
        nhd_dir / "flowlines" / region / "flowline.feather",
        columns=["geometry", "lineID", "length"],
    ).set_index("lineID")
    joins = deserialize_df(
        nhd_dir / "flowlines" / region / "flowline_joins.feather",
        columns=["downstream_id", "upstream_id"],
    )

    print(
        "Creating spatial index on waterbodies and flowlines, this might take a while..."
    )

    wb = df[["geometry", "wbID"]]
    wb.sindex

    lines = flowlines[["geometry"]]
    lines.sindex

    print("Joining waterbodies to flowines")

    join_start = time()
    joined = gp.sjoin(wb, lines, how="inner", op="intersects").rename(
        columns={"index_right": "lineID"}
    )
    print("Joined {:,} flowlines in {:,}".format(len(joined), time() - join_start))

    # join in flowline geometry and attributes
    joined = joined.join(flowlines.rename(columns={"geometry": "line"}), on="lineID")

    ### Rerun the spatial join on the subset of waterbodies and flowlines that intersect
    # No idea why this is faster than just running .contains() on the line, but it is.

    print("Identifying flowlines that are completely contained by waterbodies...")

    # Extract waterbodies that had joins, and rebuild index
    wb = wb.loc[wb.wbID.isin(joined.wbID)].copy()
    wb.sindex

    # Figure out those that are contained, so we can sidestep cutting them.
    # Extract subset of the lines that we intersected above, which are
    # completely contained by waterbodies.

    lines = lines.loc[lines.index.isin(joined.lineID)].copy()
    lines.sindex

    join_start = time()
    contained = gp.sjoin(wb, lines, how="inner", op="contains").rename(
        columns={"index_right": "lineID"}
    )
    print(
        "Identified {:,} flowlines contained by waterbodies in {:,}".format(
            len(contained), time() - join_start
        )
    )

    # NOTE: some lines may be touched by multiple polygons, but should only be contained by one
    # any that aren't completely contained should be evaluated via intersection
    contained["contained"] = True
    joined = (
        joined.set_index(["wbID", "lineID"])
        .join(contained.set_index(["wbID", "lineID"]).contained)
        .reset_index()
    )
    joined.contained = joined.contained.fillna(False)

    # Copy the contained lines across as geometry
    lines = gp.GeoSeries(joined.line)
    idx = joined.contained
    joined.loc[idx, "geometry"] = lines.loc[idx]

    # Run the intersection on the remainder
    print("Cutting flowlines by waterbodies, this might take a really long while...")
    # WARNING: intersection may produce a variety of geometry type outputs: Point, MultiPoint, etc
    # Only LineString is valid
    cut_start = time()
    idx = ~joined.contained
    joined.loc[idx, "geometry"] = joined.loc[idx].geometry.intersection(lines.loc[idx])

    ### Cleanup geometry issues
    # MultiLineStrings are cases where they cross the edge, likely due to poor position of flowline
    # within waterbody.  Just grab the original uncut line.
    idx = joined.geometry.type == "MultiLineString"
    joined.loc[idx, "geometry"] = gp.GeoSeries(joined[idx].line)

    # Drop everything else (Point, MultiPoint)
    joined = joined.loc[joined.geometry.type == "LineString"].copy()

    print(
        "Retained {:,} flowlines after cutting in {:,}".format(
            len(contained), time() - cut_start
        )
    )

    joined = joined.drop(columns=["line"])
    joined["length"] = joined.length

    wb_stats = (
        joined.groupby("wbID")
        .agg({"length": "sum", "lineID": "count"})
        .rename(columns={"lineID": "numSegments", "length": "flowlineLength"})
    )
    wb_stats.numSegments = wb_stats.numSegments.astype("uint16")
    wb_stats.flowlineLength = wb_stats.flowlineLength.astype("float32")

    serialize_df(
        joined[["wbID", "lineID"]].join(wb_stats, on="wbID").reset_index(drop=True),
        out_dir / "waterbody_flowline_joins.feather",
    )

    print("Dropping all waterbodies that do not intersect flowlines")
    df = df.join(wb_stats, on="wbID", how="inner").reset_index(drop=True)

    print("serializing {:,} waterbodies to feather".format(len(df)))
    to_geofeather(df, out_dir / "waterbodies.feather")

    ### Find the downstream most point(s) on the flowline for each waterbody
    # this is used for snapping barriers, if possible
    tmp = joined[["lineID", "wbID"]].set_index("lineID")
    drains = (
        joins.loc[joins.upstream_id.isin(joined.lineID)]
        .join(tmp.wbID.rename("upstream_wbID"), on="upstream_id")
        .join(tmp.wbID.rename("downstream_wbID"), on="downstream_id")
    )

    # Only keep those that terminate outside the same waterbody as the upstream end
    drains = drains.loc[drains.upstream_wbID != drains.downstream_wbID].copy()

    drain_pts = (
        joined.loc[joined.lineID.isin(drains.upstream_id)]
        .join(wb_stats, on="wbID")
        .join(df.set_index("wbID")[["AreaSqKm"]], on="wbID")
        .drop(columns=["length", "contained"])
        .reset_index(drop=True)
    )

    # create a point from the last coordinate, which is the furthest one downstream
    drain_pts.geometry = drain_pts.geometry.apply(
        lambda g: Point(np.column_stack(g.xy)[-1])
    )

    drain_pts.wbID = drain_pts.wbID.astype("uint32")
    drain_pts.lineID = drain_pts.lineID.astype("uint32")
    drain_pts.flowlineLength = drain_pts.flowlineLength.astype("float32")

    to_geofeather(drain_pts, out_dir / "waterbody_drain_points.feather")

    print("Region done in {:.0f}s".format(time() - region_start))


print("Done in {:.2f}s\n============================".format(time() - start))
