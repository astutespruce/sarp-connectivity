from pathlib import Path
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from pyogrio import read_dataframe, write_dataframe
import shapely

from analysis.constants import CRS
from analysis.lib.graph.speedups import LinearDirectedGraph, DirectedGraph
from analysis.lib.geometry.lines import merge_lines
from analysis.lib.io import read_arrow_tables

warnings.filterwarnings("ignore", category=UserWarning, message=".*Measured.*")

SELECTION_TOLERANCE = 50  # meters; used to select flowlines that are near habitat
# outer overlap used to check overlap of flowlines filled in gaps
OUTER_OVERLAP_TOLERANCE = 200  # meters;
ENDPOINT_TOLERANCE = 1  # meters; used to determine if endpoints are on habitat
MIN_LINE_LENGTH = 10  # meters
# required amount of overlap required beween flowline and buffer around habitat line
MIN_OVERLAP_RATIO = 0.65  # proportion

MAX_LINE_DIFF = 1000  # meters


data_dir = Path("data")
src_dir = data_dir / "species/source"
nhd_dir = data_dir / "nhd/clean"
out_dir = data_dir / "species/derived"

infilename = src_dir / "CA_BaselineFishHabitat_v3.gdb"
layer = "Baseline_Fish_Habitat_V3"

# manually-identified keep lines:

# NHDPlusIDs
keep_nhd_ids = np.array([50000300034240])


df = read_dataframe(
    infilename, layer=layer, use_arrow=True, columns=["REACHCODE", "COMID"]
)
df["geometry"] = shapely.force_2d(df.geometry.values)
df = df.to_crs(CRS)

# fix missing reach code values (there are 2, one is just a fragment)
df.loc[df.REACHCODE.isnull() & (df.COMID == 2707001), "REACHCODE"] = "18010105000198"
df.loc[df.REACHCODE.isnull() & (df.COMID == 8258809), "REACHCODE"] = "18010210000727"

# merge up to reach code level
df = merge_lines(df.explode(ignore_index=True), by="REACHCODE").set_index("REACHCODE")
df["mr_length"] = shapely.length(df.geometry.values)

# DEBUG:
write_dataframe(df.reset_index(), "/tmp/ca_baseline_fish_habitat_source.fgb")


################################################################################
### Load flowlines in HUC4s with species data
################################################################################
print("\n-------------------------------------------------------------------\n")
print("Loading flowlines and joins")
huc4_df = gp.read_feather(
    data_dir / "boundaries/huc4.feather", columns=["geometry", "HUC4", "HUC2"]
)
ix = shapely.STRtree(df.geometry.values).query(
    huc4_df.geometry.values, predicate="intersects"
)[0]
huc4s = sorted(huc4_df.HUC4.take(ix).unique())
huc2s = sorted(huc4_df.HUC2.take(ix).unique())
huc4_df = huc4_df.loc[huc4_df.HUC4.isin(huc4s)].copy()

flowlines = read_arrow_tables(
    [nhd_dir / huc2 / "flowlines.feather" for huc2 in huc2s],
    columns=[
        "geometry",
        "lineID",
        "NHDPlusID",
        "ReachCode",
        "GNIS_Name",
        "HUC4",
        "length",
        "loop",
        "offnetwork",
        "FType",
    ],
    filter=pc.is_in(pc.field("HUC4"), pa.array(huc4s)),
    new_fields={"HUC2": huc2s},
).filter(pc.field("offnetwork") == False)

flowlines = gp.GeoDataFrame(
    flowlines.select(
        [c for c in flowlines.column_names if c not in {"geometry", "offnetwork"}]
    ).to_pandas(),
    geometry=shapely.from_wkb(flowlines.column("geometry")),
    crs=CRS,
).set_index("lineID")

# mark canals; these require higher confidence of overlap since they may spatially
# interact with habitat but not functionally
# include those with canal in the name since many are not marked via FType
flowlines["canal"] = (flowlines.FType == 336) | (
    flowlines.GNIS_Name.fillna("").str.lower().str.contains(" canal")
)
canal_ids = flowlines.loc[flowlines.canal].index.values

