from pathlib import Path
from time import time

import numpy as np
import geopandas as gp
import pandas as pd
import pygeos as pg
from pyogrio import write_dataframe

from analysis.prep.barriers.lib.points import connect_points
from analysis.lib.geometry import nearest
from analysis.constants import SNAP_ENDPOINT_TOLERANCE
from analysis.lib.util import ndarray_append_strings

# distance from edge of an NHD dam poly to be considered associated
NHD_DAM_TOLERANCE = 50
# dams will initially snap by SNAP_TOLERANCE, but any that are within waterbodies and don't snap elsewhere
# will snap to their waterbody's drain up to this tolerance
WB_DRAIN_MAX_TOLERANCE = 250

# dams within this distance will be considered for possible relationship to a waterbody
NEAR_WB_TOLERANCE = 50

nhd_dir = Path("data/nhd")


def snap_estimated_dams_to_drains(df, to_snap):
    """Snap estimated dams to waterbody drain points.

    Dams that were estimated from waterbodies are snapped to the nearest drain
    points (should be very small snap_dist).

    Other estimated dams often occur inside / immediately adjacent to waterbodies
    and are snapped to the nearest drain point of those waterbodies if < 2km.

    Parameters
    ----------
    df : GeoDataFrame
        master dataset, this is where all snapping gets recorded
    to_snap : DataFrame
        data frame containing pygeos geometries to snap ("geometry")
        and snapping tolerance ("snap_tolerance")

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
        (df, to_snap)
    """
    snap_start = time()

    # if estimated dam and was not manually reviewed and moved or verified at correct location
    ix = (to_snap.snap_group.isin([1, 3])) & (~to_snap.ManualReview.isin([4, 13]))
    estimated = to_snap.loc[ix].copy()
    print(f"=================\nSnapping {len(estimated):,} estimated dams...")

    for huc2 in sorted(estimated.HUC2.unique()):
        wb = gp.read_feather(
            nhd_dir / "clean" / huc2 / "waterbodies.feather",
            columns=["wbID", "geometry"],
        ).set_index("wbID")

        drains = gp.read_feather(
            nhd_dir / "clean" / huc2 / "waterbody_drain_points.feather",
            columns=["drainID", "wbID", "lineID", "geometry"],
        ).set_index("drainID")

        in_huc2 = estimated.loc[estimated.HUC2 == huc2].copy()

        # most estimated dams were originally derived from waterbody drain points,
        # so process those first
        tmp = in_huc2.loc[in_huc2.snap_group == 3]
        if len(tmp):
            max_drain_dist = tmp.snap_tolerance.unique()[0]
            tree = pg.STRtree(drains.geometry.values.data)
            left, right = tree.nearest_all(
                tmp.geometry.values.data, max_distance=max_drain_dist
            )
            drain_joins = (
                pd.DataFrame(
                    {
                        "id": tmp.index.values.take(left),
                        "geometry": tmp.geometry.values.take(left),
                        "drainID": drains.index.values.take(right),
                        "drain": drains.geometry.values.take(right),
                        "wbID": drains.wbID.values.take(right),
                        "lineID": drains.lineID.values.take(right),
                    }
                )
                .groupby("id")
                .first()
            )

            drain_joins["snap_dist"] = pg.distance(
                drain_joins.geometry.values.data, drain_joins.drain.values.data
            )

            ix = drain_joins.index
            df.loc[ix, "snapped"] = True
            df.loc[ix, "geometry"] = drain_joins.drain
            df.loc[ix, "snap_dist"] = drain_joins.snap_dist
            df.loc[ix, "snap_ref_id"] = drain_joins.drainID
            df.loc[ix, "lineID"] = drain_joins.lineID
            df.loc[ix, "wbID"] = drain_joins.wbID
            df.loc[
                ix, "snap_log"
            ] = "snapped: dams estimated from waterbody snapped to nearest drain point"

            to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

            print(
                f"HUC {huc2}: snapped {len(drain_joins):,} of {len(drain_joins):,} dams estimated from waterbodies in region to waterbody drain points"
            )

        in_huc2 = in_huc2.loc[in_huc2.snap_group == 1]

        # Some estimated dams are just barely outside their waterbodies
        # so we take the nearest waterbody for each, within a tolerance of 1m
        tree = pg.STRtree(wb.geometry.values.data)
        left, right = tree.nearest_all(in_huc2.geometry.values.data, max_distance=1)
        # take the first in case of duplicates
        in_wb = (
            pd.DataFrame(
                {
                    "id": in_huc2.index.values.take(left),
                    "wbID": wb.index.values.take(right),
                }
            )
            .groupby("id")
            .first()
            .join(in_huc2.geometry)
            .join(
                drains[["wbID", "lineID", "geometry"]]
                .reset_index()
                .set_index("wbID")
                .rename(columns={"geometry": "drain"}),
                on="wbID",
            )
        )

        in_wb["snap_dist"] = pg.distance(
            in_wb.geometry.values.data, in_wb.drain.values.data
        )
        grouped = in_wb.sort_values(by="snap_dist").groupby(level=0)
        in_wb = grouped.first()

        # any waterbodies that have > 2 drains are dubious fits; remove them
        s = grouped.size()
        ix = s[s > 2].index
        in_wb = in_wb.loc[~in_wb.index.isin(ix)].copy()

        # any that are >2,000m away are likely incorrect; some ones near that length are OK
        in_wb = in_wb.loc[in_wb.snap_dist <= 2000].copy()

        ix = in_wb.index
        df.loc[ix, "snapped"] = True
        df.loc[ix, "geometry"] = in_wb.drain
        df.loc[ix, "snap_dist"] = in_wb.snap_dist
        df.loc[ix, "snap_ref_id"] = in_wb.drainID
        df.loc[ix, "lineID"] = in_wb.lineID
        df.loc[ix, "wbID"] = in_wb.wbID
        df.loc[
            ix, "snap_log"
        ] = "snapped: estimated dam in waterbody snapped to nearest drain point"

        to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

        print(
            f"HUC {huc2}: snapped {len(in_wb):,} of {len(in_huc2):,} estimated dams in region to waterbody drain points"
        )

    print(
        f"Snapped {len(df.loc[df.snap_log.str.startswith('snapped: estimated dam')]):,} estimated dams to waterbody drain points in {time() - snap_start:.2f}s"
    )

    return df, to_snap


