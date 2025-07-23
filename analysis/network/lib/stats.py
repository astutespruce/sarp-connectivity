from pathlib import Path

import pandas as pd
import pyarrow as pa
from pyarrow.dataset import dataset
import pyarrow.compute as pc
import numpy as np

from analysis.constants import METERS_TO_MILES, KM2_TO_ACRES, EPA_CAUSE_TO_CODE
from analysis.lib.graph.speedups import DirectedGraph

data_dir = Path("data")


COUNT_KINDS = ["waterfalls", "dams", "small_barriers", "road_crossings", "headwaters"]


def calculate_upstream_functional_network_stats(
    up_network_df, joins, focal_barrier_joins, barrier_joins, unaltered_waterbodies, unaltered_wetlands
):
    """Calculate upstream functional network statistics.  Each network starts
    at a downstream terminal or a barrier.

    Parameters
    ----------
    up_network_df : Pandas DataFrame
        upstream networks indexed on networkID of the lineID upstream of the
        barrier.  Includes the basic metrics for each flowline segment:
        * length
        * size class
        * altered
        * intermittent

    joins : Pandas DataFrame
        network joins:
        * upstream_id
        * downstream_id
        * kind

    focal_barrier_joins : Pandas DataFrame
        limited to the barrier joins that cut the network type being analyzed
        contains:
        * upstream_id
        * downstream_id
        * kind

    barrier_joins : Pandas DataFrame
        all barrier joins including those that do not cut the network type being analyzed
        contains:
        * upstream_id
        * downstream_id
        * kind

    unaltered_waterbodies : Pandas DataFrame
        mapping of lineID to wbID

    unaltered_wetlands : Pandas DataFrame
        mapping of lineID to wetlandID

    Returns
    -------
    Pandas DataFrame
        Summary statistics, with one row per functional network.
    """

    # find the HUC2 of the network origin
    network_root = up_network_df.loc[up_network_df.index == up_network_df.lineID, ["NHDPlusID", "HUC2"]].rename(
        columns={"HUC2": "origin_HUC2"}
    )

    # lineIDs for all flowlines that terminate in marine or Great Lakes
    marine_ids = (
        pa.dataset.dataset(data_dir / "nhd/clean/all_marine_flowlines.feather", format="feather")
        .to_table(filter=pc.is_in(pc.field("NHDPlusID"), pa.array(up_network_df.NHDPlusID.unique())))["NHDPlusID"]
        .to_numpy()
    )
    network_root["flows_to_ocean"] = network_root.NHDPlusID.isin(marine_ids)

    great_lake_ids = (
        pa.dataset.dataset(data_dir / "nhd/clean/all_great_lakes_flowlines.feather", format="feather")
        .to_table(filter=pc.is_in(pc.field("NHDPlusID"), pa.array(up_network_df.NHDPlusID.unique())))["NHDPlusID"]
        .to_numpy()
    )
    network_root["flows_to_great_lakes"] = network_root.NHDPlusID.isin(great_lake_ids)

    # count unique size classes in upstream functional network
    sizeclasses = up_network_df.groupby(level=0).sizeclass.nunique().astype("uint8").rename("sizeclasses")
    perennial_sizeclasses = (
        up_network_df.loc[~up_network_df.intermittent]
        .groupby(level=0)
        .sizeclass.nunique()
        .astype("uint8")
        .rename("perennial_sizeclasses")
    )

    # create series of networkID indexed by lineID
    networkID = up_network_df.reset_index().set_index("lineID").networkID
    networkIDs = pd.Series(networkID.unique(), name="networkID")

    headwaters_ids = joins.loc[joins.type == "origin"].downstream_id

    ### Count the number of barriers of each type WITHIN or TERMINATING the upstream functional
    # network of each barrier.  Barriers of a lesser type than the one
    # used to cut the network are within the network, those of equal or greater type
    # terminate the network.  By definition, they are any with downstream_ids
    # that are in the lineIDs associated with the current networkID

    # limit barrier_joins to those with downstream IDs present within these networks
    upstream_barrier_joins = barrier_joins.loc[barrier_joins.downstream_id.isin(networkID.index.unique())].copy()

    fn_barriers_upstream = (
        upstream_barrier_joins[["downstream_id", "kind"]]
        .join(networkID, on="downstream_id", how="inner")
        .reset_index()[["networkID", "kind"]]
    )
    # calculate the number of network origins (headwaters) in the upstream network
    fn_headwaters_upstream = (
        networkID.loc[headwaters_ids].reset_index().groupby("networkID").size().rename("headwaters")
    )

    fn_upstream_counts = (
        fn_barriers_upstream.groupby(["networkID", "kind"])
        .size()
        .rename("count")
        .reset_index()
        .pivot(index="networkID", columns="kind", values="count")
        .join(fn_headwaters_upstream, how="outer")
        .fillna(0)
        .rename(
            columns={
                "dam": "fn_dams",
                "waterfall": "fn_waterfalls",
                "small_barrier": "fn_small_barriers",
                "road_crossing": "fn_road_crossings",
                "headwaters": "fn_headwaters",
            }
        )
    )
    # make sure all count columns are present and in correct order
    cols = [f"fn_{kind}" for kind in COUNT_KINDS]
    for col in cols:
        if col not in fn_upstream_counts.columns:
            fn_upstream_counts[col] = 0

    fn_upstream_counts = fn_upstream_counts[cols]
    fn_upstream_area = (up_network_df.groupby(level=0).AreaSqKm.sum() * KM2_TO_ACRES).rename("fn_da_acres")

    ### Count TOTAL barriers of each kind in the total upstream network(s),
    # (not limited to upstream functional network) using a directed graph of
    # network joins facing upstream

    # find all focal joins that are internal to the network (not at upstream or
    # downstream end) then use these to define the joins between adjacent networks
    # NOTE: upstream_ids that are not also networks (because of confluences) are
    # removed prior to calling here
    network_joins = (
        focal_barrier_joins.loc[(focal_barrier_joins.upstream_id != 0) & (focal_barrier_joins.downstream_id != 0)]
        .join(networkID, on="downstream_id")
        .rename(
            columns={
                "networkID": "downstream_network",
                "upstream_id": "upstream_network",
            }
        )[["upstream_network", "downstream_network", "kind"]]
    )

    upstream_graph = DirectedGraph(
        network_joins.downstream_network.values.astype("int64"),
        network_joins.upstream_network.values.astype("int64"),
    )
    upstreams = (
        pd.Series(
            upstream_graph.descendants(networkIDs.values.astype("int64")),
            index=networkIDs,
            name="upstream_network",
        )
        .explode()
        .dropna()
    )

    # totals are the sum of all functional network counts UPSTREAM of each network
    # plus the functional network counts for each network
    tot_upstream_counts = (
        pd.concat(
            [
                pd.DataFrame(upstreams)
                .join(fn_upstream_counts, on="upstream_network")
                .drop(columns=["upstream_network"])
                .fillna(0)
                .reset_index(),
                fn_upstream_counts.reset_index(),
            ],
            ignore_index=True,
            sort=False,
        )
        .rename(
            columns={
                "fn_dams": "tot_dams",
                "fn_waterfalls": "tot_waterfalls",
                "fn_small_barriers": "tot_small_barriers",
                "fn_road_crossings": "tot_road_crossings",
                "fn_headwaters": "tot_headwaters",
            }
        )
        .groupby("networkID")
        .sum()
    )

    cols = [f"tot_{kind}" for kind in COUNT_KINDS]
    for col in cols:
        if col not in tot_upstream_counts.columns:
            tot_upstream_counts[col] = 0

    tot_upstream_counts = tot_upstream_counts[cols]

    # determine the barrier type associated with this functional network
    network_barrier = (
        focal_barrier_joins.loc[focal_barrier_joins.upstream_id != 0, ["kind", "upstream_id"]]
        .reset_index()
        .join(networkID, on="upstream_id", how="inner")
        .set_index("networkID")[["id", "kind"]]
        .rename(columns={"id": "barrier_id", "kind": "barrier"})
    )

    ### Collect results
    results = (
        calculate_geometry_stats(up_network_df)
        .join(calculate_species_habitat_stats(up_network_df))
        .join(calculate_floodplain_stats(up_network_df))
        .join(calculate_upstream_waterbody_wetland_stats(up_network_df, unaltered_waterbodies, unaltered_wetlands))
        .join(sizeclasses)
        .join(perennial_sizeclasses)
        .join(fn_upstream_counts)
        .join(fn_upstream_area)
        .join(tot_upstream_counts)
        .join(network_barrier)
        .join(network_root[["origin_HUC2", "flows_to_ocean", "flows_to_great_lakes"]])
    )

    # index name is getting dropped in some cases
    results.index.name = "networkID"

    # backfill count columns
    count_cols = fn_upstream_counts.columns.tolist() + tot_upstream_counts.columns.tolist()
    results[count_cols] = results[count_cols].fillna(0)

    # backfill sizeclass columns
    results["perennial_sizeclasses"] = results.perennial_sizeclasses.fillna(0).astype("uint8")

    return results


