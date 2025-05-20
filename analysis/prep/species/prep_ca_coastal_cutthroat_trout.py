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
from analysis.lib.io import read_arrow_tables

warnings.filterwarnings("ignore", category=UserWarning, message=".*Measured.*")

SELECTION_TOLERANCE = 100  # meters; used to select flowlines that are near habitat
# outer overlap used to check overlap of flowlines filled in gaps
OUTER_OVERLAP_TOLERANCE = 300  # meters;
ENDPOINT_TOLERANCE = 1  # meters; used to determine if endpoints are on habitat
MIN_LINE_LENGTH = 10  # meters
# required amount of overlap required beween flowline and buffer around habitat line
MIN_OVERLAP_RATIO = 0.65  # proportion
MAX_LENGTH_DIFF = 2000  # meters
MAX_ENDPOINT_DIFF = 1000  # meters

data_dir = Path("data")
src_dir = data_dir / "species/source"
# must use raw data to be able to join on NHDPlusID later
nhd_dir = data_dir / "nhd/raw"
out_dir = data_dir / "species/derived"

infilename = src_dir / "Trout_EPA_forBrendan.gdb"
layer = "Lines_Coastal_Cutthroat_psmfc"


df = read_dataframe(infilename, layer=layer, columns=[]).to_crs(CRS)


################################################################################
### Load flowlines in HUC4s with species data
################################################################################
print("\n-------------------------------------------------------------------\n")
print("Loading flowlines and joins")
huc4_df = gp.read_feather(data_dir / "boundaries/huc4.feather", columns=["geometry", "HUC4", "HUC2"])
# limit to region 18
huc4_df = huc4_df.loc[huc4_df.HUC2 == "18"].reset_index()

left, right = shapely.STRtree(df.geometry.values).query(huc4_df.geometry.values, predicate="intersects")
huc4s = sorted(huc4_df.HUC4.take(left).unique())
huc2s = sorted(huc4_df.HUC2.take(left).unique())
huc4_df = huc4_df.loc[huc4_df.HUC4.isin(huc4s)].copy()

# keep only habitat in these HUCs
df = df.take(np.unique(right)).reset_index(drop=True)

# DEBUG
# write_dataframe(df, "/tmp/ca_coastal_cutthroat_trout_lines.fgb")


flowlines = read_arrow_tables(
    [nhd_dir / huc2 / "flowlines.feather" for huc2 in huc2s],
    columns=[
        "geometry",
        "NHDPlusID",
        "GNIS_Name",
        "HUC4",
        "length",
        "loop",
        "offnetwork",
        "FType",
        "FCode",
    ],
    filter=pc.is_in(pc.field("HUC4"), pa.array(huc4s)),
    new_fields={"HUC2": huc2s},
).filter(pc.field("offnetwork") == False)

flowlines = gp.GeoDataFrame(
    flowlines.select([c for c in flowlines.column_names if c not in {"geometry", "offnetwork"}]).to_pandas(),
    geometry=shapely.from_wkb(flowlines.column("geometry")),
    crs=CRS,
).set_index("NHDPlusID")

# mark canals; these require higher confidence of overlap since they may spatially
# interact with habitat but not functionally
# include those with canal in the name since many are not marked via FType
flowlines["canal"] = (flowlines.FType == 336) | (flowlines.GNIS_Name.fillna("").str.lower().str.contains(" canal"))
canal_ids = flowlines.loc[flowlines.canal].index.values

joins = read_arrow_tables(
    [nhd_dir / huc2 / "flowline_joins.feather" for huc2 in huc2s],
    columns=["upstream", "downstream", "loop"],
).to_pandas()
joins = joins.loc[
    joins.upstream.isin(flowlines.index.values) | joins.downstream.isin(flowlines.index.values)
].reset_index(drop=True)


# create a linear graph facing downstream
# NOTE: this can't handle loops
tmp = joins.loc[(joins.upstream != 0) & (joins.downstream != 0) & (~joins.loop)].copy()
downstream_graph = LinearDirectedGraph(tmp.upstream.values.astype("int64"), tmp.downstream.values.astype("int64"))


################################################################################
### Associate habitat linework with NHD flowlines by proximity
################################################################################
df["buf"] = shapely.buffer(df.geometry.values, SELECTION_TOLERANCE, cap_style="flat")

# DEBUG:
write_dataframe(
    gp.GeoDataFrame(geometry=df.buf, crs=CRS),
    "/tmp/ca_coastal_cutthroat_trout_source_buffer.fgb",
)

# add upstream / downstream points
flowlines["nhd_upstream_pt"] = shapely.get_point(flowlines.geometry.values, 0)
flowlines["nhd_downstream_pt"] = shapely.get_point(flowlines.geometry.values, -1)

