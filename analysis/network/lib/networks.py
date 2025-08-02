from pathlib import Path
from time import time
import warnings

import pandas as pd
import pyarrow as pa
from pyarrow.dataset import dataset
import pyarrow.compute as pc
from pyarrow.feather import write_feather
import numpy as np

from analysis.constants import HUC2_EXITS, NETWORK_TYPES, EPA_CAUSE_TO_CODE, FLOWLINE_JOIN_TYPES

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


data_dir = Path("data")


def connect_huc2s(joins, huc2s):
    """Find all connected groups of HUC2s.

    This reads in all flowline joins for all HUC2s and detects those that cross
    HUC2 boundaries to determine which HUC2s are connected.

    Region 03 is specifically prevented from connecting to 08.

    Parameters
    ----------
    joins : DataFrame
        contains HUC2, downstream_id, upstream_id, downstream, type

    huc2s : list-like of str

    Returns
    -------
    (joins, groups)
    joins: updated joins across HUC2 boundaries
        groups: list of lists; each list contains one or more HUC2s
    """

    ### Extract the joins that cross region boundaries, and set new upstream IDs for them
    # We can join on the ids we generate (upstream_id, downstream_id) because there are no
    # original flowlines split at HUC2 join areas
    # NOTE: we drop connections from region 03 into 08; these are negligible with respect
    # to results but avoids lumping already very large analysis regions
    # NOTE: these join from the downstream NHDPlusID to the upstream NHDPlusID of joins from another region

    cross_region_upstream = (
        joins.select(["downstream", "downstream_id", "HUC2"])
        .filter(pc.not_equal(joins["HUC2"], "03"))
        .rename_columns({"downstream": "join_key", "downstream_id": "upstream_id", "HUC2": "upstream_HUC2"})
    )

    cross_region_downstream = (
        joins.filter(
            # we are specifically looking for ones marked as incoming to HUC and with no assigned upstream_id
            pc.and_(
                pc.and_(pc.equal(joins["type"], "huc_in"), pc.equal(joins["upstream_id"], 0)),
                # these don't go anywhere downstream, so drop them
                pc.not_equal(joins["downstream"], 0),
            ),
        )
        .select(["upstream", "downstream", "downstream_id", "type", "HUC2"])
        .rename_columns({"HUC2": "downstream_HUC2"})
    )

    cross_region = (
        cross_region_upstream.join(
            cross_region_downstream, "join_key", "upstream", coalesce_keys=False, join_type="inner"
        )
        .drop(["join_key"])
        .group_by(
            ["upstream", "upstream_id", "upstream_HUC2", "downstream", "downstream_id", "downstream_HUC2", "type"]
        )
        .aggregate([])
    )

    # something here is causing a lot of extra joins we shouldn't have
    # upstream_id 5246729 has many upstreams; this is unexpected (there should be only 1 upstream per upstream_id)
    joins = (
        joins.join(
            cross_region.select(["upstream_id", "downstream", "downstream_id"]).rename_columns(
                {"downstream": "downstream_new_upstream", "downstream_id": "downstream_id_new_upstream"}
            ),
            "upstream_id",
        )
        .join(
            cross_region.filter(pc.not_equal(cross_region["downstream_id"], 0))
            .select(["downstream_id", "upstream_id"])
            .rename_columns({"upstream_id": "upstream_id_new_downstream"}),
            "downstream_id",
        )
        .combine_chunks()
    )

    has_new_upstream = pc.is_valid(joins["downstream_id_new_upstream"]).combine_chunks()
    has_new_downstream = pc.and_(
        pc.is_valid(joins["upstream_id_new_downstream"]), pc.equal(joins["upstream_id"], 0)
    ).combine_chunks()

    # add information about the HUC2 drain points
    huc2_exits = set()
    for exits in HUC2_EXITS.values():
        huc2_exits.update(exits)
    huc2_exits = pa.array(huc2_exits)

    cols = ["upstream", "downstream", "type", "marine", "great_lakes", "HUC2"]
    joins = (
        pa.Table.from_pydict(
            {
                "upstream": joins["upstream"],
                "upstream_id": pc.if_else(
                    has_new_downstream, joins["upstream_id_new_downstream"], joins["upstream_id"]
                ),
                "downstream": pc.if_else(has_new_upstream, joins["downstream_new_upstream"], joins["downstream"]),
                "downstream_id": pc.if_else(
                    has_new_upstream, joins["downstream_id_new_upstream"], joins["downstream_id"]
                ),
                # mark new huc2 joins and drains
                "type": pc.if_else(
                    has_new_upstream,
                    "huc2_join",
                    pc.if_else(pc.is_in(joins["downstream"], huc2_exits), "huc2_drain", joins["type"]),
                ),
                "marine": joins["marine"],
                "great_lakes": joins["great_lakes"],
                "HUC2": joins["HUC2"],
            }
        )
        .group_by(["upstream_id", "downstream_id"], use_threads=False)
        .aggregate([(c, "first") for c in cols])
        .rename_columns({f"{c}_first": c for c in cols})
        .combine_chunks()
    )

    # make symmetric pairs of HUC2s so that we get all those that are connected
    # NOTE: we have to convert to strings for graph to work
    upstream_huc2 = pc.cast(cross_region["upstream_HUC2"], pa.int64()).combine_chunks()
    downstream_huc2 = pc.cast(cross_region["downstream_HUC2"], pa.int64()).combine_chunks()
    graph = DirectedGraph(
        pa.concat_arrays([upstream_huc2, downstream_huc2]).to_numpy().astype("int64"),
        pa.concat_arrays([downstream_huc2, upstream_huc2]).to_numpy().astype("int64"),
    )

    connected_huc2 = [[f"{huc2:02}" for huc2 in group] for group in graph.components()]
    all_connected_huc2 = set()
    for huc2_group in connected_huc2:
        all_connected_huc2 = all_connected_huc2.union(huc2_group)

    isolated_huc2 = [[huc2] for huc2 in set(huc2s).difference(all_connected_huc2)]

    return joins, sorted(connected_huc2 + isolated_huc2, key=lambda x: list(x)[0])


