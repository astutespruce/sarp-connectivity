from time import time

import pandas as pd
import geopandas as gp
import numpy as np
import pygeos as pg

from analysis.lib.joins import find_joins
from analysis.lib.graph import DirectedGraph
from analysis.lib.geometry import sjoin_geometry


def create_drain_points(flowlines, joins, waterbodies, wb_joins):
    """Create drain points from furthest downstream point of flowlines that overlap with waterbodies.

    WARNING: If multiple flowlines intersect at the drain point, there will be multiple drain points at the same location

    Parameters
    ----------
    flowlines : GeoDataFrame
    joins : DataFrame
        flowline joins
    waterbodies : GeoDataFrame
    wb_joins : DataFrame
        waterbody / flowline joins

    Returns
    -------
    GeoDataFrame
        Drain points dataframe
    """
    start = time()

    wb_atts = waterbodies[["altered", "km2", "flowlineLength"]].copy()

    tmp_flowlines = flowlines[
        [
            "geometry",
            "FCode",
            "FType",
            "MaxElevSmo",
            "MinElevSmo",
            "Slope",
            "TotDASqKm",
            "StreamOrde",
            "sizeclass",
            "HUC4",
            "loop",
        ]
    ].rename(columns={"FCode": "lineFCode", "FType": "lineFType"})

    ### Find the downstream most point(s) on the flowline for each waterbody
    # This is used for snapping barriers, if possible.
    # Drop any where there is no flowline below the drain point (often pipelines
    # that were removed)
    tmp = wb_joins[["lineID", "wbID"]].set_index("lineID")
    drains = (
        joins.loc[joins.upstream_id.isin(wb_joins.lineID) & (joins.downstream_id != 0)]
        .join(tmp.wbID.rename("upstream_wbID"), on="upstream_id")
        .join(tmp.wbID.rename("downstream_wbID"), on="downstream_id")
    )

    # Only keep those that terminate outside the same waterbody as the upstream end
    drains = drains.loc[drains.upstream_wbID != drains.downstream_wbID].copy()

    # Join in stats from waterbodies and geometries from flowlines
    drain_pts = (
        wb_joins.loc[wb_joins.lineID.isin(drains.upstream_id)]
        .join(wb_atts, on="wbID",)
        .join(tmp_flowlines, on="lineID",)
        .reset_index(drop=True)
    )

    # create a point from the last coordinate, which is the furthest one downstream
    drain_pts.geometry = pg.get_point(drain_pts.geometry.values.data, -1)
    drain_pts["headwaters"] = False

    ### Extract the drain points of upstream headwaters waterbodies
    # these are flowlines that originate at a waterbody
    wb_geom = waterbodies.loc[waterbodies.flowlineLength == 0].geometry
    wb_geom = pd.Series(wb_geom.values.data, index=wb_geom.index)
    # take only the upstream most point
    tmp_flowline_pts = tmp_flowlines.copy()
    tmp_flowline_pts["geometry"] = pg.get_point(flowlines.geometry.values.data, 0)
    fl_pt = pd.Series(
        tmp_flowline_pts.geometry.values.data, index=tmp_flowline_pts.index
    )
    headwaters = (
        sjoin_geometry(wb_geom, fl_pt, predicate="intersects")
        .rename("lineID")
        .reset_index()
    )
    headwaters = (
        headwaters.join(wb_atts, on="wbID",)
        .join(tmp_flowline_pts, on="lineID",)
        .reset_index(drop=True)
    )
    headwaters["headwaters"] = True
    print(
        f"Found {len(headwaters):,} headwaters waterbodies, adding drain points for these too"
    )

    drain_pts = drain_pts.append(headwaters, sort=False, ignore_index=True).reset_index(
        drop=True
    )

    drain_pts = gp.GeoDataFrame(drain_pts, geometry="geometry", crs=flowlines.crs)

    # calculate unique index
    huc_id = drain_pts["HUC4"].astype("uint16") * 1000000
    drain_pts["drainID"] = drain_pts.index.values.astype("uint32") + huc_id

    # sort by drainage area so that smaller streams come first because
    # we are searching from upstream end
    drain_pts = drain_pts.sort_values(by=["wbID", "loop", "TotDASqKm"], ascending=True)

    ### Deduplicate by location
    # First deduplicate any that have the same point, and take the non-loop side if possible.
    # Sometimes multiple lines converge at the same drain point.
    # calculate the hash of the wkb
    orig = len(drain_pts)
    drain_pts["hash"] = pd.util.hash_array(pg.to_wkb(drain_pts.geometry.values.data))
    drain_pts = drain_pts.groupby("hash").first().reset_index().drop(columns=["hash"])
    print(f"Dropped {orig - len(drain_pts):,} drain points at duplicate locations")

    ### Deduplicate drains by network topology
    # Find the downstream-most drains for waterbodies when there are multiple.
    # These may result from flowlines that cross in and out of waterbodies multiple
    # times (not valid), or there may be drains on downstream loops
    # (esp. at dams) (valid).

    dups = drain_pts.groupby("wbID").size() > 1
    if dups.sum():
        print(
            f"Found {dups.sum():,} waterbodies with multiple drain points; cleaing up"
        )
        # find all waterbodies that have duplicate drains
        ix = drain_pts.wbID.isin(dups[dups].index)
        wb_ids = drain_pts.loc[ix].wbID.unique()
        # find all corresponding line IDs
        line_ids = wb_joins.loc[wb_joins.wbID.isin(wb_ids)].lineID.unique()
        lines_per_wb = (
            drain_pts.loc[drain_pts.wbID.isin(wb_ids)].groupby("wbID").lineID.unique()
        )
        # search within 3 degrees removed from ids; this hopefully
        # picks up any gaps where lines exit waterbodies for a ways then re-enter
        pairs = find_joins(
            joins,
            line_ids,
            downstream_col="downstream_id",
            upstream_col="upstream_id",
            expand=3,
        )[["upstream_id", "downstream_id"]]

        # remove any terminal points
        pairs = pairs.loc[(pairs.upstream_id != 0) & (pairs.downstream_id != 0)]

        # create a directed graph facing DOWNSTREAM
        graph = DirectedGraph(pairs, source="upstream_id", target="downstream_id")
        # find all lines that are upstream of other lines
        # these are "parents" in the directed graph
        upstreams = graph.find_all_parents(lines_per_wb.values)
        ix = pd.Series(upstreams).explode().dropna().unique()
        print(
            f"Dropping {len(ix):,} drains that are upstream of other drains in the same waterbody"
        )
        drain_pts = drain_pts.loc[~drain_pts.lineID.isin(ix)]

    # Convert back to GeoDataFrame; above steps make it into a DataFrame
    drain_pts = gp.GeoDataFrame(drain_pts, geometry="geometry", crs=flowlines.crs)
    drain_pts.wbID = drain_pts.wbID.astype("uint32")
    drain_pts.lineID = drain_pts.lineID.astype("uint32")
    drain_pts.flowlineLength = drain_pts.flowlineLength.astype("float32")

    print(
        "Done extracting {:,} waterbody drain points in {:.2f}s".format(
            len(drain_pts), time() - start
        )
    )

    return drain_pts
