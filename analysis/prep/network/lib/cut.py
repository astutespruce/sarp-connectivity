from time import time

import geopandas as gp
import pandas as pd
import pygeos as pg
import numpy as np
from pyogrio import write_dataframe

from nhdnet.nhd.joins import update_joins
from analysis.lib.pygeos_util import explode, sjoin_geometry, cut_line_at_points
from analysis.prep.network.lib.lines import calculate_sinuosity
from analysis.constants import CRS


# In order to cut a flowline, it must be at least this long, and at least
# this different from original flowline
CUT_TOLERANCE = 1


def cut_lines_by_waterbodies(flowlines, joins, waterbodies, wb_joins, out_dir):
    """
    Cut lines by waterbodies.
    1. Intersects all previously intersected flowlines with waterbodies.
    2. For those that cross but are not completely contained by waterbodies, cut them.
    3. Evaluate the cuts, only those that have substantive cuts inside and outside are retained as cuts.
    4. Any flowlines that are not contained or crossing waterbodies are dropped from wb_joins

    Parameters
    ----------
    flowlines : GeoDataFrame
    joins : DataFrame
        flowline joins
    waterbodies : GeoDataFrame
    wb_joins : DataFrame
        waterbody flowline joins
    out_dir : pathlib.Path
        output directory for writing error files, if needed

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame, GeoDataFrame, DataFrame)
        (flowlines, joins, waterbodies, waterbody joins)
    """

    start = time()

    # convert to Series for easier processing
    fl_geom = flowlines.loc[flowlines.index.isin(wb_joins.lineID)].geometry
    fl_geom = pd.Series(fl_geom.values.data, name="flowline", index=fl_geom.index)

    # Many waterbodies have interior polygons (islands); these break the analysis below for cutting lines
    # Extract a new polygon of just their outer boundary
    wb_geom = pd.Series(
        pg.polygons(pg.get_exterior_ring(waterbodies.geometry.values.data)),
        name="waterbody",
        index=waterbodies.index,
    )

    print("Validating waterbodies...")
    ix = ~pg.is_valid(wb_geom.values)
    invalid_count = ix.sum()
    if invalid_count:
        print("{:,} invalid waterbodies found, repairing...".format(invalid_count))

        # Buffer by 0 to fix
        # TODO: may need to do this by a small fraction and simplify instead
        repair_start = time()
        wb_geom.loc[ix] = pg.buffer(wb_geom.loc[ix].values, 0)
        print("Repaired geometry in {:.2f}s".format(time() - repair_start))

    ### Find flowlines that cross edge of waterbodies
    print("Finding waterbodies that overlap flowlines...")
    # these are the only ones that need to be cut
    # NOTE: it is faster to use intersects w/ tree first, then crosses afterward
    join_start = time()
    df = (
        pd.DataFrame(sjoin_geometry(wb_geom, fl_geom).rename("lineID").reset_index())
        .join(wb_geom, on="wbID")
        .join(fl_geom, on="lineID")
    )
    print(
        f"Identified {len(df):,} intersections between flowlines and waterbodies in {time() - join_start:.2f}s"
    )

    pg.prepare(df.waterbody)

    # find those that are completely contained
    contained_start = time()
    df["contains"] = pg.contains(df.waterbody, df.flowline)
    print(
        f"Identified {df.contains.sum():,} flowlines contained by waterbodies in {time() - contained_start:.2f}s"
    )

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

    print("Cutting flowlines by waterbodies...")
    cut_start = time()
    ix = df.crosses
    tmp = df.loc[ix]
    df["geometry"] = df.flowline
    df.loc[ix, "geometry"] = pg.intersection(tmp.flowline, tmp.waterbody)
    df["length"] = pg.length(df.geometry)
    df["flength"] = pg.length(df.flowline)

    # Cut only single lines (rest are noise) that are long enough and different
    # enough from the original lines
    df["to_cut"] = False
    tmp = df.loc[df.crosses]
    keep = (
        tmp.crosses
        & (pg.get_type_id(tmp.geometry) == 1)
        & (tmp.length >= CUT_TOLERANCE)
        & ((tmp.flength - tmp.length).abs() >= CUT_TOLERANCE)
    )
    df.loc[keep[keep].index, "to_cut"] = True
    print(
        f"Found {df.to_cut.sum():,} segments that need to be cut by flowlines in {time() - cut_start:.2f}s"
    )

    # Sanity check - we will get problems if a flowline is cut by more than one waterbody
    errors = df.loc[df.to_cut].groupby("lineID").size() > 1
    if errors.sum():
        multiple_wb = gp.GeoDataFrame(
            df.loc[errors[errors].index, ["wbID", "lineID", "geometry"]],
            crs=waterbodies.crs,
        )
        write_dataframe(multiple_wb, "/tmp/multiple_wb_fl_cuts.gpkg")

        raise ValueError(
            "ERROR: one or more flowlines cut by multiple waterbodies.  See /tmp/multiple_wb_fl_cuts.gpkg"
        )

    # mark those that are completely contained or mostly within as in waterbodies
    # except those to be cut
    df["in_wb"] = False
    ix = ((df.length / df.flength) >= 0.5) & (  # must be at least 50% in waterbody
        ~df.to_cut
    )
    df.loc[ix, "in_wb"] = True

    # Update wb_joins based on this
    wb_joins = df.loc[ix, ["wbID", "lineID", "length"]].copy()

    ### Cut lines
    print("Cutting lines...")
    df = df.loc[df.to_cut].copy()

    # Find the points of the new segment in the waterbody that are within flowline endpoints
    # note: since lines are oriented the same way, we know the point is interior
    # to the line if first is > 0 or last < length of flowline
    first = pg.get_point(df.geometry, 0)
    last = pg.get_point(df.geometry, -1)

    # get index of intersected segment within the split lines
    # either it is the first segment, or it is at index 1 (for 3 lines, or second of 2 lines)
    df["in_wb_ix"] = (pg.line_locate_point(df.flowline, first) > CUT_TOLERANCE).astype(
        "uint8"
    )

    split_lines = gp.GeoDataFrame(
        {
            "geometry": df.apply(
                lambda row: cut_line_at_points(
                    row.flowline,
                    pg.get_point(row.geometry, [0, -1]),
                    tolerance=CUT_TOLERANCE,
                ),
                axis=1,
            )
        },
        index=df.index,
        crs=waterbodies.crs,
    ).join(
        (pg.line_locate_point(df.flowline, first) != 0)
        .astype("uint8")
        .rename("in_wb_ix")
    )
    new_lines = explode(split_lines, add_position=True)
    new_lines["in_wb"] = new_lines.in_wb_ix == new_lines.position
    new_lines = (
        new_lines.drop(columns=["in_wb_ix", "position"])
        .join(df[["wbID", "lineID"]].rename(columns={"lineID": "origLineID"}))
        .join(
            flowlines.drop(columns=["geometry", "length", "sinuosity"]), on="origLineID"
        )
    )

    # recalculate length and sinuosity
    new_lines["length"] = pg.length(new_lines.geometry.values.data).astype("float32")
    new_lines["sinuosity"] = calculate_sinuosity(new_lines.geometry.values.data).astype(
        "float32"
    )

    # calculate new IDS
    next_segment_id = int(flowlines.index.max() + 1)
    new_lines["lineID"] = next_segment_id + np.arange(len(new_lines))
    new_lines.lineID = new_lines.lineID.astype("uint32")

    ### Update flowline joins
    # transform new lines to create new joins
    l = new_lines.groupby("origLineID").lineID
    # the first new line per original line is the furthest upstream, so use its
    # ID as the new downstream ID for anything that had this origLineID as its downstream
    first = l.first().rename("new_downstream_id")
    # the last new line per original line is the furthest downstream...
    last = l.last().rename("new_upstream_id")

    # Update existing joins with the new lineIDs we created at the upstream or downstream
    # ends of segments we just created
    joins = update_joins(
        joins,
        first,
        last,
        downstream_col="downstream_id",
        upstream_col="upstream_id",
    )

    ### Create new line joins for any that weren't inserted above
    # Transform all groups of new line IDs per original lineID, wbID
    # into joins structure
    pairs = lambda a: pd.Series(zip(a[:-1], a[1:]))
    new_joins = (
        new_lines.groupby(["origLineID", "wbID"])
        .lineID.apply(pairs)
        .apply(pd.Series)
        .reset_index()
        .rename(columns={0: "upstream_id", 1: "downstream_id"})
        .join(
            flowlines[["NHDPlusID", "loop", "HUC4"]].rename(
                columns={"NHDPlusID": "upstream"}
            ),
            on="origLineID",
        )
    )
    # NHDPlusID is same for both sides
    new_joins["downstream"] = new_joins.upstream
    new_joins["type"] = "internal"
    new_joins = new_joins[
        [
            "upstream",
            "downstream",
            "upstream_id",
            "downstream_id",
            "type",
            "loop",
            "HUC4",
        ]
    ]

    joins = (
        joins.append(new_joins, ignore_index=True, sort=False)
        .sort_values(["downstream_id", "upstream_id"])
        .reset_index(drop=True)
    )

    ### remove original flowlines and append these ones
    remove_ix = new_lines.origLineID.unique()
    flowlines = (
        flowlines.loc[~flowlines.index.isin(remove_ix)]
        .reset_index()
        .append(
            new_lines[["lineID"] + list(flowlines.columns)],
            ignore_index=True,
            sort=False,
        )
        .sort_values("lineID")
        .set_index("lineID")
    )

    ### add to waterbody joins
    # group to get first, just in case
    wb_joins = (
        wb_joins.append(
            new_lines.loc[new_lines.in_wb, ["wbID", "lineID", "length"]],
            sort=False,
            ignore_index=True,
        )
        .reset_index(drop=True)
        .groupby(["lineID", "wbID"])
        .first()
        .reset_index()
    )

    # set flag for flowlines in waterbodies
    flowlines["waterbody"] = flowlines.index.isin(wb_joins.lineID.unique())

    # calculate flowline stats
    stats = (
        wb_joins.groupby("wbID").length.sum().astype("float32").rename("flowlineLength")
    )
    waterbodies = waterbodies.join(stats)
    waterbodies.flowlineLength = waterbodies.flowlineLength.fillna(0)
    waterbodies.index = waterbodies.index.astype("uint32")

    wb_joins = wb_joins.drop(columns=["length"])

    print(
        "Done evaluating waterbody / flowline overlap in {:.2f}s".format(time() - start)
    )

    return flowlines, joins, waterbodies, wb_joins
