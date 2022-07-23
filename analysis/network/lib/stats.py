from pathlib import Path

import pandas as pd
import pyarrow.compute as pc
import pyarrow.dataset as pa
import numpy as np

from analysis.lib.graph.speedups import DirectedGraph

data_dir = Path("data")

METERS_TO_MILES = 0.000621371


def calculate_network_stats(
    up_network_df, down_network_df, focal_barrier_joins, barrier_joins, joins
):
    """Calculation of network statistics, for each functional network.

    Parameters
    ----------
    up_network_df : Pandas DataFrame
        upstream networks indexed on networkID of the lineID upstream of the
        barrier.  Includes the basic metrics for each flowline segment:
        * length
        * size class
        * altered
        * intermittent

    down_network_df : Pandas DataFrame
        downstream linear networks indexed on networkID of the lineID downstream
        of the barrier. Includes:
        * length

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

    joins : Pandas DataFrame
        all flowline joins
        contains:
        * upstream_id
        * downstream_id
        * type
        * marine

    Returns
    -------
    Pandas DataFrame
        Summary statistics, with one row per functional network.
    """

    down_network_df = down_network_df.reset_index().set_index("lineID")

    # re-rederive all focal barriers joins from barrier joins to keep confluences
    # which are otherwise filtered out before calling here
    all_focal_barrier_joins = barrier_joins.loc[
        barrier_joins.index.isin(focal_barrier_joins.index.unique())
    ]

    # find the HUC2 of the network origin
    root_huc2 = up_network_df.loc[
        up_network_df.index == up_network_df.lineID
    ].HUC2.rename("origin_HUC2")

    # create series of networkID indexed by lineID
    networkID = up_network_df.reset_index().set_index("lineID").networkID
    networkIDs = pd.Series(networkID.unique(), name="networkID")

    ### Count the number of barriers of each type WITHIN or TERMINATING the upstream functional
    # network of each barrier.  Barriers of a lesser type than the one
    # used to cut the network are within the network, those of equal or greater type
    # terminate the network.  By definition, they are any with downstream_ids
    # that are in the lineIDs associated with the current networkID

    # limit barrier_joins to those with downstream IDs present within these networks
    upstream_joins = barrier_joins.loc[
        barrier_joins.downstream_id.isin(networkID.index.unique())
    ].copy()

    fn_barriers_upstream = (
        upstream_joins[["downstream_id", "kind"]]
        .join(networkID, on="downstream_id", how="inner")
        .reset_index()[["networkID", "kind"]]
    )
    fn_upstream_counts = (
        fn_barriers_upstream.groupby(["networkID", "kind"])
        .size()
        .rename("count")
        .reset_index()
        .pivot(index="networkID", columns="kind", values="count")
        .fillna(0)
        .astype("uint32")
        .rename(
            columns={
                "dam": "fn_dams",
                "waterfall": "fn_waterfalls",
                "small_barrier": "fn_small_barriers",
                "road_crossing": "fn_road_crossings",
            }
        )
    )
    fn_upstream_area = up_network_df.groupby(level=0).AreaSqKm.sum().rename("fn_dakm2")

    ### Count TOTAL barriers of each kind in the total upstream network(s),
    # (not limited to upstream functional network) using a directed graph of
    # network joins facing upstream

    # find all focal joins that are internal to the network (not at upstream or
    # downstream end) then use these to define the joins between adjacent networks
    # NOTE: upstream_ids that are not also networks (because of confluences) are
    # removed prior to calling here
    network_joins = (
        focal_barrier_joins.loc[
            (focal_barrier_joins.upstream_id != 0)
            & (focal_barrier_joins.downstream_id != 0)
        ]
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
                .astype("uint32")
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
            }
        )
        .groupby("networkID")
        .sum()
    )

    ### Count barriers for the immediate catchment, spanning multiple upstream
    # networks if on the same NHDPlusID

    # for every barrier join, get associated NHDPlusID
    nhdplusID = barrier_joins.join(
        up_network_df.reset_index().set_index("lineID")[["networkID", "NHDPlusID"]],
        on="upstream_id",
        how="inner",
    ).NHDPlusID

    # use all_barrier_joins because these include confluences
    network_nhdplusID = (
        all_focal_barrier_joins.join(nhdplusID, how="inner")
        .join(networkID, on="upstream_id")
        .set_index("networkID")
        .NHDPlusID
    )

    # then for each set of upstream barriers within the functional network of a given
    # barrier, filter those to ones on the same NHDPlusID
    cat_barriers_upstream = (
        (
            upstream_joins[["downstream_id", "kind"]].join(
                networkID, on="downstream_id", how="inner"
            )
        )
        .join(nhdplusID, how="inner")
        .join(network_nhdplusID, on="networkID", rsuffix="_network", how="inner")
    )
    cat_barriers_upstream = cat_barriers_upstream.loc[
        cat_barriers_upstream.NHDPlusID == cat_barriers_upstream.NHDPlusID_network
    ]

    cat_upstream_counts = (
        cat_barriers_upstream.groupby(["networkID", "kind"])
        .size()
        .rename("count")
        .reset_index()
        .pivot(index="networkID", columns="kind", values="count")
        .fillna(0)
        .astype("uint32")
        .rename(
            columns={
                "dam": "cat_dams",
                "waterfall": "cat_waterfalls",
                "small_barrier": "cat_small_barriers",
                "road_crossing": "cat_road_crossings",
            }
        )
    )

    ### Count barriers that are DOWNSTREAM (linear to terminal / river outlet) of each barrier
    # using a directed graph of all network joins facing downstream

    # First, count all barriers by type per downstream linear network
    # IMPORTANT: the networkID here is the DOWNSTREAM linear network ID
    # also note that there should only ever be 1 of a network-breaking barrier
    # type in the downstream linear network (it terminates the downstream linear network)
    downstream_joins = barrier_joins.loc[barrier_joins.downstream_id != 0].copy()

    # NOTE: ln_downstream also includes the barrier at the join
    ln_downstream = (
        downstream_joins[["downstream_id", "kind"]]
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
        .astype("uint32")
    )

    # calculate total length of each downstream network
    ln_downstream_length = down_network_df.groupby("networkID").length.sum()

    # Next use a graph of network joins facing downward to aggregate these to a
    # total count per barrier

    # extract joins between downstream linear networks using all_focal_barrier_joins
    # to traverse confluences
    # NOTE: these won't have any entries at top of network
    # WARNING: this does not include entries for any confluences where one side
    # is not part of a barrier downstream network (i.e., has no cutting barriers
    # upstream)

    downstream_network_joins = all_focal_barrier_joins.join(
        down_network_df.networkID, on="upstream_id", how="inner"
    ).rename(
        columns={"networkID": "upstream_network", "downstream_id": "downstream_network"}
    )

    downstream_graph = DirectedGraph(
        downstream_network_joins.upstream_network.values.astype("int64"),
        downstream_network_joins.downstream_network.values.astype("int64"),
    )

    # search from the lineID immediately downstream of each focal barrier
    # but indexed on the barrierID so that we can rejoin to networkID for barrier
    # which might be different than upstream_id of downstream_joins because
    # of confluences
    search_ids = focal_barrier_joins.loc[
        (focal_barrier_joins.upstream_id != 0)
        & (focal_barrier_joins.downstream_id != 0)
    ].downstream_id

    # mapping of upstream functional networkID to all downstream linear network
    # downstream of the linear network immediately below the barrier
    next_downstreams = (
        pd.Series(
            downstream_graph.descendants(search_ids.values.astype("int64")),
            index=search_ids.index,
            name="downstream_network",
        )
        .explode()
        .dropna()
    )

    # add in all entries for each barrierID to immediate downstream network
    downstreams = (
        all_focal_barrier_joins.loc[all_focal_barrier_joins.upstream_id != 0][
            ["upstream_id"]
        ]
        .rename(columns={"upstream_id": "networkID"})
        .join(
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
            ).set_index("barrierID")
        )
    ).drop_duplicates()

    # Downstream stats quantify how many barriers / length exists on the linear
    # downstream BELOW the upstream functional network associated with each barrier
    # without counting that barrier itself (subtracted below)

    downstream_stats = (
        downstreams.join(ln_downstream_counts, on="downstream_network")
        .join(ln_downstream_length, on="downstream_network")
        .drop(columns=["downstream_network"])
        .groupby("networkID")
        .sum()
        # join in count of barrier type of the upstream network so we can subtract it
        .join(
            network_joins.groupby(["upstream_network", "kind"])
            .size()
            .rename("count")
            .reset_index()
            .pivot(index="upstream_network", columns="kind", values="count"),
            rsuffix="_self",
        )
        .fillna(0)
    )
    downstream_stats["length"] = (downstream_stats["length"] * METERS_TO_MILES).astype(
        "float32"
    )

    # subtract barrier type of the upstream network from the stats
    self_cols = [c for c in downstream_stats.columns if c.endswith("_self")]
    for col in self_cols:
        main_col = col.replace("_self", "")
        downstream_stats[main_col] = downstream_stats[main_col] - downstream_stats[col]

    downstream_stats = downstream_stats.drop(columns=self_cols).rename(
        columns={
            "dam": "totd_dams",
            "waterfall": "totd_waterfalls",
            "small_barrier": "totd_small_barriers",
            "road_crossing": "totd_road_crossings",
            "length": "miles_to_outlet",
        }
    )

    # DEBUG: to output a downstream network based on an upstream functional networkID <nid>
    # lids = (
    #     downstreams.loc[downstreams.index == nid, ["downstream_network"]]
    #     .join(
    #         down_network_df.reset_index().set_index("networkID").lineID,
    #         on="downstream_network",
    #     )
    #     .lineID.unique()
    # )
    # write_dataframe(flowlines.loc[flowlines.index.isin(lids)],'/tmp/test_downstream.fgb')

    ### Identify networks that terminate in marine

    # networks that terminate in marine
    marine_ids = joins.loc[joins.marine].upstream_id.unique()

    # networks that connect to marine via downstream linear networks
    marine_downstream = down_network_df.loc[
        down_network_df.index.isin(marine_ids)
    ].networkID.unique()
    marine_downstream_ids = downstreams.loc[
        downstreams.downstream_network.isin(marine_downstream)
    ].networkID.unique()

    # include any that are themselves marine connected
    to_ocean = pd.Series(
        np.zeros(shape=(len(networkIDs),), dtype="bool"),
        index=networkIDs,
        name="flows_to_ocean",
    )
    to_ocean.loc[
        to_ocean.index.isin(marine_ids) | to_ocean.index.isin(marine_downstream_ids)
    ] = True

    ### Identify any networks that exit HUC2s
    # Note: only applicable for those that exit into HUC2s outside the analysis region
    exit_ids = joins.loc[joins.type == "huc2_drain"].upstream_id.unique()

    # networks directly connected to huc2 exits
    exit_connected_ids = networkID.loc[networkID.index.isin(exit_ids)].unique()

    # networks connected to huc2 exits via downstream linear networks
    exit_downstream = down_network_df.loc[
        down_network_df.index.isin(exit_ids)
    ].networkID.unique()
    exit_downstream_ids = downstreams.loc[
        downstreams.downstream_network.isin(exit_downstream)
    ].networkID.unique()

    exits_region = pd.Series(
        np.zeros(shape=(len(networkIDs),), dtype="bool"),
        index=networkIDs,
        name="exits_region",
    )
    exits_region.loc[
        exits_region.index.isin(exit_connected_ids)
        | exits_region.index.isin(exit_downstream_ids)
        # any that connect to ocean also exit the region
        | exits_region.index.isin(to_ocean.loc[to_ocean].index)
    ] = True

    ### Extract downstream barrier type.
    # on the downstream side of a network, there will only be at most a single barrier.
    # Identify all barriers that have a given network upstream of them.
    barrier_type_downstream = (
        focal_barrier_joins[["upstream_id", "kind"]]
        .join(networkID, on="upstream_id", how="inner")
        .reset_index()[["networkID", "kind"]]
        # there are some duplicates due to a barrier having multiple upstream
        # network segments at confluences
        .drop_duplicates()
        .set_index("networkID")
        .kind.rename("barrier")
    )

    sizeclasses = (
        up_network_df.groupby(level=0)
        .sizeclass.nunique()
        .astype("uint8")
        .rename("sizeclasses")
    )

    ### Collect results
    results = (
        calculate_geometry_stats(up_network_df)
        .join(calculate_floodplain_stats(up_network_df))
        .join(sizeclasses)
        .join(fn_upstream_counts)
        .join(fn_upstream_area)
        .join(cat_upstream_counts)
        .join(tot_upstream_counts)
        .join(barrier_type_downstream)
        .join(downstream_stats)
        .join(to_ocean)
        .join(exits_region)
        .join(root_huc2)
    )

    # index name is getting dropped in some cases
    results.index.name = "networkID"

    count_cols = (
        fn_upstream_counts.columns.tolist()
        + cat_upstream_counts.columns.tolist()
        + tot_upstream_counts.columns.tolist()
        + [c for c in downstream_stats.columns if c.startswith("totd_")]
    )

    # make sure all count columns are at least present
    for stat_type in ["fn", "cat", "tot", "totd"]:
        for kind in ["waterfalls", "dams", "small_barriers", "road_crossings"]:
            col = f"{stat_type}_{kind}"
            if not col in results.columns:
                results[col] = 0

    results[count_cols] = results[count_cols].fillna(0).astype("uint32")
    results.barrier = results.barrier.fillna("")
    results.miles_to_outlet = results.miles_to_outlet.fillna(0)

    return results


