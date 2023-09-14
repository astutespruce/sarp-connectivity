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
TOLERANCE = 1  # meters
MIN_LINE_LENGTH = 10
MAX_GAP = 5

data_dir = Path("data")
src_dir = data_dir / "species/source"
nhd_dir = data_dir / "nhd/raw"
out_dir = data_dir / "species/derived"


infilename = (
    src_dir
    / "Generalized Fish Distribution - All Species Combined (StreamNet - January 2019)/StreamNet_20190131.gdb"
)
layer = "FishDist_AllSpeciesCombined_20190131"
keep_species = [
    "Bonneville cutthroat trout",
    "Bull trout",
    "Chinook salmon",
    "Chum salmon",
    "Coastal cutthroat trout",
    "Coho salmon",
    "Cutthroat trout",
    "Green sturgeon",
    "Kokanee",
    "Pacific lamprey",
    "Pink salmon",
    "Redband trout",
    "Sockeye salmon",
    "Steelhead",
    "Westslope cutthroat trout",
    "White sturgeon",
    "Yellowstone cutthroat trout",
]


df = read_dataframe(
    infilename,
    layer=layer,
    use_arrow=True,
    columns=["Species", "Run", "LifeHistoryType"],
)

df = df.loc[
    df.Species.isin(keep_species) & (~shapely.is_empty(df.geometry.values))
].copy()
df["geometry"] = shapely.force_2d(df.geometry.values)
df = df.to_crs(CRS)

df["unit"] = df.Species
ix = df.Run != "N/A"
df.loc[ix, "unit"] += " (" + df.loc[ix].Run.str.lower() + ")"

df = df[["unit", "geometry"]].explode(ignore_index=True)

# first, drop any identical duplicates
print("Dropping duplicates")
df["hash"] = pd.util.hash_array(shapely.to_wkb(df.geometry.values))
df = gp.GeoDataFrame(
    df.groupby(by=["unit", "hash"]).first().reset_index()[["unit", "geometry"]],
    geometry="geometry",
    crs=CRS,
)


# use species and run (where not N/A)
# spp = "Green sturgeon"
unit = "Coho salmon"
spp_df = df.loc[df.unit == unit].reset_index(drop=True)

################################################################################
### Merge habitat linework for species
################################################################################
# use unary union (not dissolve!) with a lower grid size followed by merge lines
# in order to properly dissolve overlapping lines
geometry = shapely.unary_union(spp_df.geometry.values, grid_size=0.1)
spp_df = merge_lines(
    gp.GeoDataFrame({"unit": [unit]}, geometry=[geometry], crs=CRS).explode(
        ignore_index=True
    ),
    by="unit",
).explode(ignore_index=True)

# fill short gaps in habitat linework; these cause issues later
filled = fill_endpoint_gaps(spp_df, gap_size=MAX_GAP)
filled_count = len(filled) - len(spp_df)
if filled_count:
    print(f"Filled {filled_count:,} gaps between endoints <= {MAX_GAP}m")
    geometry = shapely.unary_union(filled.geometry.values)
    spp_df = merge_lines(
        gp.GeoDataFrame({"unit": [unit]}, geometry=[geometry], crs=CRS).explode(
            ignore_index=True
        ),
        by="unit",
    ).explode(ignore_index=True)


# drop isolated slivers that are shorter than tolerance
spp_df = spp_df.loc[shapely.length(spp_df.geometry.values) >= TOLERANCE].reset_index(
    drop=True
)

# assign group based on connected lines
# due to topology / geometry issues in the data, there are some small gaps; this
# attempts to bridge those using a 5m tolerance
tree = shapely.STRtree(spp_df.geometry.values)
left, right = tree.query(spp_df.geometry.values, predicate="dwithin", distance=5)
# add symmetric pairs
groups = DirectedGraph(
    np.concatenate([left, right]), np.concatenate([right, left])
).components()
groups = (
    pd.DataFrame(
        {i: list(g) for i, g in enumerate(groups)}.items(),
        columns=["group", "index"],
    )
    .explode("index")
    .set_index("index")
)
spp_df = spp_df.join(groups)

