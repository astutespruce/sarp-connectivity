from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import numpy as np

from analysis.constants import METERS_TO_MILES, KM2_TO_ACRES, EPA_CAUSE_TO_CODE, BARRIER_COUNT_KINDS
from analysis.lib.graph.speedups import DirectedGraph
from analysis.lib.io import read_arrow_tables

data_dir = Path("data")


def calculate_upstream_functional_network_stats(network_flowlines, joins, focal_barrier_joins, barrier_joins):
    """Calculate upstream functional network statistics.  Each network starts
    at a downstream terminal or a barrier.

    Parameters
    ----------
    network_flowlines : pyarrow Table
        upstream networks with networkID, lineID and flowline-level attributes
        for each flowline segment

    joins : pyarrow Table
        all flowline joins:
        * upstream_id
        * downstream_id
        * kind

    focal_barrier_joins : pyarrow Table
        limited to the barrier joins that cut the network type being analyzed
        WARNING: contains multiple records per barrier due to multiple upstreams
        contains:
        * id
        * upstream_id
        * downstream_id
        * kind

    barrier_joins : pyarrow Table
        all barrier joins including those that do not cut the network type being analyzed
        WARNING: contains multiple records per barrier due to multiple upstreams
        contains:
        * id
        * upstream_id
        * downstream_id
        * kind

    Returns
    -------
    pyarrow Table
        Summary statistics, with one row per functional network.
    """

    network = network_flowlines.select(["networkID", "lineID"])

    flowline_stats = calculate_flowline_stats(network_flowlines)
    out_index = flowline_stats.select(["networkID"])

    fn_upstream_waterbody_wetland_acres = calculate_functional_upstream_waterbody_wetland_stats(
        network_flowlines.select(["networkID", "lineID", "HUC2"]), out_index
    )

    fn_upstream_counts = calculate_functional_upstream_counts(network, joins, barrier_joins, out_index)

    total_fn_upstream_stats = calculate_total_functional_upstream_stats(
        network, focal_barrier_joins, fn_upstream_counts, out_index
    )
    network_barrier = get_network_barrier(network, focal_barrier_joins, out_index)
    network_root = get_network_root(network_flowlines.select(["networkID", "lineID", "NHDPlusID", "HUC2"]))

    results = (
        flowline_stats.join(fn_upstream_counts, "networkID")
        .join(fn_upstream_waterbody_wetland_acres, "networkID")
        .join(total_fn_upstream_stats, "networkID")
        .join(network_barrier, "networkID")
        .join(network_root, "networkID")
        .combine_chunks()
    )

    return results