def load_flowlines(huc2s):
    """Load flowlines and associated fields that are joined at the lineID / NHDPlusID level

    Parameters
    ----------
    huc2s : list-like of str
        HUC2s to load

    Returns
    -------
    pyarrow Table
    """
    flowlines = read_arrow_tables(
        [data_dir / "networks/raw" / huc2 / "flowlines.feather" for huc2 in huc2s],
        columns=[
            "lineID",
            "NHDPlusID",
            "length",
            "intermittent",
            "altered",
            "waterbody",
            "sizeclass",
            "AreaSqKm",
            "TotDASqKm",
            "StreamOrder",
        ],
        new_fields={"HUC2": huc2s},
        dict_fields={"HUC2"},
    )

    # mark free flowing segments (must not be in altered waterbodies)
    flowlines = flowlines.append_column(
        "free_flowing", pc.if_else(pc.and_(flowlines["waterbody"], flowlines["altered"]), False, True)
    )

    # floodplain stats join on NHDPlusID
    floodplain_stats = (
        dataset(data_dir / "floodplains" / "floodplain_stats.feather", format="feather")
        .to_table(
            filter=pc.field("HUC2").isin(huc2s),
            columns=["NHDPlusID", "floodplain_km2", "nat_floodplain_km2"],
        )
        .combine_chunks()
    )

    # TNC resilient / cold join on NHDPlusID
    resilient = (
        dataset(
            data_dir / "tnc_resilience/derived/tnc_resilient_flowlines.feather",
            format="feather",
        )
        .to_table(filter=pc.field("HUC2").isin(huc2s), columns=["NHDPlusID", "resilient", "cold"])
        .combine_chunks()
    )

    # Species habitat fields join on NHDPlusID
    habitat_dataset = dataset(data_dir / "species/derived/combined_species_habitat.feather", format="feather")
    habitat_cols = [c for c in habitat_dataset.schema.names if c not in {"HUC2", "NHDPlusID"}]
    habitat = habitat_dataset.to_table(filter=pc.field("HUC2").isin(huc2s), columns=["NHDPlusID"] + habitat_cols)
    # drop any columns not present in this set of HUC2s
    habitat_cols = [col for col in habitat_cols if pc.any(habitat[col]).as_py()]
    habitat = habitat.select(["NHDPlusID"] + habitat_cols).combine_chunks()

    # environmental justice joins on NHDPlusID
    environmental_justice = (
        dataset(
            data_dir / "boundaries/derived/environmental_justice_flowlines.feather",
            format="feather",
        )
        .to_table(filter=pc.field("HUC2").isin(huc2s), columns=["NHDPlusID", "EJTract", "EJTribal"])
        .combine_chunks()
    )

    # EPA impairments join on NHDPlusID
    epa = (
        dataset(
            data_dir / "epa/derived/epa_flowlines.feather",
            format="feather",
        )
        .to_table(filter=pc.field("HUC2").isin(huc2s), columns=["NHDPlusID"] + list(EPA_CAUSE_TO_CODE.keys()))
        .combine_chunks()
    )

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

    flowlines = pa.Table.from_pydict(out)

    return flowlines