keep_line_ids = flowlines.loc[flowlines.NHDPlusID.isin(keep_nhd_ids)].index.unique()

joins = read_arrow_tables(
    [nhd_dir / huc2 / "flowline_joins.feather" for huc2 in huc2s],
    columns=["upstream_id", "downstream_id", "loop"],
).to_pandas()
joins = joins.loc[
    joins.upstream_id.isin(flowlines.index.values)
    | joins.downstream_id.isin(flowlines.index.values)
].reset_index(drop=True)

# create a linear graph facing downstream
# NOTE: this can't handle loops
tmp = joins.loc[
    (joins.upstream_id != 0) & (joins.downstream_id != 0) & (~joins.loop)
].copy()
downstream_graph = LinearDirectedGraph(
    tmp.upstream_id.values.astype("int64"), tmp.downstream_id.values.astype("int64")
)


################################################################################
### Select NHD HR flowlines by NHD medium resolution reach code
################################################################################
# NOTE: some of the reaches are cut short, so we check for the amount of
# similarity in their overall lengths
reaches = flowlines.loc[
    flowlines.ReachCode.isin(df.loc[df.index.values].index.unique())
]
by_reach = (
    merge_lines(reaches, by="ReachCode")
    .join(
        df[["geometry", "mr_length"]].rename(columns={"geometry": "mr_line"}),
        on="ReachCode",
    )
    .explode(ignore_index=True)
)
by_reach["hr_length"] = shapely.length(by_reach.geometry.values)

# # DEBUG:
# write_dataframe(by_reach, "/tmp/reaches.fgb")
by_reach["endpoint_dist"] = shapely.distance(
    shapely.get_point(by_reach.geometry.values, 0), by_reach.mr_line.values
)
by_reach["length_diff"] = np.abs(
    by_reach.hr_length.values - by_reach.mr_length.values
) / by_reach[["mr_length", "hr_length"]].max(axis=1)

# keep them if their lengths are 75% similar and endpoint is within MAX_LINE_DIFF
# of habitat line
ix = (by_reach.length_diff < 0.75) & (by_reach.endpoint_dist < MAX_LINE_DIFF)

keep_line_ids = np.unique(
    np.concatenate(
        [
            keep_line_ids,
            reaches.loc[
                reaches.ReachCode.isin(by_reach.loc[ix].ReachCode.unique())
                & (~reaches.canal)
            ].index.unique(),
        ]
    )
)
print(
    f"selected {len(keep_line_ids):,} NHD flowlines that line up with habitat linework by NHD ReachCode"
)

remaining_flowlines = flowlines.loc[~flowlines.index.isin(keep_line_ids)].copy()


################################################################################
### Associate habitat linework with NHD flowlines by proximity
################################################################################
df["buf"] = shapely.buffer(df.geometry.values, SELECTION_TOLERANCE, cap_style="flat")

# add upstream / downstream points
remaining_flowlines["nhd_upstream_pt"] = shapely.get_point(
    remaining_flowlines.geometry.values, 0
)
remaining_flowlines["nhd_downstream_pt"] = shapely.get_point(
    remaining_flowlines.geometry.values, -1
)

# extract flowlines within SELECTION_TOLERANCE of habitat lines
# WARNING: this will include many flowlines that we should not keep
left, right = shapely.STRtree(remaining_flowlines.geometry.values).query(
    df.buf.values, predicate="intersects"
)
pairs = (
    pd.DataFrame(
        {
            "lineID": remaining_flowlines.index.values.take(right),
            "ReachCode": df.index.values.take(left),
        }
    )
    .join(
        remaining_flowlines[
            [
                "geometry",
                "length",
                "canal",
                "loop",
                "nhd_upstream_pt",
                "nhd_downstream_pt",
            ]
        ].rename(columns={"geometry": "nhd_line"}),
        on="lineID",
    )
    .join(
        df[["geometry", "buf"]].rename(
            columns={"geometry": "spp_line", "buf": "spp_buf"}
        ),
        on="ReachCode",
    )
)

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
        "loop": "first",
    }
)
# exclude canals here because we need to analyze their overlap below
# exclude any flowlines that are loops; if there is much overlap they will be picked up below
keep_ids = tmp.loc[
    tmp.has_upstream & tmp.has_downstream & (~tmp.canal) & (~tmp.loop)
].index.unique()

