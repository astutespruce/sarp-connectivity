from pathlib import Path
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
from pyogrio import read_dataframe, write_dataframe
import shapely

from analysis.constants import CRS
from analysis.lib.graph.speedups import LinearDirectedGraph, DirectedGraph
from analysis.lib.geometry.lines import merge_lines, fill_endpoint_gaps
from analysis.lib.geometry.speedups.lines import substring

warnings.filterwarnings("ignore", category=UserWarning, message=".*Measured.*")

# tolerance within which to select flowlines
# NOTE: there are many short flowlines that are ~2m that connect tributaries to mainstems
SELECTION_TOLERANCE = 5  # meters; used to select flowlines that are near habitat
OUTER_OVERLAP_TOLERANCE = (
    100  # meters; used to check overlap of flowlines filled in gaps
)
ENDPOINT_TOLERANCE = 1  # meters; used to determine if endpoints are on habitat
MIN_LINE_LENGTH = 10  # meters
# even if 90% of NHD line overlaps with habitat line, the absolute difference
# must be less than this value
MAX_LINE_DIFF = 100  # meters

data_dir = Path("data")
src_dir = data_dir / "species/source"
nhd_dir = data_dir / "nhd/raw"
out_dir = data_dir / "species/derived"

df = gp.read_feather(src_dir / "streamnet_habitat.feather")

# TODO: just load all HUC2 flowlines and do this at once
# limit to 16, 17, 18
huc2s = ["17"]
huc2 = huc2s[0]
flowlines = gp.read_feather(
    nhd_dir / huc2 / "flowlines.feather",
    columns=[
        "geometry",
        "lineID",
        "NHDPlusID",
        "length",
        "loop",
        "offnetwork",
        "FType",
    ],
).set_index("lineID")
flowlines = flowlines.loc[~flowlines.offnetwork].copy()
# mark canals; these require higher confidence of overlap since they may spatially
# interact with habitat but not functionally
flowlines["canal"] = flowlines.FType == 428

# add upstream / downstream points
flowlines["nhd_upstream_pt"] = shapely.get_point(flowlines.geometry.values, 0)
flowlines["nhd_downstream_pt"] = shapely.get_point(flowlines.geometry.values, -1)

joins = pd.read_feather(
    nhd_dir / huc2 / "flowline_joins.feather",
    columns=["upstream_id", "downstream_id", "loop"],
)

# create a linear graph facing downstream
# NOTE: this can't handle loops
tmp = joins.loc[
    (joins.upstream_id != 0) & (joins.downstream_id != 0) & (~joins.loop)
].copy()
downstream_graph = LinearDirectedGraph(
    tmp.upstream_id.values.astype("int64"), tmp.downstream_id.values.astype("int64")
)


#### Process species / run

unit = "Coho salmon"
spp_df = df.loc[df.unit == unit].reset_index(drop=True)

# assign segment ids used for analysis below
spp_df["id"] = spp_df.index.values

# create buffers for analysis
spp_df["buf"] = shapely.buffer(
    spp_df.geometry.values, SELECTION_TOLERANCE, cap_style="flat"
)

# extract flowlines within SELECTION_TOLERANCE of habitat lines
# WARNING: this will include many flowlines that we should not keep
left, right = shapely.STRtree(flowlines.geometry.values).query(
    spp_df.buf.values, predicate="intersects"
)
pairs = (
    pd.DataFrame(
        {
            "lineID": flowlines.index.values.take(right),
            "spp_line_id": spp_df.id.values.take(left),
        }
    )
    .join(
        flowlines[
            ["geometry", "length", "canal", "nhd_upstream_pt", "nhd_downstream_pt"]
        ].rename(columns={"geometry": "nhd_line"}),
        on="lineID",
    )
    .join(
        spp_df[["geometry", "group", "buf"]].rename(
            columns={"geometry": "spp_line", "group": "spp_group", "buf": "spp_buf"}
        ),
        on="spp_line_id",
    )
)