def snap_to_nhd_dams(df, to_snap):
    """Attempt to snap points from to_snap to NHD dams.

    Updates df with snapping results, and returns to_snap as set of dams still
    needing to be snapped after this operation.

    Parameters
    ----------
    df : GeoDataFrame
        master dataset, this is where all snapping gets recorded
    to_snap : DataFrame
        data frame containing pygeos geometries to snap ("geometry")
        and snapping tolerance ("snap_tolerance")

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
        (df, to_snap)
    """

    snap_start = time()

    print("=================\nSnapping to NHD dams...")

    nhd_dams_poly = gp.read_feather(
        nhd_dir / "merged" / "nhd_dams_poly.feather", columns=["damID", "geometry"]
    ).set_index("damID")

    # NOTE: there may be multiple points per damID
    nhd_dams = gp.read_feather(
        nhd_dir / "merged" / "nhd_dams_pt.feather",
        columns=["damID", "wbID", "lineID", "loop", "sizeclass", "geometry"],
    ).set_index("damID")
    # set nulls back to na
    nhd_dams.wbID = nhd_dams.wbID.replace(-1, np.nan)

    ### Find dams that are really close (50m) to NHD dam polygons
    # Those that have multiple dams nearby are usually part of a dam complex
    near_nhd = nearest(
        pd.Series(to_snap.geometry.values.data, index=to_snap.index),
        pd.Series(nhd_dams_poly.geometry.values.data, index=nhd_dams_poly.index),
        max_distance=NHD_DAM_TOLERANCE,
    )[["damID"]]

    # snap to nearest dam point for that dam (some are > 1 km away)
    # NOTE: this will create multiple entries for some dams; the closest is used
    near_nhd = near_nhd.join(to_snap.geometry.rename("source_pt")).join(
        nhd_dams, on="damID"
    )
    near_nhd.reset_index().drop_duplicates(
        subset=["id", "damID", "lineID", "geometry"]
    ).set_index("id")
    near_nhd["snap_dist"] = pg.distance(
        near_nhd.geometry.values.data, near_nhd.source_pt.values.data
    )
    # Sort to prioritize larger size classes and non-loops, then distance
    # this also drops duplicates
    near_nhd = (
        near_nhd.reset_index()
        .sort_values(
            by=["id", "sizeclass", "loop", "snap_dist"],
            ascending=[True, False, True, True],
        )
        .groupby("id")
        .first()
    )

    ix = near_nhd.index
    df.loc[ix, "snapped"] = True
    df.loc[ix, "geometry"] = near_nhd.geometry
    df.loc[ix, "snap_dist"] = near_nhd.snap_dist
    df.loc[ix, "snap_ref_id"] = near_nhd.damID
    df.loc[ix, "lineID"] = near_nhd.lineID
    df.loc[ix, "wbID"] = near_nhd.wbID
    df.loc[ix, "snap_log"] = ndarray_append_strings(
        "snapped: within ", NHD_DAM_TOLERANCE, "m of NHD dam polygon"
    )
    to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()
    print(
        "Snapped {:,} dams to NHD dam polygons in {:.2f}s".format(
            len(ix), time() - snap_start
        )
    )

    ### Find dams that are close (within snapping tolerance) of NHD dam points
    # most of these should have been picked up above, but this picks up ones that are
    # greater than NHD_DAM_TOLERANCE away due to bad locations
    snap_start = time()
    tmp = nhd_dams.reset_index()  # reset index so we have unique index to join on
    near_nhd = nearest(
        pd.Series(to_snap.geometry.values.data, index=to_snap.index),
        pd.Series(tmp.geometry.values.data, index=tmp.index),
        max_distance=to_snap.snap_tolerance,
    ).rename(columns={"distance": "snap_dist"})

    near_nhd = near_nhd.join(to_snap.geometry.rename("source_pt")).join(
        tmp, on="index_right"
    )
    near_nhd = (
        near_nhd.reset_index()
        .sort_values(
            by=["id", "sizeclass", "loop", "snap_dist"],
            ascending=[True, False, True, True],
        )
        .groupby("id")
        .first()
    )

    ix = near_nhd.index
    df.loc[ix, "snapped"] = True
    df.loc[ix, "geometry"] = near_nhd.geometry
    df.loc[ix, "snap_dist"] = near_nhd.snap_dist
    df.loc[ix, "snap_ref_id"] = near_nhd.damID
    df.loc[ix, "lineID"] = near_nhd.lineID
    df.loc[ix, "wbID"] = near_nhd.wbID
    df.loc[ix, "snap_log"] = ndarray_append_strings(
        "snapped: within ",
        to_snap.loc[ix].snap_tolerance,
        "m tolerance of NHD dam point but >",
        NHD_DAM_TOLERANCE,
        "m from NHD dam polygon",
    )
    to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()
    print(f"Snapped {len(ix):,} dams to NHD dam points in {time() - snap_start:.2f}s")

    return df, to_snap