def coalesce_multiple_upstream_networks(network_segments, joins, flowlines):
    """Coalesce networks that originate at same location (same barrier or network outlet)
    by setting all to the networkID of the largest drainage area / stream order.

    Note: This intentionally does not try to fuse sibling networks at a
    downstream-most origin point (downstream_id==0).


    Parameters
    ----------
    network_segments : pyarrow Table
        contains networkID, lineID
    joins : pyarrow Table
        contains upstream_id, downstream_id
    flowlines : pyarrow Table
        flowlines within analysis area, contains lineID, TotDASqKm, StreamOrder

    Returns
    -------
    pyarrow Table
        same structure as network_segments, with networkIDs updated for networks that
        were coalesced
    """

    networks_at_junctions = (
        network_segments.select(["networkID"])
        .filter(pc.equal(network_segments["networkID"], network_segments["lineID"]))
        .join(
            joins.select(["upstream_id", "downstream_id"]).filter(joins["junction"]),
            "networkID",
            "upstream_id",
            join_type="inner",
        )
        .combine_chunks()
    )

    if len(networks_at_junctions):
        print(
            f"Merging multiple upstream networks at network junctions, affects {len(networks_at_junctions):,} networks"
        )

        # create mapping from downstream_id of the junctions to the networkID to retain
        new_networkIDs = (
            networks_at_junctions.join(flowlines.select(["lineID", "TotDASqKm", "StreamOrder"]), "networkID", "lineID")
            # sort to preserve the one with largest drainage area / stream order
            .sort_by([("downstream_id", "ascending"), ("TotDASqKm", "descending"), ("StreamOrder", "descending")])
            .group_by(["downstream_id"], use_threads=False)
            .aggregate([("networkID", "first")])
            .rename_columns({"networkID_first": "new_networkID"})
            .combine_chunks()
        )

        new_networkIDs = (
            joins.select(["upstream_id", "downstream_id"])
            .join(new_networkIDs, "downstream_id", join_type="inner")
            .filter(pc.field("upstream_id") != pc.field("new_networkID"))
            .combine_chunks()
            .select(["upstream_id", "new_networkID"])
            .rename_columns({"upstream_id": "prev_networkID"})
        )

        if len(new_networkIDs):
            network_segments = network_segments.join(new_networkIDs, "networkID", "prev_networkID")
            network_segments = pa.Table.from_pydict(
                {
                    "networkID": pc.if_else(
                        pc.is_valid(network_segments["new_networkID"]),
                        network_segments["new_networkID"],
                        network_segments["networkID"],
                    ),
                    "lineID": network_segments["lineID"],
                }
            ).combine_chunks()

    return network_segments