spp_groups = (
    pairs.groupby("lineID")
    .spp_group.agg(["first", lambda x: len(set(x))])
    .reset_index()
)
spp_groups.columns = ["lineID", "spp_group", "group_count"]

canal_ids = pairs.loc[pairs.canal].lineID.unique()


# keep any NHD flowlines where both endpoints are in habitat and discard from
# further processing
pairs["has_upstream"] = shapely.dwithin(
    pairs.nhd_upstream_pt, pairs.spp_line.values, ENDPOINT_TOLERANCE
)
pairs["has_downstream"] = shapely.dwithin(
    pairs.nhd_downstream_pt, pairs.spp_line.values, ENDPOINT_TOLERANCE
)

tmp = pairs.groupby("lineID").agg(
    {
        "has_upstream": "max",
        "has_downstream": "max",
        "canal": "first",
    }
)
# exclude canals here because we need to analyze their overlap below
# exclude any NHD flowolines that bridge disjunct species groups
keep_line_ids = tmp.loc[
    tmp.has_upstream
    & tmp.has_downstream
    & (~tmp.canal)
    & (~tmp.index.isin(spp_groups.loc[spp_groups.group_count > 1].lineID.unique()))
].index.unique()
pairs = pairs.loc[~pairs.lineID.isin(keep_line_ids)].copy()
print(
    f"keeping {len(keep_line_ids):,} NHD lines with endpoints that completely overlap habitat"
)


# keep any flowlines that are >= 95 covered by buffer of habitat line and drop
# them from further analysis and drop any where the overlap is too short
pairs["overlap"] = shapely.length(
    shapely.intersection(pairs.nhd_line.values, pairs.spp_buf.values)
)
drop_ix = pairs.overlap < MIN_LINE_LENGTH
print(f"Dropping {drop_ix.sum():,} pairs that barely overlap")
pairs = pairs.loc[~drop_ix]

# keep any where there is a high degree of overlap across all habitat lines
# unless they overlap multiple species groups
total_overlap = pairs.groupby("lineID").agg(
    {"overlap": "sum", "length": "first", "canal": "first"}
)

keep_ids = np.setdiff1d(
    total_overlap.loc[
        (total_overlap.overlap / total_overlap["length"] >= 0.9)
        & (total_overlap["length"] - total_overlap.overlap < MAX_LINE_DIFF)
    ].index.unique(),
    spp_groups.loc[spp_groups.group_count > 1].lineID.values,
)

# drop any canals with low total overlap from pairs; these didn't have sufficient
# overlap to keep them and they cause a lot of issues in subsequent steps
drop_ids = total_overlap.loc[
    total_overlap.canal & (total_overlap.overlap < MIN_LINE_LENGTH)
].index.unique()

keep_line_ids = np.unique(np.concatenate([keep_line_ids, keep_ids]))
pairs = pairs.loc[
    ~(pairs.lineID.isin(np.unique(np.concatenate([keep_line_ids, drop_ids]))))
].reset_index()
print(f"keeping {len(keep_ids):,} NHD lines that mostly overlap habitat")

# update species groups
tmp = (
    pairs.groupby("lineID")
    .spp_group.agg(["first", lambda x: len(set(x))])
    .reset_index()
)
tmp.columns = ["lineID", "spp_group", "group_count"]
spp_groups = pd.concat(
    [spp_groups.loc[spp_groups.lineID.isin(keep_line_ids)], tmp], ignore_index=True
)


### Do a first pass of gap-filling by tracing downstream network
# if there exists a route from a given keep line through ones still in pairs
# to another keep line, and it is in same habitat group, then fill those gaps

# extract the upstream and downstream joins from joins based on keep_line_ids
# in order to find linear networks downstream of downstreams that terminate at
# any of the upstream points
# do not traverse downstream of any canals; these are questionable

