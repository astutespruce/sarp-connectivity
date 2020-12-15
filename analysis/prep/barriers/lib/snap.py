from pathlib import Path
from time import time

import numpy as np
import geopandas as gp
import pandas as pd
import pygeos as pg
from pyogrio import write_dataframe
from nhdnet.geometry.lines import snap_to_line
from nhdnet.geometry.points import snap_to_point

from analysis.prep.barriers.lib.points import nearest, near, connect_points
from analysis.lib.pygeos_util import sjoin
from analysis.constants import CRS
from analysis.lib.util import ndarray_append_strings, append
from analysis.lib.io import read_feathers

# distance from edge of an NHD dam poly to be considered associated
NHD_DAM_TOLERANCE = 50
# dams will initially snap by SNAP_TOLERANCE, but any that are within waterbodies and don't snap elsewhere
# will snap to their waterbody's drain up to this tolerance
WB_DRAIN_MAX_TOLERANCE = 250

# dams within this distance will be considered for possible relationship to a waterbody
NEAR_WB_TOLERANCE = 50

nhd_dir = Path("data/nhd")


def snap_estimated_dams_to_drains(df, to_snap):
    snap_start = time()

    estimated = to_snap.loc[to_snap.ManualReview == 20].copy()

    merged = None
    for huc2 in sorted(estimated.HUC2.unique()):
        wb = gp.read_feather(
            nhd_dir / "clean" / huc2 / "waterbodies.feather",
            columns=["wbID", "geometry"],
        ).set_index("wbID")
        drains = gp.read_feather(
            nhd_dir / "clean" / huc2 / "waterbody_drain_points.feather",
            columns=["wbID", "lineID", "geometry"],
        )
        drains.index.name = "drainID"

        in_huc2 = estimated.loc[estimated.HUC2 == huc2].copy()

        # Take the first intersection with waterbodies to prevent creating
        # duplicates
        in_wb = (
            sjoin(in_huc2, wb, how="inner", predicate="within")
            .index_right.rename("wbID")
            .groupby(level=0)
            .first()
        )

        # for those in waterbodies, snap to the nearest non-loop drain point
        in_wb = (
            pd.DataFrame(in_wb)
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

        merged = append(merged, in_wb)

        print(
            f"HUC {huc2}: snapped {len(in_wb):,} of {len(in_huc2):,} estimated dams in region to waterbody drain points"
        )

    in_wb = merged

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
        f"Snapped {len(ix):,} estimated dams to waterbody drain points in {time() - snap_start:.2f}s"
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

    print("Snapping to NHD dams...")

    nhd_dams_poly = gp.read_feather(
        nhd_dir / "merged" / "nhd_dams_poly.feather", columns=["damID", "geometry"]
    ).set_index("damID")

    # NOTE: there may be multiple points per damID
    nhd_dams = gp.read_feather(
        nhd_dir / "merged" / "nhd_dams_pt.feather",
        columns=["damID", "wbID", "lineID", "geometry"],
    ).set_index("damID")
    # set nulls back to na
    nhd_dams.wbID = nhd_dams.wbID.replace(-1, np.nan)

    ### Find dams that are really close (50m) to NHD dam polygons
    # Those that have multiple dams nearby are usually part of a dam complex
    near_nhd = nearest(
        pd.Series(to_snap.geometry.values.data, index=to_snap.index),
        pd.Series(nhd_dams_poly.geometry.values.data, index=nhd_dams_poly.index),
        distance=NHD_DAM_TOLERANCE,
    )[["damID"]]

    # snap to nearest dam point for that dam (some are > 1 km away)
    # NOTE: this will create multiple entries for some dams; the closest is used
    near_nhd = near_nhd.join(to_snap.geometry.rename("source_pt")).join(
        nhd_dams, on="damID"
    )
    near_nhd["snap_dist"] = pg.distance(
        near_nhd.geometry.values.data, near_nhd.source_pt.values.data
    )
    near_nhd = (
        near_nhd.reset_index().sort_values(by=["id", "snap_dist"]).groupby("id").first()
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
    # most of these should have been picked up above
    snap_start = time()
    tmp = nhd_dams.reset_index()  # reset index so we have unique index to join on
    near_nhd = nearest(
        pd.Series(to_snap.geometry.geometry.values.data, index=to_snap.index),
        pd.Series(tmp.geometry.geometry.values.data, index=tmp.index),
        distance=to_snap.snap_tolerance,
    ).rename(columns={"distance": "snap_dist"})

    near_nhd = near_nhd.join(to_snap.geometry.rename("source_pt")).join(
        tmp, on="index_right"
    )
    near_nhd = (
        near_nhd.reset_index().sort_values(by=["id", "snap_dist"]).groupby("id").first()
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

    ### TODO: identify any NHD dam points that didn't get claimed  (need to do this after snapping others)

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

    huc2s = sorted(to_snap.HUC2.unique())
    wb = read_feathers(
        [nhd_dir / "clean" / huc2 / "waterbodies.feather" for huc2 in huc2s],
        columns=["wbID", "geometry"],
        geo=True,
    ).set_index("wbID")

    drains = read_feathers(
        [nhd_dir / "clean" / huc2 / "waterbody_drain_points.feather" for huc2 in huc2s],
        columns=["wbID", "lineID", "geometry"],
        geo=True,
    )
    drains.index.name = "drainID"  # NOTE: this isn't the correct global drain ID

    ### Attempt to snap to waterbody drain points for major waterbodies
    # Use larger tolerance for larger waterbodies
    print("Snapping to waterbodies and drain points..")
    # wb = gp.read_feather(nhd_dir / "merged" / "waterbodies.feather", columns=['wbID', 'geometry']).set_index("wbID")
    # drains = (
    #     gp.read_feather(nhd_dir / "merged" / "waterbody_drain_points.feather", columns=['drainID', 'wbID', 'lineID', 'geometry'])
    #     .set_index("drainID")
    # )

    ### First pass - find the dams that are contained by waterbodies
    contained_start = time()

    in_wb = sjoin(to_snap, wb, how="inner").index_right.rename("wbID")

    # update wbID in dataset, but this doesn't mean it is snapped
    ix = in_wb.index
    df.loc[ix, "wbID"] = in_wb

    print(
        f"Found {len(in_wb):,} dams in waterbodies in {time() - contained_start:.2f}s"
    )

    print("Finding nearest drain points...")
    snap_start = time()
    # join back to pygeos geoms and join to drains
    # NOTE: this may produce multiple drains for some waterbodies

    # FIXME: this isn't working properly
    in_wb = (
        pd.DataFrame(in_wb)
        .join(to_snap[["geometry", "snap_tolerance"]])
        .join(
            drains.reset_index()
            .set_index("wbID")[["geometry", "drainID", "lineID"]]
            .rename(columns={"geometry": "drain"}),
            on="wbID",
        )
        .dropna(subset=["drain"])
    )
    in_wb["snap_dist"] = pg.distance(
        in_wb.geometry.values.data, in_wb.drain.values.data
    )

    # drop any that are > 500 m away, these aren't useful
    in_wb = in_wb.loc[in_wb.snap_dist <= 500].copy()

    # take the closest drain point
    in_wb.index.name = "index"
    in_wb = (
        in_wb.reset_index()
        .sort_values(by=["index", "snap_dist"])
        .groupby("index")
        .first()
    )

    # Any that are within the snap tolerance just snap to that drain
    close_enough = in_wb.loc[in_wb.snap_dist <= in_wb.snap_tolerance]
    ix = close_enough.index
    df.loc[ix, "snapped"] = True
    df.loc[ix, "geometry"] = close_enough.drain
    df.loc[ix, "snap_dist"] = close_enough.snap_dist
    df.loc[ix, "snap_ref_id"] = close_enough.drainID
    df.loc[ix, "lineID"] = close_enough.lineID
    df.loc[ix, "wbID"] = close_enough.wbID
    df.loc[ix, "snap_log"] = ndarray_append_strings(
        "snapped: within ",
        to_snap.loc[ix].snap_tolerance,
        "m tolerance of drain point for waterbody that contains this dam",
    )

    to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

    print(
        f"Found {len(ix):,} dams within tolerance of the drain points for their waterbody in {time() - snap_start:.2f}s"
    )

    # Any that are > tolerance away from their own drain, but within tolerance of another drain
    # should snap to the other drain; these are in chains of multiple waterbodies.
    # Visually confirmed this by looking at several.
    snap_start = time()
    further = in_wb.loc[in_wb.snap_dist > in_wb.snap_tolerance].copy()
    nearest_drains = nearest(
        pd.Series(further.geometry.values.data, index=further.index),
        pd.Series(drains.geometry.values.data, index=drains.index),
        further.snap_tolerance,
    )

    maybe_near_neighbor = further.join(nearest_drains, rsuffix="_nearest")

    ix = maybe_near_neighbor.loc[
        maybe_near_neighbor.distance < maybe_near_neighbor.snap_dist
    ].index
    near_neighbor = (
        (
            maybe_near_neighbor.loc[ix]
            .drop(columns=["drain", "drainID", "wbID", "lineID", "snap_dist"])
            .rename(columns={"drainID_nearest": "drainID", "distance": "snap_dist"})
            .join(
                drains[["geometry", "lineID", "wbID"]].rename(
                    columns={"geometry": "drain"}
                ),
                on="drainID",
            )
        )
        .sort_values(by="snap_dist")
        .groupby(level=0)
        .first()
    )

    df.loc[ix, "snapped"] = True
    df.loc[ix, "geometry"] = near_neighbor.drain
    df.loc[ix, "snap_dist"] = near_neighbor.snap_dist
    df.loc[ix, "snap_ref_id"] = near_neighbor.drainID
    df.loc[ix, "lineID"] = near_neighbor.lineID
    df.loc[ix, "wbID"] = near_neighbor.wbID
    df.loc[ix, "snap_log"] = ndarray_append_strings(
        "snapped: within ",
        to_snap.loc[ix].snap_tolerance,
        "m tolerance of drain point for adjacent waterbody",
    )

    to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

    print(
        "Found {:,} dams close to drain points for an adjacent waterbody in {:.2f}s".format(
            len(ix), time() - snap_start
        )
    )

    # Any that remain and are < 250 in their waterbody snap to nearest drain
    further = further.loc[
        ~further.index.isin(ix) & (further.snap_dist <= WB_DRAIN_MAX_TOLERANCE)
    ].copy()

    ix = further.index
    df.loc[ix, "snapped"] = True
    df.loc[ix, "geometry"] = further.drain
    df.loc[ix, "snap_dist"] = further.snap_dist
    df.loc[ix, "snap_ref_id"] = further.drainID
    df.loc[ix, "lineID"] = further.lineID
    df.loc[ix, "wbID"] = further.wbID
    df.loc[ix, "snap_log"] = ndarray_append_strings(
        "snapped: within ",
        to_snap.loc[ix].snap_tolerance,
        "-",
        WB_DRAIN_MAX_TOLERANCE,
        "m tolerance of drain point of waterbody that contains this dam",
    )
    to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

    print(
        "Found {:,} dams within <{}m of the drain points for their waterbody".format(
            len(ix), WB_DRAIN_MAX_TOLERANCE
        )
    )

    ### Find the ones that are not in a waterbody but within tolerance of a drain
    # Visually inspected several that had multiple waterbodies nearby
    # in all cases, the nearest one was sufficient
    print("Finding nearest waterbody drains for unsnapped dams...")
    snap_start = time()
    nearest_drains = nearest(
        pd.Series(to_snap.geometry.values.data, index=to_snap.index),
        pd.Series(drains.geometry.values.data, index=drains.index),
        to_snap.snap_tolerance,
    )

    nearest_drains = nearest_drains.join(to_snap.geometry).join(
        drains[["geometry", "wbID", "lineID"]].rename(columns={"geometry": "drain"}),
        on="drainID",
    )

    ix = nearest_drains.index
    df.loc[ix, "snapped"] = True
    df.loc[ix, "geometry"] = nearest_drains.drain
    df.loc[ix, "snap_dist"] = nearest_drains.distance
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

    # TODO: need to track which waterbodies were claimed by dams

    return df, to_snap


def snap_to_flowlines(df, to_snap):
    """Snap to nearest flowline, within tolerance

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

    for huc2 in sorted(df.HUC2.unique()):
        region_start = time()

        print(f"----- {huc2} ------")
        print("Reading flowlines...")

        flowlines = gp.read_feather(
            nhd_dir / "clean" / huc2 / "flowlines.feather",
            columns=["geometry", "lineID"],
        ).set_index("lineID")

        in_huc2 = to_snap.loc[to_snap.HUC2 == huc2].copy()
        print(
            f"Selected {len(in_huc2):,} barriers in region to snap against {len(flowlines):,} flowlines"
        )

        print("Finding nearest flowlines...")
        # TODO: can use near instead of nearest, and persist list of near lineIDs per barrier
        # so that we can construct subnetworks with just those
        lines = nearest(
            pd.Series(in_huc2.geometry.values.data, index=in_huc2.index),
            pd.Series(flowlines.geometry.values.data, index=flowlines.index),
            in_huc2.snap_tolerance.values,
        )
        lines = lines.join(in_huc2.geometry).join(
            flowlines.geometry.rename("line"),
            on="lineID",
        )

        # project the point to the line,
        # find out its distance on the line,
        # then interpolate its new coordinates
        lines["geometry"] = pg.line_interpolate_point(
            lines.line.values.data,
            pg.line_locate_point(lines.line.values.data, lines.geometry.values.data),
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


def snap_to_large_waterbodies(df, to_snap):
    """Snap to nearest large waterbody.

    NOTE: only run this on dams that could not snap to flowlines, to avoid
    moving them far away.

    This captures large dam centerpoints that are not near enough to flowlines.

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
    wb = gp.read_feather(nhd_dir / "merged" / "large_waterbodies.feather").set_index(
        "wbID"
    )
    drains = (
        gp.read_feather(nhd_dir / "merged" / "large_waterbody_drain_points.feather")
        .rename(columns={"id": "drainID"})
        .set_index("drainID")
    )

    near_wb = nearest(to_snap.geometry, pg.boundary(wb.geometry), NEAR_WB_TOLERANCE)
    near_wb = (
        pd.DataFrame(near_wb)
        .join(to_snap.geometry)
        .join(
            drains.reset_index()
            .set_index("wbID")[["geometry", "drainID", "lineID"]]
            .rename(columns={"geometry": "drain"}),
            on="wbID",
        )
        .dropna(subset=["drain"])
    )
    near_wb["snap_dist"] = pg.distance(near_wb.geometry, near_wb.drain)

    # drop any that are > 250 m away, these aren't useful
    near_wb = near_wb.loc[near_wb.snap_dist <= WB_DRAIN_MAX_TOLERANCE].copy()

    # take the closest drain point
    near_wb = near_wb.sort_values(by="snap_dist").groupby(level=0).first()

    ix = near_wb.index
    df.loc[ix, "snapped"] = True
    df.loc[ix, "geometry"] = near_wb.drain
    df.loc[ix, "snap_dist"] = near_wb.distance
    df.loc[ix, "snap_ref_id"] = near_wb.drainID
    df.loc[ix, "lineID"] = near_wb.lineID
    df.loc[ix, "wbID"] = near_wb.wbID

    df.loc[ix, "snap_log"] = ndarray_append_strings(
        "snapped: within ",
        WB_DRAIN_MAX_TOLERANCE,
        "m tolerance of drain point of large waterbody that is within ",
        NEAR_WB_TOLERANCE,
        "m of dam",
    )

    to_snap = to_snap.loc[~to_snap.index.isin(ix)].copy()

    print(
        "Found {:,} dams within {}m of large waterbodies and within {}m of the drain point of those waterbodies".format(
            len(near_wb), NEAR_WB_TOLERANCE, WB_DRAIN_MAX_TOLERANCE
        )
    )

    return df, to_snap


# def snap_by_region(df, regions, default_tolerance=None):
#     """Snap barriers based on nearest flowline within tolerance.

#     If available, a 'tolerance' column is used to define the tolerance to snap by;
#     otherwise, default_tolerance must be provided.

#     Parameters
#     ----------
#     df : GeoDataFrame
#         Input barriers to be snapped
#     regions : dict
#         Dictionary of region IDs to list of units in region
#     default_tolerance : float, optional (default: None)
#         distance within which to allow snapping to flowlines

#     Returns
#     -------
#     GeoDataFrame
#         snapped barriers (unsnapped are dropped) with additional fields from snapping:
#         lineID, NHDPlusID, snap_dist, nearby
#     """

#     if "tolerance" not in df.columns and default_tolerance is None:
#         raise ValueError(
#             "Either 'tolerance' column or default_tolerance must be defined"
#         )

#     merged = None

#     for region in regions:

#         print("\n----- {} ------\n".format(region))
#         region_dir = nhd_dir / "flowlines" / region

#         # Extract out barriers in this HUC
#         in_region = df.loc[df.HUC2.isin(regions[region])]
#         print("Selected {:,} barriers in region".format(len(in_region)))

#         if len(in_region) == 0:
#             continue

#         print("Reading flowlines")
#         flowlines = (
#             deserialize_gdf(
#                 region_dir / "flowline.feather",
#                 columns=["geometry", "lineID", "NHDPlusID", "streamorder", "sizeclass"],
#             )
#             .rename(columns={"streamorder": "StreamOrder", "sizeclass": "SizeClass"})
#             .set_index("lineID", drop=False)
#         )
#         print("Read {:,} flowlines".format(len(flowlines)))

#         print("Reading spatial index on flowlines")
#         sindex = deserialize_sindex(region_dir / "flowline.sidx")

#         print("Snapping to flowlines")
#         if "tolerance" in df.columns:
#             # Snap for each tolerance level
#             snapped = None
#             for tolerance in df.tolerance.unique():

#                 at_tolerance = in_region.loc[in_region.tolerance == tolerance]

#                 if not len(at_tolerance):
#                     continue

#                 print("snapping {} barriers by {}".format(len(at_tolerance), tolerance))

#                 temp = snap_to_line(
#                     at_tolerance, flowlines, tolerance=tolerance, sindex=sindex
#                 )
#                 print("snapped {} barriers".format(len(temp)))

#                 if snapped is None:
#                     snapped = temp

#                 else:
#                     snapped = snapped.append(temp, ignore_index=True, sort=False)

#         else:
#             snapped = snap_to_line(
#                 in_region, flowlines, tolerance=default_tolerance, sindex=sindex
#             )

#         print("{:,} barriers were successfully snapped".format(len(snapped)))

#         if merged is None:
#             merged = snapped
#         else:
#             merged = merged.append(snapped, sort=False, ignore_index=True)

#     return merged


# def update_from_snapped(df, snapped):
#     """Update snapped coordinates into dataset.

#     Parameters
#     ----------
#     df : GeoDataFrame
#         Master dataset to update with snapped coordinates
#     snapped : GeoDataFrame
#         Snapped dataset with coordinates to apply

#     Returns
#     -------
#     GeoDataFrame
#     """

#     df["snapped"] = False
#     df = df.join(
#         snapped.set_index("id")[
#             ["geometry", "snap_dist", "lineID", "NHDPlusID", "StreamOrder", "SizeClass"]
#         ],
#         on="id",
#         rsuffix="_snapped",
#     )
#     idx = df.loc[df.lineID.notnull()].index
#     df.loc[idx, "geometry"] = df.loc[idx].geometry_snapped
#     df.loc[idx, "snapped"] = True
#     df = df.drop(columns=["geometry_snapped"])

#     return df


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
    tmp = df.loc[
        df.snapped, ["geometry", "Name", "SARPID", "snapped", "snap_dist", "snap_log"]
    ].join(original_locations.geometry.rename("orig_pt"))
    tmp["new_pt"] = tmp.geometry.copy()
    tmp["geometry"] = connect_points(tmp.new_pt, tmp.orig_pt)

    write_dataframe(
        tmp.drop(columns=["new_pt", "orig_pt"]).reset_index(drop=True),
        out_dir / "{}pre_snap_to_post_snap".format(prefix),
    )
    write_dataframe(
        tmp.drop(columns=["geometry", "new_pt"])
        .rename(columns={"orig_pt": "geometry"})
        .reset_index(drop=True),
        out_dir / "{}pre_snap".format(prefix),
    )
    write_dataframe(
        tmp.drop(columns=["geometry", "orig_pt"])
        .rename(columns={"new_pt": "geometry"})
        .reset_index(drop=True),
        out_dir / "{}post_snap".format(prefix),
    )
