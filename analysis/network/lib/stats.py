from pathlib import Path

import pandas as pd
import numpy as np

from analysis.lib.graph import DirectedGraph

data_dir = Path("data")

METERS_TO_MILES = 0.000621371


def calculate_network_stats(df, barrier_joins, joins):
    """Calculation of network statistics, for each functional network.

    Parameters
    ----------
    df : Pandas DataFrame
        data frame including the basic metrics for each flowline segment, including:
        * length
        * sinuosity
        * size class
        * altered
        * intermittent

    barrier_joins : Pandas DataFrame
        contains:
        * upstream_id
        * downstream_id
        * kind

    joins : Pandas DataFrame
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

    # find the HUC2 of the network origin
    root_huc2 = df.loc[df.index == df.lineID].HUC2.rename("origin_HUC2")

    # create series of networkID indexed by lineID
    networkID = df.reset_index().set_index("lineID").networkID
    networkIDs = networkID.unique()

    ### Find those that terminate in marine
    marine_terminals = pd.Series(
        np.zeros(shape=(len(networkIDs),), dtype="bool"), index=networkIDs,
    )
    marine_terminals.loc[
        marine_terminals.index.isin(joins.loc[joins.marine].upstream_id)
    ] = True

    ### Find those that terminate in HUC2 drain points
    # Note: only applicable for those that exit into HUC2s outside the analysis region
    huc2_drains = pd.Series(
        np.zeros(shape=(len(networkIDs),), dtype="bool"), index=networkIDs
    )
    huc2_drains.loc[
        huc2_drains.index.isin(joins.loc[joins.type == "huc2_drain"].upstream_id)
    ] = True

    ### Identify all barriers that are upstream of a given network
    # by joining on their downstream line ID (downstream_id)
    barriers_upstream = (
        barrier_joins[["downstream_id", "kind"]]
        .join(networkID, on="downstream_id")
        .reset_index()[["networkID", "kind"]]
        .dropna()
    )
    barriers_upstream.networkID = barriers_upstream.networkID.astype("uint32")

    ### Count barriers that have a given network DOWNSTREAM of them
    upstream_counts = (
        barriers_upstream.groupby(["networkID", "kind"])
        .size()
        .rename("count")
        .reset_index()
        .pivot(index="networkID", columns="kind", values="count")
        .rename(
            columns={
                "dam": "up_ndams",
                "waterfall": "up_nwfs",
                "small_barrier": "up_nsbs",
            }
        )
    )

    ### Count barriers that are DOWNSTREAM (linear to terminal) of each barrier
    # create directed graph of barrier joins facing downstream
    # Note: origins (upstream_id==0) are excluded
    # the upstream side is already a networkID, calculate the networkID for the downstream side
    j = (
        barrier_joins.loc[
            (barrier_joins.upstream_id != 0)  # & (barrier_joins.downstream_id != 0)
        ]
        .join(networkID, on="downstream_id")
        .rename(columns={"networkID": "downstream_network"})
    )

    g = DirectedGraph(j, source="upstream_id", target="downstream_network")
    # count number that are downstream of each network
    # NOTE: this includes the barrier that creates each network
    downstreams = pd.Series(
        g.descendants(networkIDs), index=networkIDs, name="dowstream_network"
    )

    num_downstream = downstreams.apply(len).rename("num_downstream")

    ### Calculate if any downstream network is a marine terminal or exits HUC2s
    # create a mapping of every network to all networks downstream of it
    tmp = downstreams.explode().dropna().astype("uint64")
    ix = marine_terminals.loc[marine_terminals].index
    connects_marine = tmp.loc[tmp.isin(ix)].index.unique()

    # include any that are themselves marine connected
    to_ocean = pd.Series(
        np.zeros(shape=(len(networkIDs),), dtype="bool"),
        index=networkIDs,
        name="flows_to_ocean",
    )
    to_ocean.loc[to_ocean.index.isin(ix) | to_ocean.index.isin(connects_marine)] = True

    ix = huc2_drains.loc[huc2_drains].index
    connects_to_exit = tmp.loc[tmp.isin(ix)].index.unique()
    exits_region = pd.Series(
        np.zeros(shape=(len(networkIDs),), dtype="bool"),
        index=networkIDs,
        name="exits_region",
    )
    exits_region.loc[
        exits_region.index.isin(ix) | exits_region.index.isin(connects_to_exit)
    ] = True

    ### Extract downstream barrier type.
    # on the downstream side of a network, there will only ever be a single barrier.
    # Identify all barriers that have a given network upstream of them.
    barriers_downstream = (
        barrier_joins[["upstream_id", "kind"]]
        .join(networkID, on="upstream_id")
        .reset_index()[["networkID", "kind"]]
        .dropna()
        # there are some duplicates due to a barrier having multiple upstream network segments
        .drop_duplicates()
    )
    barriers_downstream.networkID = barriers_downstream.networkID.astype("uint32")
    barriers_downstream = barriers_downstream.set_index("networkID").kind.rename(
        "barrier"
    )

    ### Aggregate bounds to network (currently unused and expensive to create)
    # bounds = df.groupby(level=0).agg(
    #     {"xmin": "min", "ymin": "min", "xmax": "max", "ymax": "max"}
    # )

    sizeclasses = (
        df.groupby(level=0).sizeclass.nunique().astype("uint8").rename("sizeclasses")
    )

    ### Collect results
    results = (
        calculate_geometry_stats(df)
        # .join(bounds)
        .join(calculate_floodplain_stats(df))
        .join(sizeclasses)
        .join(upstream_counts)
        .join(barriers_downstream)
        .join(num_downstream)
        .join(to_ocean)
        .join(exits_region)
        .join(root_huc2)
    )

    # any that flow into ocean also leave the HUC2
    results.loc[results.flows_to_ocean, "exits_region"] = True

    results[upstream_counts.columns] = (
        results[upstream_counts.columns].fillna(0).astype("uint16")
    )
    results.barrier = results.barrier.fillna("")

    results["num_downstream"] = results["num_downstream"].fillna(0).astype("uint16")

    return results


def calculate_geometry_stats(df):
    """Calculate total network miles, free-flowing miles (not in waterbodies),
    free-flowing unaltered miles (not in waterbodies, not altered), total
    perennial miles, total free-flowing unaltered perennial miles,
    length-weighted sinuosity, and count of segments.

    Parameters
    ----------
    df : DataFrame
        must have length, sinuosity, waterbody, altered, and perennial, and be indexed on networkID

    Returns
    -------
    DataFrame
        contains total_miles, free_miles, *_miles, sinuosity, segments
    """

    # total lengths used for upstream network
    total_length = df["length"].groupby(level=0).sum().rename("total")
    perennial_length = (
        df.loc[~df.intermittent, "length"].groupby(level=0).sum().rename("perennial")
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
        .join(altered_length)
        .join(unaltered_length)
        .join(perennial_unaltered_length)
        .join(free_length)
        .join(free_perennial)
        .join(free_altered_length)
        .join(free_unaltered_length)
        .join(free_perennial_unaltered)
        .fillna(0)
        * METERS_TO_MILES
    ).astype("float32")
    lengths.columns = [f"{c}_miles" for c in lengths.columns]

    # calculate percent altered
    lengths["pct_altered"] = 100 * (
        (lengths.total_miles - lengths.unaltered_miles) / lengths.total_miles
    )

    temp_df = df[["length", "sinuosity"]].join(total_length)

    # Calculate length-weighted sinuosity
    wtd_sinuosity = (
        (temp_df.sinuosity * (temp_df.length / temp_df.total))
        .groupby(level=0)
        .sum()
        .astype("float32")
        .rename("sinuosity")
    )

    segments = df.groupby(level=0).size().astype("uint32").rename("segments")

    return lengths.join(wtd_sinuosity).join(segments)


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
    # Read in associated floodplain info and join
    fp_stats = (
        pd.read_feather(data_dir / "floodplains" / "floodplain_stats.feather")
        .set_index("NHDPlusID")
        .drop(columns=["HUC2"])
    )
    df = df.join(fp_stats, on="NHDPlusID")

    pct_nat_df = df[["floodplain_km2", "nat_floodplain_km2"]].groupby(level=0).sum()

    return (
        (100 * pct_nat_df.nat_floodplain_km2 / pct_nat_df.floodplain_km2)
        .astype("float32")
        .rename("natfldpln")
    )
