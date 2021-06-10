from pathlib import Path
from operator import itemgetter

import geopandas as gp
import pandas as pd
import pygeos as pg
import numpy as np

from analysis.constants import GEO_CRS
from analysis.lib.graph import DirectedGraph

data_dir = Path("data")


def calculate_network_stats(df, barrier_joins, joins):
    """Calculation of network statistics, for each functional network.

    Parameters
    ----------
    df : Pandas DataFrame
        data frame including the basic metrics for each flowline segment, including:
        * length
        * sinuosity
        * size class

    _barrier_joins : Pandas DataFrame
        contains:
        * upstream_id
        * downstream_id
        * kind

    joins_joins : Pandas DataFrame
        contains:
        * upstream_id
        * downstream_id
        * kind

    Returns
    -------
    Pandas DataFrame
        Summary statistics, with one row per functional network.
    """

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

    ### Calculate if any downstream network is a marine terminal
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

    ### Collect results
    results = (
        calculate_geometry_stats(df)
        # .join(bounds)
        .join(calculate_floodplain_stats(df))
        .join(df.groupby(level=0).sizeclass.nunique().rename("sizeclasses"))
        .join(upstream_counts)
        .join(barriers_downstream)
        .join(num_downstream)
        .join(to_ocean)
    )

    results[upstream_counts.columns] = (
        results[upstream_counts.columns].fillna(0).astype("uint16")
    )
    results.barrier = results.barrier.fillna("")

    results["num_downstream"] = results["num_downstream"].fillna(0).astype("uint16")

    return results


def calculate_geometry_stats(df):
    """Calculate total network miles, free-flowing miles (not in waterbodies),
    length-weighted sinuosity, and count of segments

    Parameters
    ----------
    df : DataFrame
        must have length, sinuosity, waterbody, and be indexed on networkID

    Returns
    -------
    DataFrame
        contains miles, free_miles, sinuosity, segments
    """

    network_length = df.groupby(level=0)[["length"]].sum()
    free_length = (
        df.loc[~df.waterbody].groupby(level=0).length.sum().rename("free_length")
    )

    temp_df = df[["length", "sinuosity"]].join(network_length, rsuffix="_total")

    # Calculate length-weighted sinuosity
    wtd_sinuosity = (
        (temp_df.sinuosity * (temp_df.length / temp_df.length_total))
        .groupby(level=0)
        .sum()
        .rename("sinuosity")
    )

    lengths = network_length.join(free_length)
    lengths.free_length = lengths.free_length.fillna(0)

    # convert meters to miles
    miles = (lengths * 0.000621371).rename(
        columns={"length": "miles", "free_length": "free_miles"}
    )

    return miles.join(wtd_sinuosity).join(df.groupby(level=0).size().rename("segments"))


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
    fp_stats = pd.read_feather(
        data_dir / "floodplains" / "floodplain_stats.feather"
    ).set_index("NHDPlusID")
    df = df.join(fp_stats, on="NHDPlusID")

    pct_nat_df = df[["floodplain_km2", "nat_floodplain_km2"]].groupby(level=0).sum()

    return (
        (100 * pct_nat_df.nat_floodplain_km2 / pct_nat_df.floodplain_km2)
        .astype("float32")
        .rename("natfldpln")
    )
