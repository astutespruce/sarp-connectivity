from time import time

import pandas as pd
import geopandas as gp
import numpy as np
import pygeos as pg

from analysis.lib.pygeos_util import sjoin_geometry


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
        ]
    ].rename(columns={"FCode": "lineFCode", "FType": "lineFType"})

    ### Find the downstream most point(s) on the flowline for each waterbody
    # this is used for snapping barriers, if possible
    tmp = wb_joins[["lineID", "wbID"]].set_index("lineID")
    drains = (
        joins.loc[joins.upstream_id.isin(wb_joins.lineID)]
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
    fl_geom = pd.Series(flowlines.geometry.values.data, index=flowlines.index)
    headwaters = (
        sjoin_geometry(wb_geom, fl_geom, predicate="intersects")
        .rename("lineID")
        .reset_index()
    )
    headwaters = (
        headwaters.join(wb_atts, on="wbID",)
        .join(tmp_flowlines, on="lineID",)
        .reset_index(drop=True)
    )
    headwaters.geometry = pg.get_point(headwaters.geometry.values.data, 0)
    headwaters["headwaters"] = True
    print(
        f"Found {len(headwaters):,} headwaters waterbodies, adding drain points for these too"
    )

    drain_pts = drain_pts.append(headwaters, sort=False, ignore_index=True).reset_index(
        drop=True
    )

    # calculate unique index
    huc_id = drain_pts["HUC4"].astype("uint16") * 1000000
    drain_pts["drainID"] = drain_pts.index.values.astype("uint32") + huc_id

    drain_pts.wbID = drain_pts.wbID.astype("uint32")
    drain_pts.lineID = drain_pts.lineID.astype("uint32")
    drain_pts.flowlineLength = drain_pts.flowlineLength.astype("float32")
    drain_pts = gp.GeoDataFrame(drain_pts, geometry="geometry", crs=flowlines.crs)

    print(
        "Done extracting {:,} waterbody drain points in {:.2f}s".format(
            len(drain_pts), time() - start
        )
    )

    return drain_pts
