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
    df.wbID = df.wbID.astype("uint32") + 1

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
    flowlines.sindex

    print("Joining waterbodies to flowines")
    joined = gp.sjoin(wb, lines, how="inner", op="intersects").rename(
        columns={"index_right": "lineID"}
    )

    # join in flowline geometry and attributes
    joined = joined.join(flowlines.rename(columns={"geometry": "line"}), on="lineID")

    # drop any that just touch; these are typically segments that are already cut at the waterbody
    print("Identifying touching flowlines and dropping them...")

    # TODO: double check this, since it may eliminate any that are on the inside too
    only_touch = joined.geometry.touches(gp.GeoSeries(joined.line))
    joined = joined.loc[~only_touch].copy()

    # intersect with lines and tally stats based on the intersection
    print("Cutting flowlines by waterbodies...")
    joined["geometry"] = joined.geometry.intersection(gp.GeoSeries(joined.line))
    joined = joined.drop(columns=["line"])
    joined["length"] = joined.length

    wb_stats = (
        joined.groupby("wbID")
        .agg({"length": "sum", "lineID": "count"})
        .rename(columns={"lineID": "numSegments", "length": "flowlineLength"})
    )
    wb_stats.numSegments = wb_stats.numSegments.astype("uint16")

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
        .reset_index(drop=True)
    )

    # Remove any flowlines that cross waterbodies (these were originally due to pipelines)
    # drain_pts = drain_pts.loc[drain_pts.geometry.type != "MultiLineString"].copy()
    idx = drain_pts.loc[drain_pts.geometry.type == "MultiLineString"].index
    if len(idx):
        print(
            "WARNING: there are {:,} flowlines that were cut into multiple parts within waterbodies".format(
                len(idx)
            )
        )

        # take the first of each
        drain_pts.loc[idx, "geometry"] = drain_pts.loc[idx].geometry.apply(
            lambda g: g[0]
        )

    # create a point from the last coordinate, which is the furthest one downstream
    drain_pts.geometry = drain_pts.geometry.apply(
        lambda g: Point(np.column_stack(g.xy)[-1])
    )

    to_geofeather(drain_pts, out_dir / "waterbody_drain_points.feather")

    print("serializing to shp")
    to_shp(df, out_dir / "waterbodies.shp")
    to_shp(drain_pts, out_dir / "waterbody_drain_points.shp")

    print("Region done in {:.0f}s".format(time() - region_start))


# TODO: merge!


print("Done in {:.2f}s\n============================".format(time() - start))
