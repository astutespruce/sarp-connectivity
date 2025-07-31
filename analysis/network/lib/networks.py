from pathlib import Path
from time import time
import warnings

import pandas as pd
import pyarrow as pa
from pyarrow.dataset import dataset
import pyarrow.compute as pc
import numpy as np

from analysis.constants import HUC2_EXITS, NETWORK_TYPES, EPA_CAUSE_TO_CODE

from analysis.lib.graph.speedups import DirectedGraph, LinearDirectedGraph
from analysis.lib.io import read_arrow_tables
from analysis.network.lib.stats import (
    calculate_upstream_functional_network_stats,
    calculate_upstream_mainstem_network_stats,
    calculate_downstream_mainstem_network_stats,
    calculate_downstream_linear_network_stats,
)

pd.set_option("future.no_silent_downcasting", True)
warnings.filterwarnings("ignore", message=".*DataFrame is highly fragmented.*")

MAINSTEM_DRAINAGE_AREA = 2.58999  # (one square mile)

# Core flowline attributes used for network stats
FLOWLINE_COLS = [
    "NHDPlusID",
    "intermittent",
    "altered",
    "waterbody",
    "sizeclass",
    "length",
    "AreaSqKm",
    "TotDASqKm",
    "StreamOrder",
]

MAINSTEM_FLOWLINE_COLUMNS = [
    "lineID",
    "NHDPlusID",
    "length",
    "free_flowing",
    "altered",
    "intermittent",
    "sizeclass",
] + list(EPA_CAUSE_TO_CODE)


data_dir = Path("data")


def connect_huc2s(joins):
    """Find all connected groups of HUC2s.

    This reads in all flowline joins for all HUC2s and detects those that cross
    HUC2 boundaries to determine which HUC2s are connected.

    Region 03 is specifically prevented from connecting to 08.

    Parameters
    ----------
    joins : DataFrame
        contains HUC2, downstream_id, upstream_id, downstream, type

    Returns
    -------
    (groups, joins)
        groups: list of sets; each set contains one or more HUC2s
        joins: updated joins across HUC2 boundaries
    """

    ### Extract the joins that cross region boundaries, and set new upstream IDs for them
    # We can join on the ids we generate (upstream_id, downstream_id) because there are no
    # original flowlines split at HUC2 join areas
    # Note: we drop connections from region 03 into 08; these are negligible with respect
    # to results but avoids lumping already very large analysis regions

    cross_region = joins.loc[
        (joins.type == "huc_in") & (joins.upstream_id == 0),
        ["upstream", "downstream", "downstream_id", "type", "HUC2"],
    ].rename(columns={"HUC2": "downstream_HUC2"})

    cross_region = cross_region.join(
        joins.loc[
            joins.downstream.isin(cross_region.upstream) & (joins.HUC2 != "03"),
            ["downstream", "downstream_id", "HUC2"],
        ]
        .set_index("downstream")
        .rename(columns={"downstream_id": "upstream_id", "HUC2": "upstream_HUC2"}),
        on="upstream",
        how="inner",
    ).drop_duplicates()

    # update joins to include those that cross region boundaries
    joins = joins.join(
        # upstream side of join
        cross_region[["upstream_id", "downstream", "downstream_id"]].set_index("upstream_id"),
        on="upstream_id",
        rsuffix="_new_upstream",
    ).join(
        # downstream side of join
        cross_region[["downstream_id", "upstream_id"]].set_index("downstream_id"),
        on="downstream_id",
        rsuffix="_new_downstream",
    )

    # update upstream side
    ix = joins.downstream_id_new_upstream.notnull()
    tmp = joins.loc[ix]
    joins.loc[ix, "downstream"] = tmp.downstream_new_upstream.astype(joins.downstream.dtype)
    joins.loc[ix, "downstream_id"] = tmp.downstream_id_new_upstream.astype(joins.downstream_id.dtype)
    joins.loc[ix, "type"] = "huc2_join"

    # update downstream side
    ix = joins.upstream_id_new_downstream.notnull() & (joins.upstream_id == 0)
    joins.loc[ix, "upstream_id"] = joins.loc[ix].upstream_id_new_downstream.astype(joins.upstream_id.dtype)

    joins = joins.drop(
        columns=[
            "downstream_new_upstream",
            "downstream_id_new_upstream",
            "upstream_id_new_downstream",
        ]
    )

    joins = joins.drop_duplicates(subset=["downstream_id", "upstream_id"]).copy()

    # add information about the HUC2 drain points
    huc2_exits = set()
    for exits in HUC2_EXITS.values():
        huc2_exits.update(exits)

    joins.loc[(joins.downstream == 0) & joins.upstream.isin(huc2_exits), "type"] = "huc2_drain"

    # make symmetric pairs of HUC2s so that we get all those that are connected
    tmp = cross_region[["upstream_HUC2", "downstream_HUC2"]]
    source = np.append(tmp.upstream_HUC2, tmp.downstream_HUC2)
    target = np.append(tmp.downstream_HUC2, tmp.upstream_HUC2)

    # Create a graph to coalesce into connected components
    # Note: these are temporarily converted to int64 to use DirectedGraph
    g = DirectedGraph(source.astype("int64"), target.astype("int64"))
    connected_huc2 = g.components()

    # convert back to strings
    connected_huc2 = [{f"{huc2:02}" for huc2 in group} for group in connected_huc2]

    isolated_huc2 = [
        {huc2}
        for huc2 in np.setdiff1d(
            joins.HUC2.unique(),
            np.unique(np.append(cross_region.upstream_HUC2, cross_region.downstream_HUC2)),
        )
    ]

    return (connected_huc2 + isolated_huc2), joins


