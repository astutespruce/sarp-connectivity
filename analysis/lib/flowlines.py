from time import time

import geopandas as gp
import pandas as pd
import shapely
import numpy as np
from analysis.lib.geometry.polygons import get_interior_rings


from analysis.lib.joins import index_joins, find_joins, update_joins, remove_joins
from analysis.lib.geometry import union_or_combine

from analysis.lib.geometry import explode
from analysis.lib.geometry.speedups.lines import cut_lines_at_points
from analysis.lib.graph.speedups import DirectedGraph

from analysis.constants import SNAP_ENDPOINT_TOLERANCE

# In order to cut a flowline, it must be at least this long, and at least
# this different from original flowline
CUT_TOLERANCE = 1


def remove_pipelines(flowlines, joins, max_pipeline_length=100, keep_ids=None):
    """Remove pipelines that are above max length,
    based on contiguous length of pipeline segments.

    Parameters
    ----------
    flowlines : GeoDataFrame
    joins : DataFrame
        joins between flowlines
    max_pipeline_length : int, optional (default: 100)
        length above which pipelines are dropped
    keep_ids : list-like (default: None)
        list of pipeline IDs to keep


    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
            (flowlines, joins)
    """

    start = time()

    keep_ids = keep_ids or []

    pids = flowlines.loc[
        (flowlines.FType == 428) & (~flowlines.NHDPlusID.isin(keep_ids))
    ].index
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
    graph = DirectedGraph(
        np.append(left, right).astype("int64"), np.append(right, left).astype("int64")
    )
    groups, values = graph.flat_components()
    groups = pd.DataFrame(
        {
            "group": groups,
        },
        index=values,
    )

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


