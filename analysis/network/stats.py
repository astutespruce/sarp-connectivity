from pathlib import Path
import pandas as pd

from nhdnet.io import deserialize_df


data_dir = Path("data")


def calculate_network_stats(df):
    """Calculation of network statistics, for each functional network.
    
    Parameters
    ----------
    df : Pandas DataFrame
        data frame including the basic metrics for each flowline segment, including:
        * length
        * sinuosity
        * size class
    
    Returns
    -------
    Pandas DataFrame
        Summary statistics, with one row per functional network.
    """

    return (
        calculate_geometry_stats(df)
        .join(calculate_floodplain_stats(df))
        .join(calculate_size_classes_gained(df))
    )


def calculate_geometry_stats(df):
    """Calculate total network miles, length-weighted sinuosity, and count of segments
    
    Parameters
    ----------
    df : DataFrame
        must have length and sinuosity, and be indexed on networkID
    
    Returns
    -------
    DataFrame
        contains miles, NetworkSinuosity, NumSegments
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
            "NetworkSinuosity": wtd_sinuosity,
            "NumSegments": df.groupby(level=0).size(),
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
        percent natural landcover
    """

    # Sum floodplain and natural floodplain values, and calculate percent natural floodplain
    # Read in associated floodplain info and join
    fp_stats = deserialize_df(
        data_dir / "floodplains" / "floodplain_stats.feather"
    ).set_index("NHDPlusID")
    df = df.join(fp_stats, on="NHDPlusID")

    pct_nat_df = df[["floodplain_km2", "nat_floodplain_km2"]].groupby(level=0).sum()
    # pct_nat_df["PctNatFloodplain"] = (
    #     100 * pct_nat_df.nat_floodplain_km2 / pct_nat_df.floodplain_km2
    # ).astype("float32")

    return (
        (100 * pct_nat_df.nat_floodplain_km2 / pct_nat_df.floodplain_km2)
        .astype("float32")
        .rename("PctNatFloodplain")
    )


def calculate_size_classes_gained(df):
    """Calculate the number of new size classes gained in the upstream network
    
    Parameters
    ----------
    df : DataFrame
        Network data frame, must include sizeclasses and be indexed on networkID
    
    Returns
    -------
    Series
        number of size classes gained
    """
    # Calculate number of unique size classes beyond the first size class.
    # Because a unique count of 1 is equivalent to gaining no additional size classes.

    return (df.groupby(level=0).sizeclass.nunique() - 1).rename("NumSizeClassGained")
