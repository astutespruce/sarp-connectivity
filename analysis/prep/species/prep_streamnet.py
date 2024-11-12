from pathlib import Path
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
import pyarrow as pa
from pyarrow.dataset import dataset
import pyarrow.compute as pc
from pyogrio import read_dataframe, write_dataframe
import shapely

from analysis.constants import CRS
from analysis.lib.graph.speedups import LinearDirectedGraph, DirectedGraph
from analysis.lib.geometry.lines import merge_lines, fill_endpoint_gaps
from analysis.lib.io import read_arrow_tables

from analysis.lib.util import append

warnings.filterwarnings("ignore", category=UserWarning, message=".*Measured.*")


MIN_SPECIES_SEGMENT_LENGTH = 1  # meters;
MAX_GAP = 5  # meters; maximum space between endpoints to bridge
# the maximum distance between lines in a group is primarily used to prevent
# tracing the downstream path from one to another causing those groups to be
# combined; however, there are large false gaps in StreamNet due to missing
# segments on mainstems that look like valid habitat
# NOTE: it is not a problem to join groups across ridgelines; there is no
# downstream path that will connect them
MAX_GROUP_DISTANCE = 1000  # meters
MAX_ANADROMOUS_MARINE_DISTANCE = 5000  # meters; used to identify small isolated groups too far inland
MIN_ANDROMOUS_GROUP_LENGTH = 1000  # meters, used to identify small isolated groups
SELECTION_TOLERANCE = 50  # meters; used to select flowlines that are near habitat
OUTER_OVERLAP_TOLERANCE = 100  # meters; used to check overlap of flowlines filled in gaps
ENDPOINT_TOLERANCE = 1  # meters; used to determine if endpoints are on habitat
MIN_LINE_LENGTH = 10  # meters
# required amount of overlap required beween flowline and buffer around habitat line
MIN_OVERLAP_RATIO = 0.65  # proportion
# even if MIN_OVERLAP_RATIO of NHD line overlaps with habitat line, the absolute difference
# must be less than this value
MAX_LINE_DIFF = 500  # meters


data_dir = Path("data")
src_dir = data_dir / "species/source"
nhd_dir = data_dir / "nhd/clean"
out_dir = data_dir / "species/derived"

infilename = (
    src_dir / "Generalized Fish Distribution - All Species Combined (StreamNet - January 2019)/StreamNet_20190131.gdb"
)
layer = "FishDist_AllSpeciesCombined_20190131"
keep_species = [
    "Bonneville cutthroat trout",
    "Bull trout",
    "Chinook salmon",
    "Chum salmon",
    "Coastal cutthroat trout",
    "Coho salmon",
    # "Cutthroat trout",  # duplicates linework of subspecies, don't use
    "Green sturgeon",
    "Kokanee",
    "Pacific lamprey",
    "Pink salmon",
    "Rainbow trout",
    "Redband trout",
    "Sockeye salmon",
    "Steelhead",
    "Westslope cutthroat trout",
    "White sturgeon",
    "Yellowstone cutthroat trout",
]
# split by run for these species; aggregate the others
# NOTE: for now, lump all at species / major geography instead
run_species = [
    # "Chinook salmon",
    # "Steelhead"
]


################################################################################
### Prepare species habitat data for analysis
################################################################################

print("Reading StreamNet habitat data")
df = read_dataframe(
    infilename,
    layer=layer,
    use_arrow=True,
    columns=["Species", "Run", "LifeHistoryType"],
)

df = df.loc[df.Species.isin(keep_species) & (~shapely.is_empty(df.geometry.values))].copy()
df["geometry"] = shapely.force_2d(df.geometry.values)
df = df.to_crs(CRS)

df["unit"] = df.Species
ix = df.Species.isin(run_species)
df.loc[ix, "unit"] += " (" + df.loc[ix].Run.str.lower() + ")"