def calculate_flowline_stats(network_flowlines):
    """Calculate statistics based on flowline attributes.
    Includes various network lengths (total, free flowling, perennial, etc) and
    lengths by habitat, floodplain acreage, and overlap with certain indicators
    like EJ tracts / tribal and EPA impairments.

    WARNING: Flowlines without associated catchments will have 0 values for
    floodplain_acres, nat_floodplain_acres, natfldpln, fn_drainage_area

    Parameters
    ----------
    network_flowlines : pyarrow Table
        must have networkID, NHDPlusID, length, free_flowing, perennial, resilient, cold, etc

    Returns
    -------
    DataFrame
        stats based on aggregating flowline properties
    """

    required_columns = {
        "networkID",
        "length",
        "altered",
        "intermittent",
        "free_flowing",
        "resilient",
        "cold",
        "sizeclass",
        "AreaSqKm",
        "floodplain_km2",
        "nat_floodplain_km2",
        "EJTract",
        "EJTribal",
    }.union(EPA_CAUSE_TO_CODE.keys())
    missing = required_columns.difference(network_flowlines.column_names)
    if missing:
        print(f"Missing required columns from flowline attributes table: {', '.join(missing)}")

    miles = pc.multiply(network_flowlines["length"], METERS_TO_MILES)
    free_miles = pc.if_else(network_flowlines["free_flowing"], miles, 0)

    # construct a new table with mileage / acreage by each type of flowline
    flowline_stats = {
        "networkID": network_flowlines["networkID"],
        # NOTE: this skips counting of null sizeclasses (these are flowlines without drainage area)
        "sizeclasses": network_flowlines["sizeclass"],
        "perennial_sizeclasses": pc.if_else(network_flowlines["intermittent"], None, network_flowlines["sizeclass"]),
        "fn_drainage_acres": pc.multiply(network_flowlines["AreaSqKm"], KM2_TO_ACRES),
        "total_miles": miles,
        "perennial_miles": pc.if_else(network_flowlines["intermittent"], 0, miles),
        "intermittent_miles": pc.if_else(network_flowlines["intermittent"], miles, 0),
        "altered_miles": pc.if_else(network_flowlines["altered"], miles, 0),
        "unaltered_miles": pc.if_else(network_flowlines["altered"], 0, miles),
        "perennial_unaltered_miles": pc.if_else(
            pc.or_(network_flowlines["intermittent"], network_flowlines["altered"]), 0, miles
        ),
        "resilient_miles": pc.if_else(network_flowlines["resilient"], miles, 0),
        "cold_miles": pc.if_else(network_flowlines["cold"], miles, 0),
        "free_miles": free_miles,
        "free_perennial_miles": pc.if_else(network_flowlines["intermittent"], 0, free_miles),
        "free_intermittent_miles": pc.if_else(network_flowlines["intermittent"], free_miles, 0),
        "free_altered_miles": pc.if_else(network_flowlines["altered"], free_miles, 0),
        "free_unaltered_miles": pc.if_else(network_flowlines["altered"], 0, free_miles),
        "free_perennial_unaltered_miles": pc.if_else(
            pc.or_(network_flowlines["intermittent"], network_flowlines["altered"]), 0, free_miles
        ),
        "free_resilient_miles": pc.if_else(network_flowlines["resilient"], free_miles, 0),
        "free_cold_miles": pc.if_else(network_flowlines["cold"], free_miles, 0),
        "floodplain_acres": pc.multiply(network_flowlines["floodplain_km2"], KM2_TO_ACRES),
        "nat_floodplain_acres": pc.multiply(network_flowlines["nat_floodplain_km2"], KM2_TO_ACRES),
        "has_ej_tract": network_flowlines["EJTract"],
        "has_ej_tribal": network_flowlines["EJTribal"],
    }

    # calculate mileage by habitat that is present
    habitat_cols = [c for c in network_flowlines.column_names if c.endswith("_habitat")]
    for habitat in habitat_cols:
        present = pc.fill_null(network_flowlines[habitat], False)
        flowline_stats[f"{habitat}_miles"] = pc.if_else(present, miles, 0)
        flowline_stats[f"free_{habitat}_miles"] = pc.if_else(present, free_miles, 0)

    measure_cols = [c for c in flowline_stats.keys() if c.endswith("_miles") or c.endswith("_acres")]
    presence_cols = [c for c in flowline_stats.keys() if c.startswith("has_")]
    distinct_cols = ["sizeclasses", "perennial_sizeclasses"]

    network_stats = (
        pa.Table.from_pydict(flowline_stats)
        .group_by("networkID")
        .aggregate(
            [(col, "sum") for col in measure_cols]
            + [(col, "any") for col in presence_cols]
            + [(col, "count_distinct") for col in distinct_cols]
        )
        .rename_columns(
            {
                **{f"{col}_sum": col for col in measure_cols},
                **{f"{col}_any": col for col in presence_cols},
                **{f"{col}_count_distinct": col for col in distinct_cols},
            }
        )
        .combine_chunks()
    )

    # cast to smaller types (percents calculated below remain floats)
    schema = network_stats.schema
    for i, col in enumerate(schema.names):
        field_type = schema.field(col).type
        if field_type == pa.float64():
            schema = schema.set(i, pa.field(col, pa.float32()))
        elif col.endswith("sizeclasses"):
            schema = schema.set(i, pa.field(col, pa.uint8()))
    network_stats = network_stats.cast(schema)

    ### calculate percents based on total network stats
    pct_unaltered = np.clip(
        pc.multiply(pc.divide(network_stats["unaltered_miles"], network_stats["total_miles"]), 100), 0, 100
    )
    pct_perennial_unaltered = np.clip(
        pc.multiply(
            pc.if_else(
                pc.greater(network_stats["perennial_miles"], 0),
                pc.divide(network_stats["perennial_unaltered_miles"], network_stats["perennial_miles"]),
                0,
            ),
            100,
        ),
        0,
        100,
    )
    pct_resilient = np.clip(
        pc.multiply(pc.divide(network_stats["resilient_miles"], network_stats["total_miles"]), 100), 0, 100
    )
    pct_cold = np.clip(pc.multiply(pc.divide(network_stats["cold_miles"], network_stats["total_miles"]), 100), 0, 100)

    natfldpln = np.clip(
        pc.multiply(
            pc.if_else(
                pc.greater(network_stats["floodplain_acres"], 0),
                pc.divide(network_stats["nat_floodplain_acres"], network_stats["floodplain_acres"]),
                0,
            ),
            100,
        ),
        0,
        100,
    )

    percents = {
        "networkID": network_stats["networkID"],
        "pct_unaltered": pct_unaltered,
        "pct_perennial_unaltered": pct_perennial_unaltered,
        "pct_resilient": pct_resilient,
        "pct_cold": pct_cold,
        "natfldpln": natfldpln,
    }

    network_stats = network_stats.join(pa.Table.from_pydict(percents), "networkID").combine_chunks()

    return network_stats


