from pathlib import Path
from time import time

import geopandas as gp
import pandas as pd
import pygeos as pg
import numpy as np


from analysis.lib.joins import index_joins, find_joins, update_joins, remove_joins
from analysis.lib.graph import find_adjacent_groups
from analysis.lib.geometry import calculate_sinuosity

from analysis.lib.geometry import (
    cut_lines_at_multipoints,
    explode,
    cut_line_at_points,
)

from analysis.constants import SNAP_ENDPOINT_TOLERANCE

# In order to cut a flowline, it must be at least this long, and at least
# this different from original flowline
CUT_TOLERANCE = 1


def prep_new_flowlines(flowlines, new_segments):
    """Add necessary attributes to new segments then append to flowlines and return.

    Calculates length and sinuosity for new segments.

    Parameters
    ----------
    flowlines : GeoDataFrame
        flowlines to append to
    new_segments : GeoDataFrame
        new segments to append to flowlines.

    Returns
    -------
    GeoDataFrame
    """
    # join in data from flowlines into new segments
    new_flowlines = new_segments.join(
        flowlines.drop(columns=["geometry", "lineID"]), on="origLineID"
    )

    # calculate length and sinuosity
    new_flowlines["length"] = new_flowlines.length
    new_flowlines["sinuosity"] = calculate_sinuosity(
        new_flowlines.geometry.values.data
    ).astype("float32")

    return new_flowlines