def snap_to_waterbodies(df, to_snap):
    """Attempt to snap points from to_snap to waterbody drain points.

    Updates df with snapping results, and returns to_snap as set of dams still
    needing to be snapped after this operation.

    Parameters
    ----------
    df : GeoDataFrame
        master dataset, this is where all snapping gets recorded
    to_snap : DataFrame
        data frame containing pygeos geometries to snap ("geometry")
        and snapping tolerance ("snap_tolerance")

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
        (df, to_snap)
    """

    ### Attempt to snap to waterbody drain points for major waterbodies
    # Use larger tolerance for larger waterbodies
    # NOTE: this specifically excludes known lowhead dams from snapping to waterbodies
    print("=================\nSnapping to waterbodies and drain points..")

    for huc2 in sorted(to_snap.HUC2.unique()):
        print(f"\n----- {huc2} ------")
        in_huc2 = to_snap.loc[(to_snap.HUC2 == huc2) & (to_snap.LowheadDam != 1)].copy()

        wb = gp.read_feather(
            nhd_dir / "clean" / huc2 / "waterbodies.feather",
            columns=["wbID", "geometry"],
        ).set_index("wbID")
        drains = gp.read_feather(
            nhd_dir / "clean" / huc2 / "waterbody_drain_points.feather",
            columns=["drainID", "wbID", "lineID", "loop", "sizeclass", "geometry"],
        ).set_index("drainID")

        print(
            f"HUC {huc2} selected {len(in_huc2):,} barriers in region to snap against {len(wb):,} waterbodies"
        )

        ### First pass - find the dams that are contained by waterbodies
        contained_start = time()

        # Join to nearest waterbodies within 1m (basically inside)
        # and keep only the first match
        tree = pg.STRtree(wb.geometry.values.data)
        left, right = tree.nearest_all(in_huc2.geometry.values.data, max_distance=1)
        in_wb = (
            pd.DataFrame(
                {
                    "id": in_huc2.index.values.take(left),
                    "wbID": wb.index.values.take(right),
                }
            )
            .groupby("id")
            .first()
        )

        in_wb_index = in_wb.index

        # update wbID in dataset, but this doesn't mean it is snapped
        df.loc[in_wb.index, "wbID"] = in_wb.wbID

        print(
            f"Found {len(in_wb):,} dams in waterbodies in {time() - contained_start:.2f}s"
        )

        print("Finding nearest drain points...")
        snap_start = time()

        # join back to pygeos geoms and join to drains
        # NOTE: this may bring in multiple drains for some waterbodies, we take the
        # closest drain below
        in_wb = (
            in_wb.join(to_snap[["geometry", "snap_tolerance"]])
            .join(
                drains.reset_index()
                .set_index("wbID")[
                    ["drainID", "lineID", "loop", "sizeclass", "geometry"]
                ]
                .rename(columns={"geometry": "drain"}),
                on="wbID",
            )
            .dropna(subset=["drain"])
        )
        in_wb["snap_dist"] = pg.distance(
            in_wb.geometry.values.data, in_wb.drain.values.data
        )

        # sort drains by largest size class, nonloop, then descending distance
        in_wb = (
            in_wb.loc[in_wb.snap_dist <= in_wb.snap_tolerance]
            .reset_index()
            .sort_values(
                by=["sizeclass", "loop", "snap_dist"], ascending=[False, True, True],
            )
            .groupby("id")
            .first()
        )

        # Any that are within the snap tolerance just snap to that drain
        ix = in_wb.index
        df.loc[ix, "snapped"] = True
        df.loc[ix, "geometry"] = in_wb.drain
        df.loc[ix, "snap_dist"] = in_wb.snap_dist
        df.loc[ix, "snap_ref_id"] = in_wb.drainID
        df.loc[ix, "lineID"] = in_wb.lineID
        df.loc[ix, "wbID"] = in_wb.wbID
        df.loc[ix, "snap_log"] = ndarray_append_strings(
            "snapped: within ",
            to_snap.loc[ix].snap_tolerance,
            "m tolerance of drain point for waterbody that contains this dam",
        )

        to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

        print(
            f"Found {len(ix):,} dams within tolerance of the drain points for their waterbody in {time() - snap_start:.2f}s"
        )

        ### Find the ones that are not in a waterbody but within tolerance of a drain
        # Visually inspected several that had multiple waterbodies nearby
        # in all cases, the nearest waterbody was sufficient
        print("Finding nearest waterbody drains for unsnapped dams...")
        snap_start = time()

        # only snap those that are not in waterbodies
        not_in_wb = in_huc2.loc[~in_huc2.index.isin(in_wb_index.unique())].copy()

        nearest_drains = nearest(
            pd.Series(not_in_wb.geometry.values.data, index=not_in_wb.index),
            pd.Series(drains.geometry.values.data, index=drains.index),
            to_snap.snap_tolerance,
        )

        # join in all drains for waterbody of nearest drain point
        nearest_drains = (
            nearest_drains.drop(columns=["distance"])
            .join(not_in_wb[["geometry", "snap_tolerance"]])
            .join(drains.wbID, on="drainID",)
            .drop(columns=["drainID"])
            .join(
                drains.reset_index()
                .set_index("wbID")[
                    ["geometry", "drainID", "lineID", "loop", "sizeclass"]
                ]
                .rename(columns={"geometry": "drain"}),
                on="wbID",
            )
        )

        nearest_drains["snap_dist"] = pg.distance(
            nearest_drains.geometry.values.data, nearest_drains.drain.values.data
        )
        # take the nearest, largest non-loop drain point within tolerance
        nearest_drains = (
            nearest_drains.loc[nearest_drains.snap_dist < nearest_drains.snap_tolerance]
            .sort_values(
                by=["sizeclass", "loop", "snap_dist"], ascending=[False, True, True],
            )
            .groupby(level=0)
            .first()
        )

        ix = nearest_drains.index
        df.loc[ix, "snapped"] = True
        df.loc[ix, "geometry"] = nearest_drains.drain
        df.loc[ix, "snap_dist"] = nearest_drains.snap_dist
        df.loc[ix, "snap_ref_id"] = nearest_drains.drainID
        df.loc[ix, "lineID"] = nearest_drains.lineID
        df.loc[ix, "wbID"] = nearest_drains.wbID

        df.loc[ix, "snap_log"] = ndarray_append_strings(
            "snapped: within ",
            to_snap.loc[ix].snap_tolerance,
            "m tolerance of drain point of waterbody (dam not in waterbody)",
        )

        to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

        print(
            "Found {:,} dams within {}m of waterbody drain points".format(
                len(ix), to_snap.snap_tolerance.max()
            )
        )

    return df, to_snap