def calculate_functional_upstream_waterbody_wetland_stats(network, out_index):
    """Calculate total waterbody and wetland acreage per network.

    NOTE: this counts each waterbody / wetland only once per network, so we have
    to do this separate from above flowline stats

    Parameters
    ----------
    network : pyarrow Table
        upstream network table, must have networkID, lineID, and HUC2
    out_index : pyarrow Table
        table of unique networkIDs that all stats are joined back to
    """

    huc2s = pc.unique(network["HUC2"]).tolist()

    wb = read_arrow_tables(
        [data_dir / "networks/raw" / huc2 / "flowline_waterbodies.feather" for huc2 in huc2s],
        columns=["lineID", "wbID", "km2"],
    )
    network_wb = out_index.join(
        network.join(wb, "lineID", join_type="inner")
        .group_by(["networkID", "wbID"], use_threads=False)
        .aggregate([("km2", "first")])
        .group_by("networkID")
        .aggregate([("km2_first", "sum")]),
        "networkID",
    ).combine_chunks()
    unaltered_waterbody_acres = pa.Table.from_pydict(
        {
            "networkID": network_wb["networkID"],
            "unaltered_waterbody_acres": pc.cast(
                pc.multiply(pc.fill_null(network_wb["km2_first_sum"], 0), KM2_TO_ACRES), pa.float32()
            ),
        }
    )

    wetlands = read_arrow_tables(
        [data_dir / "networks/raw" / huc2 / "flowline_wetlands.feather" for huc2 in huc2s],
        columns=["lineID", "wetlandID", "km2"],
    )
    network_wetlands = out_index.join(
        network.join(wetlands, "lineID", join_type="inner")
        .group_by(["networkID", "wetlandID"], use_threads=False)
        .aggregate([("km2", "first")])
        .group_by("networkID")
        .aggregate([("km2_first", "sum")]),
        "networkID",
    ).combine_chunks()
    unaltered_wetland_acres = pa.Table.from_pydict(
        {
            "networkID": network_wetlands["networkID"],
            "unaltered_wetland_acres": pc.cast(
                pc.multiply(pc.fill_null(network_wetlands["km2_first_sum"], 0), KM2_TO_ACRES), pa.float32()
            ),
        }
    )

    return unaltered_waterbody_acres.join(unaltered_wetland_acres, "networkID").combine_chunks()


def calculate_functional_upstream_counts(network, joins, barrier_joins, out_index):
    """Count the number of barriers of each type WITHIN or TERMINATING the upstream functional
    network of each barrier.  Barriers of a lesser type than the one
    used to cut the network are within the network, those of equal or greater type
    terminate the network.  By definition, they are any with downstream_ids
    that are in the lineIDs associated with the current networkID

    Parameters
    ----------
    network : pyarrow Table
        upstream network table, must have networkID and lineID
    joins : pyarrow Table
        network joins
    barrier_joins : pyarrow Table
        all barrier joins including those that do not cut the network type being analyzed
    out_index : pyarrow Table
        table of unique networkIDs that all stats are joined back to

    Returns
    -------
    pyarrow Table
    """

    # calculate the number of network origins (headwaters) in the upstream network
    fn_upstream_headwaters = (
        network.join(
            joins.select(["type", "downstream_id"]).filter(pc.equal(joins["type"], "origin")),
            "lineID",
            "downstream_id",
            join_type="inner",
        )
        .group_by("networkID")
        .aggregate([("lineID", "count_distinct")])
        .rename_columns({"lineID_count_distinct": "fn_headwaters"})
    )

    # deduplicate due to multiple upstreams at confluences
    barrier_downstreams = (
        barrier_joins.select(["id", "kind", "downstream_id"])
        .group_by("id", use_threads=False)
        .aggregate([("kind", "first"), ("downstream_id", "first")])
        .rename_columns({"kind_first": "kind", "downstream_id_first": "downstream_id"})
    )

    upstream_barriers = network.join(
        barrier_downstreams.select("downstream_id", "kind"), "lineID", "downstream_id", join_type="inner"
    )

    counts = (
        pa.Table.from_pydict(
            {
                "networkID": upstream_barriers["networkID"],
                **{
                    f"fn_{kind}s": pc.if_else(pc.equal(upstream_barriers["kind"], kind), 1, 0)
                    for kind in BARRIER_COUNT_KINDS
                },
            }
        )
        .group_by("networkID")
        .aggregate([(f"fn_{kind}s", "sum") for kind in BARRIER_COUNT_KINDS])
        .rename_columns({f"fn_{kind}s_sum": f"fn_{kind}s" for kind in BARRIER_COUNT_KINDS})
    )

    # backfill counts so this is complete then set to smallest data types
    counts = out_index.join(counts, "networkID").join(fn_upstream_headwaters, "networkID")
    out = {"networkID": counts["networkID"]}
    for col in [c for c in counts.column_names if c.startswith("fn_")]:
        max = pc.max(counts[col]).as_py()
        values = pc.fill_null(counts[col], 0)
        if max <= 255:
            values = pc.cast(values, pa.uint8())
        elif max <= 65535:
            values = pc.cast(values, pa.uint16())
        else:
            values = pc.cast(values, pa.uint32())

        out[col] = values

    counts = pa.Table.from_pydict(out)

    return counts