# have to group by upstream_id because it may have multiple downstreams
tmp = joins.loc[
    joins.upstream_id.isin(keep_line_ids) & (~joins.upstream_id.isin(canal_ids))
].copy()
tmp["has_downstream"] = tmp.downstream_id.isin(keep_line_ids)
has_downstream = tmp.groupby("upstream_id").has_downstream.max()
downstreams = has_downstream.loc[~has_downstream].index.unique().values.astype("int64")

upstreams = (
    joins.loc[
        joins.downstream_id.isin(keep_line_ids) & ~joins.upstream_id.isin(keep_line_ids)
    ]
    .upstream_id.unique()
    .astype("int64")
)

paths = downstream_graph.extract_paths(
    downstreams,
    upstreams,
    max_depth=100,
)
paths = pd.DataFrame({"path": range(len(paths)), "lineID": paths})
paths = paths.loc[paths.lineID.apply(len) > 0].explode(column="lineID")

# merge paths that have overlapping lineIDs
tmp = (
    paths.join(paths.groupby("lineID").path.unique().rename("other_path"), on="lineID")
    .explode(column="other_path")[["path", "other_path"]]
    .drop_duplicates()
)
# add symmetric pairs
tmp = pd.concat([tmp, tmp.rename(columns={"path": "other_path", "other_path": "path"})])
groups = DirectedGraph(
    tmp.path.values.astype("int64"), tmp.other_path.values.astype("int64")
).components()
groups = (
    pd.DataFrame({"group": range(len(groups)), "path": groups})
    .explode(column="path")
    .set_index("path")
)
paths = (
    paths.join(groups, on="path")
    .groupby(["group", "lineID"])[[]]
    .first()
    .reset_index()
    .rename(columns={"group": "path"})
    .join(flowlines[["geometry", "length"]], on="lineID")
)


# drop any where a given flowline has multiple species groups; these are problematic
# then join in the group associated with the flowline
# also drop any where the path goes through canals; these are also questionable
drop_ids = paths.loc[
    paths.lineID.isin(
        np.unique(
            np.concatenate(
                [spp_groups.loc[spp_groups.group_count > 1].lineID.values, canal_ids]
            )
        )
    )
].path.unique()
paths = paths.loc[~paths.path.isin(drop_ids)]

# drop any where either of the path endpoints has multiple groups; keep the rest
# and remove them from further analysis
starts = pd.DataFrame({"path": range(len(downstreams)), "lineID": downstreams})
starts = starts.loc[starts.path.isin(paths.path.unique())]
ends = paths.groupby("path")[["lineID"]].last().reset_index()
ends = (
    ends.join(
        joins.loc[joins.upstream_id.isin(ends.lineID)]
        .set_index("upstream_id")
        .downstream_id,
        on="lineID",
    )
    .drop(columns=["lineID"])
    .rename(columns={"downstream_id": "lineID"})
)
path_endpoints = (
    pd.concat([starts, ends], ignore_index=True)
    .join(spp_groups.set_index("lineID").spp_group, on="lineID")
    .dropna()
)
ix = path_endpoints.groupby("path").spp_group.unique().apply(len) > 1
drop_ids = ix[ix].index
paths = paths.loc[~paths.path.isin(drop_ids)]


