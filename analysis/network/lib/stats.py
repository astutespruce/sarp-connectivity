from pathlib import Path
import pandas as pd

from nhdnet.io import deserialize_df


data_dir = Path("data")


def calculate_network_stats(df, barrier_joins):
    """Calculation of network statistics, for each functional network.
    
    Parameters
    ----------
    df : Pandas DataFrame
        data frame including the basic metrics for each flowline segment, including:
        * length
        * sinuosity
        * size class

    barrier_barrier_joins : Pandas DataFrame
        contains ...TODO: 


    Returns
    -------
    Pandas DataFrame
        Summary statistics, with one row per functional network.
    """

    # create series of networkID indexed by lineID
    networkID = df.reset_index().set_index("lineID").networkID

    # identify all barriers that are upstream of a given network
    # by joining on their downstream line ID (downstream_id)
    barriers_upstream = (
        barrier_joins[["downstream_id", "kind"]]
        .join(networkID, on="downstream_id")
        .reset_index()[["networkID", "kind"]]
        .dropna()
    )
    barriers_upstream.networkID = barriers_upstream.networkID.astype("uint32")

    # Count barriers that have a given network DOWNSTREAM of them
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

    # Extract downstream barrier type.
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

    results = (
        calculate_geometry_stats(df)
        .join(calculate_floodplain_stats(df))
        .join(df.groupby(level=0).sizeclass.nunique().rename("sizeclasses"))
        .join(upstream_counts)
        .join(barriers_downstream)
    )

    results[upstream_counts.columns] = (
        results[upstream_counts.columns].fillna(0).astype("uint32")
    )
    results.barrier = results.barrier.fillna("")

    return results


def calculate_geometry_stats(df):
    """Calculate total network miles, length-weighted sinuosity, and count of segments
    
    Parameters
    ----------
    df : DataFrame
        must have length and sinuosity, and be indexed on networkID
    
    Returns
    -------
    DataFrame
        contains miles, sinuosity, segments
    """

    network_length = df.groupby(level=0).length.sum()
    temp_df = df[["length", "sinuosity"]].join(network_length, rsuffix="_total")

    # Calculate length-weighted sinuosity
    wtd_sinuosity = (
        (temp_df.sinuosity * (temp_df.length / temp_df.length_total))
        .groupby(level=0)
        .sum()
    )

    # convert meters to miles
    return pd.DataFrame(
        data={
            "miles": network_length * 0.000621371,
            "sinuosity": wtd_sinuosity,
            "segments": df.groupby(level=0).size(),
        }
    )


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
    fp_stats = deserialize_df(
        data_dir / "floodplains" / "floodplain_stats.feather"
    ).set_index("NHDPlusID")
    df = df.join(fp_stats, on="NHDPlusID")

    pct_nat_df = df[["floodplain_km2", "nat_floodplain_km2"]].groupby(level=0).sum()

    return (
        (100 * pct_nat_df.nat_floodplain_km2 / pct_nat_df.floodplain_km2)
        .astype("float32")
        .rename("natfldpln")
    )