# track anadromous status at species level
df["anadromous"] = df.LifeHistoryType.str.lower().str.contains("anadromous")
# make sure rainbow trout are not marked as anadromous; if they are, they should
# be marked as steelhead instead.
# make sure that Kokanee are not marked as anadromous; if they are, they should
# be marked as Chinook instead.  There is not clean separation of Kokanee vs
# Chinook in the data.
# make sure redband trout are not marked as anadromous
df.loc[df.unit.isin(["Rainbow trout", "Kokanee", "Redband trout"]), "anadromous"] = False
is_anadromous = df.groupby("unit").anadromous.max()
anadromous_spp = sorted(is_anadromous[is_anadromous].index)

df = df[["unit", "geometry"]].explode(ignore_index=True)

# first, drop any identical duplicates
df = df.drop_duplicates(subset=["unit", "geometry"])


merged = None
group_start_index = 0
for unit in sorted(df.unit.unique()):
    print(f"\n------------- Processing {unit}-------------")
    spp_df = df.loc[df.unit == unit].reset_index(drop=True)

    # Merge habitat linework for species
    # use unary union (not dissolve!) with a lower grid size followed by merge lines
    # in order to properly dissolve overlapping lines
    # use grid_size to coalesce very near parallel lines
    geometry = shapely.unary_union(spp_df.geometry.values, grid_size=0.01)
    spp_df = merge_lines(
        gp.GeoDataFrame({"unit": [unit]}, geometry=[geometry], crs=CRS).explode(ignore_index=True),
        by="unit",
    ).explode(ignore_index=True)

    # fill short gaps in habitat linework; these cause issues later
    filled = fill_endpoint_gaps(spp_df, gap_size=MAX_GAP)
    filled_count = len(filled) - len(spp_df)
    if filled_count:
        print(f"Filled {filled_count:,} gaps between endoints <= {MAX_GAP}m")
        geometry = shapely.unary_union(filled.geometry.values)
        spp_df = merge_lines(
            gp.GeoDataFrame({"unit": [unit]}, geometry=[geometry], crs=CRS).explode(ignore_index=True),
            by="unit",
        ).explode(ignore_index=True)

    # drop isolated slivers that are shorter than MIN_SPECIES_SEGMENT_LENGTH
    spp_df = spp_df.loc[shapely.length(spp_df.geometry.values) >= MIN_SPECIES_SEGMENT_LENGTH].reset_index(drop=True)

    # assign group based on connected lines
    # due to topology / geometry issues in the data, there may still be some
    # small gaps; this attempts to bridge those using MAX_GROUP_DISTANCE
    tree = shapely.STRtree(spp_df.geometry.values)
    left, right = tree.query(spp_df.geometry.values, predicate="dwithin", distance=MAX_GROUP_DISTANCE)
    groups = DirectedGraph(left, right).components()
    groups = (
        pd.DataFrame(
            {i: list(g) for i, g in enumerate(groups)}.items(),
            columns=["group", "index"],
        )
        .explode("index")
        .set_index("index")
    )
    # make sure groups are globally unique
    groups["group"] += group_start_index
    group_start_index = groups.group.max() + 1
    spp_df = spp_df.join(groups)

    merged = append(merged, spp_df)

df = merged.reset_index(drop=True).join(is_anadromous, on="unit")

df.to_feather(src_dir / "streamnet_habitat.feather")
write_dataframe(df, src_dir / "streamnet_habitat.fgb")


################################################################################
### Find overlapping HUC2s / HUC4s for loading data
################################################################################
huc4_df = gp.read_feather(data_dir / "boundaries/huc4.feather", columns=["geometry", "HUC4", "HUC2"])
ix = shapely.STRtree(df.geometry.values).query(huc4_df.geometry.values, predicate="intersects")[0]
huc4s = huc4_df.HUC4.take(ix).unique()
huc2s = sorted(huc4_df.HUC2.take(ix).unique())
huc4_df = huc4_df.loc[huc4_df.HUC4.isin(huc4s)].copy()


################################################################################
### Identify and remove small isolated habitat groups for anadromous species
# NOTE: it is important that we discard these early on because we trace downstream
# from segments to reconnect networks
################################################################################
print("\n-------------------------------------------------------------------\n")
print("Finding and removing isolated habitat segments")