def create_functional_upstream_networks(
    joins,
    focal_barrier_joins,
    upstream_joins,
    flowlines,
):
    """Create upstream functional networks based on network breaks located at
    focal_barrier_joins

    Upstream functional networks are assigned a networkID based on the upstream_id
    at a given focal barrier join.

    Parameters
    ----------
    joins : pyarrow Table
        contains upstream_id, downstream_id
    focal_barrier_joins : pyarrow Table
        contains upstream_id, downstream_id
    upstream_joins : pyarrow Table
        subset of joins that exclude any joins where focal barriers are located
    flowlines : pyarrow Table
        contains lineID, TotDASqKm, StreamOrder

    Returns
    -------
    pyarrow Table
    """

    start = time()

    ### Find network terminals (roots of networks); we call them origins below
    # find joins that are not marked as terminated, but do not have downstreams in the region;
    # this happens for flowlines that extend into CAN / MEX
    unterminated = joins.filter(
        pc.and_(
            # not already a downstream terminal
            pc.not_equal(joins["downstream_id"], 0),
            # but corresponding upstream for this downstream side is not present in the joins
            pc.equal(pc.is_in(joins["downstream_id"], joins["upstream_id"]), False),
        )
    )

    origin_ids = pc.unique(
        pa.concat_arrays(
            [
                # anything that has no downstream is an origin
                joins.filter(pc.equal(joins["downstream_id"], 0))["upstream_id"].combine_chunks(),
                # if downstream_id is not in upstream_id for region, and is in flowlines, add downstream id as origin
                unterminated.filter(pc.is_in(unterminated["downstream_id"], flowlines["lineID"]))[
                    "downstream_id"
                ].combine_chunks(),
                # otherwise add upstream id
                unterminated.filter(pc.equal(pc.is_in(unterminated["downstream_id"], flowlines["lineID"]), False))[
                    "upstream_id"
                ].combine_chunks(),
            ]
        )
    )

    # remove any origins that have associated barriers (this also ensures a unique list)
    barrier_upstream_ids = pc.unique(
        focal_barrier_joins.filter(pc.not_equal(focal_barrier_joins["upstream_id"], 0))["upstream_id"]
    )
    origin_ids = origin_ids.filter(pc.equal(pc.is_in(origin_ids, barrier_upstream_ids), False))

    ### Create a directed graph facing upstream and traverse joins to create
    # origin networks and barrier networks
    upstream_graph = DirectedGraph(
        upstream_joins["downstream_id"].to_numpy().astype("int64"),
        upstream_joins["upstream_id"].to_numpy().astype("int64"),
    )

    print(f"Generating networks for {len(origin_ids):,} origin points")
    if len(origin_ids) > 0:
        origin_network_segments = pa.Table.from_arrays(
            upstream_graph.network_pairs(origin_ids.to_numpy().astype("int64")).T.astype("uint32"),
            ["networkID", "lineID"],
        )
        origin_network_segments = coalesce_multiple_upstream_networks(origin_network_segments, joins, flowlines)

    else:
        origin_network_segments = pa.Table.from_arrays(
            [[], []], schema=pa.schema([("networkID", pa.uint32()), ("lineID", pa.uint32())])
        )

    print(f"Generating networks for {len(barrier_upstream_ids):,} barriers")
    if len(barrier_upstream_ids):
        barrier_network_segments = pa.Table.from_arrays(
            upstream_graph.network_pairs(barrier_upstream_ids.to_numpy().astype("int64")).T.astype("uint32"),
            ["networkID", "lineID"],
        )
        barrier_network_segments = coalesce_multiple_upstream_networks(barrier_network_segments, joins, flowlines)

    else:
        barrier_network_segments = pa.Table.from_arrays(
            [[], []], schema=pa.schema([("networkID", pa.uint32()), ("lineID", pa.uint32())])
        )

    # use categorical type to store network type
    network_type_values = pa.array(["origin", "barrier"])
    origin_network_segments = origin_network_segments.append_column(
        "type",
        pa.DictionaryArray.from_arrays(np.repeat(np.int8(0), len(origin_network_segments)), network_type_values),
    )
    barrier_network_segments = barrier_network_segments.append_column(
        "type",
        pa.DictionaryArray.from_arrays(np.repeat(np.int8(1), len(barrier_network_segments)), network_type_values),
    )

    upstream_functional_network_segments = pa.concat_tables(
        [origin_network_segments, barrier_network_segments]
    ).combine_chunks()

    # check for duplicates
    dups = (
        upstream_functional_network_segments.group_by("lineID")
        .aggregate([("lineID", "count_distinct")])
        .rename_columns({"lineID_count_distinct": "count"})
        .filter(pc.field("count") > 1)
        .combine_chunks()
    )
    if len(dups):
        write_feather(dups, "/tmp/dup_upstream_functional_networks.feather")
        raise ValueError(
            f"{len(dups)} lineIDs are found in multiple networks: {', '.join([str(v) for v in dups['lineID'][:10].to_pylist()])}..."
        )

    print(
        f"{len(pc.unique(upstream_functional_network_segments['networkID'])):,} upstream functional networks created in {time() - start:.2f}s"
    )

    return upstream_functional_network_segments