def calculate_geometry_stats(df):
    """Calculate total network miles, free-flowing miles (not in waterbodies),
    free-flowing unaltered miles (not in waterbodies, not altered), total
    perennial miles, total free-flowing unaltered perennial miles.

    Parameters
    ----------
    df : DataFrame
        must have NHDPlusID, HUC2, length, free_flowing, and perennial, and be indexed on
        networkID

    Returns
    -------
    DataFrame
        contains total_miles, free_miles, *_miles
    """

    resilient = (
        dataset(
            data_dir / "tnc_resilience/derived/tnc_resilient_flowlines.feather",
            format="feather",
        )
        .to_table(filter=pc.field("HUC2").isin(df.HUC2.unique()), columns=["NHDPlusID", "resilient", "cold"])
        .to_pandas()
        .groupby("NHDPlusID")
        .first()
    )
    if len(resilient) == 0:
        df["resilient"] = False
        df["cold"] = False
    else:
        df = df.join(resilient, on="NHDPlusID")
        df["resilient"] = df.resilient.fillna(0).astype("bool")
        df["cold"] = df.cold.fillna(0).astype("bool")

    # total lengths used for upstream network
    total_miles = (df["length"].groupby(level=0).sum() * METERS_TO_MILES).rename("total_miles")
    perennial_miles = (df.loc[~df.intermittent, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename(
        "perennial_miles"
    )
    intermittent_miles = (df.loc[df.intermittent, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename(
        "intermittent_miles"
    )
    altered_miles = (df.loc[df.altered, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename("altered_miles")
    unaltered_miles = (df.loc[~df.altered, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename("unaltered_miles")
    perennial_unaltered_miles = (
        df.loc[~(df.intermittent | df.altered), "length"].groupby(level=0).sum() * METERS_TO_MILES
    ).rename("perennial_unaltered_miles")
    resilient_miles = (df.loc[df.resilient, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename(
        "resilient_miles"
    )
    cold_miles = (df.loc[df.cold, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename("cold_miles")

    # free lengths used for downstream network; these deduct lengths in altered waterbodies
    free_miles = (df.loc[df.free_flowing, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename("free_miles")
    free_perennial_miles = (
        df.loc[df.free_flowing & ~df.intermittent, "length"].groupby(level=0).sum() * METERS_TO_MILES
    ).rename("free_perennial_miles")
    free_intermittent_miles = (
        df.loc[df.free_flowing & df.intermittent, "length"].groupby(level=0).sum() * METERS_TO_MILES
    ).rename("free_intermittent_miles")
    free_altered_miles = (
        df.loc[df.free_flowing & df.altered, "length"].groupby(level=0).sum() * METERS_TO_MILES
    ).rename("free_altered_miles")
    free_unaltered_miles = (
        df.loc[df.free_flowing & ~df.altered, "length"].groupby(level=0).sum() * METERS_TO_MILES
    ).rename("free_unaltered_miles")
    free_perennial_unaltered_miles = (
        df.loc[df.free_flowing & ~(df.intermittent | df.altered), "length"].groupby(level=0).sum() * METERS_TO_MILES
    ).rename("free_perennial_unaltered_miles")
    free_resilient_miles = (
        df.loc[df.free_flowing & df.resilient, "length"].groupby(level=0).sum() * METERS_TO_MILES
    ).rename("free_resilient_miles")
    free_cold_miles = (df.loc[df.free_flowing & df.cold, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename(
        "free_cold_miles"
    )

    lengths = (
        pd.DataFrame(total_miles)
        .join(perennial_miles)
        .join(intermittent_miles)
        .join(altered_miles)
        .join(unaltered_miles)
        .join(perennial_unaltered_miles)
        .join(resilient_miles)
        .join(cold_miles)
        .join(free_miles)
        .join(free_perennial_miles)
        .join(free_intermittent_miles)
        .join(free_altered_miles)
        .join(free_unaltered_miles)
        .join(free_perennial_unaltered_miles)
        .join(free_resilient_miles)
        .join(free_cold_miles)
        .fillna(0)
    ).astype("float32")

    # calculate percent altered
    lengths["pct_unaltered"] = (100.0 * (lengths.unaltered_miles / lengths.total_miles)).clip(0, 100).astype("float32")
    # Note: if there are no perennial miles, this should be 0
    lengths["pct_perennial_unaltered"] = 0.0
    ix = lengths.perennial_miles > 0
    lengths.loc[ix, "pct_perennial_unaltered"] = (
        (100.0 * (lengths.loc[ix].perennial_unaltered_miles / lengths.loc[ix].perennial_miles))
        .clip(0, 100)
        .astype("float32")
    )
    lengths["pct_perennial_unaltered"] = lengths.pct_perennial_unaltered.clip(0, 100).astype("float32")

    lengths["pct_resilient"] = (100 * lengths.resilient_miles / lengths.total_miles).clip(0, 100).astype("float32")
    lengths["pct_cold"] = (100 * lengths.cold_miles / lengths.total_miles).clip(0, 100).astype("float32")

    return lengths


def calculate_floodplain_stats(df):
    """Calculate percent of floodplain covered by natural landcover.

    Parameters
    ----------
    df : DataFrame
        network data frame, must have NHDPlusID and be indexed on networkID

    Returns
    -------
    DataFrame
        natfldpln (percent), nat_floodplain_acres, floodplain_acres
    """

    # Sum floodplain and natural floodplain values, and calculate percent natural floodplain
    # Read in associated floodplain info (using pyarrow for speed in filtering) and join
    fp_stats = (
        dataset(data_dir / "floodplains" / "floodplain_stats.feather", format="feather")
        .to_table(
            filter=pc.field("HUC2").isin(df.HUC2.unique()),
            columns=["NHDPlusID", "floodplain_km2", "nat_floodplain_km2"],
        )
        .to_pandas()
        .set_index("NHDPlusID")
    )
    fp_stats = fp_stats.loc[fp_stats.index.isin(df.NHDPlusID.unique())]

    # sum values to NHDPlusID
    fp_stats = (
        df.join(fp_stats, on="NHDPlusID")[["floodplain_km2", "nat_floodplain_km2"]].groupby(level=0).sum()
        * KM2_TO_ACRES
    ).rename(columns={"floodplain_km2": "floodplain_acres", "nat_floodplain_km2": "nat_floodplain_acres"})
    fp_stats["natfldpln"] = 100 * fp_stats.nat_floodplain_acres / fp_stats.floodplain_acres

    return fp_stats


def calculate_species_habitat_stats(df):
    habitat = (
        pa.dataset.dataset(
            data_dir / "species/derived/combined_species_habitat.feather",
            format="feather",
        )
        .to_table(filter=pc.field("HUC2").isin(df.HUC2.unique()))
        .to_pandas()
        .groupby("NHDPlusID")
        .first()
        .drop(columns=["HUC2"])
    )
    if len(habitat) == 0:
        return pd.DataFrame([], index=df.index.unique().values)

    habitat_cols = habitat.columns

    habitat = df[["NHDPlusID", "length", "free_flowing"]].join(habitat, on="NHDPlusID")

    # drop any columns not present in this set of HUC2s
    habitat_cols = habitat_cols[habitat[habitat_cols].max()].to_list()
    if len(habitat_cols) == 0:
        return pd.DataFrame([], index=df.index.unique().values)

    out = None
    for col in habitat_cols:
        habitat[col] = habitat[col].fillna(0).astype("bool")
        total_miles = (habitat[col] * habitat.length).groupby(level=0).sum().rename(f"{col}_miles") * METERS_TO_MILES
        free_miles = ((habitat[col] & df.free_flowing) * habitat.length).groupby(level=0).sum().rename(
            f"free_{col}_miles"
        ) * METERS_TO_MILES
        habitat_miles = pd.DataFrame(total_miles).join(free_miles)

        if out is None:
            out = habitat_miles
        else:
            out = out.join(habitat_miles)

    return pd.DataFrame([], index=np.unique(df.index.values)).join(out).fillna(0)


def calculate_upstream_waterbody_wetland_stats(df, unaltered_waterbodies, unaltered_wetlands):
    # make sure to count unique wetlands by ID and not double-count if multiple
    # flowlines in network touch same waterbody or
    unaltered_waterbody_acres = (
        (
            (
                df[["lineID"]]
                .join(unaltered_waterbodies, on="lineID", how="inner")
                .reset_index()
                .groupby(["networkID", "wbID"])
                .first()
                .reset_index()
                .groupby("networkID")
                .km2.sum()
            )
            * KM2_TO_ACRES
        )
        .rename("unaltered_waterbody_acres")
        .astype("float32")
    )

    unaltered_wetland_acres = (
        (
            (
                df[["lineID"]]
                .join(unaltered_wetlands, on="lineID", how="inner")
                .reset_index()
                .groupby(["networkID", "wetlandID"])
                .first()
                .reset_index()
                .groupby("networkID")
                .km2.sum()
            )
            * KM2_TO_ACRES
        )
        .rename("unaltered_wetland_acres")
        .astype("float32")
    )

    return (
        pd.DataFrame([], index=np.unique(df.index.values))
        .join(unaltered_waterbody_acres)
        .join(unaltered_wetland_acres)
        .fillna(0)
    )


def calculate_epa_impairment(df):
    """Calculate set of impairments as identified by EPA present in the network.

    Parameters
    ----------
    df : DataFrame
        must have NHDPlusID, HUC2 and be indexed on networkID

    Returns
    -------
    Series
        contains impairment
    """
    cols = [
        "temperature",
        "cause_unknown_impaired_biota",
        "oxygen_depletion",
        "algal_growth",
        "flow_alterations",
        "habitat_alterations",
        "hydrologic_alteration",
        "cause_unknown_fish_kills",
    ]

    epa = (
        dataset(
            data_dir / "epa/derived/epa_flowlines.feather",
            format="feather",
        )
        .to_table(filter=pc.field("HUC2").isin(df.HUC2.unique()), columns=["NHDPlusID"] + cols)
        .to_pandas()
        .set_index("NHDPlusID")
    )
    epa = df.join(epa, on="NHDPlusID", how="inner")
    for col in cols:
        epa[col] = epa[col].fillna(0).astype("bool")

    epa = epa[cols].groupby(level=0).max()
    # convert to codes
    for col in cols:
        epa[col] = epa[col].map({False: "", True: EPA_CAUSE_TO_CODE[col]})

    return epa[cols].apply(lambda row: ",".join([x for x in row if x]), axis=1).rename("impairment")


def calculate_upstream_mainstem_network_stats(df):
    """Calculate total network miles, total perennial miles, total unaltered
    perennial miles based on the upstream mainstem network.

    Parameters
    ----------
    df : DataFrame
        must have HUC2, NHDPlusID, length, perennial, and sizeclass, and be
        indexed on networkID

    Returns
    -------
    DataFrame
        contains mainstem_*_miles columns
    """

    total_miles = (df["length"].groupby(level=0).sum() * METERS_TO_MILES).rename("total_upstream_mainstem_miles")
    perennial_miles = (df.loc[~df.intermittent, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename(
        "perennial_upstream_mainstem_miles"
    )
    intermittent_miles = (df.loc[df.intermittent, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename(
        "intermittent_upstream_mainstem_miles"
    )
    altered_miles = (df.loc[df.altered, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename(
        "altered_upstream_mainstem_miles"
    )
    unaltered_miles = (df.loc[~df.altered, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename(
        "unaltered_upstream_mainstem_miles"
    )
    perennial_unaltered_miles = (
        df.loc[~(df.intermittent | df.altered), "length"].groupby(level=0).sum() * METERS_TO_MILES
    ).rename("perennial_unaltered_upstream_mainstem_miles")

    # calculate percent altered
    pct_unaltered = (
        (100.0 * (unaltered_miles / total_miles))
        .clip(0, 100)
        .astype("float32")
        .rename("pct_upstream_mainstem_unaltered")
    )

    sizeclasses = df.groupby(level=0).sizeclass.nunique().astype("uint8").rename("upstream_mainstem_sizeclasses")

    impairment = calculate_epa_impairment(df).rename("upstream_mainstem_impairment")

    results = (
        pd.DataFrame(total_miles)
        .join(perennial_miles)
        .join(intermittent_miles)
        .join(altered_miles)
        .join(unaltered_miles)
        .join(perennial_unaltered_miles)
        .join(pct_unaltered)
        .join(sizeclasses)
        .join(impairment)
    )

    for col in [c for c in results.columns if c.endswith("_miles")]:
        results[col] = results[col].fillna(0).astype("float32")

    results["upstream_mainstem_sizeclasses"] = results.upstream_mainstem_sizeclasses.fillna(0).astype("uint8")
    results["upstream_mainstem_impairment"] = results.upstream_mainstem_impairment.fillna("")

    return results


def calculate_downstream_mainstem_network_stats(df, focal_barrier_joins):
    """Calculate total network miles, total perennial miles, total unaltered
    perennial miles based on the downstream mainstem network.

    Parameters
    ----------
    df : DataFrame
        must have HUC2, NHDPlusID, length, free_flowing, perennial, and sizeclass, and be indexed on
        networkID

    Returns
    -------
    DataFrame
        contains mainstem_*_miles columns
    """

    total_miles = (df["length"].groupby(level=0).sum() * METERS_TO_MILES).rename("total_downstream_mainstem_miles")
    free_miles = (df.loc[df.free_flowing, "length"].groupby(level=0).sum() * METERS_TO_MILES).rename(
        "free_downstream_mainstem_miles"
    )
    free_perennial_miles = (
        df.loc[df.free_flowing & ~df.intermittent, "length"].groupby(level=0).sum() * METERS_TO_MILES
    ).rename("free_perennial_downstream_mainstem_miles")
    free_intermittent_miles = (
        df.loc[df.free_flowing & df.intermittent, "length"].groupby(level=0).sum() * METERS_TO_MILES
    ).rename("free_intermittent_downstream_mainstem_miles")
    free_altered_miles = (
        df.loc[df.free_flowing & df.altered, "length"].groupby(level=0).sum() * METERS_TO_MILES
    ).rename("free_altered_downstream_mainstem_miles")
    free_unaltered_miles = (
        df.loc[df.free_flowing & ~df.altered, "length"].groupby(level=0).sum() * METERS_TO_MILES
    ).rename("free_unaltered_downstream_mainstem_miles")

    # NOTE: impairment is for the full downstream mainstem, not just free-flowing
    impairment = calculate_epa_impairment(df).rename("downstream_mainstem_impairment")

    # join to barrier downstreams
    results = (
        focal_barrier_joins[["downstream_id"]]
        .join(total_miles, on="downstream_id")
        .join(free_miles, on="downstream_id")
        .join(free_perennial_miles, on="downstream_id")
        .join(free_intermittent_miles, on="downstream_id")
        .join(free_altered_miles, on="downstream_id")
        .join(free_unaltered_miles, on="downstream_id")
        .join(impairment, on="downstream_id")
        .drop(columns=["downstream_id"])
    )

    for col in [c for c in results.columns if c.endswith("_miles")]:
        results[col] = results[col].fillna(0).astype("float32")

    results["downstream_mainstem_impairment"] = results.downstream_mainstem_impairment.fillna("")

    return results


def calculate_downstream_linear_network_stats(down_network_df, focal_barrier_joins, barrier_joins):
    """Calculate downstream statistics for each barrier based on its linear
    downstream network (to next barrier downstream or terminal / outlet) and
    total downstream (to final terminal / outlet).

    Parameters
    ----------
    down_network_df : Pandas DataFrame
        downstream linear networks indexed on networkID of the lineID downstream
        of the barrier. Includes:
        * length
        * free_flowing

    focal_barrier_joins : Pandas DataFrame
        limited to the barrier joins that cut the network type being analyzed
        contains:
        * upstream_id
        * downstream_id
        * kind

    barrier_joins : Pandas DataFrame
        all barrier joins including those that do not cut the network type being analyzed
        contains:
        * upstream_id
        * downstream_id
        * kind

    Returns
    -------
    Pandas DataFrame
        Summary statistics, with one row per barrier.
    """

    # TODO: avoid the reindexing
    down_network_df = down_network_df.reset_index().set_index("lineID")

    # re-derive all focal barriers joins from barrier joins to keep confluences
    # which are otherwise filtered out before calling here
    # TODO: is there a way we can avoid removing these before calling into stats?
    all_focal_barrier_joins = barrier_joins.loc[barrier_joins.index.isin(focal_barrier_joins.index.unique())]

    ### Count barriers that are DOWNSTREAM (linear to terminal / river outlet) of each barrier
    # using a directed graph of all network joins facing downstream

    # First, count all barriers by type per downstream linear network
    # IMPORTANT: the networkID here is the DOWNSTREAM linear network ID
    # also note that there should only ever be 1 of a network-breaking barrier
    # type in the downstream linear network (it terminates the downstream linear network)
    downstream_joins = barrier_joins.loc[barrier_joins.downstream_id != 0].copy()

    # NOTE: ln_downstream also includes the barrier at the join
    ln_downstream = (
        downstream_joins[["downstream_id", "kind", "invasive"]]
        .join(down_network_df[["networkID", "length"]], on="downstream_id", how="inner")
        .reset_index(drop=True)
    )

    ln_downstream_counts = (
        ln_downstream.groupby(["networkID", "kind"])
        .size()
        .rename("count")
        .reset_index()
        .pivot(index="networkID", columns="kind", values="count")
        .fillna(0)
    )

    # make sure all barrier types have a count column
    for kind in ["waterfall", "dam", "small_barrier", "road_crossing"]:
        if kind not in ln_downstream_counts.columns:
            ln_downstream_counts[kind] = 0

    # calculate total length of each individual downstream network (to next barrier downstream)
    total_miles = (down_network_df.groupby("networkID").length.sum() * METERS_TO_MILES).rename(
        "total_linear_downstream_miles"
    )

    free_miles = (
        down_network_df.loc[down_network_df.free_flowing].groupby("networkID").length.sum() * METERS_TO_MILES
    ).rename("free_linear_downstream_miles")
    free_perennial_miles = (
        down_network_df.loc[(~down_network_df.intermittent) & down_network_df.free_flowing]
        .groupby("networkID")
        .length.sum()
        * METERS_TO_MILES
    ).rename("free_perennial_linear_downstream_miles")
    free_intermittent_miles = (
        down_network_df.loc[down_network_df.intermittent & down_network_df.free_flowing]
        .groupby("networkID")
        .length.sum()
        * METERS_TO_MILES
    ).rename("free_intermittent_linear_downstream_miles")
    free_altered_miles = (
        down_network_df.loc[down_network_df.altered & down_network_df.free_flowing].groupby("networkID").length.sum()
        * METERS_TO_MILES
    ).rename("free_altered_linear_downstream_miles")
    free_unaltered_miles = (
        down_network_df.loc[(~down_network_df.altered) & down_network_df.free_flowing].groupby("networkID").length.sum()
        * METERS_TO_MILES
    ).rename("free_unaltered_linear_downstream_miles")

    # join to barrier downstreams
    barrier_downstream_miles = (
        focal_barrier_joins[["downstream_id"]]
        .join(total_miles, on="downstream_id")
        .join(free_miles, on="downstream_id")
        .join(free_perennial_miles, on="downstream_id")
        .join(free_intermittent_miles, on="downstream_id")
        .join(free_altered_miles, on="downstream_id")
        .join(free_unaltered_miles, on="downstream_id")
        .drop(columns=["downstream_id"])
        .fillna(0)
        .astype("float32")
    )

    ### Use a graph of network joins facing downward to aggregate these to a
    # total count per barrier

    # extract joins between downstream linear networks using all_focal_barrier_joins
    # to traverse confluences
    # NOTE: these won't have any entries at top of network
    # WARNING: this does not include entries for any confluences where one side
    # is not part of a barrier downstream network (i.e., has no cutting barriers
    # upstream)

    downstream_network_joins = all_focal_barrier_joins.join(
        down_network_df.networkID, on="upstream_id", how="inner"
    ).rename(columns={"networkID": "upstream_network", "downstream_id": "downstream_network"})

    downstream_graph = DirectedGraph(
        downstream_network_joins.upstream_network.values.astype("int64"),
        downstream_network_joins.downstream_network.values.astype("int64"),
    )

    # search from the lineID immediately downstream of each focal barrier
    # but indexed on the id
    search_ids = focal_barrier_joins.loc[(focal_barrier_joins.downstream_id != 0)].downstream_id

    # mapping of id to all downstream linear networks downstream of the
    # linear network immediately below the barrier
    next_downstreams = (
        pd.Series(
            downstream_graph.descendants(search_ids.values.astype("int64")),
            index=search_ids.index,
            name="downstream_network",
        )
        .explode()
        .dropna()
    )

    # add in all entries for each id to downstream network that starts
    # from its downstream_id
    downstreams = (
        pd.concat(
            [
                search_ids.reset_index().rename(
                    columns={
                        "downstream_id": "downstream_network",
                    }
                ),
                next_downstreams.reset_index(),
            ],
            ignore_index=True,
            sort=False,
        )
        .drop_duplicates()
        .set_index("id")
    )

    # Downstream stats quantify how many barriers / length exists on the linear
    # downstream BELOW the upstream functional network associated with each barrier
    # without counting that barrier itself (subtracted below)

    # count of barrier type of the barrier itself so that we can subtract it
    # from the count of barriers at or below the barrier

    self_counts = (
        focal_barrier_joins.reset_index()
        .groupby(["id", "kind"])
        .size()
        .rename("count")
        .reset_index()
        .pivot(index="id", columns="kind", values="count")
    )

    total_downstream_stats = (
        downstreams.join(ln_downstream_counts, on="downstream_network")
        .join(total_miles.rename("miles_to_outlet"), on="downstream_network")
        .drop(columns=["downstream_network"])
        .groupby(level=0)
        .sum()
        .join(self_counts, rsuffix="_self")
        .fillna(0)
    )

    # subtract barrier type of the upstream network from the stats
    self_cols = [c for c in total_downstream_stats.columns if c.endswith("_self")]
    for col in self_cols:
        main_col = col.replace("_self", "")
        total_downstream_stats[main_col] = total_downstream_stats[main_col] - total_downstream_stats[col]

    total_downstream_stats = total_downstream_stats.drop(columns=self_cols).rename(
        columns={
            "dam": "totd_dams",
            "waterfall": "totd_waterfalls",
            "small_barrier": "totd_small_barriers",
            "road_crossing": "totd_road_crossings",
        }
    )

    # DEBUG: to output a downstream network based on a id <bid>
    # lids = (
    #     downstreams.loc[downstreams.index == bid, ["downstream_network"]]
    #     .join(
    #         down_network_df.reset_index().set_index("networkID").lineID,
    #         on="downstream_network",
    #     )
    #     .lineID.unique()
    # )
    # write_dataframe(flowlines.loc[flowlines.index.isin(lids)],'/tmp/test_downstream.fgb')

    ### Identify networks that have an invasive barrier downstream
    invasive_barriers = all_focal_barrier_joins.loc[all_focal_barrier_joins.invasive].index.unique()
    invasive_ids = focal_barrier_joins.loc[focal_barrier_joins.invasive].upstream_id.unique()
    invasive_downstream = down_network_df.loc[down_network_df.index.isin(invasive_ids)].networkID.unique()
    invasive_downstream_ids = downstreams.loc[downstreams.downstream_network.isin(invasive_downstream)].index.unique()
    invasive_network = pd.Series(
        np.zeros(shape=(len(focal_barrier_joins),), dtype="bool"),
        index=focal_barrier_joins.index,
        name="invasive_network",
    )
    invasive_network.loc[
        invasive_network.index.isin(invasive_barriers) | invasive_network.index.isin(invasive_downstream_ids)
    ] = True

    results = focal_barrier_joins[[]].join(barrier_downstream_miles).join(total_downstream_stats).join(invasive_network)

    # set appropriate nodata
    count_cols = [c for c in total_downstream_stats.columns if c.startswith("totd_")]
    results[count_cols] = results[count_cols].fillna(0).astype("uint32")
    results.miles_to_outlet = results.miles_to_outlet.fillna(0)

    return results