def remove_pipelines(flowlines, joins, max_pipeline_length=100):
    """Remove pipelines that are above max length,
    based on contiguous length of pipeline segments.

    Parameters
    ----------
    flowlines : GeoDataFrame
    joins : DataFrame
            joins between flowlines
    max_pipeline_length : int, optional (default: 100)
            length above which pipelines are dropped

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
            (flowlines, joins)
    """

    start = time()
    pids = flowlines.loc[flowlines.FType == 428].index
    pjoins = find_joins(
        joins, pids, downstream_col="downstream_id", upstream_col="upstream_id"
    )[["downstream_id", "upstream_id"]]
    print(f"Found {len(pids):,} pipelines and {len(pjoins):,} pipeline-related joins")

    # Drop any isolated pipelines no matter what size
    # these either are one segment long, or are upstream / downstream terminals for
    # non-pipeline segments
    join_idx = index_joins(
        pjoins, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    drop_ids = join_idx.loc[
        (
            join_idx.upstream_id == join_idx.downstream_id
        )  # has upstream and downstream of 0s
        | (
            ((join_idx.upstream_id == 0) & (~join_idx.downstream_id.isin(pids)))
            | ((join_idx.downstream_id == 0) & (~join_idx.upstream_id.isin(pids)))
        )
    ].index
    print(f"Removing {len(drop_ids):,} isolated segments")

    # remove from flowlines, joins, pjoins
    flowlines = flowlines.loc[~flowlines.index.isin(drop_ids)].copy()
    joins = remove_joins(
        joins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    pjoins = remove_joins(
        pjoins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    join_idx = join_idx.loc[~join_idx.index.isin(drop_ids)].copy()

    # Find single connectors between non-pipeline segments
    # drop those > max_pipeline_length
    singles = join_idx.loc[
        ~(join_idx.upstream_id.isin(pids) | join_idx.downstream_id.isin(pids))
    ].join(flowlines["length"])
    drop_ids = singles.loc[singles.length >= max_pipeline_length].index

    print(
        f"Found {len(drop_ids):,} pipeline segments between flowlines that are > {max_pipeline_length:,}m; they will be dropped"
    )

    # remove from flowlines, joins, pjoins
    flowlines = flowlines.loc[~flowlines.index.isin(drop_ids)].copy()
    joins = remove_joins(
        joins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    pjoins = remove_joins(
        pjoins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )
    join_idx = join_idx.loc[~join_idx.index.isin(drop_ids)].copy()

    ### create a network of pipelines to group them together
    # Only use contiguous pipelines; those that are not contiguous should have been handled above
    pairs = pjoins.loc[pjoins.upstream_id.isin(pids) & pjoins.downstream_id.isin(pids)]
    left = pairs.downstream_id.values
    right = pairs.upstream_id.values

    # make symmetric by adding each to the end of the other
    groups = find_adjacent_groups(np.append(left, right), np.append(right, left))
    groups = pd.DataFrame(pd.Series(groups).apply(list).explode().rename("index"))
    groups.index.name = "group"
    groups = groups.reset_index().set_index("index")

    groups = groups.join(flowlines[["length"]])
    stats = groups.groupby("group").agg({"length": "sum"})
    drop_groups = stats.loc[stats.length >= max_pipeline_length].index
    drop_ids = groups.loc[groups.group.isin(drop_groups)].index

    print(
        f"Dropping {len(drop_ids):,} pipelines that are greater than {max_pipeline_length:,}m"
    )

    flowlines = flowlines.loc[~flowlines.index.isin(drop_ids)].copy()
    joins = remove_joins(
        joins, drop_ids, downstream_col="downstream_id", upstream_col="upstream_id"
    )

    # update NHDPlusIDs to match zeroed out ids
    joins.loc[
        (joins.downstream_id == 0) & (joins.type == "internal"), "type"
    ] = "former_pipeline_join"

    print(f"Done processing pipelines in {time() - start:.2f}s")

    return flowlines, joins


def cut_flowlines_at_barriers(flowlines, joins, barriers, next_segment_id=None):
    """Cut flowlines by barriers.

    Parameters
    ----------
    flowlines : GeoDataFrame
        ALL flowlines for region.
    barriers : GeoDataFrame
        Barriers that will be used to cut flowlines.
    joins : DataFrame
        Joins between flowlines (upstream, downstream pairs).
    next_segment_id : int, optional
        Used as starting point for IDs of new segments created by cutting flowlines.

    Returns
    -------
    GeoDataFrame, DataFrame, DataFrame
        updated flowlines, updated joins, barrier joins (upstream / downstream flowline ID per barrier)
    """

    start = time()
    print(f"Starting number of segments: {len(flowlines):,}")
    print(f"Cutting in {len(barriers):,} barriers")

    # Our segment ids are ints, so just increment from the last one we had from NHD
    if next_segment_id is None:
        next_segment_id = int(flowlines.index.max() + 1)

    # join barriers to lines and extract those that have segments (via inner join)
    segments = (
        flowlines[["lineID", "NHDPlusID", "geometry"]]
        .rename(columns={"geometry": "flowline"})
        .join(
            barriers[["geometry", "barrierID", "lineID"]]
            .set_index("lineID")
            .rename(columns={"geometry": "barrier"}),
            how="inner",
        )
    )

    # Calculate the position of each barrier on each segment.
    # Barriers are on upstream or downstream end of segment if they are within
    # SNAP_ENDPOINT_TOLERANCE of the ends.  Otherwise, they are splits
    segments["linepos"] = pg.line_locate_point(
        segments.flowline.values.data, segments.barrier.values.data
    )

    ### Upstream and downstream endpoint barriers
    segments["on_upstream"] = segments.linepos <= SNAP_ENDPOINT_TOLERANCE
    segments["on_downstream"] = (
        segments.linepos
        >= pg.length(segments.flowline.values.data) - SNAP_ENDPOINT_TOLERANCE
    )
    print(
        f"{segments.on_upstream.sum():,} barriers on upstream point of their segments"
    )
    print(
        f"{segments.on_downstream.sum():,} barriers on downstream point of their segments"
    )

    # Barriers on upstream endpoint:
    # their upstream_id is the upstream_id(s) of their segment from joins,
    # and their downstream_is is the segment they are on.
    # NOTE: a barrier may have multiple upstreams if it occurs at a fork in the network.
    # All terminal upstreams should be already coded as 0 in joins, but just in case
    # we assign N/A to 0.

    upstream_barrier_joins = (
        (
            segments.loc[segments.on_upstream][["barrierID", "lineID"]]
            .rename(columns={"lineID": "downstream_id"})
            .join(joins.set_index("downstream_id").upstream_id, on="downstream_id")
        )
        .fillna(0)
        .astype("uint64")
    )

    # Barriers on downstream endpoint:
    # their upstream_id is the segment they are on and their downstream_id is the
    # downstream_id of their segment from the joins.
    # Some downstream_ids may be missing if the barrier is on the downstream-most point of the
    # network (downstream terminal) and further downstream segments were removed due to removing
    # coastline segments.
    downstream_barrier_joins = (
        (
            segments.loc[segments.on_downstream][["barrierID", "lineID"]]
            .rename(columns={"lineID": "upstream_id"})
            .join(joins.set_index("upstream_id").downstream_id, on="upstream_id")
        )
        .fillna(0)
        .astype("uint64")
    )

    barrier_joins = upstream_barrier_joins.append(
        downstream_barrier_joins, ignore_index=True, sort=False
    ).set_index("barrierID", drop=False)

    ### Split segments have barriers that are not at endpoints

    split_segments = segments.loc[~(segments.on_upstream | segments.on_downstream)]
    # join in count of barriers that SPLIT this segment
    split_segments = split_segments.join(
        split_segments.groupby(level=0).size().rename("barriers")
    )

    print(f"{(split_segments.barriers == 1).sum():,} segments to cut have one barrier")
    print(
        f"{(split_segments.barriers > 1).sum():,} segments to cut have more than one barrier"
    )

    # ordinate the barriers by their projected distance on the line
    # Order this so we are always moving from upstream end to downstream end
    split_segments = split_segments.rename_axis("idx").sort_values(
        by=["idx", "linepos"], ascending=True
    )

    # Convert to DataFrame so that geometry cols are arrays of pygeos geometries
    tmp = pd.DataFrame(split_segments.copy())
    tmp.flowline = tmp.flowline.values.data
    tmp.barrier = tmp.barrier.values.data

    # Group barriers by line so that we can split geometries in one pass
    grouped = (
        tmp[["lineID", "NHDPlusID", "barrierID", "barriers", "flowline", "barrier",]]
        .groupby("lineID")
        .agg(
            {
                "lineID": "first",
                "NHDPlusID": "first",
                "flowline": "first",
                "barrierID": list,
                "barriers": "first",
                "barrier": list,
            }
        )
    )

    # cut line for all barriers
    geoms = grouped.apply(
        lambda row: cut_line_at_points(row.flowline, row.barrier), axis=1,
    )

    # Split multilines into new rows
    new_segments = (
        explode(gp.GeoDataFrame(geometry=geoms, crs=flowlines.crs), add_position=True)
        .reset_index()
        .rename(columns={"lineID": "origLineID"})
    )
    new_segments["lineID"] = next_segment_id + new_segments.index

    # Add in new flowlines by copying props from original ones
    new_flowlines = prep_new_flowlines(flowlines, new_segments)

    # transform new segments to create new joins
    l = new_segments.groupby("origLineID").lineID
    # the first new line per original line is the furthest upstream, so use its
    # ID as the new downstream ID for anything that had this origLineID as its downstream
    first = l.first().rename("new_downstream_id")
    # the last new line per original line is the furthest downstream...
    last = l.last().rename("new_upstream_id")

    # Update existing joins with the new lineIDs we created at the upstream or downstream
    # ends of segments we just created
    updated_joins = update_joins(
        joins, first, last, downstream_col="downstream_id", upstream_col="upstream_id"
    )

    # also need to update any barrier joins already created for those on endpoints
    barrier_joins = update_joins(
        barrier_joins,
        first,
        last,
        downstream_col="downstream_id",
        upstream_col="upstream_id",
    )

    # For all new interior joins, create upstream & downstream ids per original line
    upstream_side = (
        new_segments.loc[~new_segments.lineID.isin(last)][
            ["origLineID", "position", "lineID"]
        ]
        .set_index(["origLineID", "position"])
        .rename(columns={"lineID": "upstream_id"})
    )

    downstream_side = new_segments.loc[~new_segments.lineID.isin(first)][
        ["origLineID", "position", "lineID"]
    ].rename(columns={"lineID": "downstream_id"})
    downstream_side.position = downstream_side.position - 1
    downstream_side = downstream_side.set_index(["origLineID", "position"])

    new_joins = (
        grouped.barrierID.apply(pd.Series)
        .stack()
        .astype("uint32")
        .reset_index()
        .rename(columns={"lineID": "origLineID", "level_1": "position", 0: "barrierID"})
        .set_index(["origLineID", "position"])
        .join(upstream_side)
        .join(downstream_side)
        .reset_index()
        .join(grouped.NHDPlusID.rename("upstream"), on="origLineID")
    )
    new_joins["downstream"] = new_joins.upstream
    new_joins["type"] = "internal"

    updated_joins = updated_joins.append(
        new_joins[["upstream", "downstream", "upstream_id", "downstream_id", "type"]],
        ignore_index=True,
        sort=False,
    ).sort_values(["downstream_id", "upstream_id"])

    barrier_joins = (
        barrier_joins.append(
            new_joins[["barrierID", "upstream_id", "downstream_id"]],
            ignore_index=True,
            sort=False,
        )
        .set_index("barrierID", drop=False)
        .astype("uint32")
    )

    # extract flowlines that are not split by barriers and merge in new flowlines
    unsplit_segments = flowlines.loc[~flowlines.index.isin(split_segments.index)]
    updated_flowlines = unsplit_segments.append(
        new_flowlines.drop(columns=["origLineID", "position"]),
        ignore_index=True,
        sort=False,
    ).set_index("lineID", drop=False)

    print(f"Done cutting flowlines in {time() - start:.2}s")

    return updated_flowlines, updated_joins, barrier_joins


def cut_flowlines_at_points(flowlines, joins, points, next_lineID):
    """General method for cutting flowlines at points and updating joins.

    Only new flowlines are returned; any that are not cut by points are omitted.

    Parameters
    ----------
    flowlines : GeoDataFrame
    joins : DataFrame
        flowline joins
    points : ndarray of MultiPoint or Point geometries
        expected to match to flowlines
    next_lineID : int
        id of next flowline to be created

    Returns
    -------
    (GeoDataFrame, DataFrame, ndarray)
        new flowlines, updated joins, remove_ids (original flowline IDs that
        need to be removed before merging in returned flowlines)
    """

    flowlines = flowlines.copy()
    joins = joins.copy()

    flowlines["geometry"] = cut_lines_at_multipoints(
        flowlines.geometry.values.data, points
    )

    # discard any that have only one segment; they weren't split and we don't want
    # to update them.  Split the rest into parts.
    ix = pg.get_num_geometries(flowlines.geometry.values.data) > 1
    flowlines = explode(
        flowlines.loc[ix].reset_index().rename(columns={"lineID": "origLineID"})
    ).reset_index(drop=True)

    # recalculate length and sinuosity
    flowlines["length"] = pg.length(flowlines.geometry.values.data).astype("float32")
    flowlines["sinuosity"] = calculate_sinuosity(flowlines.geometry.values.data).astype(
        "float32"
    )

    # calculate new ID
    flowlines["lineID"] = (flowlines.index + next_lineID).astype("uint32")

    ### Update flowline joins
    # transform new lines to create new joins at the upstream / downstream most
    # points of the original line
    l = flowlines.groupby("origLineID").lineID
    # the first new line per original line is the furthest upstream, so use its
    # ID as the new downstream ID for anything that had this origLineID as its downstream
    first = l.first().rename("new_downstream_id")
    # the last new line per original line is the furthest downstream...
    last = l.last().rename("new_upstream_id")

    # Update existing joins with the new lineIDs we created at the upstream or downstream
    # ends of segments we just created
    joins = update_joins(
        joins, first, last, downstream_col="downstream_id", upstream_col="upstream_id",
    )

    ### Create new line joins for any that weren't inserted above
    # Transform all groups of new line IDs per original lineID
    # into joins structure

    atts = (
        flowlines.groupby("origLineID")[["NHDPlusID", "loop", "HUC4"]]
        .first()
        .rename(columns={"NHDPlusID": "upstream"})
    )

    # function to make upstream / downstream side of join
    pairs = lambda a: pd.Series(zip(a[:-1], a[1:]))
    new_joins = (
        l.apply(pairs)
        .apply(pd.Series)
        .reset_index()
        .rename(columns={0: "upstream_id", 1: "downstream_id"})
        .join(atts, on="origLineID")
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

    remove_ids = flowlines.origLineID.unique()

    flowlines = flowlines.drop(columns=["origLineID"]).set_index("lineID")

    return flowlines, joins, remove_ids


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


def save_cut_flowlines(out_dir, flowlines, joins, barrier_joins):
    """Save cut flowline data frames to disk.

    Parameters
    ----------
    out_dir : str
    flowlines : GeoDataFrame
        cut flowlines
    joins : DataFrame
        updated joins
    barrier_joins : DataFrame
        barrier joins
    """

    print("serializing {:,} cut flowlines...".format(len(flowlines)))
    start = time()

    flowlines = flowlines.reset_index(
        drop=flowlines.index.name and flowlines.index.name in flowlines.columns
    )
    flowlines.to_feather(out_dir / "flowlines.feather")
    # write_dataframe(flowlines, out_dir / "flowlines.gpkg")
    joins.reset_index(drop=True).to_feather(out_dir / "flowline_joins.feather")
    barrier_joins.reset_index(drop=True).to_feather(out_dir / "barrier_joins.feather",)


def remove_flowlines(flowlines, joins, ids):
    """Remove flowlines specified by ids from flowlines and joins

    Parameters
    ----------
    flowlines : GeoDataFrame
    joins : DataFrame
            joins between flowlines
    ids : list-like
            list of ids of flowlines to remove

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
            (flowlines, joins)
    """
    # drop from flowlines
    flowlines = flowlines.loc[~flowlines.NHDPlusID.isin(ids)].copy()

    # IDs are based on NHDPlusID, make sure to use correct columns for joins
    joins = remove_joins(
        joins, ids, downstream_col="downstream", upstream_col="upstream"
    )

    # update our ids to match zeroed out ids
    joins.loc[joins.downstream == 0, "downstream_id"] = 0
    joins.loc[joins.downstream == 0, "type"] = "terminal"
    joins.loc[joins.upstream == 0, "upstream_id"] = 0

    return flowlines, joins