def create_upstream_mainstem_networks(joins, focal_barrier_joins, upstream_joins, mainstem_flowlines):
    """Calcluate upstream mainstem networks.

    Mainstems have >= 1 sq mile drainage area and are limited to joins of the same stream order.
    This avoids smaller incoming tributaries on the upstream side and confluences
    that result in a larger stream order on the downstream side.

    Upstream mainstem networks are assigned a networkID based on the upstream_id
    at a given focal barrier join.

    Parameters
    ----------
    joins : pyarrow Table
        contains upstream_id, downstream_id
    focal_barrier_joins : pyarrow Table
        contains upstream_id, downstream_id
    upstream_joins : pyarrow Table
        subset of joins that exclude any joins where focal barriers are located
    mainstem_flowlines : pyarrow Table
        subset of flowlines for mainstems

    Returns
    -------
    pyarrow Table
    """
    start = time()

    # find barriers that are on large enough flowlines
    # NOTE: joining from mainstems is fastest
    mainstem_barrier_upstream_ids = (
        mainstem_flowlines.select(["lineID"])
        .join(focal_barrier_joins.select(["upstream_id"]), "lineID", "upstream_id", join_type="inner")["lineID"]
        .combine_chunks()
    )

    if len(mainstem_barrier_upstream_ids):
        print("Extracting upstream mainstem barrier networks")

        # find mainstem joins: must be on large enough flowline (drainage area) and same stream order on either side of join
        # WARNING: there are cases due to bad data from NHD where the downstream stream order may be less than the upstream,
        # which is not correct.  However, we still break at these to avoid issues traversing the mainstem networks
        upstream_mainstem_joins = (
            upstream_joins.join(
                mainstem_flowlines.rename_columns({"StreamOrder": "upstream_streamorder"}),
                "upstream_id",
                "lineID",
                join_type="inner",
            )
            .join(
                mainstem_flowlines.rename_columns({"StreamOrder": "downstream_streamorder"}),
                "downstream_id",
                "lineID",
            )
            .filter(pc.field("upstream_streamorder") == pc.field("downstream_streamorder"))
            .combine_chunks()
        )

        # create graph of mainstem joins facing in the upstream direction
        upstream_mainstem_graph = DirectedGraph(
            upstream_mainstem_joins["downstream_id"].to_numpy().astype("int64"),
            upstream_mainstem_joins["upstream_id"].to_numpy().astype("int64"),
        )

        upstream_mainstem_network_segments = pa.Table.from_arrays(
            upstream_mainstem_graph.network_pairs(mainstem_barrier_upstream_ids.to_numpy().astype("int64")).T.astype(
                "uint32"
            ),
            ["networkID", "lineID"],
        )
        upstream_mainstem_network_segments = coalesce_multiple_upstream_networks(
            upstream_mainstem_network_segments, joins, mainstem_flowlines
        )

        # check for duplicates
        dups = (
            upstream_mainstem_network_segments.group_by("lineID")
            .aggregate([("lineID", "count_distinct")])
            .rename_columns({"lineID_count_distinct": "count"})
            .filter(pc.field("count") > 1)
            .combine_chunks()
        )
        if len(dups):
            write_feather(dups, "/tmp/dup_upstream_mainstem_networks.feather")
            raise ValueError(
                f"{len(dups)} lineIDs are found in multiple networks: {', '.join([str(v) for v in dups['lineID'][:10].to_pylist()])}..."
            )

        del upstream_mainstem_graph

    else:
        upstream_mainstem_network_segments = pa.Table.from_arrays(
            [[], []], schema=pa.schema([("networkID", pa.uint32()), ("lineID", pa.uint32())])
        )

    print(
        f"{len(pc.unique(upstream_mainstem_network_segments['networkID'])):,} upstream mainstem networks created in {time() - start:.2f}s"
    )

    return upstream_mainstem_network_segments