def snap_to_flowlines(df, to_snap):
    """Snap to nearest flowline, within tolerance

    Updates df with snapping results, and returns to_snap as set of dams still
    needing to be snapped after this operation.

    If dams are within SNAP_ENDPOINT_TOLERANCE of the endpoints of the line, they
    will be snapped to the endpoint instead of closest point on line.

    Parameters
    ----------
    df : GeoDataFrame
        master dataset, this is where all snapping gets recorded
    to_snap : DataFrame
        data frame containing pygeos geometries to snap ("geometry")
        and snapping tolerance ("snap_tolerance")

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
        (df, to_snap)
    """

    print("=================\nSnapping to flowlines...")

    for huc2 in sorted(to_snap.HUC2.unique()):
        region_start = time()

        print(f"\n----- {huc2} ------")
        in_huc2 = to_snap.loc[to_snap.HUC2 == huc2].copy()
        flowlines = gp.read_feather(
            nhd_dir / "clean" / huc2 / "flowlines.feather",
            columns=["geometry", "lineID"],
        ).set_index("lineID")

        print(
            f"HUC {huc2} selected {len(in_huc2):,} barriers in region to snap against {len(flowlines):,} flowlines"
        )

        lines = nearest(
            pd.Series(in_huc2.geometry.values.data, index=in_huc2.index),
            pd.Series(flowlines.geometry.values.data, index=flowlines.index),
            in_huc2.snap_tolerance.values,
        )
        lines = lines.join(in_huc2.geometry).join(
            flowlines.geometry.rename("line"), on="lineID",
        )

        # project the point to the line,
        # find out its distance on the line,
        lines["line_pos"] = pg.line_locate_point(
            lines.line.values.data, lines.geometry.values.data
        )

        # if within tolerance of start point, snap to start
        ix = lines["line_pos"] <= SNAP_ENDPOINT_TOLERANCE
        lines.loc[ix, "line_pos"] = 0

        # if within tolerance of endpoint, snap to end
        end = pg.length(lines.line.values.data)
        ix = lines["line_pos"] >= end - SNAP_ENDPOINT_TOLERANCE
        lines.loc[ix, "line_pos"] = end[ix]

        # then interpolate its new coordinates
        lines["geometry"] = pg.line_interpolate_point(
            lines.line.values.data, lines["line_pos"]
        )

        ix = lines.index
        df.loc[ix, "snapped"] = True
        df.loc[ix, "geometry"] = lines.geometry
        df.loc[ix, "snap_dist"] = lines.distance
        df.loc[ix, "snap_ref_id"] = lines.lineID
        df.loc[ix, "lineID"] = lines.lineID
        df.loc[ix, "snap_log"] = ndarray_append_strings(
            "snapped: within ",
            to_snap.loc[ix].snap_tolerance,
            "m tolerance of flowline",
        )

        to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

        print(
            "{:,} barriers snapped in region in {:.2f}s".format(
                len(ix), time() - region_start
            )
        )

    # TODO: flag those that joined to loops

    return df, to_snap