# extract flowlines within SELECTION_TOLERANCE of habitat lines
# WARNING: this will include many flowlines that we should not keep
left, right = shapely.STRtree(flowlines.geometry.values).query(df.buf.values, predicate="intersects")
pairs = pd.DataFrame(
    {
        "NHDPlusID": flowlines.index.values.take(right),
        "spp_line": df.geometry.values.take(left),
        "spp_buf": df.buf.values.take(left),
    }
).join(
    flowlines[
        [
            "geometry",
            "length",
            "canal",
            "loop",
            "nhd_upstream_pt",
            "nhd_downstream_pt",
        ]
    ].rename(columns={"geometry": "nhd_line"}),
    on="NHDPlusID",
)

pairs["upstream_dist"] = shapely.distance(pairs.nhd_upstream_pt, pairs.spp_line.values)
pairs["downstream_dist"] = shapely.distance(pairs.nhd_downstream_pt, pairs.spp_line.values)

tmp = pairs.groupby("NHDPlusID").agg(
    {
        "upstream_dist": "min",
        "downstream_dist": "min",
        "canal": "first",
        "loop": "first",
    }
)


# keep any NHD flowlines where both endpoints are in habitat and discard from
# further processing
# exclude canals here because we need to analyze their overlap below
# exclude any flowlines that are loops; if there is much overlap they will be picked up below
keep_line_ids = tmp.loc[
    (tmp.upstream_dist < ENDPOINT_TOLERANCE) & (tmp.downstream_dist < ENDPOINT_TOLERANCE) & (~tmp.canal) & (~tmp.loop)
].index.unique()

# drop any that are too far away
drop_ids = tmp.loc[(tmp.upstream_dist > MAX_ENDPOINT_DIFF) | (tmp.downstream_dist > MAX_ENDPOINT_DIFF)].index.unique()

pairs = pairs.loc[~pairs.NHDPlusID.isin(np.unique(np.concatenate([keep_line_ids, drop_ids])))].copy()
print(f"keeping {len(keep_line_ids):,} NHD lines with endpoints that completely overlap habitat")

# keep any flowlines that are sufficiently covered by buffer of habitat line and drop
# them from further analysis and drop any where the overlap is too short
pairs["overlap"] = shapely.length(shapely.intersection(pairs.nhd_line.values, pairs.spp_buf.values))
pairs["overlap_ratio"] = pairs.overlap / pairs["length"]

# keep any where there is a high degree of overlap across all habitat lines
# unless they overlap multiple species groups
total_overlap = pairs.groupby("NHDPlusID").agg(
    {
        "overlap": "sum",
        "length": "first",
        "canal": "first",
    }
)
total_overlap["overlap_ratio"] = total_overlap.overlap / total_overlap.length

drop_ids = total_overlap.loc[total_overlap.overlap < MIN_LINE_LENGTH].index.unique().values
print(f"dropping {len(drop_ids):,} NHD lines that barely overlap habitat")

upstream_in_habitat = pairs.loc[pairs.upstream_dist < ENDPOINT_TOLERANCE].NHDPlusID.unique()

keep_ids = np.setdiff1d(
    total_overlap.loc[
        (
            (total_overlap.length - total_overlap.overlap < MAX_LENGTH_DIFF)
            & (total_overlap.overlap_ratio >= MIN_OVERLAP_RATIO)
        )
    ].index.unique(),
    drop_ids,
)

# filter out short segments with upstreams that are not in keep_ids; these
# are short root points of incoming tribs that are not themselves included
potential_fragments = pd.Series(
    total_overlap.loc[
        (total_overlap.overlap_ratio >= MIN_OVERLAP_RATIO) & (total_overlap.length < 3 * SELECTION_TOLERANCE)
    ].index.unique()
)

# do this iteratively in case we leave fragments after removing ones upstream of them
# this gets small enough after 10 iterations
for i in range(10):
    potential_keep = np.unique(np.concatenate([keep_line_ids, keep_ids]))
    keep_fragments = joins.loc[
        joins.downstream.isin(potential_fragments.values) & joins.upstream.isin(potential_keep)
    ].downstream.unique()
    drop_fragments = potential_fragments.loc[~potential_fragments.isin(keep_fragments)].values

    if len(drop_fragments) == 0:
        break

    keep_ids = np.setdiff1d(keep_ids, drop_fragments)
    potential_fragments = pd.Series(np.setdiff1d(potential_fragments, drop_fragments))


keep_line_ids = np.unique(np.concatenate([keep_line_ids, keep_ids]))
pairs = pairs.loc[~(pairs.NHDPlusID.isin(np.unique(np.concatenate([keep_line_ids, drop_ids]))))].reset_index()
print(f"keeping {len(keep_ids):,} NHD lines that mostly overlap habitat")


