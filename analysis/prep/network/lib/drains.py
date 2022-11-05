from time import time

import pandas as pd
import geopandas as gp
import shapely

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
            "MaxElev",
            "MinElev",
            "Slope",
            "TotDASqKm",
            "StreamOrder",
            "sizeclass",
            "Divergence",
            "AnnualFlow",
            "AnnualVelocity",
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
        joins.loc[
            joins.upstream_id.isin(wb_joins.lineID.unique())
            & (joins.downstream_id != 0)
        ]
        .join(tmp.wbID.rename("upstream_wbID"), on="upstream_id")
        .join(tmp.wbID.rename("downstream_wbID"), on="downstream_id")
    )

    # Only keep those that terminate outside the same waterbody as the upstream end
    drains = drains.loc[drains.upstream_wbID != drains.downstream_wbID].copy()

    # Join in stats from waterbodies and geometries from flowlines
    drain_pts = (
        wb_joins.loc[wb_joins.lineID.isin(drains.upstream_id.unique())]
        .join(
            wb_atts,
            on="wbID",
        )
        .join(
            tmp_flowlines[["geometry", "loop", "TotDASqKm"]],
            on="lineID",
        )
        .reset_index(drop=True)
    )

    # create a point from the last coordinate, which is the furthest one downstream
    drain_pts.geometry = shapely.get_point(drain_pts.geometry.values.data, -1)

    # drop any that are downstream terminals; these are most likely waterbodies
    # that do not have further downstream networks (e.g., flow to ocean)
    ix = joins.loc[
        joins.upstream_id.isin(drain_pts.lineID) & (joins.downstream_id == 0)
    ].upstream_id
    drain_pts = drain_pts.loc[~drain_pts.lineID.isin(ix)].copy()

    ### Find all drain points that share the same geometry.
    # These are most likely multiple segments that terminate in same drain point,
    # so we need to assign them their common downstream ID instead so that
    # snapping dams to these works properly later (otherwise snapped to only one of segments)
    drain_pts["hash"] = pd.util.hash_array(
        shapely.to_wkb(drain_pts.geometry.values.data)
    )
    s = drain_pts.groupby("hash").size()
    ix = drain_pts.hash.isin(s[s > 1].index)
    if ix.sum():
        print(f"Deduplicating {ix.sum():,} duplicate drain points")
        # find downstream_id for each of these, and deduplicate if there are multiple
        # downstreams, favoring the non-loops
        j = (
            joins.loc[
                joins.upstream_id.isin(drain_pts.loc[ix].lineID)
                & (joins.downstream_id != 0),
                ["upstream_id", "downstream_id", "loop"],
            ]
            .sort_values(by=["upstream_id", "loop"], ascending=True)
            .groupby("upstream_id")
            .first()
            .downstream_id
        )

        drain_pts = drain_pts.join(j, on="lineID")

        # for those at same location that share the same downstream line, use that line instead
        s = (
            drain_pts.loc[drain_pts.downstream_id.notnull()]
            .groupby("downstream_id")
            .size()
        )
        ix = drain_pts.downstream_id.isin(s[s > 1].index.astype("uint32"))
        drain_pts.loc[ix, "lineID"] = drain_pts.loc[ix].downstream_id.astype("uint32")
        # update the line properties to match that lineID
        lids = drain_pts.loc[ix].lineID.values
        drain_pts.loc[ix, "flowlineLength"] = flowlines.loc[lids, "length"].values
        drain_pts.loc[ix, "loop"] = flowlines.loc[lids].loop.values
        drain_pts.loc[ix, "TotDASqKm"] = flowlines.loc[lids].TotDASqKm.values
        drain_pts = drain_pts.drop(columns=["downstream_id"])

    # keep the first unique drain point and sort the rest so they are oriented
    # from upstream to downstream
    drain_pts = (
        drain_pts.drop(columns=["hash"])
        .groupby(["lineID", "wbID"])
        .first()
        .sort_values(by="TotDASqKm", ascending=True)
        .reset_index()
    )

    drain_pts = gp.GeoDataFrame(drain_pts, geometry="geometry", crs=flowlines.crs)

    ### Deduplicate drains by network topology
    # Find the downstream-most drains for waterbodies when there are multiple distinct ones per waterbody.
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
        # find all corresponding line IDs for these waterbodies
        line_ids = wb_joins.loc[wb_joins.wbID.isin(wb_ids)].lineID.unique()
        lines_per_wb = (
            drain_pts.loc[drain_pts.wbID.isin(wb_ids)].groupby("wbID").lineID.unique()
        )
        # search within 20 degrees removed from ids; this hopefully
        # picks up any gaps where lines exit waterbodies for a ways then re-enter
        # some floodplain areas have very big loops outside waterbody
        pairs = find_joins(
            joins,
            line_ids,
            downstream_col="downstream_id",
            upstream_col="upstream_id",
            expand=20,
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

    ### check if drain points are on a loop and very close to the junction
    # of the loop and nonloop (e.g., Hoover Dam, HUC2 == 15)
    drain_pts["snap_to_junction"] = False
    drain_pts["snap_dist"] = 0

    drains_by_wb = drain_pts.groupby("wbID").size()
    multiple_drain_wb = drains_by_wb[drains_by_wb > 1].index

    # limit this to drain points on loops where there are multiple drains per waterbody
    loop_pts = drain_pts.loc[
        drain_pts.loop & (drain_pts.wbID.isin(multiple_drain_wb))
    ].copy()

    # search within 3 degrees removed from ids; this hopefully
    # picks up any downstream junctions
    pairs = find_joins(
        joins,
        loop_pts.lineID.unique(),
        downstream_col="downstream_id",
        upstream_col="upstream_id",
        expand=3,
    )[["upstream_id", "downstream_id"]]

    # drop endpoints
    pairs = pairs.loc[(pairs.upstream_id != 0) & (pairs.downstream_id != 0)].copy()

    # find all junctions that have > 1 flowline upstream of them
    grouped = pairs.groupby("downstream_id").size()
    downstream_junctions = grouped[grouped > 1].index
    # extract upstream endoint for each junction line
    downstream_junction_pts = pd.Series(
        shapely.get_point(flowlines.loc[downstream_junctions].geometry.values.data, 0),
        index=downstream_junctions,
    )
    # find the nearest junctions within 5m tolerance of drain points on loops
    tree = shapely.STRtree(downstream_junction_pts.values.data)
    left, right = tree.query_nearest(loop_pts.geometry.values.data, max_distance=5)

    # make sure they are connected on the network
    g = DirectedGraph(pairs, source="upstream_id", target="downstream_id")
    ix = g.is_reachable(
        loop_pts.iloc[left].lineID.values, downstream_junction_pts.iloc[right].index
    )
    left = left[ix]
    right = right[ix]

    if len(left):
        print(
            f"Found {len(left)} drains on loops within 5m upstream of a junction, updating them..."
        )
        # NOTE: these are attributed to the flowline that is DOWNSTREAM of the junction point
        # whereas other drains are attributed to the flowline upstream of themselves
        ix = loop_pts.index.take(left)
        drain_pts.loc[ix, "snap_to_junction"] = True
        drain_pts.loc[ix, "snap_dist"] = shapely.distance(
            drain_pts.loc[ix].geometry.values.data,
            downstream_junction_pts.iloc[right].values,
        )
        drain_pts.loc[ix, "lineID"] = downstream_junction_pts.iloc[right].index
        drain_pts.loc[ix, "geometry"] = downstream_junction_pts.iloc[right].values

    ### Extract the drain points of upstream headwaters waterbodies
    # these are flowlines that originate at a waterbody
    wb_geom = waterbodies.loc[waterbodies.flowlineLength == 0].geometry
    wb_geom = pd.Series(wb_geom.values.data, index=wb_geom.index)
    # take only the upstream most point
    tmp_flowline_pts = tmp_flowlines[["geometry", "loop", "TotDASqKm"]].copy()
    tmp_flowline_pts["geometry"] = shapely.get_point(flowlines.geometry.values.data, 0)
    fl_pt = pd.Series(
        tmp_flowline_pts.geometry.values.data, index=tmp_flowline_pts.index
    )
    headwaters = (
        sjoin_geometry(wb_geom, fl_pt, predicate="intersects")
        .rename("lineID")
        .reset_index()
    )
    headwaters = (
        headwaters.join(
            wb_atts,
            on="wbID",
        )
        .join(
            tmp_flowline_pts,
            on="lineID",
        )
        .reset_index(drop=True)
    )
    headwaters["headwaters"] = True
    headwaters["snap_to_junction"] = False
    headwaters["snap_dist"] = 0
    print(
        f"Found {len(headwaters):,} headwaters waterbodies, adding drain points for these too"
    )

    drain_pts["headwaters"] = False
    drain_pts = pd.concat(
        [drain_pts, headwaters], sort=False, ignore_index=True
    ).reset_index(drop=True)

    # join in line properties
    drain_pts = drain_pts.drop(columns=["loop", "TotDASqKm"]).join(
        tmp_flowlines.drop(columns=["geometry"]), on="lineID"
    )

    # calculate unique index
    huc_id = drain_pts["HUC4"].astype("uint16") * 1000000
    drain_pts["drainID"] = drain_pts.index.values.astype("uint32") + huc_id

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
