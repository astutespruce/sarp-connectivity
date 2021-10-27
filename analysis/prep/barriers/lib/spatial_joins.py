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

    ### Protected lands
    print("Joining to protected areas")
    protected = gp.read_feather(boundaries_dir / "protected_areas.feather")
    df = unique_sjoin(df, protected)
    df.OwnerType = df.OwnerType.fillna(0).astype("uint8")
    df.ProtectedLand = df.ProtectedLand.fillna(False).astype("bool")

    ### Priority layers
    print("Joining to priority watersheds")
    priorities = (
        pd.read_feather(boundaries_dir / "priorities.feather")
        .rename(columns={"HUC_8": "HUC8"})
        .set_index("HUC8")
        .rename(columns={"usfs": "HUC8_USFS", "coa": "HUC8_COA", "sgcn": "HUC8_SGCN"})
    )
    df = df.join(priorities, on="HUC8")
    df[priorities.columns] = df[priorities.columns].fillna(0).astype("uint8")

    ### Join in T&E Spp stats
    spp_df = (
        pd.read_feather(
            data_dir / "species/derived/spp_HUC12.feather",
            columns=["HUC12", "federal", "sgcn", "regional"],
        )
        .rename(
            columns={
                "federal": "TESpp",
                "sgcn": "StateSGCNSpp",
                "regional": "RegionalSGCNSpp",
            }
        )
        .set_index("HUC12")
    )
    df = df.join(spp_df, on="HUC12")
    for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
        df[col] = df[col].fillna(0).astype("uint8")

    return df