def load_flowlines(huc2s):
    """Load flowlines and associated fields that are joined at the lineID / NHDPlusID level

    Parameters
    ----------
    huc2s : list-like of str
        HUC2s to load

    Returns
    -------
    DataFrame
    """
    flowlines = read_arrow_tables(
        [data_dir / "networks/raw" / huc2 / "flowlines.feather" for huc2 in huc2s],
        columns=[
            "lineID",
        ]
        + FLOWLINE_COLS,
        new_fields={"HUC2": huc2s},
        dict_fields={"HUC2"},
    )

    flowlines = flowlines.append_column(
        "free_flowing", pc.if_else(pc.and_(flowlines["waterbody"], flowlines["altered"]), False, True)
    )

    # floodplain stats join on NHDPlusID
    floodplain_stats = dataset(data_dir / "floodplains" / "floodplain_stats.feather", format="feather").to_table(
        filter=pc.field("HUC2").isin(huc2s),
        columns=["NHDPlusID", "floodplain_km2", "nat_floodplain_km2"],
    )

    # TNC resilient / cold join on NHDPlusID
    resilient = dataset(
        data_dir / "tnc_resilience/derived/tnc_resilient_flowlines.feather",
        format="feather",
    ).to_table(filter=pc.field("HUC2").isin(huc2s), columns=["NHDPlusID", "resilient", "cold"])

    # Species habitat fields join on NHDPlusID
    habitat_dataset = dataset(data_dir / "species/derived/combined_species_habitat.feather", format="feather")
    habitat_cols = [c for c in habitat_dataset.schema.names if c not in {"HUC2", "NHDPlusID"}]
    habitat = habitat_dataset.to_table(filter=pc.field("HUC2").isin(huc2s), columns=["NHDPlusID"] + habitat_cols)
    # drop any columns not present in this set of HUC2s
    habitat_cols = [col for col in habitat_cols if pc.any(habitat[col]).as_py()]
    habitat = habitat.select(["NHDPlusID"] + habitat_cols)

    # environmental justice joins on NHDPlusID
    environmental_justice = dataset(
        data_dir / "boundaries/derived/environmental_justice_flowlines.feather",
        format="feather",
    ).to_table(filter=pc.field("HUC2").isin(huc2s), columns=["NHDPlusID", "EJTract", "EJTribal"])

    # EPA impairments join on NHDPlusID
    epa = dataset(
        data_dir / "epa/derived/epa_flowlines.feather",
        format="feather",
    ).to_table(filter=pc.field("HUC2").isin(huc2s), columns=["NHDPlusID"] + list(EPA_CAUSE_TO_CODE.keys()))

    flowlines = (
        flowlines.join(floodplain_stats, "NHDPlusID")
        .join(resilient, "NHDPlusID")
        .join(habitat, "NHDPlusID")
        .join(environmental_justice, "NHDPlusID")
        .join(epa, "NHDPlusID")
        .combine_chunks()
    )

    # fill nulls and set smaller dtypes
    out = {}
    for col in flowlines.column_names:
        out[col] = flowlines[col]

        if col in ["floodplain_km2", "nat_floodplain_km2"]:
            out[col] = pc.cast(pc.fill_null(flowlines[col], 0), pa.float32())
        elif col in ["resilient", "cold", "EJTract", "EJTribal"] + habitat_cols + list(EPA_CAUSE_TO_CODE.keys()):
            out[col] = pc.fill_null(flowlines[col], False)
        elif col == "sizeclass":
            # set sizeclass blanks to null (prevents counting it with other size classes) and set to categorical type
            # TODO: do this in cut_flowlines instead
            # NOTE: values not present in values list are set to null
            # not sure why this is so slow
            # TODO: this can be skipped altogether if keeping flowlines as a table, since pyarrow string type is efficient
            values = pa.array(["1a", "1b", "2", "3a", "3b", "4", "5"])
            out[col] = pa.DictionaryArray.from_arrays(
                pc.cast(pc.index_in(flowlines["sizeclass"], values), pa.int8()),
                values,
            )

    flowlines = pa.Table.from_pydict(out)

    return flowlines.to_pandas().set_index("lineID")