# DEBUG:
# write_dataframe(
#     flowlines.loc[flowlines.index.isin(keep_line_ids)].join(total_overlap[["overlap", "overlap_ratio"]]).reset_index(),
#     "/tmp/ca_coastal_cutthroat_trout_high_overlap_keep_lines.fgb",
# )


################################################################################
### Trace the downstream network and fill gaps
################################################################################
# if there exists a route from a given keep line through ones still in pairs
# to another keep line, and it is in same habitat group, then fill those gaps

# extract the upstream and downstream joins from joins based on keep_line_ids
# in order to find linear networks downstream of downstreams that terminate at
# any of the upstream points
# do not traverse downstream of any canals; these are questionable
# have to group by upstream because it may have multiple downstreams
# exclude loops
tmp = joins.loc[joins.upstream.isin(keep_line_ids) & (~joins.upstream.isin(canal_ids)) & (~joins.loop)].copy()
tmp["has_downstream"] = tmp.downstream.isin(keep_line_ids)
has_downstream = tmp.groupby("upstream").has_downstream.max()
downstreams = has_downstream.loc[~has_downstream].index.unique().values.astype("int64")
upstreams = (
    joins.loc[joins.downstream.isin(keep_line_ids) & ~joins.upstream.isin(keep_line_ids)]
    .upstream.unique()
    .astype("int64")
)

print(f"trying to fill gaps from {len(downstreams):,} starting points")

paths = downstream_graph.extract_paths(
    downstreams,
    upstreams,
    max_depth=100,
)
paths = pd.DataFrame({"path": range(len(paths)), "NHDPlusID": paths})
paths = paths.loc[paths.NHDPlusID.apply(len) > 0].explode(column="NHDPlusID")

# drop any paths that pass through canals; these cause issues
drop_paths = paths.loc[paths.NHDPlusID.isin(canal_ids)].path.unique()
paths = paths.loc[~paths.path.isin(drop_paths)].copy()

# merge paths that have overlapping NHDPlusIDs
tmp = (
    paths.join(paths.groupby("NHDPlusID").path.unique().rename("other_path"), on="NHDPlusID")
    .explode(column="other_path")[["path", "other_path"]]
    .drop_duplicates()
)
# add symmetric pairs
tmp = pd.concat([tmp, tmp.rename(columns={"path": "other_path", "other_path": "path"})])
groups = DirectedGraph(tmp.path.values.astype("int64"), tmp.other_path.values.astype("int64")).components()

groups = pd.DataFrame({"group": range(len(groups)), "path": groups}).explode(column="path").set_index("path")
paths = (
    paths.join(groups, on="path")
    .groupby(["group", "NHDPlusID"])[[]]
    .first()
    .reset_index()
    .rename(columns={"group": "path"})
    .join(flowlines[["geometry", "length"]], on="NHDPlusID")
)

# Limit these to ones with >= 50% overlap with a OUTER_OVERLAP_TOLERANCE buffer
# around habitat lines
# create a buffer of OUTER_OVERLAP_TOLERANCE around any nearby habitat lines
print(f"calculating total overlap of paths and {OUTER_OVERLAP_TOLERANCE} m buffer around habitat lines")

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
    .agg({"spp_buf": lambda x: shapely.union_all(shapely.buffer(x, OUTER_OVERLAP_TOLERANCE, cap_style="flat"))})
    .join(path_total)
)

path_pairs["overlap_ratio"] = (
    shapely.length(shapely.intersection(path_pairs.geometry.values, path_pairs.spp_buf.values)) / path_pairs.length
)

# we can use low overlap because the downstream lines are lower resolution
# but generally we are tracing the right general direction
keep_paths = path_pairs.overlap_ratio.loc[path_pairs.overlap_ratio >= 0.1].index
keep_ids = paths.loc[paths.path.isin(keep_paths)].NHDPlusID.unique()
print(f"adding {len(keep_ids):,} filler lines between disconnected upstream and downstream habitat")

keep_line_ids = np.unique(np.concatenate([keep_line_ids, keep_ids]))


flowlines["ca_coastal_cutthroat_trout_habitat"] = flowlines.index.isin(keep_line_ids)

print(
    f"species habitat: {shapely.length(df.geometry.values).sum() / 1000:,.1f} km; "
    f"extracted {flowlines.loc[flowlines.ca_coastal_cutthroat_trout_habitat, ['length']].values.sum() / 1000:,.1f} km from NHD"
)

out = flowlines.loc[flowlines.ca_coastal_cutthroat_trout_habitat].reset_index()
write_dataframe(out, out_dir / "ca_coastal_cutthroat_trout_habitat.fgb")
out[["NHDPlusID", "HUC2", "ca_coastal_cutthroat_trout_habitat"]].to_feather(
    out_dir / "ca_coastal_cutthroat_trout_habitat.feather"
)