### for anadromous species, we find short isolated segments that are well inland
# from marine areas; these are likely data errors
marine = (
    dataset(data_dir / "nhd/merged/nhd_marine.feather", format="feather")
    .to_table(filter=pc.is_in(pc.field("HUC2"), pa.array(huc2s)), columns=["geometry"])
    .to_pandas()
)
marine = gp.GeoDataFrame(marine, geometry=shapely.from_wkb(marine.geometry.values), crs=CRS)
# drop holes; these are islands and we don't need to consider them at the moment
marine["geometry"] = shapely.polygons(shapely.get_exterior_ring(marine.geometry.values))
marine_buffer = shapely.buffer(shapely.multipolygons(marine.geometry.values), MAX_ANADROMOUS_MARINE_DISTANCE)

tmp = df.loc[df.anadromous].copy()
# promote length to a column so that we can aggregate it when grouping
tmp["length"] = tmp.length.values
group_length = tmp.groupby("group").length.sum()

tree = shapely.STRtree(tmp.geometry.values)
close_enough = np.unique(tree.query(marine_buffer, predicate="intersects"))
close_enough_groups = tmp.group.take(close_enough).unique()
too_small_groups = group_length[group_length < MIN_ANDROMOUS_GROUP_LENGTH].index.values
drop_groups = np.setdiff1d(too_small_groups, close_enough_groups)

df = df.loc[~df.group.isin(drop_groups)].reset_index(drop=True)


################################################################################
### Load flowlines in HUC4s with species data
################################################################################
print("\n-------------------------------------------------------------------\n")
print("Loading flowlines and joins")
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
    ],
    filter=pc.is_in(pc.field("HUC4"), pa.array(huc4s)),
    new_fields={"HUC2": huc2s},
).filter(pc.field("offnetwork") == False)  # noqa: E712

flowlines = gp.GeoDataFrame(
    flowlines.select([c for c in flowlines.column_names if c not in {"geometry", "offnetwork"}]).to_pandas(),
    geometry=shapely.from_wkb(flowlines.column("geometry")),
    crs=CRS,
).set_index("NHDPlusID")

# mark canals; these require higher confidence of overlap since they may spatially
# interact with habitat but not functionally
# include those with canal in the name since many are not marked via FType
flowlines["canal"] = (flowlines.FType == 336) | (flowlines.GNIS_Name.fillna("").str.lower().str.contains(" canal"))

# set anadromous status to False to start
flowlines["streamnet_anadromous_habitat"] = False

# add upstream / downstream points
flowlines["nhd_upstream_pt"] = shapely.get_point(flowlines.geometry.values, 0)
flowlines["nhd_downstream_pt"] = shapely.get_point(flowlines.geometry.values, -1)