# assign segment ids used for analysis below
spp_df["id"] = spp_df.index.values

# create buffer for analysis
spp_df["buf"] = shapely.buffer(spp_df.geometry.values, TOLERANCE, cap_style="flat")


# TODO: just load all HUC2 flowlines and do this at once
# limit to 16, 17, 18
huc2s = ["17"]


huc2 = huc2s[0]
flowlines = gp.read_feather(
    nhd_dir / huc2 / "flowlines.feather",
    columns=["geometry", "lineID", "NHDPlusID", "length", "loop", "offnetwork"],
).set_index("lineID")
flowlines = flowlines.loc[~flowlines.offnetwork].copy()

# add upstream / downstream points
flowlines["nhd_upstream_pt"] = shapely.get_point(flowlines.geometry.values, 0)
flowlines["nhd_downstream_pt"] = shapely.get_point(flowlines.geometry.values, -1)

joins = pd.read_feather(
    nhd_dir / huc2 / "flowline_joins.feather",
    columns=["upstream_id", "downstream_id", "loop"],
)


# extract flowlines within TOLERANCE of habitat lines
# WARNING: this will include many flowlines that we should not keep
tree = shapely.STRtree(flowlines.geometry.values)
left, right = tree.query(spp_df.buf.values, predicate="intersects")
pairs = (
    pd.DataFrame(
        {
            "lineID": flowlines.index.values.take(right),
            "spp_line_id": spp_df.id.values.take(left),
        }
    )
    .join(
        flowlines[
            ["geometry", "length", "nhd_upstream_pt", "nhd_downstream_pt"]
        ].rename(columns={"geometry": "nhd_line"}),
        on="lineID",
    )
    .join(
        spp_df[["geometry", "buf"]].rename(
            columns={"geometry": "spp_line", "buf": "spp_buf"}
        ),
        on="spp_line_id",
    )
)


# keep any NHD flowlines where both endpoints are in habitat and discard from
# further processing
pairs["has_upstream"] = shapely.dwithin(
    pairs.nhd_upstream_pt, pairs.spp_line.values, TOLERANCE
)
pairs["has_downstream"] = shapely.dwithin(
    pairs.nhd_downstream_pt, pairs.spp_line.values, TOLERANCE
)

tmp = pairs.groupby("lineID")[["has_upstream", "has_downstream"]].max()
keep_line_ids = tmp.loc[tmp.has_upstream & tmp.has_downstream].index.unique()

# keep_line_ids = pairs.loc[pairs.has_upstream & pairs.has_downstream].lineID.unique()
pairs = pairs.loc[~pairs.lineID.isin(keep_line_ids)].copy()
print(f"keeping {len(keep_line_ids):,} NHD lines that completely overlap habitat")

# drop any where the location of NHD upstream or downstream points on spp_line
# are within TOLERANCE of each other; this helps drop any where there are
# multiple NHD lines per species line but only some of them are applicable
upstream_loc = shapely.line_locate_point(
    pairs.spp_line.values, pairs.nhd_upstream_pt.values
)
downstream_loc = shapely.line_locate_point(
    pairs.spp_line.values, pairs.nhd_downstream_pt.values
)
ix = np.isclose(upstream_loc, downstream_loc, atol=TOLERANCE)
pairs = pairs.loc[~ix].copy()
print(f"dropping {(~ix).sum():,} pairs below tolerance")


