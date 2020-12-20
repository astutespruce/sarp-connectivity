from pathlib import Path
from time import time

import geopandas as gp
import pandas as pd
import pygeos as pg
import numpy as np


from nhdnet.nhd.joins import update_joins, remove_joins
from pyogrio import write_dataframe
from analysis.lib.pygeos_util import explode, cut_line_at_points

from analysis.constants import SNAP_ENDPOINT_TOLERANCE


def calculate_sinuosity(geometries):
    """Calculate sinuosity of the line.

    This is the length of the line divided by the distance between the endpoints of the line.
    By definition, it is always >=1.

    Parameters
    ----------
    geometries : Series or ndarray of pygeos geometries

    Returns
    -------
    Series or ndarray
        sinuosity values
    """

    # By definition, sinuosity should not be less than 1
    first = pg.get_point(geometries, 0)
    last = pg.get_point(geometries, -1)
    straight_line_distance = pg.distance(first, last)

    sinuosity = np.ones((len(geometries),)).astype("float32")

    # if there is no straight line distance there can be no sinuosity
    ix = straight_line_distance > 0

    # by definition, all values must be at least 1, so clip lower bound
    sinuosity[ix] = (pg.length(geometries[ix]) / straight_line_distance).clip(1)

    if isinstance(geometries, pd.Series):
        return pd.Series(sinuosity, index=geometries.index)

    return sinuosity


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
        tmp[
            [
                "lineID",
                "NHDPlusID",
                "barrierID",
                "barriers",
                "flowline",
                "barrier",
            ]
        ]
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
        lambda row: cut_line_at_points(row.flowline, row.barrier),
        axis=1,
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
        new_flowlines, ignore_index=True, sort=False
    ).set_index("lineID", drop=False)

    return updated_flowlines, updated_joins, barrier_joins


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

    print(f"Done serializing cut flowlines in {time() - start:.2f}s")


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