def calculate_total_functional_upstream_stats(network, focal_barrier_joins, fn_upstream_counts, out_index):
    """Count TOTAL barriers of each kind in the total upstream network(s),
    (not limited to upstream functional network) using a directed graph of
    network joins facing upstream

    This finds all focal joins that are internal to the network (not at upstream or
    downstream end) then use these to define the joins between adjacent networks
    NOTE: upstream_ids that are not also networks (because of confluences) are
    removed prior to calling here.

    This also marks all invasive networks, which are any that are terminated at
    or upstream of an invasive barrier.

    Parameters
    ----------
    network : pyarrow Table
        upstream network table, must have networkID and lineID
    focal_barrier_joins : pyarrow Table
        limited to the barrier joins that cut the network type being analyzed
    fn_upstream_counts : pyarrow Table
        counts by barrier type per functional network
    out_index : pyarrow Table
        table of unique networkIDs that all stats are joined back to

    Returns
    -------
    pyarrow Table
    """

    # use downstream_id to determine associated networkID for the downstream
    # side of this barrier join
    # NOTE: because multiple barriers may occur at the upstream endpoints of a
    # given network, there will be several entries for a given network ID
    network_joins = network.join(
        focal_barrier_joins.filter(pc.not_equal(focal_barrier_joins["upstream_id"], 0)).select(
            ["downstream_id", "upstream_id"]
        ),
        "lineID",
        "downstream_id",
        join_type="inner",
    )

    # construct graph facing upstream
    upstream_graph = DirectedGraph(
        network_joins["networkID"].to_numpy().astype("int64"),  # downstream side of join
        network_joins["upstream_id"].to_numpy().astype("int64"),  # upstream side of join
    )

    upstreams = pa.Table.from_arrays(
        upstream_graph.network_pairs(pc.unique(network["networkID"]).to_numpy().astype("int64")).T.astype("uint32"),
        ["networkID", "upstream_network"],
    )

    count_cols = [c for c in fn_upstream_counts.column_names if c.startswith("fn_")]
    counts = (
        upstreams.join(fn_upstream_counts, "upstream_network", "networkID")
        .group_by("networkID")
        .aggregate([(col, "sum") for col in count_cols])
        .rename_columns({f"{col}_sum": col.replace("fn_", "tot_") for col in count_cols})
    )

    # backfill counts so this is complete then set to smallest data types
    counts = out_index.join(counts, "networkID")
    out = {"networkID": counts["networkID"]}
    for col in [c for c in counts.column_names if c.startswith("tot_")]:
        max = pc.max(counts[col]).as_py()
        values = pc.fill_null(counts[col], 0)
        if max <= 255:
            values = pc.cast(values, pa.uint8())
        elif max <= 65535:
            values = pc.cast(values, pa.uint16())
        else:
            values = pc.cast(values, pa.uint32())

        out[col] = values

    counts = pa.Table.from_pydict(out)

    ### Find any networks that have a (focal) invasive barrier at their root
    invasive_roots = (
        network.select(["networkID", "lineID"])
        .join(
            focal_barrier_joins.filter(focal_barrier_joins["invasive"]).select(["upstream_id"]),
            "lineID",
            "upstream_id",
            join_type="inner",
        )
        .drop(["lineID"])
    )

    # find all upstream networks for these
    invasive_upstreams = invasive_roots.join(upstreams, "networkID", join_type="inner")

    # combine both sets of IDs
    invasive_network_ids = pc.unique(
        pa.concat_arrays(
            [invasive_upstreams["upstream_network"].combine_chunks(), invasive_roots["networkID"].combine_chunks()]
        )
    )

    invasive_networks = out_index.join(
        pa.Table.from_pydict(
            {
                "networkID": invasive_network_ids,
                "invasive_network": pa.array(np.repeat(True, len(invasive_network_ids))),
            }
        ),
        "networkID",
    )
    invasive_networks = pa.Table.from_pydict(
        {
            "networkID": invasive_networks["networkID"],
            "invasive_network": pc.fill_null(invasive_networks["invasive_network"], False),
        }
    )

    return counts.join(invasive_networks, "networkID").combine_chunks()