# keep any flowlines that are >= 95 covered by buffer of habitat line and drop
# them from further analysis and drop any where the overlap is too short
overlap = shapely.length(
    shapely.intersection(pairs.nhd_line.values, pairs.spp_buf.values)
)
drop_ix = overlap < MIN_LINE_LENGTH
keep_ids = pairs.loc[overlap / pairs["length"] >= 0.95].lineID.unique()
keep_line_ids = np.unique(np.concatenate([keep_line_ids, keep_ids]))
pairs = pairs.loc[~(pairs.lineID.isin(keep_ids) | drop_ix)].copy()
print(
    f"keeping {len(keep_ids):,} NHD lines that mostly overlap habitat and dropping {drop_ix.sum():,} pairs that barely overlap"
)


# look at overlaps of the endpoints of the habitat line with the NHD flowline
# NOTE: the habitat line may be oriented in the opposite direction as the
# flowline, so we need to detect this and flip it
pairs["spp_pt1"] = shapely.get_point(pairs.spp_line.values, 0)
pairs["spp_loc1"] = shapely.line_locate_point(pairs.nhd_line.values, pairs.spp_pt1)
pairs["spp_pt1_on_nhd"] = shapely.dwithin(
    pairs.spp_pt1, pairs.nhd_line.values, TOLERANCE
)

pairs["spp_pt2"] = shapely.get_point(pairs.spp_line.values, -1)
pairs["spp_loc2"] = shapely.line_locate_point(pairs.nhd_line.values, pairs.spp_pt2)
pairs["spp_pt2_on_nhd"] = shapely.dwithin(
    pairs.spp_pt2, pairs.nhd_line.values, TOLERANCE
)

# if both loc1 and loc2 are within TOLERANCE of each other, this likely indicates
# there is very little overlap with the line, so discard these
pairs = pairs.loc[~np.isclose(pairs.spp_loc1, pairs.spp_loc2, atol=TOLERANCE)].copy()

# reorient so that habitat points are aligned with upstream / downstream direction
# of flowline
# habitat line is oriented same as NHD
ix = pairs.spp_loc1 < pairs.spp_loc2
pairs.loc[ix, "spp_upstream_pt"] = pairs.loc[ix].spp_pt1
pairs.loc[ix, "spp_upstream_loc"] = pairs.loc[ix].spp_loc1
pairs.loc[ix, "spp_upstream_on_nhd"] = pairs.loc[ix].spp_pt1_on_nhd
pairs.loc[ix, "spp_downstream_pt"] = pairs.loc[ix].spp_pt2
pairs.loc[ix, "spp_downstream_loc"] = pairs.loc[ix].spp_loc2
pairs.loc[ix, "spp_downstream_on_nhd"] = pairs.loc[ix].spp_pt2_on_nhd

ix = ~ix
# also reverse the line
pairs.loc[ix, "spp_line"] = shapely.reverse(pairs.loc[ix].spp_line)
pairs.loc[ix, "spp_upstream_pt"] = pairs.loc[ix].spp_pt2
pairs.loc[ix, "spp_upstream_loc"] = pairs.loc[ix].spp_loc2
pairs.loc[ix, "spp_upstream_on_nhd"] = pairs.loc[ix].spp_pt2_on_nhd
pairs.loc[ix, "spp_downstream_pt"] = pairs.loc[ix].spp_pt1
pairs.loc[ix, "spp_downstream_loc"] = pairs.loc[ix].spp_loc1
pairs.loc[ix, "spp_downstream_on_nhd"] = pairs.loc[ix].spp_pt1_on_nhd


# if the upstream point of NHD line is on habitat line, set loc to 0
pairs.loc[pairs.has_upstream, "spp_upstream_loc"] = pairs.loc[
    pairs.has_upstream, "length"
]
# if the downstream point of NHD line is on habitat line, set loc to length of line
pairs.loc[pairs.has_downstream, "spp_downstream_loc"] = pairs.loc[
    pairs.has_downstream, "length"
]


pairs = pairs.drop(
    columns=[
        "spp_pt1",
        "spp_pt2",
        "spp_loc1",
        "spp_loc2",
        "spp_pt1_on_nhd",
        "spp_pt2_on_nhd",
    ]
).sort_values(by=["spp_upstream_loc", "spp_downstream_loc"])
