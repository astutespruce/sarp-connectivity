from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import numpy as np

from analysis.lib.graph.speedups import DirectedGraph

data_dir = Path("data")

METERS_TO_MILES = 0.000621371
COUNT_KINDS = ["waterfalls", "dams", "small_barriers", "road_crossings", "headwaters"]


def calculate_upstream_network_stats(up_network_df, joins, focal_barrier_joins, barrier_joins):
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

    Returns
    -------
    Pandas DataFrame
        Summary statistics, with one row per functional network.
    """

    # find the HUC2 of the network origin
    root_huc2 = up_network_df.loc[up_network_df.index == up_network_df.lineID].HUC2.rename("origin_HUC2")

    # count unique size classes in upstream functional network
    sizeclasses = up_network_df.groupby(level=0).sizeclass.nunique().astype("uint8").rename("sizeclasses")

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
    fn_upstream_area = up_network_df.groupby(level=0).AreaSqKm.sum().rename("fn_dakm2")

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
        .join(networkID, on="upstream_id", how="inner")
        .set_index("networkID")
        .kind.rename("barrier")
    )

    ### Collect results
    results = (
        calculate_geometry_stats(up_network_df)
        .join(calculate_species_habitat_stats(up_network_df))
        .join(calculate_floodplain_stats(up_network_df))
        .join(sizeclasses)
        .join(fn_upstream_counts)
        .join(fn_upstream_area)
        .join(tot_upstream_counts)
        .join(network_barrier)
        .join(root_huc2)
    )

    # index name is getting dropped in some cases
    results.index.name = "networkID"

    # backfill count columns
    count_cols = fn_upstream_counts.columns.tolist() + tot_upstream_counts.columns.tolist()
    results[count_cols] = results[count_cols].fillna(0)

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
    perennial_length = df.loc[~df.intermittent, "length"].groupby(level=0).sum().rename("perennial")
    intermittent_length = df.loc[df.intermittent, "length"].groupby(level=0).sum().rename("intermittent")
    altered_length = df.loc[df.altered, "length"].groupby(level=0).sum().rename("altered")
    unaltered_length = df.loc[~df.altered, "length"].groupby(level=0).sum().rename("unaltered")
    perennial_unaltered_length = (
        df.loc[~(df.intermittent | df.altered), "length"].groupby(level=0).sum().rename("perennial_unaltered")
    )

    # free lengths used for downstream network; these deduct lengths in waterbodies
    free_length = df.loc[~df.waterbody, "length"].groupby(level=0).sum().rename("free")
    free_perennial = df.loc[~(df.intermittent | df.waterbody), "length"].groupby(level=0).sum().rename("free_perennial")
    free_intermittent = (
        df.loc[df.intermittent & (~df.waterbody), "length"].groupby(level=0).sum().rename("free_intermittent")
    )
    free_altered_length = df.loc[df.altered & (~df.waterbody), "length"].groupby(level=0).sum().rename("free_altered")
    free_unaltered_length = (
        df.loc[~(df.waterbody | df.altered), "length"].groupby(level=0).sum().rename("free_unaltered")
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
    lengths["pct_unaltered"] = (100.0 * (lengths.unaltered_miles / lengths.total_miles)).astype("float32")
    # Note: if there are no perennial miles, this should be 0
    lengths["pct_perennial_unaltered"] = 0.0
    ix = lengths.perennial_miles > 0
    lengths.loc[ix, "pct_perennial_unaltered"] = (
        100.0 * (lengths.loc[ix].perennial_unaltered_miles / lengths.loc[ix].perennial_miles)
    ).astype("float32")
    lengths["pct_perennial_unaltered"] = lengths.pct_perennial_unaltered.astype("float32")

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
        natfldpln (percent), nat_floodplain_km2, floodplain_km2
    """

    # Sum floodplain and natural floodplain values, and calculate percent natural floodplain
    # Read in associated floodplain info (using pyarrow for speed in filtering) and join
    fp_stats = (
        pa.dataset.dataset(data_dir / "floodplains" / "floodplain_stats.feather", format="feather")
        .to_table(
            filter=pc.field("HUC2").isin(df.HUC2.unique()),
            columns=["NHDPlusID", "floodplain_km2", "nat_floodplain_km2"],
        )
        .to_pandas()
        .set_index("NHDPlusID")
    )
    fp_stats = fp_stats.loc[fp_stats.index.isin(df.NHDPlusID.unique())]

    # sum values to NHDPlusID
    fp_stats = df.join(fp_stats, on="NHDPlusID")[["floodplain_km2", "nat_floodplain_km2"]].groupby(level=0).sum()
    fp_stats["natfldpln"] = 100 * fp_stats.nat_floodplain_km2 / fp_stats.floodplain_km2

    return fp_stats


def calculate_species_habitat_stats(df):
    habitat = (
        pa.dataset.dataset(
            data_dir / "species/derived/combined_species_habitat.feather",
            format="feather",
        )
        .to_table(filter=pc.field("HUC2").isin(df.HUC2.unique()))
        .to_pandas()
        .set_index("NHDPlusID")
        .drop(columns=["HUC2"])
    )
    if len(habitat) == 0:
        return pd.DataFrame([], index=df.index.unique().values)

    habitat_cols = habitat.columns

    habitat = df[["NHDPlusID", "length", "waterbody"]].join(habitat, on="NHDPlusID")

    # drop any columns not present in this set of HUC2s
    habitat_cols = habitat_cols[habitat[habitat_cols].max()].to_list()
    if len(habitat_cols) == 0:
        return pd.DataFrame([], index=df.index.unique().values)

    out = None
    for col in habitat_cols:
        habitat[col] = habitat[col].fillna(False)
        total_miles = (habitat[col] * habitat.length).groupby(level=0).sum().rename(f"{col}_miles") * METERS_TO_MILES
        free_miles = ((habitat[col] & (~habitat.waterbody)) * habitat.length).groupby(level=0).sum().rename(
            f"free_{col}_miles"
        ) * METERS_TO_MILES
        habitat_miles = pd.DataFrame(total_miles).join(free_miles)

        if out is None:
            out = habitat_miles
        else:
            out = out.join(habitat_miles)

    return pd.DataFrame([], index=np.unique(df.index.values)).join(out).fillna(0)