def coalesce_multiple_upstream_networks(up_network_df, joins, flowlines):
    """Coalesce networks that originate at same location (same barrier or network outlet)
    by setting all to the networkID of the largest drainage area / stream order.

    Note: This intentionally does not try to fuse sibling networks at a
    downstream-most origin point (downstream_id==0).


    Parameters
    ----------
    up_network_df : DataFrame
        upstream network DataFrame
    joins : DataFrame
        contains upstream_id, downstream_id
    flowlines : DataFrame
        flowline within analysis area, indexed on lineID

    Returns
    -------
    DataFrame
        same structure as up_network_df, with networkIDs updated for networks that
        were coalesced
    """
    # find all networks where the downstream side of the network origin is a junction
    networks_at_junctions = np.intersect1d(
        up_network_df.networkID.unique(), joins.loc[joins.junction].upstream_id.unique()
    )
    if len(networks_at_junctions):
        print(
            f"Merging multiple upstream networks at network junctions, affects {len(networks_at_junctions):,} networks"
        )
        up_network_df = up_network_df.join(flowlines[["TotDASqKm", "StreamOrder"]], on="lineID")

        downstreams = joins.loc[joins.upstream_id.isin(networks_at_junctions)].downstream_id.unique()
        for downstream_id in downstreams:
            # find all the networks that have the same downstream and fuse them
            # sort to preserve the one with largest drainage area / stream order
            networkIDs = (
                up_network_df.loc[
                    up_network_df.networkID.isin(joins.loc[joins.downstream_id == downstream_id].upstream_id)
                ]
                .groupby("networkID")
                .agg({"TotDASqKm": "max", "StreamOrder": "max"})
                .sort_values(by=["TotDASqKm", "StreamOrder"], ascending=False)
                .index.values
            )
            # use the networkID with longest number of segments as out networkID
            networkID = networkIDs[0]
            up_network_df.loc[up_network_df.networkID.isin(networkIDs), "networkID"] = networkID

        up_network_df = up_network_df.drop(columns=["TotDASqKm", "StreamOrder"])

    return up_network_df