def calculate_geometry_stats(df):
    """Calculate total network miles, free-flowing miles (not in waterbodies),
    free-flowing unaltered miles (not in waterbodies, not altered), total
    perennial miles, total free-flowing unaltered perennial miles.

    Parameters
    ----------
    df : DataFrame
        must have length, waterbody, altered, and perennial, and be indexed on
        networkID

    Returns
    -------
    DataFrame
        contains total_miles, free_miles, *_miles
    """

    # total lengths used for upstream network
    total_length = df["length"].groupby(level=0).sum().rename("total")
    perennial_length = (
        df.loc[~df.intermittent, "length"].groupby(level=0).sum().rename("perennial")
    )
    intermittent_length = (
        df.loc[df.intermittent, "length"].groupby(level=0).sum().rename("intermittent")
    )
    altered_length = (
        df.loc[df.altered, "length"].groupby(level=0).sum().rename("altered")
    )
    unaltered_length = (
        df.loc[~df.altered, "length"].groupby(level=0).sum().rename("unaltered")
    )
    perennial_unaltered_length = (
        df.loc[~(df.intermittent | df.altered), "length"]
        .groupby(level=0)
        .sum()
        .rename("perennial_unaltered")
    )

    # free lengths used for downstream network; these deduct lengths in waterbodies
    free_length = df.loc[~df.waterbody, "length"].groupby(level=0).sum().rename("free")
    free_perennial = (
        df.loc[~(df.intermittent | df.waterbody), "length"]
        .groupby(level=0)
        .sum()
        .rename("free_perennial")
    )
    free_intermittent = (
        df.loc[df.intermittent & (~df.waterbody), "length"]
        .groupby(level=0)
        .sum()
        .rename("free_intermittent")
    )
    free_altered_length = (
        df.loc[df.altered & (~df.waterbody), "length"]
        .groupby(level=0)
        .sum()
        .rename("free_altered")
    )
    free_unaltered_length = (
        df.loc[~(df.waterbody | df.altered), "length"]
        .groupby(level=0)
        .sum()
        .rename("free_unaltered")
    )
    free_perennial_unaltered = (
        df.loc[~(df.intermittent | df.waterbody | df.altered), "length"]
        .groupby(level=0)
        .sum()
        .rename("free_perennial_unaltered")
    )

    lengths = (
        pd.DataFrame(total_length)
        .join(perennial_length)
        .join(intermittent_length)
        .join(altered_length)
        .join(unaltered_length)
        .join(perennial_unaltered_length)
        .join(free_length)
        .join(free_perennial)
        .join(free_intermittent)
        .join(free_altered_length)
        .join(free_unaltered_length)
        .join(free_perennial_unaltered)
        .fillna(0)
        * METERS_TO_MILES
    ).astype("float32")
    lengths.columns = [f"{c}_miles" for c in lengths.columns]

    # calculate percent altered
    lengths["pct_unaltered"] = (
        100 * (lengths.unaltered_miles / lengths.total_miles)
    ).astype("float32")
    # Note: if there are no perennial miles, this should be 0
    lengths["pct_perennial_unaltered"] = 0
    lengths.loc[lengths.perennial_miles > 0, "pct_perennial_unaltered"] = 100 * (
        lengths.perennial_unaltered_miles / lengths.perennial_miles
    )
    lengths["pct_perennial_unaltered"] = lengths.pct_perennial_unaltered.astype(
        "float32"
    )

    return lengths


def calculate_floodplain_stats(df):
    """Calculate percent of floodplain covered by natural landcover.

    Parameters
    ----------
    df : DataFrame
        network data frame, must have NHDPlusID and be indexed on networkID

    Returns
    -------
    Series
        natfldpln
    """

    # Sum floodplain and natural floodplain values, and calculate percent natural floodplain
    # Read in associated floodplain info (using pyarrow for speed in filtering) and join
    fp_stats = (
        pa.dataset(
            data_dir / "floodplains" / "floodplain_stats.feather", format="feather"
        )
        .to_table(
            filter=pc.field("NHDPlusID").isin(df.NHDPlusID.unique()),
            columns=["NHDPlusID", "floodplain_km2", "nat_floodplain_km2"],
        )
        .to_pandas()
        .set_index("NHDPlusID")
    )

    df = df.join(fp_stats, on="NHDPlusID")

    pct_nat_df = df[["floodplain_km2", "nat_floodplain_km2"]].groupby(level=0).sum()

    return (
        (100 * pct_nat_df.nat_floodplain_km2 / pct_nat_df.floodplain_km2)
        .astype("float32")
        .rename("natfldpln")
    )