# Limit these to ones with >= 50% overlap with a OUTER_OVERLAP_TOLERANCE buffer
# around habitat lines
if len(paths):
    # create a buffer of OUTER_OVERLAP_TOLERANCE around any nearby habitat lines
    # NOTE: use a combination of dwithin and intersects because of https://github.com/libgeos/geos/issues/958
    tree = shapely.STRtree(spp_df.geometry.values)
    ix = np.unique(
        np.concatenate(
            [
                tree.query(
                    paths.geometry.values,
                    predicate="dwithin",
                    distance=OUTER_OVERLAP_TOLERANCE,
                )[1],
                tree.query(paths.geometry.values, predicate="intersects")[1],
            ]
        )
    )
    buffer = shapely.union_all(
        shapely.buffer(
            spp_df.geometry.values.take(ix), OUTER_OVERLAP_TOLERANCE, cap_style="flat"
        )
    )
    tmp = paths.groupby("path").agg({"geometry": shapely.union_all})
    tmp["length"] = shapely.length(tmp.geometry.values)
    overlap = (
        shapely.length(shapely.intersection(tmp.geometry.values, buffer))
        / tmp["length"]
    )

    keep_ids = paths.loc[
        paths.path.isin(overlap[overlap >= 0.5].index.values)
    ].lineID.unique()

    keep_line_ids = np.unique(np.concatenate([keep_line_ids, keep_ids]))
    pairs = pairs.loc[~pairs.lineID.isin(keep_ids)].copy()


# look at overlaps of the endpoints of the habitat line with the NHD flowline
# NOTE: the habitat line may be oriented in the opposite direction as the
# flowline, so we need to detect this and flip it
pairs["spp_pt1"] = shapely.get_point(pairs.spp_line.values, 0)
pairs["spp_loc1"] = shapely.line_locate_point(pairs.nhd_line.values, pairs.spp_pt1)
pairs["spp_pt2"] = shapely.get_point(pairs.spp_line.values, -1)
pairs["spp_loc2"] = shapely.line_locate_point(pairs.nhd_line.values, pairs.spp_pt2)

# if both loc1 and loc2 are within TOLERANCE of each other, this likely indicates
# there is very little overlap with the line, so discard these
pairs = pairs.loc[~np.isclose(pairs.spp_loc1, pairs.spp_loc2, atol=TOLERANCE)].copy()

# reorient so that habitat points are aligned with upstream / downstream direction
# of flowline
# habitat line is oriented same as NHD
ix = pairs.spp_loc1 < pairs.spp_loc2
pairs.loc[ix, "spp_upstream_pt"] = pairs.loc[ix].spp_pt1
pairs.loc[ix, "spp_upstream_loc"] = pairs.loc[ix].spp_loc1
pairs.loc[ix, "spp_downstream_pt"] = pairs.loc[ix].spp_pt2
pairs.loc[ix, "spp_downstream_loc"] = pairs.loc[ix].spp_loc2

# habitat line is opposite NHD; flip it
ix = ~ix
pairs.loc[ix, "spp_line"] = shapely.reverse(pairs.loc[ix].spp_line)
pairs.loc[ix, "spp_upstream_pt"] = pairs.loc[ix].spp_pt2
pairs.loc[ix, "spp_upstream_loc"] = pairs.loc[ix].spp_loc2
pairs.loc[ix, "spp_downstream_pt"] = pairs.loc[ix].spp_pt1
pairs.loc[ix, "spp_downstream_loc"] = pairs.loc[ix].spp_loc1

pairs["spp_upstream_on_nhd"] = shapely.dwithin(
    pairs.spp_upstream_pt, pairs.nhd_line.values, TOLERANCE
)
pairs["spp_downsteam_on_nhd"] = shapely.dwithin(
    pairs.spp_downstream_pt, pairs.nhd_line.values, TOLERANCE
)

# if the upstream point of NHD line is on habitat line, set loc to 0
# if the downstream point of NHD line is on habitat line, set loc to length of line
# this ensures we only consider the line from either end rather than the actual
# loc of the habitat line endpoints, which could be somewhere else
pairs.loc[pairs.has_upstream, "spp_upstream_loc"] = pairs.loc[
    pairs.has_upstream, "length"
]
pairs.loc[pairs.has_downstream, "spp_downstream_loc"] = pairs.loc[
    pairs.has_downstream, "length"
]

pairs = pairs.drop(
    columns=[
        "spp_pt1",
        "spp_pt2",
        "spp_loc1",
        "spp_loc2",
    ]
).sort_values(by=["spp_upstream_loc", "spp_downstream_loc"])