def get_network_barrier(network, focal_barrier_joins, out_index):
    """Determine the barrier type associated with this functional network

    Parameters
    ----------
    network : pyarrow Table
        upstream network table, must have networkID and lineID
    focal_barrier_joins : pyarrow Table
        limited to the barrier joins that cut the network type being analyzed
    out_index : pyarrow Table
        table of unique networkIDs that all stats are joined back to

    Returns
    -------
    pyarrow Table
    """

    network_barrier = out_index.join(
        # resolve barrier upstream_id to networkID
        network.join(
            focal_barrier_joins.select(["id", "kind", "upstream_id"]), "lineID", "upstream_id", join_type="inner"
        )
        # this has duplicates because of multiple upstreams coalesced for barrier
        # NOTE: have to do grouping without threads
        .group_by("networkID", use_threads=False)
        .aggregate([("id", "first"), ("kind", "first")])
        .rename_columns({"id_first": "barrier_id", "kind_first": "barrier"}),
        "networkID",
    ).combine_chunks()

    filled = pc.fill_null(network_barrier["barrier"], "")
    values, indices = np.unique(filled, return_inverse=True)
    network_barrier = pa.Table.from_pydict(
        {
            "networkID": network_barrier["networkID"],
            "barrier_id": pc.fill_null(network_barrier["barrier_id"], 0),
            "barrier": pa.DictionaryArray.from_arrays(indices.astype("int8"), values),
        }
    )

    return network_barrier


def get_network_root(network):
    """Find the root of each network and determine origin HUC2 and
    marine / Great Lakes connectivity

    Parameters
    ----------
    network : pyarrow Table
        must have networkID, lineID, NHDPlusID, HUC2

    Returns
    -------
    pyarrow Table
    """
    network_root = (
        network.filter(pc.equal(network["networkID"], network["lineID"]))
        .select(["networkID", "NHDPlusID", "HUC2"])
        .rename_columns({"HUC2": "origin_HUC2"})
    )

    # load NHDPlusIDs for all flowlines that terminate in marine or Great Lakes
    root_nhd_ids = pc.unique(network_root["NHDPlusID"])
    marine_ids = pa.dataset.dataset(data_dir / "nhd/clean/all_marine_flowlines.feather", format="feather").to_table(
        filter=pc.is_in(pc.field("NHDPlusID"), root_nhd_ids)
    )["NHDPlusID"]
    great_lake_ids = pa.dataset.dataset(
        data_dir / "nhd/clean/all_great_lakes_flowlines.feather", format="feather"
    ).to_table(filter=pc.is_in(pc.field("NHDPlusID"), root_nhd_ids))["NHDPlusID"]

    network_root = network_root.append_column("flows_to_ocean", pc.is_in(network_root["NHDPlusID"], marine_ids))
    network_root = network_root.append_column(
        "flows_to_great_lakes", pc.is_in(network_root["NHDPlusID"], great_lake_ids)
    )

    return network_root.select(["networkID", "origin_HUC2", "flows_to_ocean", "flows_to_great_lakes"]).combine_chunks()