def calculate_downstream_stats(
    down_network_df,
    focal_barrier_joins,
    barrier_joins,
    marine_ids,
    great_lake_ids,
    exit_ids,
):
    """Calculate downstream statistics for each barrier.  Downstream networks
    are linear from the barrier to the downstream terminal.

    Parameters
    ----------
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

    marine_ids : ndarray
        lineIDs of segments that directly connect to marine

    great_lake_ids : ndarray
        lineIDs of segments that directly connect to Great Lakes

    exit_ids : ndarray
        lineIDs of segments that directly leave the HUC2

    Returns
    -------
    Pandas DataFrame
        Summary statistics, with one row per barrier.
    """

    # TODO: avoid the reindexing
    down_network_df = down_network_df.reset_index().set_index("lineID")

    # re-rederive all focal barriers joins from barrier joins to keep confluences
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
    )

    # make sure all barrier types have a count column
    for kind in ["waterfall", "dam", "small_barrier", "road_crossing"]:
        if kind not in ln_downstream_counts.columns:
            ln_downstream_counts[kind] = 0

    # calculate total length of each downstream network
    ln_downstream_length = down_network_df.groupby("networkID").length.sum()

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

    downstream_stats = (
        downstreams.join(ln_downstream_counts, on="downstream_network")
        .join(ln_downstream_length, on="downstream_network")
        .drop(columns=["downstream_network"])
        .groupby(level=0)
        .sum()
        .join(self_counts, rsuffix="_self")
        .fillna(0)
    )
    downstream_stats["length"] = downstream_stats["length"] * METERS_TO_MILES

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

    ### Identify networks that terminate in marine
    # ids of barriers that connect directly to marine
    marine_barriers = all_focal_barrier_joins.loc[all_focal_barrier_joins.upstream_id.isin(marine_ids)].index.unique()

    # downstream networks that connect to marine via downstream linear networks
    marine_downstream = down_network_df.loc[down_network_df.index.isin(marine_ids)].networkID.unique()
    marine_downstream_ids = downstreams.loc[downstreams.downstream_network.isin(marine_downstream)].index.unique()

    to_ocean = pd.Series(
        np.zeros(shape=(len(focal_barrier_joins),), dtype="bool"),
        index=focal_barrier_joins.index,
        name="flows_to_ocean",
    )
    to_ocean.loc[to_ocean.index.isin(marine_barriers) | to_ocean.index.isin(marine_downstream_ids)] = True

    ### Identify networks that terminate in Great Lakes
    # ids of barriers that connect directly to Great Lakes
    great_lake_barriers = all_focal_barrier_joins.loc[
        all_focal_barrier_joins.upstream_id.isin(great_lake_ids)
    ].index.unique()

    # downstream networks that connect to Great Lakes via downstream linear networks
    great_lake_downstream = down_network_df.loc[down_network_df.index.isin(great_lake_ids)].networkID.unique()
    great_lake_downstream_ids = downstreams.loc[
        downstreams.downstream_network.isin(great_lake_downstream)
    ].index.unique()

    to_great_lakes = pd.Series(
        np.zeros(shape=(len(focal_barrier_joins),), dtype="bool"),
        index=focal_barrier_joins.index,
        name="flows_to_great_lakes",
    )
    to_great_lakes.loc[
        to_great_lakes.index.isin(great_lake_barriers) | to_great_lakes.index.isin(great_lake_downstream_ids)
    ] = True

    ### Identify any networks that exit HUC2s
    # Note: only applicable for those that exit into HUC2s outside the analysis region

    # ids of barriers that connect directly to exits
    exit_barriers = all_focal_barrier_joins.loc[all_focal_barrier_joins.upstream_id.isin(exit_ids)].index.unique()

    # networks connected to huc2 exits via downstream linear networks
    exit_downstream = down_network_df.loc[down_network_df.index.isin(exit_ids)].networkID.unique()
    exit_downstream_ids = downstreams.loc[downstreams.downstream_network.isin(exit_downstream)].index.unique()

    exits_region = pd.Series(
        np.zeros(shape=(len(focal_barrier_joins),), dtype="bool"),
        index=focal_barrier_joins.index,
        name="exits_region",
    )
    exits_region.loc[
        exits_region.index.isin(exit_barriers)
        | exits_region.index.isin(exit_downstream_ids)
        # any that connect to ocean also exit the region
        | exits_region.index.isin(to_ocean.loc[to_ocean].index)
    ] = True

    results = focal_barrier_joins[[]].join(downstream_stats).join(to_ocean).join(to_great_lakes).join(exits_region)

    # set appropriate nodata
    count_cols = [c for c in downstream_stats.columns if c.startswith("totd_")]
    results[count_cols] = results[count_cols].fillna(0).astype("uint32")
    results.miles_to_outlet = results.miles_to_outlet.fillna(0)

    return results