def create_downstream_mainstem_networks(joins, focal_barrier_joins, downstream_joins, mainstem_flowlines):
    """Calculate downstream mainstem networks.

    See create_upstream_mainstem_networks for definition of mainstems.

    Downstream mainstem networks are in the downstream linear (flow) direction
    and are assigned networkID based on the downstream_id at a given focal barrier
    join.

    NOTE: mainstem networks are only calculated for barriers, not origins

    NOTE: there will be duplicate lineIDs in these networks because the same
    flowline may be shared in multiple downstream networks


    Parameters
    ----------
    joins : pyarrow Table
        contains upstream_id, downstream_id
    focal_barrier_joins : pyarrow Table
        contains upstream_id, downstream_id
    downstream_joins : pyarrow Table
        subset of joins that exclude any joins where focal barriers are located
    mainstem_flowlines : pyarrow Table
        subset of flowlines for mainstems

    Returns
    -------
    pyarrow Table
    """

    start = time()

    # NOTE: we have to use unique here since downstream_id occurs multiple times at barriers on confluences
    mainstem_barrier_downstream_ids = pc.unique(
        mainstem_flowlines.select(["lineID"])
        .join(focal_barrier_joins.select(["downstream_id"]), "lineID", "downstream_id", join_type="inner")["lineID"]
        .combine_chunks()
    )

    if len(mainstem_barrier_downstream_ids):
        print("Extracting downstream mainstem barrier networks")

        downstream_mainstem_joins = (
            downstream_joins.join(
                mainstem_flowlines.rename_columns({"StreamOrder": "downstream_streamorder"}),
                "downstream_id",
                "lineID",
                join_type="inner",
            )
            .join(
                mainstem_flowlines.rename_columns({"StreamOrder": "upstream_streamorder"}),
                "upstream_id",
                "lineID",
            )
            .filter(pc.field("upstream_streamorder") == pc.field("downstream_streamorder"))
            .combine_chunks()
        )

        # create linear graph facing in the downstream direction
        downstream_mainstem_graph = LinearDirectedGraph(
            downstream_mainstem_joins["upstream_id"].to_numpy().astype("int64"),
            downstream_mainstem_joins["downstream_id"].to_numpy().astype("int64"),
        )

        downstream_mainstem_network_segments = pa.Table.from_arrays(
            downstream_mainstem_graph.network_pairs(
                mainstem_barrier_downstream_ids.to_numpy().astype("int64")
            ).T.astype("uint32"),
            ["networkID", "lineID"],
        )

        del downstream_mainstem_graph

    else:
        downstream_mainstem_network_segments = pa.Table.from_arrays(
            [[], []], schema=pa.schema([("networkID", pa.uint32()), ("lineID", pa.uint32())])
        )

    print(
        f"{len(pc.unique(downstream_mainstem_network_segments['networkID'])):,} upstream mainstem networks created in {time() - start:.2f}s"
    )

    return downstream_mainstem_network_segments