read_ids = pa.array(flowlines.index.values)

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
### Associate habitat linework with NHD flowlines
################################################################################
units = sorted(df.unit.unique())
for unit in units:
    print(f"\n------------- Processing {unit}-------------")

    spp_df = df.loc[df.unit == unit].reset_index(drop=True)

    # assign segment ids used for analysis below
    spp_df["id"] = spp_df.index.values

    # create buffers for analysis
    spp_df["buf"] = shapely.buffer(spp_df.geometry.values, SELECTION_TOLERANCE, cap_style="flat")

    # DEBUG:
    # write_dataframe(spp_df.drop(columns=["buf"]), f"/tmp/{unit}_lines.fgb")
    # write_dataframe(
    #     spp_df.set_geometry("buf").drop(columns=["geometry"]).set_crs(CRS),
    #     f"/tmp/{unit}_buffer.fgb",
    # )

    spp_huc4s = huc4_df.HUC4.take(
        np.unique(shapely.STRtree(spp_df.geometry.values).query(huc4_df.geometry.values, predicate="intersects")[0])
    )

    exclude_huc4s = []
    if unit == "Yellowstone cutthroat trout":
        # this includes what appear to be erroneous isolated segments in a
        # HUC4 well removed from core habitat
        spp_huc4s = [huc4 for huc4 in spp_huc4s if huc4 != "1701"]

    spp_flowlines = flowlines.loc[flowlines.HUC4.isin(spp_huc4s)]

    # extract flowlines within SELECTION_TOLERANCE of habitat lines
    # WARNING: this will include many flowlines that we should not keep
    left, right = shapely.STRtree(spp_flowlines.geometry.values).query(spp_df.buf.values, predicate="intersects")
    pairs = (
        pd.DataFrame(
            {
                "NHDPlusID": spp_flowlines.index.values.take(right),
                "spp_line_id": spp_df.id.values.take(left),
            }
        )
        .join(
            spp_flowlines[
                [
                    "geometry",
                    "length",
                    "FType",
                    "canal",
                    "loop",
                    "nhd_upstream_pt",
                    "nhd_downstream_pt",
                ]
            ].rename(columns={"geometry": "nhd_line"}),
            on="NHDPlusID",
        )
        .join(
            spp_df[["geometry", "group", "buf"]].rename(
                columns={"geometry": "spp_line", "group": "spp_group", "buf": "spp_buf"}
            ),
            on="spp_line_id",
        )
    )

    spp_groups = pairs.groupby("NHDPlusID").spp_group.agg(["first", lambda x: len(set(x))]).reset_index()
    spp_groups.columns = ["NHDPlusID", "spp_group", "group_count"]

    canal_ids = pairs.loc[pairs.canal].NHDPlusID.unique()

    # keep any NHD flowlines where both endpoints are in habitat and discard from
    # further processing
    pairs["has_upstream"] = shapely.dwithin(pairs.nhd_upstream_pt, pairs.spp_line.values, ENDPOINT_TOLERANCE)
    pairs["has_downstream"] = shapely.dwithin(pairs.nhd_downstream_pt, pairs.spp_line.values, ENDPOINT_TOLERANCE)

    tmp = pairs.groupby("NHDPlusID").agg(
        {
            "has_upstream": "max",
            "has_downstream": "max",
            "canal": "first",
            "loop": "first",
        }
    )
    # exclude canals here because we need to analyze their overlap below
    # exclude any flowlines that bridge disjunct species groups
    # exclude any flowlines that are loops; if there is much overlap they will be picked up below
    keep_line_ids = tmp.loc[
        tmp.has_upstream
        & tmp.has_downstream
        & (~tmp.canal)
        & (~tmp.index.isin(spp_groups.loc[spp_groups.group_count > 1].NHDPlusID.unique()))
        & (~tmp.loop)
    ].index.unique()
    pairs = pairs.loc[~pairs.NHDPlusID.isin(keep_line_ids)].copy()
    print(f"keeping {len(keep_line_ids):,} NHD lines with endpoints that completely overlap habitat")

    # keep any flowlines that are >= 95 covered by buffer of habitat line and drop
    # them from further analysis and drop any where the overlap is too short
    pairs["overlap"] = shapely.length(shapely.intersection(pairs.nhd_line.values, pairs.spp_buf.values))
    pairs["overlap_ratio"] = pairs.overlap / pairs["length"]

    # DEBUG:
    # pairs[["NHDPlusID", "spp_line_id", "length", "overlap", "overlap_ratio"]].reset_index(
    #     drop=True
    # ).to_feather(f"/tmp/{unit}_pairs.feather")

    # keep any where there is a high degree of overlap across all habitat lines
    total_overlap = pairs.groupby("NHDPlusID").agg({"overlap": "sum", "length": "first", "canal": "first"})
    total_overlap["overlap_ratio"] = total_overlap.overlap / total_overlap.length

    drop_ids = total_overlap.loc[total_overlap.overlap < MIN_LINE_LENGTH].index.unique().values

    if unit not in anadromous_spp:
        # also drop any flowlines associated with multiple groups
        drop_ids = np.unique(
            np.concatenate(
                [
                    drop_ids,
                    spp_groups.loc[spp_groups.group_count > 1].NHDPlusID.values,
                ]
            )
        )

    print(f"dropping {len(drop_ids):,} NHD lines that barely overlap habitat")

    # identify flowlines with a large amount of overlap and a small total difference
    # as well as any river / lake artificial lines
    artificial_path_ids = pairs.loc[pairs.FType == 558].NHDPlusID.unique()

    keep_ids = np.setdiff1d(
        np.unique(
            np.concat(
                [
                    total_overlap.loc[
                        (total_overlap.overlap_ratio >= MIN_OVERLAP_RATIO)
                        & (total_overlap.length - total_overlap.overlap < MAX_LINE_DIFF)
                    ].index.unique(),
                    artificial_path_ids,
                ]
            )
        ),
        drop_ids,
    )

    # filter out short segments with upstreams that are not in keep_ids; these
    # are short root points of incoming tribs that are not themselves included
    # but OK to keep those that are within wider rivers when coded as artificial paths
    potential_fragments = pd.Series(
        total_overlap.loc[
            ((total_overlap.overlap_ratio >= MIN_OVERLAP_RATIO) & (total_overlap.length < 3 * SELECTION_TOLERANCE))
            & (~total_overlap.index.isin(artificial_path_ids))
        ].index.unique()
    )

    # do this iteratively in case we leave fragments after removing ones upstream of them
    for i in range(2):
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

    # update species groups
    tmp = pairs.groupby("NHDPlusID").spp_group.agg(["first", lambda x: len(set(x))]).reset_index()
    tmp.columns = ["NHDPlusID", "spp_group", "group_count"]
    spp_groups = pd.concat(
        [spp_groups.loc[spp_groups.NHDPlusID.isin(keep_line_ids)], tmp],
        ignore_index=True,
    )

    # DEBUG:
    # write_dataframe(
    #     spp_flowlines.loc[spp_flowlines.index.isin(keep_line_ids)]
    #     .join(total_overlap[["overlap", "overlap_ratio"]])
    #     .reset_index(),
    #     f"/tmp/{unit}_high_overlap_keep_lines.fgb",
    # )

    ### Trace the downstream network
    # if there exists a route from a given keep line through ones still in pairs
    # to another keep line, and it is in same habitat group, then fill those gaps

    # extract the upstream and downstream joins from joins based on keep_line_ids
    # in order to find linear networks downstream of downstreams that terminate at
    # any of the upstream points
    # do not traverse downstream of any canals; these are questionable
    # have to group by upstream because it may have multiple downstreams

    tmp = joins.loc[joins.upstream.isin(keep_line_ids) & (~joins.upstream.isin(canal_ids))].copy()
    tmp["has_downstream"] = tmp.downstream.isin(keep_line_ids)
    has_downstream = tmp.groupby("upstream").has_downstream.max()
    downstreams = has_downstream.loc[~has_downstream].index.unique().values.astype("int64")

    upstreams = (
        joins.loc[joins.downstream.isin(keep_line_ids) & ~joins.upstream.isin(keep_line_ids)]
        .upstream.unique()
        .astype("int64")
    )

    if len(downstreams) > 0 and len(upstreams) > 0:
        print(f"trying to fill gaps from {len(downstreams):,} starting points")

        paths = downstream_graph.extract_paths(
            downstreams,
            upstreams,
            max_depth=100,
        )
        paths = pd.DataFrame({"path": range(len(paths)), "NHDPlusID": paths})
        paths = paths.loc[paths.NHDPlusID.apply(len) > 0].explode(column="NHDPlusID")

        # drop any where the total amount in canals is > 500m; these are questionable for habitat
        canal_length = (
            spp_flowlines.loc[spp_flowlines.index.isin(np.intersect1d(paths.NHDPlusID, canal_ids))]
            .groupby("NHDPlusID")
            .length.sum()
            .rename("canal_length")
        )
        paths = paths.join(canal_length, on="NHDPlusID")
        paths["canal_length"] = paths.canal_length.fillna(0)

        total_canal_length = paths.groupby("path").canal_length.sum()
        drop_ids = paths.loc[
            paths.path.isin(total_canal_length[total_canal_length > 500].index.unique())
        ].NHDPlusID.unique()

        if unit not in anadromous_spp:
            # drop any where a given flowline has multiple species groups; these are problematic
            drop_ids = np.unique(
                np.concatenate([drop_ids, spp_groups.loc[spp_groups.group_count > 1].NHDPlusID.values])
            )

        paths = paths.loc[~paths.path.isin(paths.loc[paths.NHDPlusID.isin(drop_ids)].path.unique())]

        if unit not in anadromous_spp:
            # drop any where either of the path endpoints has multiple groups; keep the rest
            # and remove them from further analysis
            starts = pd.DataFrame({"path": range(len(downstreams)), "NHDPlusID": downstreams})
            starts = starts.loc[starts.path.isin(paths.path.unique())]
            ends = paths.groupby("path")[["NHDPlusID"]].last().reset_index()
            ends = (
                ends.join(
                    joins.loc[joins.upstream.isin(ends.NHDPlusID)].set_index("upstream").downstream,
                    on="NHDPlusID",
                )
                .drop(columns=["NHDPlusID"])
                .rename(columns={"downstream": "NHDPlusID"})
            )
            path_endpoints = (
                pd.concat([starts, ends], ignore_index=True)
                .join(spp_groups.set_index("NHDPlusID").spp_group, on="NHDPlusID")
                .dropna()
            )
            ix = path_endpoints.groupby("path").spp_group.unique().apply(len) > 1
            drop_ids = ix[ix].index
            paths = paths.loc[~paths.path.isin(drop_ids)]

        # merge paths that have overlapping NHDPlusIDs
        tmp = (
            paths.join(
                paths.groupby("NHDPlusID").path.unique().rename("other_path"),
                on="NHDPlusID",
            )
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
        if len(paths):
            if unit in anadromous_spp:
                # for anadromous species, ignore bad overlap and just keep all filler lines
                keep_ids = paths.NHDPlusID.unique()

            else:
                # create a buffer of OUTER_OVERLAP_TOLERANCE around any nearby habitat lines
                print(f"calculating total overlap of paths and {OUTER_OVERLAP_TOLERANCE} buffer around habitat lines")

                # aggregate paths
                path_total = paths.groupby("path").agg({"geometry": shapely.union_all})
                path_total["length"] = shapely.length(path_total.geometry.values)

                # NOTE: have to use buffer because dwithin is not working properly in GEOS
                path_total["buf"] = shapely.buffer(path_total.geometry.values, OUTER_OVERLAP_TOLERANCE)

                tree = shapely.STRtree(spp_df.geometry.values)
                left, right = tree.query(
                    path_total.buf.values,
                    predicate="intersects",
                )

                path_pairs = (
                    pd.DataFrame(
                        {
                            "right": spp_df.index.values.take(right),
                            "path": path_total.index.values.take(left),
                        }
                    )
                    .join(spp_df.geometry.rename("spp_buf"), on="right")
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
                    shapely.length(shapely.intersection(path_pairs.geometry.values, path_pairs.spp_buf.values))
                    / path_pairs.length
                )
                keep_paths = overlap_ratio.loc[overlap_ratio >= 0.5].index
                keep_ids = paths.loc[paths.path.isin(keep_paths)].NHDPlusID.unique()

            print(f"adding {len(keep_ids):,} filler lines between disconnected upstream and downstream habitat")

            # DEBUG:
            write_dataframe(
                flowlines.loc[flowlines.index.isin(keep_ids)].reset_index(),
                f"/tmp/{unit}_filler.fgb",
            )

            keep_line_ids = np.unique(np.concatenate([keep_line_ids, keep_ids]))
            pairs = pairs.loc[~pairs.NHDPlusID.isin(keep_ids)].copy()

    #########################################
    flowlines[unit] = flowlines.index.isin(keep_line_ids)
    if spp_df.anadromous.iloc[0]:
        flowlines.loc[flowlines[unit], "streamnet_anadromous_habitat"] = True

    print(
        f"species habitat: {shapely.length(spp_df.geometry.values).sum() / 1000:,.1f} km; "
        f" extracted {spp_flowlines.loc[spp_flowlines.index.isin(keep_line_ids), ['length']].values.sum() / 1000:,.1f} km from NHD"
    )

    write_dataframe(
        spp_flowlines.loc[spp_flowlines.index.isin(keep_line_ids)].reset_index(),
        f"/tmp/{unit}_keep_lines.fgb",
    )

out = flowlines.loc[
    flowlines[units].any(axis=1),
    ["geometry", "HUC2", "streamnet_anadromous_habitat"] + units,
].reset_index()
out = out.rename(columns={c: f"{c.lower().replace(' ', '_')}_habitat" for c in units})

write_dataframe(out, out_dir / "streamnet_habitat.fgb")
out.drop(columns=["geometry"]).to_feather(out_dir / "streamnet_habitat.feather")