def cut_flowlines_at_barriers(flowlines, joins, barriers, next_segment_id):
    """Cut flowlines by barriers.

    Parameters
    ----------
    flowlines : GeoDataFrame
        ALL flowlines for region.
    barriers : GeoDataFrame
        Barriers that will be used to cut flowlines.
    joins : DataFrame
        Joins between flowlines (upstream, downstream pairs).

    Returns
    -------
    GeoDataFrame, DataFrame, DataFrame
        updated flowlines, updated joins, barrier joins (upstream / downstream flowline ID per barrier)
    """

    start = time()
    print(f"Starting number of segments: {len(flowlines):,}")
    print(f"Cutting in {len(barriers):,} barriers")

    # join barriers to lines and extract those that have segments (via inner join)
    segments = (
        flowlines[["lineID", "NHDPlusID", "geometry"]]
        .rename(columns={"geometry": "flowline"})
        .join(
            barriers[["geometry", "id", "lineID"]]
            .set_index("lineID")
            .rename(columns={"geometry": "barrier"}),
            how="inner",
        )
    )

    # Calculate the position of each barrier on each segment.
    # Barriers are on upstream or downstream end of segment if they are within
    # SNAP_ENDPOINT_TOLERANCE of the ends.  Otherwise, they are splits
    segments["linepos"] = shapely.line_locate_point(
        segments.flowline.values.data, segments.barrier.values.data
    )

    ### Upstream and downstream endpoint barriers
    segments["on_upstream"] = segments.linepos <= SNAP_ENDPOINT_TOLERANCE
    segments["on_downstream"] = (
        segments.linepos
        >= shapely.length(segments.flowline.values.data) - SNAP_ENDPOINT_TOLERANCE
    )

    # if line length is < SNAP_ENDPOINT_TOLERANCE, then barrier could be tagged
    # to both sides, which is incorrect.  Default to on_downstream.
    segments.loc[segments.on_upstream & segments.on_downstream, "on_upstream"] = False

    print(
        f"{segments.on_upstream.sum():,} barriers on upstream point of their segments"
    )
    print(
        f"{segments.on_downstream.sum():,} barriers on downstream point of their segments"
    )

    # Barriers on upstream endpoint:
    # their upstream_id is the upstream_id(s) of their segment from joins,
    # and their downstream_is is the segment they are on.
    # NOTE: a barrier may have multiple upstreams if it occurs immediately downstream
    # of a confluence (the line it is on has multiple upstreams).
    # All terminal upstreams should be already coded as 0 in joins, but just in case
    # we assign N/A to 0.

    upstream_barrier_joins = (
        segments.loc[segments.on_upstream][["id", "lineID"]]
        .rename(columns={"lineID": "downstream_id"})
        .join(
            joins.set_index("downstream_id")[["upstream_id", "type", "marine"]],
            on="downstream_id",
        )
    )

    upstream_barrier_joins.upstream_id = upstream_barrier_joins.upstream_id.fillna(
        0
    ).astype("uint32")
    upstream_barrier_joins["type"] = upstream_barrier_joins["type"].fillna("origin")
    upstream_barrier_joins.marine = upstream_barrier_joins.marine.fillna(False)

    # Barriers on downstream endpoint:
    # their upstream_id is the segment they are on and their downstream_id is the
    # downstream_id of their segment from the joins.
    # Some downstream_ids may be missing if the barrier is on the downstream-most point of the
    # network (downstream terminal) and further downstream segments were removed due to removing
    # coastline segments.
    downstream_barrier_joins = (
        segments.loc[segments.on_downstream][["id", "lineID"]]
        .rename(columns={"lineID": "upstream_id"})
        .join(
            joins.set_index("upstream_id")[["downstream_id", "type", "marine"]],
            on="upstream_id",
        )
    )

    downstream_barrier_joins.downstream_id = (
        downstream_barrier_joins.downstream_id.fillna(0).astype("uint32")
    )
    downstream_barrier_joins["type"] = downstream_barrier_joins["type"].fillna(
        "terminal"
    )
    downstream_barrier_joins.marine = downstream_barrier_joins.marine.fillna(False)

    # Add sibling joins if on a confluence
    # NOTE: a barrier may have multiple sibling upstreams if it occurs at a
    # confluence but is snapped to the downstream endpoint of its line and other
    # flowlines converge at that point

    at_confluence = downstream_barrier_joins.loc[
        downstream_barrier_joins.downstream_id != 0
    ][["id", "downstream_id", "type", "marine"]].join(
        joins.loc[~joins.upstream_id.isin(downstream_barrier_joins.index)]
        .set_index("downstream_id")
        .upstream_id,
        on="downstream_id",
        how="inner",
    )
    if len(at_confluence):
        downstream_barrier_joins = pd.concat(
            [downstream_barrier_joins.reset_index(), at_confluence.reset_index()],
            ignore_index=True,
            sort=False,
        ).set_index("lineID")

    barrier_joins = pd.concat(
        [upstream_barrier_joins, downstream_barrier_joins],
        ignore_index=True,
        sort=False,
    ).set_index("id", drop=False)

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

    # check for errors
    s = split_segments.groupby(by=["lineID", "linepos"]).size()
    s = s[s > 1]
    if len(s):
        raise ValueError(f"Multiple barriers at exact same location on flowline: {s}")

    # Convert to DataFrame so that geometry cols are arrays of pygeos geometries
    tmp = pd.DataFrame(split_segments.copy())
    tmp.flowline = tmp.flowline.values.data
    tmp.barrier = tmp.barrier.values.data

    # Group barriers by line so that we can split geometries in one pass
    grouped = (
        tmp[
            [
                "lineID",
                "NHDPlusID",
                "id",
                "barriers",
                "flowline",
                "barrier",
                "linepos",
            ]
        ]
        .sort_values(by=["lineID", "linepos"])
        .groupby("lineID")
        .agg(
            {
                "lineID": "first",
                "NHDPlusID": "first",
                "flowline": "first",
                "id": list,
                "barriers": "first",
                "linepos": list,
            }
        )
    )

    # cut line for all barriers
    # WARNING: this will fail with an error like
    # "IllegalArgumentException: point array must contain 0 or >1 elements"
    # if there are repeated coordinates in the list, which is a sign that
    # input data were not properly deduplicated or prepared;
    # The most common case is when road crossings are not snapped to updated flowlines
    outer_ix, inner_ix, lines = cut_lines_at_points(
        grouped.flowline.apply(lambda x: shapely.get_coordinates(x)).values,
        grouped.linepos.apply(np.array).values,
    )

    lines = np.asarray(lines)
    new_flowlines = gp.GeoDataFrame(
        {
            "lineID": (next_segment_id + np.arange(len(outer_ix))).astype("uint32"),
            "origLineID": grouped.index.take(outer_ix),
            "position": inner_ix,
            "geometry": lines,
            "length": shapely.length(lines).astype("float32"),
        },
        crs=flowlines.crs,
    ).join(
        flowlines.drop(
            columns=[
                "geometry",
                "lineID",
                "xmin",
                "ymin",
                "xmax",
                "ymax",
                "length",
            ],
            errors="ignore",
        ),
        on="origLineID",
    )

    # transform new segments to create new joins
    l = new_flowlines.groupby("origLineID").lineID
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
        new_flowlines.loc[~new_flowlines.lineID.isin(last)][
            ["origLineID", "position", "lineID"]
        ]
        .set_index(["origLineID", "position"])
        .rename(columns={"lineID": "upstream_id"})
    )

    downstream_side = new_flowlines.loc[~new_flowlines.lineID.isin(first)][
        ["origLineID", "position", "lineID"]
    ].rename(columns={"lineID": "downstream_id"})
    downstream_side.position = downstream_side.position - 1
    downstream_side = downstream_side.set_index(["origLineID", "position"])

    new_joins = (
        grouped.id.apply(pd.Series)
        .stack()
        .astype("uint32")
        .reset_index()
        .rename(columns={"lineID": "origLineID", "level_1": "position", 0: "id"})
        .set_index(["origLineID", "position"])
        .join(upstream_side)
        .join(downstream_side)
        .reset_index()
        .join(grouped.NHDPlusID.rename("upstream"), on="origLineID")
    )
    new_joins["downstream"] = new_joins.upstream
    new_joins["type"] = "internal"
    new_joins["marine"] = False

    updated_joins = pd.concat(
        [
            updated_joins,
            new_joins[
                [
                    "upstream",
                    "downstream",
                    "upstream_id",
                    "downstream_id",
                    "type",
                    "marine",
                ]
            ],
        ],
        ignore_index=True,
        sort=False,
    ).sort_values(["downstream_id", "upstream_id"])

    barrier_joins = pd.concat(
        [
            barrier_joins,
            new_joins[["id", "upstream_id", "downstream_id", "type", "marine"]],
        ],
        ignore_index=True,
        sort=False,
    ).set_index("id", drop=False)

    barrier_joins[["upstream_id", "downstream_id"]] = barrier_joins[
        ["upstream_id", "downstream_id"]
    ].astype("uint32")

    # extract flowlines that are not split by barriers and merge in new flowlines
    unsplit_segments = flowlines.loc[~flowlines.index.isin(split_segments.index)]
    updated_flowlines = pd.concat(
        [unsplit_segments, new_flowlines.drop(columns=["origLineID", "position"])],
        ignore_index=True,
        sort=False,
    ).set_index("lineID", drop=False)

    print(f"Done cutting flowlines in {time() - start:.2f}s")

    return updated_flowlines, updated_joins, barrier_joins


