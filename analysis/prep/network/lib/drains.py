from time import time

import geopandas as gp
import numpy as np
from shapely.geometry import Point


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
    drain_pts = gp.GeoDataFrame(
        wb_joins.loc[wb_joins.lineID.isin(drains.upstream_id)]
        .join(waterbodies[["AreaSqKm", "flowlineLength"]], on="wbID")
        .join(flowlines.geometry, on="lineID")
        .reset_index(drop=True),
        crs=flowlines.crs,
    )

    # create a point from the last coordinate, which is the furthest one downstream
    drain_pts.geometry = drain_pts.geometry.apply(
        lambda g: Point(np.column_stack(g.xy)[-1])
    )

    drain_pts.wbID = drain_pts.wbID.astype("uint32")
    drain_pts.lineID = drain_pts.lineID.astype("uint32")
    drain_pts.flowlineLength = drain_pts.flowlineLength.astype("float32")

    print(
        "Done extracting {:,} waterbody drain points in {:.2f}s".format(
            len(drain_pts), time() - start
        )
    )

    return drain_pts.reset_index(drop=True)
