from time import time

import geopandas as gp
import pandas as pd
import pygeos as pg

from analysis.lib.pygeos_util import explode
from analysis.lib.flowlines import cut_flowlines_at_points


# In order to cut a flowline, it must be at least this long, and at least
# this different from original flowline
CUT_TOLERANCE = 1


def cut_lines_by_waterbodies(flowlines, joins, waterbodies, next_lineID):
    """
    Cut lines by waterbodies.
    1. Finds all intersections between waterbodies and flowlines.
    2. For those that cross but are not completely contained by waterbodies, cut them.
    3. Evaluate the cuts, only those that have substantive cuts inside and outside are retained as cuts.
    4. Any flowlines that are not contained or crossing waterbodies are dropped from wb_joins

    Parameters
    ----------
    flowlines : GeoDataFrame
    joins : DataFrame
        flowline joins
    waterbodies : GeoDataFrame
    next_lineID : int
        next lineID; must be greater than all prior lines in region

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame, GeoDataFrame, DataFrame)
        (flowlines, joins, waterbodies, waterbody joins)
    """

    start = time()

    waterbodies = waterbodies.copy()

    # Many waterbodies have interior polygons (islands); these break the analysis
    # below for cutting lines.  Extract a new polygon from just the exterior ring
    waterbodies["geometry"] = pg.polygons(
        pg.get_exterior_ring(waterbodies.geometry.values.data)
    )

    # find flowlines that intersect waterbodies
    # NOTE: this uses the outer boundary of polygons from here on out, but
    # original waterbody geometries need to be returned at the end
    join_start = time()
    tree = pg.STRtree(flowlines.geometry.values.data)
    left, right = tree.query_bulk(
        waterbodies.geometry.values.data, predicate="intersects"
    )
    df = pd.DataFrame(
        {
            "lineID": flowlines.index.take(right),
            "flowline": flowlines.geometry.values.data.take(right),
            "wbID": waterbodies.index.take(left),
            "waterbody": waterbodies.geometry.values.data.take(left),
        }
    )
    print(f"Found {len(df):,} waterbody / flowline joins in {time() - join_start:.2f}s")

    # find those that are completely contained; these don't need further processing
    pg.prepare(df.waterbody.values)
    contained_start = time()
    df["contains"] = pg.contains(df.waterbody.values, df.flowline.values)
    print(
        f"Identified {df.contains.sum():,} flowlines contained by waterbodies in {time() - contained_start:.2f}s"
    )

    # for any that are not completely contained, find the ones that overlap
    crosses_start = time()
    df["crosses"] = False
    ix = ~df.contains
    tmp = df.loc[ix]
    df.loc[ix, "crosses"] = pg.crosses(tmp.waterbody, tmp.flowline)
    print(
        f"Identified {df.crosses.sum():,} flowlines that cross edge of waterbodies in {time() - crosses_start:.2f}s"
    )

    # discard any that only touch (don't cross or are contained)
    df = df.loc[df.contains | df.crosses].copy()

    print("Intersecting flowlines and waterbodies...")
    cut_start = time()
    ix = df.crosses
    tmp = df.loc[ix]
    df["geometry"] = df.flowline
    # use intersection to cut flowlines by waterbodies.  Note: this may produce
    # nonlinear (e.g., geom collection) results
    df.loc[ix, "geometry"] = pg.intersection(tmp.flowline, tmp.waterbody)
    df["length"] = pg.length(df.geometry)
    df["flength"] = pg.length(df.flowline)

    # Cut lines that are long enough and different enough from the original lines
    df["to_cut"] = False
    tmp = df.loc[df.crosses]
    keep = (
        tmp.crosses
        & (tmp.length >= CUT_TOLERANCE)
        & ((tmp.flength - tmp.length).abs() >= CUT_TOLERANCE)
    )
    df.loc[keep[keep].index, "to_cut"] = True
    print(
        f"Found {df.to_cut.sum():,} segments that need to be cut by flowlines in {time() - cut_start:.2f}s"
    )

    # DEBUG
    # write_dataframe(
    #     flowlines.loc[np.unique(df.loc[df.to_cut].lineID)], "/tmp/to_cut_fl.gpkg"
    # )
    # write_dataframe(
    #     waterbodies.loc[np.unique(df.loc[df.to_cut].wbID)].drop(columns=["bnd"]),
    #     "/tmp/to_cut_wb.gpkg",
    # )

    # save all that are completely contained or mostly contained and not to be cut
    # must be at least 50% in waterbody to be considered mostly contained.
    # Note: there are some that are mostly outside and we exclude those here
    contained = df.loc[
        (~df.to_cut) & ((df.length / df.flength) >= 0.5), ["wbID", "lineID"]
    ].copy()

    ### Cut lines
    if df.to_cut.sum():
        # only work with those to cut from here on out
        df = gp.GeoDataFrame(df.loc[df.to_cut].copy(), crs=flowlines.crs)
        wbID = df.wbID.unique()

        # calculate all geometric intersections between the flowlines and
        # waterbody exterior rings and drop any that are not points
        # Note: these may be multipoints.
        # We ignore any shared edges, etc that result from the intersection; those
        # aren't helpful for cutting the lines
        print("Finding cut points...")
        df["geometry"] = pg.intersection(
            pg.get_exterior_ring(df.waterbody), df.flowline
        )
        df = explode(explode(df[["geometry", "lineID"]])).reset_index()
        df = df.loc[pg.get_type_id(df.geometry.values.data) == 0].copy()

        points = df.groupby("lineID").geometry.apply(
            lambda g: pg.multipoints(g.values.data)
        )

        cut_start = time()
        new_flowlines, joins, remove_ids = cut_flowlines_at_points(
            flowlines.loc[points.index],
            joins,
            points.geometry.values.data,
            next_lineID=next_lineID,
        )
        print(
            f"{len(new_flowlines):,} new flowlines created in {time() - cut_start:,.2f}s"
        )

        if len(new_flowlines):
            # recalculate overlaps with waterbodies
            print("Recalculating overlaps with waterbodies")
            wb = waterbodies.loc[wbID]
            tree = pg.STRtree(new_flowlines.geometry.values.data)
            left, right = tree.query_bulk(
                wb.geometry.values.data, predicate="intersects"
            )

            df = pd.DataFrame(
                {
                    "lineID": new_flowlines.index.take(right),
                    "flowline": new_flowlines.geometry.values.data.take(right),
                    "wbID": wb.index.take(left),
                    "waterbody": wb.geometry.values.data.take(left),
                }
            )

            pg.prepare(df.waterbody.values)
            contained_start = time()
            df["contains"] = pg.contains(df.waterbody.values, df.flowline.values)
            print(
                f"Identified {df.contains.sum():,} more flowlines contained by waterbodies in {time() - contained_start:.2f}s"
            )

            # some aren't perfectly contained, add those that are mostly in
            df["crosses"] = False
            ix = ~df.contains
            tmp = df.loc[ix]
            df.loc[ix, "crosses"] = pg.crosses(tmp.waterbody, tmp.flowline)

            # discard any that only touch (don't cross or are contained)
            df = df.loc[df.contains | df.crosses].copy()

            tmp = df.loc[df.crosses]
            df["geometry"] = df.flowline
            # use intersection to cut flowlines by waterbodies.  Note: this may produce
            # nonlinear (e.g., geom collection) results
            df.loc[ix, "geometry"] = pg.intersection(tmp.flowline, tmp.waterbody)
            df["length"] = pg.length(df.geometry)
            df["flength"] = pg.length(df.flowline)

            # keep any that are contained or >= 50% in waterbody
            contained = contained.append(
                df.loc[
                    df.contains | ((df.length / df.flength) >= 0.5), ["wbID", "lineID"]
                ],
                ignore_index=True,
            )

            flowlines = (
                flowlines.loc[~flowlines.index.isin(remove_ids)]
                .reset_index()
                .append(new_flowlines.reset_index(), ignore_index=True)
                .set_index("lineID")
            )

    # make sure that updated joins are unique
    joins = joins.drop_duplicates(subset=["upstream_id", "downstream_id"])

    # make sure that wb_joins is unique
    contained = contained.sort_values(by=["lineID", "wbID"]).drop_duplicates(
        keep="first"
    )

    # set flag for flowlines in waterbodies
    flowlines["waterbody"] = flowlines.index.isin(contained.lineID.unique())

    print(
        "Done evaluating waterbody / flowline overlap in {:.2f}s".format(time() - start)
    )

    return flowlines, joins, contained