def export_snap_dist_lines(df, original_locations, out_dir, prefix=""):
    """Creates lines from the original coordinate to the snapped coordinate
    to help QA/QC snapping operation.

    Creates geopackages in out_dir:
    - pre_snap_to_post_snap: line between snapped and unsnapped coordinate
    - pre_snap: unsnapped points
    - post_snap: snapped points

    Parameters
    ----------
    df : DataFrame
        contains pygeos geometries in "geometry" column
    original_locations : DataFrame
        contains pygeos geometries in "geometry" column
    out_dir : Path
    prefix : str
        prefix to add to filename
    """

    print("Exporting snap review datasets...")

    tmp = df.loc[
        df.snapped, ["geometry", "Name", "SARPID", "snapped", "snap_dist", "snap_log"]
    ].join(original_locations.geometry.rename("orig_pt"))
    tmp["new_pt"] = tmp.geometry.copy()
    tmp["geometry"] = connect_points(tmp.new_pt.values.data, tmp.orig_pt.values.data)

    write_dataframe(
        tmp.drop(columns=["new_pt", "orig_pt"]).reset_index(drop=True),
        out_dir / f"{prefix}pre_snap_to_post_snap.gpkg",
    )
    write_dataframe(
        tmp.drop(columns=["geometry", "new_pt"])
        .rename(columns={"orig_pt": "geometry"})
        .reset_index(drop=True),
        out_dir / f"{prefix}pre_snap.gpkg",
    )
    write_dataframe(
        tmp.drop(columns=["geometry", "orig_pt"])
        .rename(columns={"new_pt": "geometry"})
        .reset_index(drop=True),
        out_dir / f"{prefix}post_snap.gpkg",
    )