def create_downstream_linear_networks(focal_barrier_joins, downstream_joins):
    """Create linear downstream networks

    NOTE: This assumes that there are no divergences because loops are removed
    from the joins

    NOTE: it is expected that a given lineID will be claimed as a downstream
    of many downstream networks.

    Parameters
    ----------
    focal_barrier_joins : pyarrow Table
        contains upstream_id, downstream_id
    downstream_joins : pyarrow Table
        subset of joins that exclude any joins where focal barriers are located

    Returns
    -------
    pyarrow Table
    """

    start = time()

    barrier_downstream_ids = pc.unique(
        focal_barrier_joins.filter(pc.not_equal(focal_barrier_joins["downstream_id"], 0))["downstream_id"]
    )

    if len(barrier_downstream_ids):
        print("Extracting downstream linear networks for each barrier")

        downstream_linear_graph = LinearDirectedGraph(
            downstream_joins["upstream_id"].to_numpy().astype("int64"),
            downstream_joins["downstream_id"].to_numpy().astype("int64"),
        )

        downstream_linear_network_segments = pa.Table.from_arrays(
            downstream_linear_graph.network_pairs(barrier_downstream_ids.to_numpy().astype("int64")).T.astype("uint32"),
            ["networkID", "lineID"],
        )

        del downstream_linear_graph

    else:
        downstream_linear_network_segments = pa.Table.from_arrays(
            [[], []], schema=pa.schema([("networkID", pa.uint32()), ("lineID", pa.uint32())])
        )

    print(
        f"{len(pc.unique(downstream_linear_network_segments['networkID'])):,} upstream mainstem networks created in {time() - start:.2f}s"
    )

    return downstream_linear_network_segments


