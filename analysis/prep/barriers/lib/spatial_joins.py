from pathlib import Path

import pandas as pd
import geopandas as gp

from analysis.lib.geometry import unique_sjoin


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"


def add_spatial_joins(df):
    """Add spatial joins needed for network analysis.

    Parameters
    ----------
    df : GeoDataFrame

    Returns
    -------
    GeoDataFrame
        has fields added by spatial joins to other datasets
    """

    print("Joining to HUC12")
    huc12 = gp.read_feather(
        boundaries_dir / "HUC12.feather", columns=["geometry", "HUC12", "name"],
    ).rename(columns={"name": "Subwatershed"})

    df = unique_sjoin(df, huc12)

    # Expected: not all barriers fall cleanly within the states dataset
    if df.HUC12.isnull().sum():
        print(f"{df.HUC12.isnull().sum():,} barriers were not assigned HUC12")

    # Calculate HUC codes for other levels from HUC12
    df["HUC2"] = df["HUC12"].str.slice(0, 2)  # region
    df["HUC6"] = df["HUC12"].str.slice(0, 6)  # basin
    df["HUC8"] = df["HUC12"].str.slice(0, 8)  # subbasin

    # Read in HUC6...HUC12 and join in names
    huc6 = (
        pd.read_feather(boundaries_dir / "HUC6.feather", columns=["HUC6", "name"])
        .rename(columns={"name": "Basin"})
        .set_index("HUC6")
    )
    huc8 = (
        pd.read_feather(boundaries_dir / "HUC8.feather", columns=["HUC8", "name"])
        .rename(columns={"name": "Subbasin"})
        .set_index("HUC8")
    )

    df = df.join(huc6, on="HUC6").join(huc8, on="HUC8")

    print("Joining to counties")
    counties = gp.read_feather(
        boundaries_dir / "counties.feather",
        columns=["geometry", "County", "COUNTYFIPS", "STATEFIPS"],
    )

    df = unique_sjoin(df, counties)

    # Join in state name based on STATEFIPS from county
    states = pd.read_feather(
        boundaries_dir / "states.feather", columns=["STATEFIPS", "State"]
    ).set_index("STATEFIPS")
    df = df.join(states, on="STATEFIPS")

    # Expected: not all barriers fall cleanly within the states dataset
    if df.STATEFIPS.isnull().sum():
        print(f"{df.STATEFIPS.isnull().sum():,} barriers were not assigned states")

    ### Level 3 & 4 Ecoregions
    print("Joining to ecoregions")
    # Only need to join in ECO4 dataset since it has both ECO3 and ECO4 codes
    eco4 = gp.read_feather(
        boundaries_dir / "eco4.feather", columns=["geometry", "ECO3", "ECO4"]
    )
    df = unique_sjoin(df, eco4)

    # Expected: not all barriers fall cleanly within the ecoregions dataset
    if df.ECO4.isnull().sum():
        print(f"{df.ECO4.isnull().sum():,} barriers were not assigned ecoregions")

    return df