def calculate_upstream_mainstem_network_stats(network_flowlines):
    """Calculate network statistics for upstream mainstem networks.

    Parameters
    ----------
    network_flowlines : pyarrow Table
        must have networkID, NHDPlusID, length, altered, intermittent, etc

    Returns
    -------
    pyarrow Table
    """

    required_columns = {
        "networkID",
        "length",
        "altered",
        "intermittent",
        "sizeclass",
    }.union(EPA_CAUSE_TO_CODE.keys())
    missing = required_columns.difference(network_flowlines.column_names)
    if missing:
        print(f"Missing required columns from flowline attributes table: {', '.join(missing)}")

    miles = pc.multiply(network_flowlines["length"], METERS_TO_MILES)

    flowline_stats = {
        "networkID": network_flowlines["networkID"],
        "sizeclasses": network_flowlines["sizeclass"],
        "total_upstream_mainstem_miles": miles,
        "perennial_upstream_mainstem_miles": pc.if_else(network_flowlines["intermittent"], 0, miles),
        "intermittent_upstream_mainstem_miles": pc.if_else(network_flowlines["intermittent"], miles, 0),
        "altered_upstream_mainstem_miles": pc.if_else(network_flowlines["altered"], miles, 0),
        "unaltered_upstream_mainstem_miles": pc.if_else(network_flowlines["altered"], 0, miles),
        "perennial_unaltered_upstream_mainstem_miles": pc.if_else(
            pc.or_(network_flowlines["intermittent"], network_flowlines["altered"]), 0, miles
        ),
        **{f"has_upstream_mainstem_{col}": network_flowlines[col] for col in EPA_CAUSE_TO_CODE.keys()},
    }

    measure_cols = [c for c in flowline_stats.keys() if c.endswith("_miles")]
    presence_cols = [c for c in flowline_stats.keys() if c.startswith("has_")]
    distinct_cols = ["sizeclasses"]

    network_stats = (
        pa.Table.from_pydict(flowline_stats)
        .group_by("networkID")
        .aggregate(
            [(col, "sum") for col in measure_cols]
            + [(col, "any") for col in presence_cols]
            + [(col, "count_distinct") for col in distinct_cols]
        )
        .rename_columns(
            {
                **{f"{col}_sum": col for col in measure_cols},
                **{f"{col}_any": col for col in presence_cols},
                **{f"{col}_count_distinct": col for col in distinct_cols},
            }
        )
        .combine_chunks()
    )

    # cast to smaller types (percents calculated below remain floats)
    schema = network_stats.schema
    for i, col in enumerate(schema.names):
        field_type = schema.field(col).type
        if field_type == pa.float64():
            schema = schema.set(i, pa.field(col, pa.float32()))
        elif col.endswith("sizeclasses"):
            schema = schema.set(i, pa.field(col, pa.uint8()))
    network_stats = network_stats.cast(schema)

    ### calculate percents based on total network stats
    pct_unaltered = np.clip(
        pc.multiply(
            pc.divide(
                network_stats["unaltered_upstream_mainstem_miles"], network_stats["total_upstream_mainstem_miles"]
            ),
            100,
        ),
        0,
        100,
    )

    network_stats = network_stats.append_column("pct_upstream_mainstem_unaltered", pa.array(pct_unaltered))

    return network_stats


def calculate_downstream_mainstem_network_stats(network_flowlines, focal_barrier_downstreams):
    """Calculate total network miles, total perennial miles, total unaltered
    perennial miles based on the downstream mainstem network.

    network_flowlines : pyarrow Table
        must have networkID, NHDPlusID, length, free_flowing, perennial, resilient, cold, etc

    focal_barrier_downstreams : pyarrow Table
        deduplicated join table of barrier id, networkID (downstream network)

    Returns
    -------
    pyarrow Table
    """

    required_columns = {
        "networkID",
        "length",
        "free_flowing",
        "altered",
        "intermittent",
        "sizeclass",
    }.union(EPA_CAUSE_TO_CODE.keys())
    missing = required_columns.difference(network_flowlines.column_names)
    if missing:
        print(f"Missing required columns from flowline attributes table: {', '.join(missing)}")

    miles = pc.multiply(network_flowlines["length"], METERS_TO_MILES)
    free_miles = pc.if_else(network_flowlines["free_flowing"], miles, 0)

    # construct a new table with mileage / acreage by each type of flowline
    flowline_stats = {
        "networkID": network_flowlines["networkID"],
        "total_downstream_mainstem_miles": miles,
        "free_downstream_mainstem_miles": free_miles,
        "free_perennial_downstream_mainstem_miles": pc.if_else(network_flowlines["intermittent"], 0, free_miles),
        "free_intermittent_downstream_mainstem_miles": pc.if_else(network_flowlines["intermittent"], free_miles, 0),
        "free_altered_downstream_mainstem_miles": pc.if_else(network_flowlines["altered"], free_miles, 0),
        "free_unaltered_downstream_mainstem_miles": pc.if_else(network_flowlines["altered"], 0, free_miles),
        **{f"has_downstream_mainstem_{col}": network_flowlines[col] for col in EPA_CAUSE_TO_CODE.keys()},
    }

    measure_cols = [c for c in flowline_stats.keys() if c.endswith("_miles")]
    presence_cols = [c for c in flowline_stats.keys() if c.startswith("has_")]

    network_stats = (
        pa.Table.from_pydict(flowline_stats)
        .group_by("networkID")
        .aggregate([(col, "sum") for col in measure_cols] + [(col, "any") for col in presence_cols])
        .rename_columns(
            {
                **{f"{col}_sum": col for col in measure_cols},
                **{f"{col}_any": col for col in presence_cols},
            }
        )
        .combine_chunks()
    )

    # cast to smaller types
    schema = network_stats.schema
    for i, col in enumerate(schema.names):
        field_type = schema.field(col).type
        if field_type == pa.float64():
            schema = schema.set(i, pa.field(col, pa.float32()))
    network_stats = network_stats.cast(schema)

    # join to focal barrier joins to resolve to barrier ID
    network_stats = network_stats.join(
        focal_barrier_downstreams, "networkID", "downstream_id", join_type="inner"
    ).combine_chunks()

    return network_stats