def create_barrier_networks(
    barriers,
    barrier_joins,
    focal_barrier_joins,
    joins,
    flowlines,
    # FIXME: remove
    # network_segments,
    network_type,
):
    """Calculate networks based on barriers and network origins

    Parameters
    ----------
    barriers : pyarrow Table
        barrier info for all barriers within the HUC2 group to joined back to
        barrier networks (inner join)
    barrier_joins : pyarrow Table
        all barriers joins within the HUC2 group (all types)
    focal_barrier_joins : pyarrow Table
        barrier joins that denote network breaks
    joins : pyarrow Table
        all joins within the HUC2 group, used as the basis for constructing the
        networks
    flowlines : pyarrow Table
        flowline info that gets joined to the networkID for this type
    # FIXME: remove
    network_segments : pyarrow Table
        data frame to accumulate assignments of flowlines to networks
    network_type : str
        name of network network_type, one of NETWORK_TYPES keys

    Returns
    -------
    (DataFrame, DataFrame, DataFrame, DataFrame, DataFrame, DataFrame, DataFrame)
        tuple of (
            barrier_networks, network_stats, network_segments,
            downstream_mainstem_network, downstream_mainstem_network_stats,
            downstream_linear_network, downstream_linear_network_stats
        )
    """

    ############################################################################
    ### Prepare joins for network analysis
    ############################################################################

    # find joins that are interior to the network and not at upstream or downstream endpoints
    interior_joins = joins.filter(
        pc.and_(pc.not_equal(joins["upstream_id"], 0), pc.not_equal(joins["downstream_id"], 0))
    )

    # find upstream or downstream line IDs of barriers (depending on network direction)
    # and remove the associated joins before building the graph; this breaks the network at those barriers
    upstream_joins = interior_joins.join(
        focal_barrier_joins.select(["upstream_id"]).combine_chunks(),
        "upstream_id",
        # use anti-join to find interior joins that are NOT associated with a barrier
        # NOTE: this is much faster than checking membership in list of IDs
        join_type="left anti",
    ).combine_chunks()

    downstream_joins = interior_joins.join(
        focal_barrier_joins.select(["downstream_id"]).combine_chunks(),
        "downstream_id",
        join_type="left anti",
    ).combine_chunks()

    ############################################################################
    ### Create functional upstream networks
    ############################################################################
    upstream_functional_networks = create_functional_upstream_networks(
        joins, focal_barrier_joins, upstream_joins, flowlines
    )

    # find flowlines that qualify as mainstems due to drainage area
    mainstem_cols = [
        "lineID",
        "NHDPlusID",
        "length",
        "free_flowing",
        "altered",
        "intermittent",
        "sizeclass",
        "TotDASqKm",
        "StreamOrder",
    ] + list(EPA_CAUSE_TO_CODE)
    mainstem_flowlines = (
        flowlines.select(mainstem_cols)
        .filter(pc.greater_equal(flowlines["TotDASqKm"], MAINSTEM_DRAINAGE_AREA))
        .combine_chunks()
    )
    upstream_mainstem_networks = create_upstream_mainstem_networks(
        joins, focal_barrier_joins, upstream_joins, flowlines, mainstem_flowlines
    )
    downstream_mainstem_networks = create_downstream_mainstem_networks(
        joins, focal_barrier_joins, downstream_joins, mainstem_flowlines
    )

    downstream_linear_networks = create_downstream_linear_networks(focal_barrier_joins, downstream_joins)

    ############################################################################
    ### Calculate network statistics
    ############################################################################
    print("Calculating network stats...")

    stats_start = time()

    upstream_functional_network_flowlines = flowlines.join(upstream_functional_networks, "lineID").combine_chunks()
    upstream_functional_network_stats = calculate_upstream_functional_network_stats(
        upstream_functional_network_flowlines,
        joins,
        focal_barrier_joins,
        barrier_joins,
    )

    # NOTE: joining flowines to networks is faster than networks to flowlines
    # (for mainstems; for above, they are about the same)
    up_mainstem_network_flowlines = mainstem_flowlines.join(
        upstream_mainstem_networks, "lineID", join_type="inner"
    ).combine_chunks()
    upstream_mainstem_network_stats = calculate_upstream_mainstem_network_stats(up_mainstem_network_flowlines)

    # create the output index of barrier ID to downstream network ID based on a
    # deduplicated tables of focal barriers and their downstream lineIDs
    # (because a given barrier may have multiple upstreams and thus multiple joins)
    focal_barrier_downstreams = (
        focal_barrier_joins.filter(pc.not_equal(focal_barrier_joins["downstream_id"], 0))
        .rename_columns({"downstream_id": "networkID"})
        .select(["id", "kind", "networkID"])
        .group_by(["id", "kind", "networkID"])
        .aggregate([])
    )

    # down_mainstem_networks_table = pa.Table.from_pandas(downstream_mainstem_networks.reset_index())
    downstream_mainstem_network_flowlines = mainstem_flowlines.join(
        downstream_mainstem_networks, "lineID", join_type="inner"
    ).combine_chunks()
    downstream_mainstem_network_stats = calculate_downstream_mainstem_network_stats(
        downstream_mainstem_network_flowlines, focal_barrier_downstreams
    )

    downstream_linear_network_flowlines = flowlines.select(
        ["lineID", "length", "free_flowing", "intermittent", "altered", "EJTract", "EJTribal"]
    ).join(downstream_linear_networks, "lineID", join_type="inner")
    downstream_linear_network_stats, nearest_upstream_barriers = calculate_downstream_linear_network_stats(
        downstream_linear_network_flowlines,
        focal_barrier_joins,
        barrier_joins,
        focal_barrier_downstreams,
    )

    ### Join upstream network stats to downstream network stats
    # NOTE: a network will only have upstream mainstem stats and mainstem / linear
    # downstream stats if it is upstream of a barrier.  This means natural network
    # origins are not assigned a nearest upstream barrier
    # NOTE: any fields that are null at this point are intentionally null
    network_stats = (
        upstream_functional_network_stats.join(upstream_mainstem_network_stats, "networkID")
        .join(nearest_upstream_barriers, "barrier_id", "id")
        .join(downstream_mainstem_network_stats.drop(["networkID"]), "barrier_id", "id")
        .join(downstream_linear_network_stats.drop(["networkID"]), "barrier_id", "id")
        .combine_chunks()
    )

    # TODO: reorder fields
    # TODO: prefix results by network type: fn_, um_, dm_, ld_

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
    upstream_functional_networks = (
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
    upstream_functional_networks = upstream_functional_networks.rename(
        columns={
            **{
                # standardize names before title-casing
                c: c.replace("sizeclasses", "size_classes")
                .replace("pct_", "percent_")
                .replace("fn_", "upstream_")
                .replace("tot_", "total_upstream_")
                .title()
                .replace("_", "")
                for c in upstream_functional_networks.columns
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
    barrier_networks = upstream_functional_networks.join(downstream_networks).join(
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