keep_line_ids = np.unique(
    np.concatenate(
        [
            keep_line_ids,
            keep_ids,
        ]
    )
)
pairs = pairs.loc[~pairs.lineID.isin(keep_line_ids)].copy()
print(
    f"keeping {len(keep_ids):,} NHD lines with endpoints that completely overlap habitat"
)


# keep any flowlines that are >= 95 covered by buffer of habitat line and drop
# them from further analysis and drop any where the overlap is too short
pairs["overlap"] = shapely.length(
    shapely.intersection(pairs.nhd_line.values, pairs.spp_buf.values)
)
pairs["overlap_ratio"] = pairs.overlap / pairs["length"]

# DEBUG:
# pairs[["lineID", "spp_line_id", "length", "overlap", "overlap_ratio"]].reset_index(
#     drop=True
# ).to_feather(f"/tmp/{unit}_pairs.feather")

# keep any where there is a high degree of overlap across all habitat lines
# unless they overlap multiple species groups
total_overlap = pairs.groupby("lineID").agg(
    {"overlap": "sum", "length": "first", "canal": "first"}
)
total_overlap["overlap_ratio"] = total_overlap.overlap / total_overlap.length

drop_ids = (
    total_overlap.loc[total_overlap.overlap < MIN_LINE_LENGTH].index.unique().values
)
print(f"dropping {len(drop_ids):,} NHD lines that barely overlap habitat")

keep_ids = np.setdiff1d(
    total_overlap.loc[
        (
            (total_overlap.overlap_ratio >= MIN_OVERLAP_RATIO)
            & (total_overlap.length - total_overlap.overlap < 500)
        )
        # # also keep longer lines with higher overlap regardless of difference
        # | ((total_overlap.overlap_ratio >= 0.75) & (total_overlap.length >= 2000))
        # (total_overlap.overlap_ratio >= 0.75)
        # & (total_overlap.length - total_overlap.overlap < 500)
    ].index.unique(),
    drop_ids,
)

# filter out short segments with upstreams that are not in keep_ids; these
# are short root points of incoming tribs that are not themselves included
potential_fragments = pd.Series(
    total_overlap.loc[
        (total_overlap.overlap_ratio >= MIN_OVERLAP_RATIO)
        & (total_overlap.length < 3 * SELECTION_TOLERANCE)
    ].index.unique()
)

# do this iteratively in case we leave fragments after removing ones upstream of them
# this gets small enough after 10 iterations
for i in range(10):
    potential_keep = np.unique(np.concatenate([keep_line_ids, keep_ids]))
    keep_fragments = joins.loc[
        joins.downstream_id.isin(potential_fragments.values)
        & joins.upstream_id.isin(potential_keep)
    ].downstream_id.unique()
    drop_fragments = potential_fragments.loc[
        ~potential_fragments.isin(keep_fragments)
    ].values

    if len(drop_fragments) == 0:
        break

    keep_ids = np.setdiff1d(keep_ids, drop_fragments)
    potential_fragments = pd.Series(np.setdiff1d(potential_fragments, drop_fragments))


keep_line_ids = np.unique(np.concatenate([keep_line_ids, keep_ids]))
pairs = pairs.loc[
    ~(pairs.lineID.isin(np.unique(np.concatenate([keep_line_ids, drop_ids]))))
].reset_index()
print(f"keeping {len(keep_ids):,} NHD lines that mostly overlap habitat")

# DEBUG:
# write_dataframe(
#     flowlines.loc[flowlines.index.isin(keep_line_ids)]
#     .join(total_overlap[["overlap", "overlap_ratio"]])
#     .reset_index(),
#     "/tmp/ca_baseline_high_overlap_keep_lines.fgb",
# )