def calculate_downstream_linear_network_stats(
    network_flowlines, focal_barrier_joins, barrier_joins, focal_barrier_downstreams
):
    """Calculate downstream statistics for each barrier based on its linear
    downstream network (to next barrier downstream or terminal / outlet) and
    total downstream (to final terminal / outlet).

    Parameters
    ----------
    network_flowlines : pyarrow Table
        must have networkID, NHDPlusID, length, free_flowing

    focal_barrier_joins : pyarrow Table
        limited to the barrier joins that cut the network type being analyzed

    barrier_joins : pyarrow Table
        all barrier joins including those that do not cut the network type being analyzed
        contains:
        * upstream_id
        * downstream_id
        * kind

    focal_barrier_downstreams : pyarrow Table
        deduplicated join table of barrier id, networkID (downstream network)

    barrier_downstreams_table : pyarrow Table
        deduplicated table of barrier ID, kind, and downstream_id
        this acts as the index to join barrier ID to downstream networks on downstream_id

    Returns
    -------
    Pandas DataFrame
        Summary statistics, with one row per barrier.
    """

    miles = pc.multiply(network_flowlines["length"], METERS_TO_MILES)
    free_miles = pc.if_else(network_flowlines["free_flowing"], miles, 0)

    flowline_stats = {
        "networkID": network_flowlines["networkID"],
        "total_linear_downstream_miles": miles,
        "free_linear_downstream_miles": free_miles,
        "free_perennial_linear_downstream_miles": pc.if_else(network_flowlines["intermittent"], 0, free_miles),
        "free_intermittent_linear_downstream_miles": pc.if_else(network_flowlines["intermittent"], free_miles, 0),
        "free_altered_linear_downstream_miles": pc.if_else(network_flowlines["altered"], free_miles, 0),
        "free_unaltered_linear_downstream_miles": pc.if_else(network_flowlines["altered"], 0, free_miles),
    }

    measure_cols = [c for c in flowline_stats.keys() if c.endswith("_miles")]

    network_stats = (
        pa.Table.from_pydict(flowline_stats)
        .group_by("networkID")
        .aggregate([(col, "sum") for col in measure_cols])
        .rename_columns({f"{col}_sum": col for col in measure_cols})
        .combine_chunks()
    )

    # cast to smaller types
    schema = network_stats.schema
    for i, col in enumerate(schema.names):
        field_type = schema.field(col).type
        if field_type == pa.float64():
            schema = schema.set(i, pa.field(col, pa.float32()))
    network_stats = network_stats.cast(schema)

    ### Use a graph of network joins facing downward to aggregate these to a
    # total count per barrier

    # extract joins between downstream linear networks using all_focal_barrier_joins
    # to traverse confluences
    # NOTE: these won't have any entries at top of network
    # WARNING: this does not include entries for any confluences where one side
    # is not part of a barrier downstream network (i.e., has no cutting barriers
    # upstream)

    downstream_network_joins = (
        network_flowlines.select(["networkID", "lineID"])
        .join(focal_barrier_joins.select(["upstream_id", "downstream_id"]), "lineID", "upstream_id", join_type="inner")
        .rename_columns({"networkID": "upstream_network", "downstream_id": "downstream_network"})
    )

    downstream_graph = DirectedGraph(
        downstream_network_joins["upstream_network"].to_numpy().astype("int64"),
        downstream_network_joins["downstream_network"].to_numpy().astype("int64"),
    )

    network_ids = focal_barrier_downstreams["networkID"].to_numpy().astype("int64")
    downstreams = pa.Table.from_arrays(
        downstream_graph.network_pairs(network_ids).T.astype("uint32"),
        ["networkID", "downstream_network"],
    )

    # use the upstream IDs to join against the network, this gives those barriers
    # that are downstream (interior or at downstream endpoint) but not the
    # barrier at the top of the linear network (which would then need to be deducted)
    # NOTE: a given barrier may occur at the downstream end of many different linear networks
    downstream_barriers = network_flowlines.select(["networkID", "lineID"]).join(
        barrier_joins.select(["kind", "upstream_id"]), "lineID", "upstream_id", join_type="inner"
    )

    ln_downstream_stats = (
        pa.Table.from_pydict(
            {
                "networkID": downstream_barriers["networkID"],
                **{
                    f"ln_{kind}s": pc.if_else(pc.equal(downstream_barriers["kind"], kind), 1, 0)
                    for kind in BARRIER_COUNT_KINDS
                },
            }
        )
        .group_by("networkID")
        .aggregate([(f"ln_{kind}s", "sum") for kind in BARRIER_COUNT_KINDS])
        .rename_columns({**{f"ln_{kind}s_sum": f"ln_{kind}s" for kind in BARRIER_COUNT_KINDS}})
    )

    count_cols = [f"ln_{kind}s" for kind in BARRIER_COUNT_KINDS]
    tot_downstream_stats = (
        downstreams.join(ln_downstream_stats, "downstream_network", "networkID")
        .join(
            network_stats.select(["networkID", "total_linear_downstream_miles"]).rename_columns(
                {"total_linear_downstream_miles": "miles_to_outlet"}
            ),
            "downstream_network",
            "networkID",
        )
        .group_by("networkID")
        .aggregate([(col, "sum") for col in count_cols] + [("miles_to_outlet", "sum")])
        .rename_columns(
            {
                **{f"{col}_sum": col.replace("ln_", "totd_") for col in count_cols},
                "miles_to_outlet_sum": "miles_to_outlet",
            }
        )
    )

    # fill missing values then set to smallest data types
    tot_downstream_stats = (
        focal_barrier_downstreams.select(["networkID"])
        .join(tot_downstream_stats, "networkID", join_type="inner")
        .combine_chunks()
    )
    out = {
        "networkID": tot_downstream_stats["networkID"],
        "miles_to_outlet": pc.cast(pc.fill_null(tot_downstream_stats["miles_to_outlet"], 0), pa.float32()),
    }
    for col in [c for c in tot_downstream_stats.column_names if c.startswith("totd_")]:
        max = pc.max(tot_downstream_stats[col]).as_py()
        values = pc.fill_null(tot_downstream_stats[col], 0)
        if max <= 255:
            values = pc.cast(values, pa.uint8())
        elif max <= 65535:
            values = pc.cast(values, pa.uint16())
        else:
            values = pc.cast(values, pa.uint32())

        out[col] = values

    tot_downstream_stats = pa.Table.from_pydict(out)

    ### find the next focal barrier downstream; these are ones whose upstream is in the
    # linear networks of the next barrier upstream

    downstream_focal_barriers = (
        network_flowlines.select(["networkID", "lineID"])
        .join(focal_barrier_joins.select(["id", "kind", "upstream_id"]), "lineID", "upstream_id", join_type="inner")
        .drop(["lineID"])
        .rename_columns({"id": "downstream_barrier_id", "kind": "downstream_barrier"})
    )

    downstream_focal_barriers = (
        focal_barrier_downstreams.select(["networkID"])
        .join(downstream_focal_barriers, "networkID")
        .join(
            network_stats.select(["networkID", "total_linear_downstream_miles"]).rename_columns(
                {"total_linear_downstream_miles": "downstream_barrier_miles"}
            ),
            "networkID",
        )
        .combine_chunks()
    )
    downstream_focal_barriers = pa.Table.from_pydict(
        {
            "networkID": downstream_focal_barriers["networkID"],
            "downstream_barrier_id": pc.fill_null(downstream_focal_barriers["downstream_barrier_id"], 0),
            "downstream_barrier": pc.fill_null(downstream_focal_barriers["downstream_barrier"], ""),
            "downstream_barrier_miles": pc.if_else(
                pc.is_null(downstream_focal_barriers["downstream_barrier_id"]),
                0,
                pc.fill_null(downstream_focal_barriers["downstream_barrier_miles"], 0),
            ),
        }
    )

    results = (
        focal_barrier_downstreams.select(["id", "networkID"])
        .join(network_stats, "networkID")
        .join(tot_downstream_stats, "networkID")
        .join(downstream_focal_barriers, "networkID")
        .combine_chunks()
    )

    return results