def create_networks(joins, barrier_joins, flowlines):
    """Create 4 types of networks:
    - upstream functional networks that start from natural origins in network or from barriers
    - upstream mainstem networks that start from barriers
    - downstream mainstem networks that start from barriers
    - downstream linear networks that start from barriers


    Mainstems have >= 1 sq mile drainage area and are limited to joins of the same stream order.
    This avoids smaller incoming tributaries on the upstream side and confluences
    that result in a larger stream order on the downstream side.

    Parameters
    ----------
    joins : DataFrame
        contains upstream_id, downstream_id
    barrier_joins : DataFrame
        contains upstream_id, downstream_id; indexed on id
    flowlines : DataFrame
        flowline within analysis area, indexed on lineID

    Returns
    -------
    (Series, Series, Series, Series)
        (upstream functional network, upstream mainstem network, downstream mainstem network, downstream linear network)
        where each contains is indexed on lineID and haves values for networkID
    """

    lineIDs = flowlines.index
    mainstem_ids = flowlines.loc[(flowlines.TotDASqKm >= MAINSTEM_DRAINAGE_AREA)].index.values

    barrier_upstream_ids = barrier_joins.loc[barrier_joins.upstream_id != 0].upstream_id.unique()
    barrier_downstream_ids = barrier_joins.loc[barrier_joins.downstream_id != 0].downstream_id.unique()
    mainstem_barrier_upstream_ids = barrier_joins.loc[barrier_joins.upstream_id.isin(mainstem_ids)].upstream_id.unique()
    mainstem_barrier_downstream_ids = barrier_joins.loc[
        barrier_joins.downstream_id.isin(mainstem_ids)
    ].downstream_id.unique()

    ### Extract flowline joins for network traversal and break at barriers
    # Note: this drop any that are endpoints of the network
    interior_joins = (
        joins.loc[(joins.upstream_id != 0) & (joins.downstream_id != 0)]
        .join(
            flowlines[["StreamOrder", "TotDASqKm"]].rename(
                columns={"StreamOrder": "downstream_streamorder", "TotDASqKm": "downstream_drainage_km2"}
            ),
            on="downstream_id",
        )
        .join(
            flowlines[["StreamOrder", "TotDASqKm"]].rename(
                columns={"StreamOrder": "upstream_streamorder", "TotDASqKm": "upstream_drainage_km2"}
            ),
            on="upstream_id",
        )
    )

    interior_joins["mainstem"] = (
        (interior_joins.upstream_drainage_km2 >= MAINSTEM_DRAINAGE_AREA)
        & (interior_joins.downstream_drainage_km2 >= MAINSTEM_DRAINAGE_AREA)
        & (interior_joins.upstream_streamorder == interior_joins.downstream_streamorder)
    )

    upstream_joins = interior_joins.loc[
        ~interior_joins.upstream_id.isin(barrier_upstream_ids),
        ["downstream_id", "upstream_id", "mainstem"],
    ].drop_duplicates()

    downstream_joins = interior_joins.loc[
        ~interior_joins.downstream_id.isin(barrier_downstream_ids),
        ["downstream_id", "upstream_id", "mainstem"],
    ].drop_duplicates(subset=["downstream_id", "upstream_id"])

    ### Find network origins
    # find joins that are not marked as terminated, but do not have upstreams in the region;
    # this happens for flowlines that extend into CAN / MEX
    unterminated = joins.loc[(joins.downstream_id != 0) & ~joins.downstream_id.isin(joins.upstream_id)]

    origin_ids = np.concatenate(
        [
            # anything that has no downstream is an origin
            joins.loc[joins.downstream_id == 0].upstream_id.unique(),
            # if downstream_id is not in upstream_id for region, and is in flowlines, add downstream id as origin
            unterminated.loc[unterminated.downstream_id.isin(lineIDs)].downstream_id.unique(),
            # otherwise add upstream id
            unterminated.loc[~unterminated.downstream_id.isin(lineIDs)].upstream_id.unique(),
        ]
    )
    # remove any origins that have associated barriers (this also ensures a unique list)
    origin_ids = np.setdiff1d(origin_ids, barrier_upstream_ids)

    ### Create a directed graph facing upstream and traverse joins to create
    # origin networks and barrier networks
    upstream_graph = DirectedGraph(
        upstream_joins.downstream_id.values.astype("int64"),
        upstream_joins.upstream_id.values.astype("int64"),
    )

    print(f"Generating networks for {len(origin_ids):,} origin points")
    if len(origin_ids) > 0:
        origin_network_segments = pd.DataFrame(
            upstream_graph.network_pairs(origin_ids.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")
        origin_network_segments = coalesce_multiple_upstream_networks(origin_network_segments, joins, flowlines)

    else:
        origin_network_segments = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    print(f"Generating networks for {len(barrier_upstream_ids):,} barriers")
    if len(barrier_upstream_ids):
        # barrier segments are the root of each upstream network from each barrier
        # segments are indexed by the id of the segment at the root for each network
        barrier_network_segments = pd.DataFrame(
            upstream_graph.network_pairs(barrier_upstream_ids.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")
        barrier_network_segments = coalesce_multiple_upstream_networks(barrier_network_segments, joins, flowlines)

    else:
        barrier_network_segments = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    del upstream_graph

    # Append network types together
    origin_network_segments["type"] = "origin"
    barrier_network_segments["type"] = "barrier"
    up_network_df = pd.concat(
        [
            origin_network_segments,
            barrier_network_segments,
        ],
        sort=False,
        ignore_index=False,
    ).reset_index(drop=True)

    # check for duplicates
    s = up_network_df.groupby("lineID").size()
    s = s.loc[s > 1]
    if len(s):
        s.rename("count").reset_index().to_feather("/tmp/dup_networks.feather")
        raise ValueError(
            f"lineIDs are found in multiple networks: {', '.join([str(v) for v in s.index.values.tolist()[:10]])}..."
        )

    ### Extract mainstem networks
    # NOTE: mainstem networks are only calculated for barriers, not origins
    print("Extracting mainstem barrier networks")

    if len(mainstem_barrier_upstream_ids):
        upstream_mainstem_joins = upstream_joins.loc[upstream_joins.mainstem]

        upstream_mainstem_graph = DirectedGraph(
            upstream_mainstem_joins.downstream_id.values.astype("int64"),
            upstream_mainstem_joins.upstream_id.values.astype("int64"),
        )

        up_mainstem_network_df = pd.DataFrame(
            upstream_mainstem_graph.network_pairs(mainstem_barrier_upstream_ids.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")
        up_mainstem_network_df = coalesce_multiple_upstream_networks(up_mainstem_network_df, joins, flowlines)

        del upstream_mainstem_graph

        # check for duplicates
        s = up_mainstem_network_df.groupby("lineID").size()
        s = s.loc[s > 1]
        if len(s):
            s.rename("count").reset_index().to_feather("/tmp/dup_up_mainstem_networks.feather")
            raise ValueError(
                f"lineIDs are found in multiple upstream mainstem networks: {', '.join([str(v) for v in s.index.values.tolist()[:10]])}..."
            )
    else:
        up_mainstem_network_df = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    if len(mainstem_barrier_downstream_ids):
        downstream_mainstem_joins = downstream_joins.loc[downstream_joins.mainstem]

        downstream_mainstem_graph = LinearDirectedGraph(
            downstream_mainstem_joins.upstream_id.values.astype("int64"),
            downstream_mainstem_joins.downstream_id.values.astype("int64"),
        )

        down_mainstem_network_df = pd.DataFrame(
            downstream_mainstem_graph.network_pairs(mainstem_barrier_downstream_ids.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")

        del downstream_mainstem_graph
    else:
        down_mainstem_network_df = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    ### Extract linear networks facing downstream
    # This assumes that there are no divergences because loops are removed
    # from the joins
    # NOTE: it is expected that a given lineID will be claimed as a downstream
    # of many downstream networks.
    print("Extracting downstream linear networks for each barrier")

    if len(barrier_downstream_ids):
        downstream_graph = LinearDirectedGraph(
            downstream_joins.upstream_id.values.astype("int64"),
            downstream_joins.downstream_id.values.astype("int64"),
        )

        down_network_df = pd.DataFrame(
            downstream_graph.network_pairs(barrier_downstream_ids.astype("int64")),
            columns=["networkID", "lineID"],
        ).astype("uint32")

    else:
        down_network_df = pd.DataFrame([], columns=["networkID", "lineID"]).astype("uint32")

    return (
        up_network_df.set_index("lineID").networkID,
        up_mainstem_network_df.set_index("lineID").networkID,
        down_mainstem_network_df.set_index("lineID").networkID,
        down_network_df.set_index("lineID").networkID,
    )


def create_barrier_networks(
    barriers,
    barrier_joins,
    focal_barrier_joins,
    joins,
    flowlines,
    network_segments,
    network_type,
    huc2s,
):
    """Calculate networks based on barriers and network origins

    Parameters
    ----------
    barriers : DataFrame
        barrier info for all barriers within the HUC2 group to joined back to
        barrier networks (inner join)
    barrier_joins : DataFrame
        all barriers joins within the HUC2 group (all types)
    focal_barrier_joins : DataFrame
        barrier joins that denote network breaks
    joins : DataFrame
        all joins within the HUC2 group, used as the basis for constructing the
        networks
    flowlines : DataFrame
        flowline info that gets joined to the networkID for this type
    network_segments : DataFrame
        data frame to accumulate assignments of flowlines to networks, must
        have same index as flowlines
    network_type : str
        name of network network_type, one of NETWORK_TYPES keys
    huc2s : list-lie of str
        list of HUC2s for this subset of data

    Returns
    -------
    (DataFrame, DataFrame, DataFrame, DataFrame, DataFrame, DataFrame, DataFrame)
        tuple of (
            barrier_networks, network_stats, network_segments,
            downstream_mainstem_network, downstream_mainstem_network_stats,
            downstream_linear_network, downstream_linear_network_stats
        )
    """
    network_start = time()

    upstream_networks, upstream_mainstem_networks, downstream_mainstem_networks, downstream_linear_networks = (
        create_networks(
            joins,
            focal_barrier_joins,
            flowlines,
        )
    )

    print(f"{len(upstream_networks.unique()):,} networks created in {time() - network_start:.2f}s")

    # join networkID to flowlines
    # NOTE: can't join either type of downstream network here because a given
    # flowline may be shared between downstream networks of multiple barriers
    network_segments = network_segments.join(upstream_networks.rename(network_type)).join(
        upstream_mainstem_networks.rename(f"{network_type}_mainstem")
    )

    # any segment that wasn't assigned to a network can use its lineID as its network
    # assume that these are isolated segments whose upstream / downstreams were
    # removed because they were loops
    ix = network_segments[network_type].isnull()
    if ix.sum() > 0:
        print(f"Backfilling {ix.sum():,} flowlines that weren't assigned to a network")
        network_segments.loc[ix, network_type] = network_segments.loc[ix].index.values
        network_segments[network_type] = network_segments[network_type].astype("uint32")

    # TODO: create this a pyarrow Table instead
    up_network_df = (
        network_segments[[network_type]]
        .rename(columns={network_type: "networkID"})
        .reset_index()
        .set_index("networkID")
        .join(flowlines, on="lineID")
    )

    # For any barriers that had multiple upstreams, those were coalesced to a single network above
    # So drop any dangling upstream references (those that are not in networks and non-zero)
    # NOTE: these are not persisted because we want the original barrier_joins to reflect multiple upstreams
    # FIXME: we stopped doing this, make sure we're deduplicating below where necessary
    # focal_barrier_joins = focal_barrier_joins.loc[
    #     focal_barrier_joins.upstream_id.isin(upstream_networks.unique()) | (focal_barrier_joins.upstream_id == 0)
    # ].copy()

    ### Calculate network statistics
    print("Calculating network stats...")

    stats_start = time()

    fn_network_flowlines = pa.Table.from_pandas(up_network_df)
    joins_table = pa.Table.from_pandas(joins)
    barrier_joins_table = pa.Table.from_pandas(barrier_joins)
    focal_barrier_joins_table = pa.Table.from_pandas(focal_barrier_joins)
    flowlines_table = pa.Table.from_pandas(flowlines)

    # FIXME: this is now a table
    upstream_functional_network_stats = calculate_upstream_functional_network_stats(
        fn_network_flowlines,
        joins_table,
        focal_barrier_joins_table,
        barrier_joins_table,
    )

    up_mainstem_networks_table = pa.Table.from_pandas(upstream_mainstem_networks.reset_index())
    # NOTE: joining flowines to networks is MUCH faster than networks to flowlines
    up_mainstem_network_flowlines = (
        flowlines_table.select(MAINSTEM_FLOWLINE_COLUMNS)
        .join(up_mainstem_networks_table, "lineID", join_type="inner")
        .combine_chunks()
    )
    # FIXME: this is now a table
    upstream_mainstem_network_stats = calculate_upstream_mainstem_network_stats(up_mainstem_network_flowlines)

    # create deduplicated tables of barriers and their downstream lineIDs because
    # a given barrier may have multiple upstreams and thus multiple joins
    focal_barrier_downstreams_table = (
        focal_barrier_joins_table.filter(pc.not_equal(focal_barrier_joins_table["downstream_id"], 0))
        .select(["id", "kind", "invasive", "downstream_id"])
        .group_by("id", use_threads=False)
        .aggregate([("kind", "first"), ("invasive", "first"), ("downstream_id", "first")])
        # the downstream_id is the downstream mainstem / linear network
        .rename_columns({"kind_first": "kind", "invasive_first": "invasive", "downstream_id_first": "networkID"})
    )

    down_mainstem_networks_table = pa.Table.from_pandas(downstream_mainstem_networks.reset_index())
    down_mainstem_network_flowlines = (
        flowlines_table.select(MAINSTEM_FLOWLINE_COLUMNS)
        .join(down_mainstem_networks_table, "lineID", join_type="inner")
        .combine_chunks()
    )
    # FIXME: this is now a table
    downstream_mainstem_network_stats = calculate_downstream_mainstem_network_stats(
        down_mainstem_network_flowlines, focal_barrier_downstreams_table
    )

    downstream_linear_networks_table = pa.Table.from_pandas(downstream_linear_networks.reset_index())
    downstream_linear_network_flowlines = flowlines_table.select(
        ["lineID", "length", "free_flowing", "intermittent", "altered"]
    ).join(downstream_linear_networks_table, "lineID", join_type="inner")
    # FIXME: this is now a table
    downstream_linear_network_stats = calculate_downstream_linear_network_stats(
        downstream_linear_network_flowlines,
        focal_barrier_joins_table,
        barrier_joins_table,
        focal_barrier_downstreams_table,
    )

    # find nearest upstream barrier id, type, and distance based on the downstream
    # linear networks in the functional network for a given barrier
    nearest_upstream_barrier = (
        up_network_df[["lineID"]]
        .join(
            downstream_linear_network_stats[["total_linear_downstream_miles"]]
            .join(focal_barrier_joins[["kind", "downstream_id"]])
            .reset_index()
            .set_index("downstream_id")
            .rename(
                columns={
                    "id": "upstream_barrier_id",
                    "kind": "upstream_barrier",
                    "total_linear_downstream_miles": "upstream_barrier_miles",
                }
            ),
            on="lineID",
            how="inner",
        )
        .sort_values(by="upstream_barrier_miles", ascending=True)
        .groupby(level=0)[["upstream_barrier_id", "upstream_barrier_miles", "upstream_barrier"]]
        .first()
    )

    ### Join upstream network stats to downstream network stats
    # NOTE: a network will only have downstream stats if it is upstream of a
    # barrier
    network_stats = (
        upstream_functional_network_stats.join(upstream_mainstem_network_stats)
        .join(nearest_upstream_barrier)
        .join(downstream_mainstem_network_stats.join(focal_barrier_joins.upstream_id).set_index("upstream_id"))
        .join(downstream_linear_network_stats.join(focal_barrier_joins.upstream_id).set_index("upstream_id"))
    )

    # Fill missing data
    for col in ["barrier_id", "upstream_barrier_id", "downstream_barrier_id"]:
        network_stats[col] = network_stats[col].fillna(0).astype("uint64")

    for kind in ["waterfalls", "dams", "small_barriers", "road_crossings"]:
        col = f"totd_{kind}"
        network_stats[col] = network_stats[col].fillna(0).astype("uint32")

    for col in ["flows_to_ocean", "flows_to_great_lakes", "invasive_network", "has_ej_tract", "has_ej_tribal"]:
        network_stats[col] = network_stats[col].fillna(False).astype("bool")

    for col in ["sizeclasses", "perennial_sizeclasses", "mainstem_sizeclasses"]:
        network_stats[col] = network_stats[col].fillna(0).astype("uint8")

    for col in [
        "barrier",
        "upstream_barrier",
        "downstream_barrier",
        "upstream_mainstem_impairment",
        "downstream_mainstem_impairment",
    ]:
        network_stats[col] = network_stats[col].fillna("")

    for col in [
        c for c in network_stats.columns if c.endswith("_miles") or c.endswith("acres") or c.startswith("pct_")
    ] + [
        "miles_to_outlet",
    ]:
        network_stats[col] = network_stats[col].fillna(0).astype("float32")

    print(f"calculated stats in {time() - stats_start:.2f}s")

    #### Calculate up and downstream network attributes for barriers

    # NOTE: some statistics (totd_*, miles_to_outlet, flows_to_ocean, flows_to_great_lakes)
    # are evaluated from the upstream functional network (i.e., these are statistics)
    # downstream of the barrier associated with that functional network
    # WARNING: some barriers are on the upstream end or downstream end of the
    # total network and are missing either upstream or downstream network
    print("calculating upstream and downstream networks for barriers")

    # Exclude free-flowing metrics, those are only used on downstream functional networks
    # and we already know the barrier here (it is the index)
    upstream_functional_network_cols = [
        c
        for c in upstream_functional_network_stats.columns
        if not c.startswith("free_") and c not in {"barrier_id", "barrier"}
    ]
    upstream_networks = (
        focal_barrier_joins[["upstream_id"]]
        .join(
            upstream_functional_network_stats[upstream_functional_network_cols].rename(
                columns={c: c.replace("_miles", "_upstream_miles") for c in upstream_functional_network_cols}
            ),
            on="upstream_id",
        )
        .join(nearest_upstream_barrier, on="upstream_id")
        .join(
            upstream_mainstem_network_stats,
            on="upstream_id",
        )
    )
    # NOTE: by convention, barrier network stats are TitleCase when joined to barriers
    upstream_networks = upstream_networks.rename(
        columns={
            **{
                # standardize names before title-casing
                c: c.replace("sizeclasses", "size_classes")
                .replace("pct_", "percent_")
                .replace("fn_", "upstream_")
                .replace("tot_", "total_upstream_")
                .title()
                .replace("_", "")
                for c in upstream_networks.columns
            },
            "upstream_id": "upNetID",
            "origin_HUC2": "OriginHUC2",
            "natfldpln": "Landcover",
            "has_ej_tract": "HasUpstreamEJTract",
            "has_ej_tribal": "HasUpstreamEJTribal",
            "upstream_barrier_id": "UpstreamBarrierID",
        }
    )

    downstream_functional_network_cols = [
        c
        for c in upstream_functional_network_stats
        if (c.startswith("free_") or c in {"total_miles", "has_ej_tract", "has_ej_tribal"})
    ]
    downstream_networks = (
        # find the network that contains the segment immediately downstream of the barrier;
        # this is the downstream functional network
        focal_barrier_joins[["downstream_id"]]
        .join(
            up_network_df.reset_index().set_index("lineID").networkID,
            on="downstream_id",
        )
        .join(
            upstream_functional_network_stats[downstream_functional_network_cols].rename(
                columns={c: c.replace("_miles", "_downstream_miles") for c in downstream_functional_network_cols}
            ),
            on="networkID",
        )
        # downstream stats are indexed on barrier ID
        .join(downstream_mainstem_network_stats)
        .join(downstream_linear_network_stats)
        .drop(columns=["downstream_id"])
    )
    downstream_networks = downstream_networks.rename(
        columns={
            **{
                c: c.replace("totd_", "total_downstream_").title().replace("_", "") for c in downstream_networks.columns
            },
            "networkID": "downNetID",
            "has_ej_tract": "HasDownstreamEJTract",
            "has_ej_tribal": "HasDownstreamEJTribal",
            "downstream_barrier_id": "DownstreamBarrierID",
        }
    )

    # Note: the join creates duplicates if there are multiple upstream or downstream
    # networks for a given barrier, so we drop these duplicates after the join just to be sure
    # (after filling nulls or it doesn't work properly)
    barrier_networks = upstream_networks.join(downstream_networks).join(
        barriers[["kind", "HUC2"]].rename(columns={"kind": "barrier"})
    )

    # use SARPIDs for upstream / downstream barrier IDs
    for col in ["UpstreamBarrierID", "DownstreamBarrierID"]:
        barrier_networks[col] = barrier_networks[col].map(barriers.SARPID).fillna("")

    ### fill missing data
    # NOTE: upNetID or downNetID may be null if there aren't networks on that side
    for col in ["upNetID", "downNetID"]:
        barrier_networks[col] = barrier_networks[col].fillna(0).astype("uint32")

    for col in [
        c
        for c in barrier_networks
        if c.endswith("Miles") or c.endswith("Acres") or c.startswith("Percent") or c == "Landcover"
    ]:
        barrier_networks[col] = barrier_networks[col].fillna(0).astype("float32")

    for col in [
        "FlowsToOcean",
        "FlowsToGreatLakes",
        "InvasiveNetwork",
        "HasUpstreamEJTract",
        "HasUpstreamEJTribal",
        "HasDownstreamEJTract",
        "HasDownstreamEJTribal",
    ]:
        barrier_networks[col] = barrier_networks[col].fillna(False).astype("bool")

    for col in ["SizeClasses", "PerennialSizeClasses", "MainstemSizeClasses"]:
        barrier_networks[col] = barrier_networks[col].fillna(0).astype("uint8")

    for col in [
        "UpstreamBarrier",
        "DownstreamBarrier",
        "UpstreamMainstemImpairment",
        "DownstreamMainstemImpairment",
    ]:
        barrier_networks[col] = barrier_networks[col].fillna("")

    # if there is no upstream network, the network of a barrier is in the
    # same HUC2 as the barrier
    ix = barrier_networks.OriginHUC2.isnull()
    barrier_networks.loc[ix, "OriginHUC2"] = barrier_networks.loc[ix].HUC2

    barrier_networks.barrier = barrier_networks.barrier.fillna("")
    barrier_networks.OriginHUC2 = barrier_networks.OriginHUC2.fillna("")

    # if isolated network or connects to marine / Great Lakes / exit, there
    # are no further miles downstream from this network
    barrier_networks.MilesToOutlet = barrier_networks.MilesToOutlet.fillna(0).astype("float32")
    # total drainage area will be 0 for barriers at top of network
    barrier_networks.UpstreamDrainageAcres = barrier_networks.UpstreamDrainageAcres.fillna(0).astype("float32")

    # Set upstream and downstream count columns to 0 where nan; these are
    # for networks where barrier is at top of total network or bottom
    # of total network
    for stat_type in ["Upstream", "Total", "TotalDownstream"]:
        for t in [
            "Waterfalls",
            "Dams",
            "SmallBarriers",
            "RoadCrossings",
            "Headwaters",
        ]:
            col = f"{stat_type}{t}"
            if col in barrier_networks.columns:
                barrier_networks[col] = barrier_networks[col].fillna(0).astype("uint32")

    # drop any duplicates then copy to degragment data frame
    barrier_networks = barrier_networks.fillna(0).drop_duplicates().copy()

    ### Calculate miles GAINED if barrier is removed
    # this is the lesser of the upstream or free downstream lengths.
    # Non-free miles downstream (downstream waterbodies) are omitted from this analysis.

    # For barriers that flow directly into marine areas or Great Lakes
    # (no downstream barriers), their GainMiles is only based on the upstream miles
    # add count of downstream breaking barriers
    downstream_cols = [
        f"TotalDownstream{kind.title().replace('_', '')}s" for kind in NETWORK_TYPES[network_type]["kinds"]
    ]
    total_downstream_barriers = barrier_networks[downstream_cols].sum(axis=1).rename("TotalDownstreamBarriers")

    terminates_downstream_ix = (total_downstream_barriers == 0) & (
        (barrier_networks.FlowsToOcean == 1) | (barrier_networks.FlowsToGreatLakes)
    )

    total_network_miles = (
        barrier_networks[["TotalUpstreamMiles", "FreeDownstreamMiles"]].sum(axis=1).rename("FunctionalNetworkMiles")
    )
    # Calculate gain miles as minimum length of upstream and downstream sides
    gain_miles = barrier_networks[["TotalUpstreamMiles", "FreeDownstreamMiles"]].min(axis=1).rename("GainMiles")
    # if it terminates downstream only use upstream value
    gain_miles.loc[terminates_downstream_ix] = barrier_networks.loc[terminates_downstream_ix].TotalUpstreamMiles

    perennial_network_miles = (
        barrier_networks[["PerennialUpstreamMiles", "FreePerennialDownstreamMiles"]]
        .sum(axis=1)
        .rename("PerennialFunctionalNetworkMiles")
    )
    perennial_gain_miles = (
        barrier_networks[["PerennialUpstreamMiles", "FreePerennialDownstreamMiles"]]
        .min(axis=1)
        .rename("PerennialGainMiles")
    )
    perennial_gain_miles.loc[terminates_downstream_ix] = barrier_networks.loc[
        terminates_downstream_ix
    ].PerennialUpstreamMiles

    total_mainstem_network_miles = (
        barrier_networks[["TotalUpstreamMainstemMiles", "FreeDownstreamMainstemMiles"]]
        .sum(axis=1)
        .rename("MainstemNetworkMiles")
    )
    mainstem_gain_miles = (
        barrier_networks[["TotalUpstreamMainstemMiles", "FreeDownstreamMainstemMiles"]]
        .min(axis=1)
        .rename("MainstemGainMiles")
    )
    mainstem_gain_miles.loc[terminates_downstream_ix] = barrier_networks.loc[
        terminates_downstream_ix
    ].TotalUpstreamMainstemMiles

    perennial_mainstem_network_miles = (
        barrier_networks[["PerennialUpstreamMainstemMiles", "FreePerennialDownstreamMainstemMiles"]]
        .sum(axis=1)
        .rename("PerennialMainstemNetworkMiles")
    )
    perennial_mainstem_gain_miles = (
        barrier_networks[["PerennialUpstreamMainstemMiles", "FreePerennialDownstreamMainstemMiles"]]
        .min(axis=1)
        .rename("PerennialMainstemGainMiles")
    )
    perennial_mainstem_gain_miles.loc[terminates_downstream_ix] = barrier_networks.loc[
        terminates_downstream_ix
    ].PerennialUpstreamMainstemMiles

    other_stats = (
        pd.DataFrame(total_downstream_barriers)
        .join(total_network_miles)
        .join(gain_miles)
        .join(perennial_network_miles)
        .join(perennial_gain_miles)
        .join(total_mainstem_network_miles)
        .join(mainstem_gain_miles)
        .join(perennial_mainstem_network_miles)
        .join(perennial_mainstem_gain_miles)
    )
    barrier_networks = barrier_networks.join(other_stats)

    # Round floating point columns to 3 decimals
    for column in [c for c in barrier_networks.columns if c.endswith("Miles")]:
        barrier_networks[column] = barrier_networks[column].round(3).fillna(0)

    ### Round PercentUnaltered and PercentAltered to integers
    for subset in ["", "Perennial", "UpstreamMainstem"]:
        barrier_networks[f"Percent{subset}Unaltered"] = (
            barrier_networks[f"Percent{subset}Unaltered"].round().astype("int8")
        )
        barrier_networks[f"Percent{subset}Altered"] = 100 - barrier_networks[f"Percent{subset}Unaltered"]

    barrier_networks["PercentResilient"] = barrier_networks.PercentResilient.round().astype("int8")
    barrier_networks["PercentCold"] = barrier_networks.PercentCold.round().astype("int8")

    # assign downstream mainstem and linear networks to barrier IDs
    if len(focal_barrier_joins) > 0:
        downstream_mainstem_networks = (
            focal_barrier_joins[["downstream_id"]]
            .join(downstream_mainstem_networks.reset_index().set_index("networkID"), on="downstream_id", how="inner")
            .lineID.reset_index()
        )
        downstream_linear_networks = (
            focal_barrier_joins[["downstream_id"]]
            .join(downstream_linear_networks.reset_index().set_index("networkID"), on="downstream_id", how="inner")
            .lineID.reset_index()
        )
    else:
        downstream_mainstem_networks = pd.DataFrame([], columns=["id", "lineID"])
        downstream_linear_networks = pd.DataFrame([], columns=["id", "lineID"])

    return (
        barrier_networks,
        network_stats,
        network_segments,
        downstream_mainstem_networks,
        downstream_mainstem_network_stats,
        downstream_linear_networks,
        downstream_linear_network_stats,
    )