### Trace the downstream network
# if there exists a route from a given keep line through ones still in pairs
# to another keep line, and it is in same habitat group, then fill those gaps

# extract the upstream and downstream joins from joins based on keep_line_ids
# in order to find linear networks downstream of downstreams that terminate at
# any of the upstream points
# do not traverse downstream of any canals; these are questionable
# have to group by upstream_id because it may have multiple downstreams
# exclude loops
tmp = joins.loc[
    joins.upstream_id.isin(keep_line_ids)
    & (~joins.upstream_id.isin(canal_ids))
    & (~joins.loop)
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

print(f"trying to fill gaps from {len(downstreams):,} starting points")

paths = downstream_graph.extract_paths(
    downstreams,
    upstreams,
    max_depth=100,
)
paths = pd.DataFrame({"path": range(len(paths)), "lineID": paths})
paths = paths.loc[paths.lineID.apply(len) > 0].explode(column="lineID")

# drop any paths that pass through canals; these cause issues
drop_paths = paths.loc[paths.lineID.isin(canal_ids)].path.unique()
paths = paths.loc[~paths.path.isin(drop_paths)].copy()

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

# Limit these to ones with >= 50% overlap with a OUTER_OVERLAP_TOLERANCE buffer
# around habitat lines
# create a buffer of OUTER_OVERLAP_TOLERANCE around any nearby habitat lines
print(
    f"calculating total overlap of paths and {OUTER_OVERLAP_TOLERANCE} buffer around habitat lines"
)

# aggregate paths
path_total = paths.groupby("path").agg({"geometry": shapely.union_all})
path_total["length"] = shapely.length(path_total.geometry.values)

# NOTE: have to use buffer because dwithin is not working properly in GEOS
path_total["buf"] = shapely.buffer(path_total.geometry.values, OUTER_OVERLAP_TOLERANCE)

tree = shapely.STRtree(df.geometry.values)
left, right = tree.query(
    path_total.buf.values,
    predicate="intersects",
)

path_pairs = (
    pd.DataFrame(
        {
            "right": df.index.values.take(right),
            "path": path_total.index.values.take(left),
        }
    )
    .join(df.geometry.rename("spp_buf"), on="right")
    .groupby("path")
    .agg(
        {
            "spp_buf": lambda x: shapely.union_all(
                shapely.buffer(x, OUTER_OVERLAP_TOLERANCE, cap_style="flat")
            )
        }
    )
    .join(path_total)
)

overlap_ratio = (
    shapely.length(
        shapely.intersection(path_pairs.geometry.values, path_pairs.spp_buf.values)
    )
    / path_pairs.length
)
# we can use low overlap because the downstream lines are lower resolution
# but generally we are tracing the right general direction
keep_paths = overlap_ratio.loc[overlap_ratio >= 0.1].index
keep_ids = paths.loc[paths.path.isin(keep_paths)].lineID.unique()

print(
    f"adding {len(keep_ids):,} filler lines between disconnected upstream and downstream habitat"
)

# DEBUG:
write_dataframe(
    flowlines.loc[flowlines.index.isin(keep_ids)].reset_index(),
    "/tmp/ca_baseline_filler.fgb",
)

keep_line_ids = np.unique(np.concatenate([keep_line_ids, keep_ids]))

#########################################
flowlines["ca_bfh"] = flowlines.index.isin(keep_line_ids)

print(
    f"species habitat: {shapely.length(df.geometry.values).sum() / 1000:,.1f} km; "
    f"extracted {flowlines.loc[flowlines.ca_bfh, ['length']].values.sum() / 1000:,.1f} km from NHD"
)

out = flowlines.loc[flowlines.ca_bfh].reset_index()
write_dataframe(out, out_dir / "ca_baseline_fish_habitat.fgb")
out[["lineID", "NHDPlusID", "ca_bfh"]].reset_index().to_feather(
    out_dir / "ca_baseline_fish_habitat.feather"
)
