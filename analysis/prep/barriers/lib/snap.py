from pathlib import Path
from time import time

import numpy as np
import geopandas as gp
from geopandas import GeoDataFrame
import pandas as pd
from geofeather import from_geofeather
from geofeather.pygeos import from_geofeather as from_geofeather_as_pygeos
from pgpkg import to_gpkg
import pygeos as pg
from nhdnet.io import deserialize_gdf, deserialize_sindex
from nhdnet.geometry.lines import snap_to_line
from nhdnet.geometry.points import snap_to_point

from analysis.prep.barriers.lib.points import nearest, near, connect_points
from analysis.pygeos_compat import from_pygeos, to_pygeos, to_gdf
from analysis.constants import CRS, REGION_GROUPS, REGIONS
from analysis.util import ndarray_append_strings

# distance from edge of an NHD dam poly to be considered associated
NHD_DAM_TOLERANCE = 50
# dams will initially snap by SNAP_TOLERANCE, but any that are within waterbodies and don't snap elsewhere
# will snap to their waterbody's drain up to this tolerance
WB_DRAIN_MAX_TOLERANCE = 250

# dams within this distance will be considered for possible relationship to a waterbody
NEAR_WB_TOLERANCE = 50

nhd_dir = Path("data/nhd")


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

    print("Snapping to NHD dams...")
    # NOTE: id is not unique for points
    nhd_dams_poly = (
        from_geofeather_as_pygeos(nhd_dir / "merged" / "nhd_dams_poly.feather")
        .rename(columns={"id": "damID"})
        .set_index("damID")
        .drop(columns=["index"], errors="ignore")
    )
    nhd_dams = (
        from_geofeather_as_pygeos(nhd_dir / "merged" / "nhd_dams_pt.feather")
        .rename(columns={"id": "damID"})
        .set_index("damID")
    )
    # set nulls back to na
    nhd_dams.wbID = nhd_dams.wbID.replace(-1, np.nan)

    ### Find dams that are really close (50m) to NHD dam polygons
    # Those that have multiple dams nearby are usually part of a dam complex
    snap_start = time()
    near_nhd = nearest(
        to_snap.geometry, nhd_dams_poly.geometry, distance=NHD_DAM_TOLERANCE
    )[["damID"]]

    # snap to nearest dam point for that dam (some are > 1 km away)
    # NOTE: this will multiple entries for some dams
    near_nhd = near_nhd.join(to_snap.geometry.rename("source_pt")).join(
        nhd_dams, on="damID"
    )
    near_nhd["snap_dist"] = pg.distance(near_nhd.geometry, near_nhd.source_pt)
    near_nhd = (
        near_nhd.reset_index().sort_values(by=["id", "snap_dist"]).groupby("id").first()
    )

    ix = near_nhd.index
    df.loc[ix, "snapped"] = True
    df.loc[ix, "geometry"] = from_pygeos(near_nhd.geometry)
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
    snap_start = time()
    tmp = nhd_dams.reset_index()  # reset index so we have unique index to join on
    near_nhd = nearest(
        to_snap.geometry, tmp.geometry, distance=to_snap.snap_tolerance
    ).rename(columns={"distance": "snap_dist"})

    near_nhd = near_nhd.join(to_snap.geometry.rename("source_pt")).join(
        tmp, on="index_right"
    )
    near_nhd = (
        near_nhd.reset_index().sort_values(by=["id", "snap_dist"]).groupby("id").first()
    )

    ix = near_nhd.index
    df.loc[ix, "snapped"] = True
    df.loc[ix, "geometry"] = from_pygeos(near_nhd.geometry)
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
    print(
        "Snapped {:,} dams to NHD dam points in {:.2f}s".format(
            len(ix), time() - snap_start
        )
    )

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

    ### Attempt to snap to waterbody drain points for major waterbodies
    # Use larger tolerance for larger waterbodies
    print("Snapping to waterbodies and drain points..")
    wb = from_geofeather_as_pygeos(
        nhd_dir / "merged" / "waterbodies.feather"
    ).set_index("wbID")
    drains = (
        from_geofeather_as_pygeos(nhd_dir / "merged" / "waterbody_drain_points.feather")
        .rename(columns={"id": "drainID"})
        .set_index("drainID")
    )

    ### First pass - find the dams that are contained by waterbodies
    # have to do this in geopandas since it performs better than pygeos
    # until pygeos has prepared geoms
    d = to_gdf(to_snap, crs=CRS)
    wbd = to_gdf(wb, crs=CRS)
    d.sindex
    wbd.sindex
    contained_start = time()
    in_wb = gp.sjoin(d, wbd, how="inner").index_right.rename("wbID")

    # update wbID in dataset, but this doesn't mean it is snapped
    ix = in_wb.index
    df.loc[ix, "wbID"] = in_wb

    print(
        "Found {:,} dams in waterbodies in {:.2f}s".format(
            len(in_wb), time() - contained_start
        )
    )

    print("Finding nearest drain points...")
    snap_start = time()
    # join back to pygeos geoms and join to drains
    # NOTE: this may produce multiple drains for some waterbodies
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
    in_wb["snap_dist"] = pg.distance(in_wb.geometry, in_wb.drain)

    # drop any that are > 500 m away, these aren't useful
    in_wb = in_wb.loc[in_wb.snap_dist <= 500].copy()

    # take the closest drain point
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
    df.loc[ix, "geometry"] = from_pygeos(close_enough.drain)
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
        "Found {:,} dams within tolerance of the drain points for their waterbody in {:.2f}s".format(
            len(ix), time() - snap_start
        )
    )

    # Any that are > tolerance away from their own drain, but within tolerance of another drain
    # should snap to the other drain; these are in chains of multiple waterbodies.
    # Visually confirmed this by looking at several.
    snap_start = time()
    further = in_wb.loc[in_wb.snap_dist > in_wb.snap_tolerance].copy()
    nearest_drains = nearest(further.geometry, drains.geometry, further.snap_tolerance)

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
    df.loc[ix, "geometry"] = from_pygeos(near_neighbor.drain)
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
    df.loc[ix, "geometry"] = from_pygeos(further.drain)
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
    nearest_drains = nearest(to_snap.geometry, drains.geometry, to_snap.snap_tolerance)

    nearest_drains = nearest_drains.join(to_snap.geometry).join(
        drains[["geometry", "wbID", "lineID"]].rename(columns={"geometry": "drain"}),
        on="drainID",
    )

    ix = nearest_drains.index
    df.loc[ix, "snapped"] = True
    df.loc[ix, "geometry"] = from_pygeos(nearest_drains.drain)
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

    for region, HUC2s in list(REGION_GROUPS.items()):
        region_start = time()

        print("\n----- {} ------\n".format(region))

        print("Reading flowlines...")
        flowlines = from_geofeather_as_pygeos(
            nhd_dir / "clean" / region / "flowlines.feather"
        ).set_index("lineID")

        in_region = to_snap.loc[to_snap.HUC2.isin(HUC2s)]
        print(
            "Selected {:,} barriers in region to snap against {:,} flowlines".format(
                len(in_region), len(flowlines)
            )
        )

        print("Finding nearest flowlines...")
        # TODO: can use near instead of nearest, and persist list of near lineIDs per barrier
        # so that we can construct subnetworks with just those
        lines = nearest(
            in_region.geometry, flowlines.geometry, in_region.snap_tolerance
        )
        lines = lines.join(in_region.geometry).join(
            flowlines.geometry.rename("line"), on="lineID"
        )

        # project the point to the line,
        # find out its distance on the line,
        # then interpolate its new coordinates
        lines["geometry"] = pg.line_interpolate_point(
            lines.line, pg.line_locate_point(lines.line, lines.geometry)
        )

        ix = lines.index
        df.loc[ix, "snapped"] = True
        df.loc[ix, "geometry"] = from_pygeos(lines.geometry)
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
    wb = from_geofeather_as_pygeos(
        nhd_dir / "merged" / "large_waterbodies.feather"
    ).set_index("wbID")
    drains = (
        from_geofeather_as_pygeos(
            nhd_dir / "merged" / "large_waterbody_drain_points.feather"
        )
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
    df.loc[ix, "geometry"] = from_pygeos(near_wb.drain)
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

    to_gpkg(
        tmp.drop(columns=["new_pt", "orig_pt"]).reset_index(drop=True),
        out_dir / "{}pre_snap_to_post_snap".format(prefix),
        crs=CRS,
    )
    to_gpkg(
        tmp.drop(columns=["geometry", "new_pt"])
        .rename(columns={"orig_pt": "geometry"})
        .reset_index(drop=True),
        out_dir / "{}pre_snap".format(prefix),
        crs=CRS,
    )
    to_gpkg(
        tmp.drop(columns=["geometry", "orig_pt"])
        .rename(columns={"new_pt": "geometry"})
        .reset_index(drop=True),
        out_dir / "{}post_snap".format(prefix),
        crs=CRS,
    )