def cut_flowlines_at_points(flowlines, joins, points, next_lineID):
    """General method for cutting flowlines at points and updating joins.

    Only points >= SNAP_ENDPOINT_TOLERANCE are used to cut lines.

    Lines are cut starting at the upstream end; the original ordering of points
    per line is not preserved.

    Parameters
    ----------
    flowlines : GeoDataFrame
    joins : DataFrame
        flowline joins
    points : GeoSeries
        points to cut flowlines, must be indexed to join against flowlines;
        one record per singular Point.
    next_lineID : int
        id of next flowline to be created

    Returns
    -------
    (GeoDataFrame, DataFrame)
        Updated flowlines and joins.
        Note: flowlines have a "new" column to identify new flowlines created here.
    """

    df = flowlines.join(points.rename("point"), how="inner")
    df["pos"] = shapely.line_locate_point(df.geometry.values.data, df.point.values.data)

    # only keep cut points that are sufficiently interior to the line
    # (i.e., not too close to endpoints)
    ix = (df.pos >= SNAP_ENDPOINT_TOLERANCE) & (
        (df["length"] - df.pos).abs() >= SNAP_ENDPOINT_TOLERANCE
    )

    # sort remaining cut points in ascending order on their lines
    df = df.loc[ix].sort_values(by=["lineID", "pos"])
    # convert to plain DataFrame so that we can extract coords
    grouped = pd.DataFrame(df.groupby("lineID").agg({"geometry": "first", "pos": list}))
    grouped["geometry"] = grouped.geometry.values.data
    outer_ix, inner_ix, lines = cut_lines_at_points(
        grouped.geometry.apply(lambda x: shapely.get_coordinates(x)).values,
        grouped.pos.apply(np.array).values,
    )
    lines = np.asarray(lines)
    new_flowlines = gp.GeoDataFrame(
        {
            "lineID": (next_lineID + np.arange(len(outer_ix))).astype("uint32"),
            "origLineID": grouped.index.take(outer_ix),
            "geometry": lines,
            "length": shapely.length(lines).astype("float32"),
        },
        crs=flowlines.crs,
    ).join(
        flowlines.drop(
            columns=[
                "geometry",
                "lineID",
                "xmin",
                "ymin",
                "xmax",
                "ymax",
                "length",
            ],
            errors="ignore",
        ),
        on="origLineID",
    )

    ### Update flowline joins
    # transform new lines to create new joins at the upstream / downstream most
    # points of the original line
    l = new_flowlines.groupby("origLineID").lineID
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
    # Transform all groups of new line IDs per original lineID
    # into joins structure
    atts = (
        new_flowlines.groupby("origLineID")[["NHDPlusID", "loop", "HUC4"]]
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
    # new joins do not terminate in marine, so marine should always be false
    new_joins["marine"] = False
    new_joins = new_joins[
        [
            "upstream",
            "downstream",
            "upstream_id",
            "downstream_id",
            "type",
            "loop",
            "marine",
            "HUC4",
        ]
    ]

    joins = (
        pd.concat([joins, new_joins], ignore_index=True, sort=False)
        .sort_values(["downstream", "upstream", "downstream_id", "upstream_id"])
        .reset_index(drop=True)
    )

    remove_ids = new_flowlines.origLineID.unique()
    flowlines["new"] = False
    new_flowlines["new"] = True
    flowlines = pd.concat(
        [
            flowlines.loc[~flowlines.index.isin(remove_ids)].reset_index(),
            new_flowlines.drop(columns=["origLineID"]),
        ],
        ignore_index=True,
        sort=False,
    ).set_index("lineID")

    return flowlines, joins


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

    ### Find flowlines that intersect waterbodies

    join_start = time()
    tree = shapely.STRtree(flowlines.geometry.values.data)
    left, right = tree.query(waterbodies.geometry.values.data, predicate="intersects")
    df = pd.DataFrame(
        {
            "lineID": flowlines.index.take(right),
            "flowline": flowlines.geometry.values.data.take(right),
            "wbID": waterbodies.index.take(left),
            "waterbody": waterbodies.geometry.values.data.take(left),
        }
    )
    print(f"Found {len(df):,} waterbody / flowline joins in {time() - join_start:.2f}s")

    ### Find those that are completely contained; these don't need further processing
    shapely.prepare(df.waterbody.values)

    # find those that are fully contained and do not touch the edge of the waterbody (contains_properly predicate)
    # contains_properly is very fast
    contained_start = time()
    df["contains"] = shapely.contains_properly(df.waterbody.values, df.flowline.values)
    print(
        f"Identified {df.contains.sum():,} flowlines fully within waterbodies in {time() - contained_start:.2f}s"
    )

    # find those that aren't fully contained by contained and touch the edge of waterbody (contains predicate)
    contained_start = time()
    ix = ~df.contains
    tmp = df.loc[ix]
    df.loc[ix, "contains"] = shapely.contains(tmp.waterbody, tmp.flowline)
    print(
        f"Identified {df.loc[ix].contains.sum():,} more flowlines contained by waterbodies in {time() - contained_start:.2f}s"
    )

    # Sanity check: flowlines should only ever be contained by one waterbody
    if df.loc[df.contains].groupby("lineID").size().max() > 1:
        raise ValueError("ERROR: one or more lines contained by multiple waterbodies")

    # for any that are not completely contained, find the ones that overlap
    crosses_start = time()
    df["crosses"] = False
    ix = ~df.contains
    tmp = df.loc[ix]
    df.loc[ix, "crosses"] = shapely.crosses(tmp.waterbody, tmp.flowline)
    print(
        f"Identified {df.crosses.sum():,} flowlines that cross edge of waterbodies in {time() - crosses_start:.2f}s"
    )

    # discard any that only touch (ones that don't cross or are contained)
    # note that we only cut the ones that cross below; contained ones are left intact
    df = df.loc[df.contains | df.crosses].copy()

    print("Intersecting flowlines and waterbodies...")
    cut_start = time()
    ix = df.crosses
    tmp = df.loc[ix]
    df["geometry"] = df.flowline
    # use intersection to cut flowlines by waterbodies.  Note: this may produce
    # nonlinear (e.g., geom collection) results
    df.loc[ix, "geometry"] = shapely.intersection(tmp.flowline, tmp.waterbody)
    df["length"] = shapely.length(df.geometry)
    df["flength"] = shapely.length(df.flowline)

    # Cut lines that are long enough and different enough from the original lines
    df["to_cut"] = False
    tmp = df.loc[df.crosses]
    keep = (
        tmp.crosses
        & (tmp.length >= CUT_TOLERANCE)
        & ((tmp.flength - tmp.length).abs() >= CUT_TOLERANCE)
    )
    df.loc[keep[keep].index, "to_cut"] = True
    df["inside"] = (df.length / df.flength).clip(0, 1)
    print(
        f"Found {df.to_cut.sum():,} segments that need to be cut by flowlines in {time() - cut_start:.2f}s"
    )

    # save all that are completely contained or mostly contained.
    # They must be at least 50% in waterbody to be considered mostly contained.
    # Note: there are some that are mostly outside and we exclude those here.
    # We then update this after cutting
    contained = df.loc[df.inside >= 0.5, ["wbID", "lineID"]].copy()

    ### Cut lines
    if df.to_cut.sum():
        # only work with those to cut from here on out
        df = df.loc[df.to_cut, ["lineID", "flowline", "wbID", "waterbody"]].reset_index(
            drop=True
        )

        # save waterbody ids to re-evaluate intersection after cutting
        wbID = df.wbID.unique()

        # extract all intersecting interior rings for these waterbodies
        print("Extracting interior rings for intersected waterbodies")
        wb = waterbodies.loc[waterbodies.index.isin(wbID)]
        outer_index, inner_index, rings = get_interior_rings(wb.geometry.values.data)
        if len(outer_index):
            # find the pairs of waterbody rings and lines to add
            rings = np.asarray(rings)
            wb_with_rings = wb.index.values.take(outer_index)
            lines_in_wb = df.loc[df.wbID.isin(wb_with_rings)].lineID.unique()
            lines_in_wb = flowlines.loc[flowlines.index.isin(lines_in_wb)].geometry
            tree = shapely.STRtree(rings)
            left, right = tree.query(lines_in_wb.values.data, predicate="intersects")

            tmp = pd.DataFrame(
                {
                    "lineID": lines_in_wb.index.values.take(left),
                    "flowline": lines_in_wb.values.data.take(left),
                    "wbID": wb_with_rings.take(right),
                    "waterbody": rings.take(right),
                }
            )
            df = pd.concat([df, tmp], ignore_index=True, sort=False)

        # extract the outer ring for original waterbodies
        ix = shapely.get_type_id(df.waterbody.values.data) == 3
        df.loc[ix, "waterbody"] = shapely.get_exterior_ring(
            df.loc[ix].waterbody.values.data
        )

        # Calculate all geometric intersections between the flowlines and
        # waterbody rings and drop any that are not points
        # Note: these may be multipoints where line crosses the ring of waterbody
        # multiple times.
        # We ignore any shared edges, etc that result from the intersection; those
        # aren't helpful for cutting the lines
        print("Finding cut points...")
        df["geometry"] = shapely.intersection(df.flowline.values, df.waterbody.values)
        df = explode(
            explode(
                gp.GeoDataFrame(
                    df[["geometry", "lineID", "flowline"]], crs=flowlines.crs
                )
            )
        ).reset_index()
        points = (
            df.loc[shapely.get_type_id(df.geometry.values.data) == 0]
            .set_index("lineID")
            .geometry
        )

        print("cutting flowlines")
        cut_start = time()
        flowlines, joins = cut_flowlines_at_points(
            flowlines, joins, points, next_lineID=next_lineID
        )
        new_flowlines = flowlines.loc[flowlines.new]

        print(
            f"{len(new_flowlines):,} new flowlines created in {time() - cut_start:,.2f}s"
        )

        if len(new_flowlines):
            # remove any flowlines no longer present (they were replaced by cut lines)
            contained = contained.loc[
                contained.lineID.isin(flowlines.loc[~flowlines.new].index.unique())
            ].copy()

            contained_start = time()
            # recalculate overlaps with waterbodies
            print("Recalculating overlaps with waterbodies")
            wb = waterbodies.loc[wbID]
            tree = shapely.STRtree(new_flowlines.geometry.values.data)
            left, right = tree.query(wb.geometry.values.data, predicate="intersects")

            df = pd.DataFrame(
                {
                    "lineID": new_flowlines.index.take(right),
                    "flowline": new_flowlines.geometry.values.data.take(right),
                    "wbID": wb.index.take(left),
                    "waterbody": wb.geometry.values.data.take(left),
                }
            )

            shapely.prepare(df.waterbody.values)
            df["contains"] = shapely.contains(df.waterbody.values, df.flowline.values)
            print(
                f"Identified {df.contains.sum():,} more flowlines contained by waterbodies in {time() - contained_start:.2f}s"
            )

            # some aren't perfectly contained, add those that are mostly in
            df["crosses"] = False
            ix = ~df.contains
            tmp = df.loc[ix]
            df.loc[ix, "crosses"] = shapely.crosses(tmp.waterbody, tmp.flowline)

            # discard any that only touch (don't cross or are contained)
            df = df.loc[df.contains | df.crosses].copy()

            tmp = df.loc[df.crosses]
            df["geometry"] = df.flowline
            # use intersection to cut flowlines by waterbodies.  Note: this may produce
            # nonlinear (e.g., geom collection) results
            df.loc[ix, "geometry"] = shapely.intersection(tmp.flowline, tmp.waterbody)
            df["length"] = shapely.length(df.geometry)
            df["flength"] = shapely.length(df.flowline)

            # keep any that are contained or >= 50% in waterbody
            contained = pd.concat(
                [
                    contained,
                    df.loc[
                        df.contains | ((df.length / df.flength) >= 0.5),
                        ["wbID", "lineID"],
                    ],
                ],
                ignore_index=True,
                sort=False,
            )

        flowlines = flowlines.drop(columns=["new"])

    # make sure that updated joins are unique
    joins = joins.drop_duplicates()

    contained_altered = contained.loc[
        contained.wbID.isin(waterbodies.loc[waterbodies.altered].index)
    ].lineID.unique()

    # make sure that wb_joins is unique
    contained = contained.groupby(by=["lineID", "wbID"]).first().reset_index()

    # set flag for flowlines in waterbodies
    flowlines["waterbody"] = flowlines.index.isin(contained.lineID.unique())

    # mark flowlines contained in altered waterbodies as altered
    ix = flowlines.index.isin(contained_altered) & (~flowlines.altered)
    flowlines.loc[ix, "altered"] = True
    flowlines.loc[ix, "altered_src"] = "waterbodies"

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
    barrier_joins.reset_index(drop=True).to_feather(
        out_dir / "barrier_joins.feather",
    )


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


def remove_marine_flowlines(flowlines, joins, marine):
    """Remove flowlines that originate within or are mostly within marine areas
    for coastal HUC2s.  Marks any that have endpoints in marine areas or are
    upstream of those removed here as terminating in marine.

    Parameters
    ----------
    flowlines : GeoDataFrame
    joins : DataFrame
    marine : GeoDataFrame

    Returns
    -------
    (GeoDataFrame, DataFrame)
        flowlines, joins
    """

    # Remove those that start in marine areas
    points = shapely.get_point(flowlines.geometry.values.data, 0)
    tree = shapely.STRtree(points)
    left, right = tree.query(marine.geometry.values.data, predicate="intersects")
    ix = flowlines.index.take(np.unique(right))

    print(f"Removing {len(ix):,} flowlines that originate in marine areas")
    # mark any that terminated in those as marine
    joins.loc[joins.downstream_id.isin(ix), "marine"] = True
    flowlines = flowlines.loc[~flowlines.index.isin(ix)].copy()
    joins = remove_joins(
        joins, ix, downstream_col="downstream_id", upstream_col="upstream_id"
    )

    # Mark those that end in marine areas as marine
    endpoints = shapely.get_point(flowlines.geometry.values.data, -1)
    tree = shapely.STRtree(endpoints)
    left, right = tree.query(marine.geometry.values.data, predicate="intersects")
    ix = flowlines.index.take(np.unique(right))
    joins.loc[joins.upstream_id.isin(ix), "marine"] = True

    # For any that end in marine but didn't originate there, check the amount of overlap;
    # any that are >= 90% in marine should get cut
    print("Calculating overlap of remaining lines with marine areas")
    tmp = pd.DataFrame(
        {
            "lineID": flowlines.iloc[right].index,
            "geometry": flowlines.iloc[right].geometry.values.data,
            "marine": marine.iloc[left].geometry.values.data,
        }
    )
    tmp["overlap"] = shapely.intersection(tmp.geometry, tmp.marine)
    tmp["pct_overlap"] = (
        100 * shapely.length(tmp.overlap) / shapely.length(tmp.geometry)
    )

    ix = tmp.loc[tmp.pct_overlap >= 90].lineID.unique()

    print(f"Removing {len(ix):,} flowlines that mostly overlap marine areas")
    # mark any that terminated in those as marine
    joins_ix = joins.downstream_id.isin(ix)
    joins.loc[joins_ix, "marine"] = True
    joins.loc[joins_ix, "type"] = "terminal"

    flowlines = flowlines.loc[~flowlines.index.isin(ix)].copy()
    joins = remove_joins(
        joins, ix, downstream_col="downstream_id", upstream_col="upstream_id"
    )

    # mark any new terminals as such
    joins.loc[
        (joins.downstream_id == 0) & (joins.type == "internal"), "type"
    ] = "terminal"

    return flowlines, joins


def mark_altered_flowlines(flowlines, nwi):
    """Marks altered flowlines based on NHD and NWI

    Parameters
    ----------
    flowlines : GeoDataFrame
    nwi : GeoDataFrame

    Returns
    -------
    flowlines with additional columns: "altered", "altered_src"
    """

    # NHD canals / ditches & pipelines considered altered
    flowlines["altered"] = flowlines.FType.isin([336, 428])
    flowlines["altered_src"] = ""
    flowlines.loc[flowlines.altered, "altered_src"] = "NHD"

    # Overlap with NWI altered rivers is also considered altered
    print("Overlay with NWI altered rivers to determine altered status")

    # buffer by 10m before finding overlaps
    # (seemed reasonable from visual inspection in region 15)
    print("Buffering NWI...")
    b = shapely.get_parts(
        union_or_combine(shapely.buffer(nwi.geometry.values.data, 10))
    )

    # Only analyze those not marked by NHD as altered
    unaltered = flowlines.loc[~flowlines.altered]

    tree = shapely.STRtree(unaltered.geometry.values.data)
    left, right = tree.query(b, predicate="intersects")

    df = pd.DataFrame(
        {
            "lineID": unaltered.index.values.take(right),
            "line": unaltered.geometry.values.data.take(right),
            "nwi": b.take(left),
        }
    )

    df["overlap"] = shapely.length(shapely.intersection(df.line.values, df.nwi.values))
    df["pct_overlap"] = df.overlap / shapely.length(df.line.values)

    # only keep those with an overlap of >= 50% and at least 100m
    ix = flowlines.index.isin(
        df.loc[(df.pct_overlap >= 0.5) & (df.overlap >= 100)].lineID
    )
    flowlines.loc[ix, "altered"] = True
    flowlines.loc[ix, "altered_src"] = "NWI"
    del df

    return flowlines
