from pathlib import Path

import pandas as pd
import geopandas as gp

from analysis.lib.geometry import sjoin_points_to_poly


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
        boundaries_dir / "HUC12.feather",
        columns=["geometry", "HUC12", "name"],
    ).rename(columns={"name": "Subwatershed"})

    df = sjoin_points_to_poly(df, huc12)

    # Expected: not all barriers fall cleanly within the states dataset
    if df.HUC12.isnull().sum():
        print(f"{df.HUC12.isnull().sum():,} barriers were not assigned HUC12")

    # Calculate HUC codes for other levels from HUC12
    df["HUC2"] = df["HUC12"].str.slice(0, 2)  # region
    df["HUC4"] = df["HUC12"].str.slice(0, 4)  # subregion
    df["HUC6"] = df["HUC12"].str.slice(0, 6)  # basin
    df["HUC8"] = df["HUC12"].str.slice(0, 8)  # subbasin
    df["HUC10"] = df["HUC12"].str.slice(0, 10)  # watershed

    # Read in HUC6...HUC12 and join in names
    huc6 = (
        pd.read_feather(boundaries_dir / "HUC6.feather", columns=["HUC6", "name"])
        .rename(columns={"name": "Basin"})
        .set_index("HUC6")
    )
    huc8 = (
        pd.read_feather(
            boundaries_dir / "HUC8.feather", columns=["HUC8", "name", "coastal"]
        )
        .rename(columns={"name": "Subbasin", "coastal": "CoastalHUC8"})
        .set_index("HUC8")
    )

    df = df.join(huc6, on="HUC6").join(huc8, on="HUC8")

    print("Joining to counties")
    counties = gp.read_feather(
        boundaries_dir / "counties.feather",
        columns=["geometry", "County", "COUNTYFIPS", "STATEFIPS"],
    )

    df = sjoin_points_to_poly(df, counties)

    # Join in state name based on STATEFIPS from county
    states = (
        pd.read_feather(boundaries_dir / "states.feather", columns=["STATEFIPS", "id"])
        .set_index("STATEFIPS")
        .rename(columns={"id": "State"})
    )
    df = df.join(states, on="STATEFIPS").drop(columns=["STATEFIPS"])

    # Expected: not all barriers fall cleanly within the states dataset
    if df.State.isnull().sum():
        print(f"{df.State.isnull().sum():,} barriers were not assigned states")

    ### Protected lands
    print("Joining to protected areas")
    protected = gp.read_feather(boundaries_dir / "protected_areas.feather")
    df = sjoin_points_to_poly(df, protected)
    df.OwnerType = df.OwnerType.fillna(0).astype("uint8")
    df.ProtectedLand = df.ProtectedLand.fillna(False).astype("bool")

    ### Priority layers
    print("Joining to priority watersheds")
    priorities = (
        pd.read_feather(boundaries_dir / "priorities.feather")
        .rename(columns={"HUC_8": "HUC8"})
        .set_index("HUC8")
        .rename(columns={"coa": "HUC8_COA"})
    )
    df = df.join(priorities, on="HUC8")
    df[priorities.columns] = df[priorities.columns].fillna(0).astype("uint8")

    ### Join in T&E Spp stats
    # note: trout is presence / absence
    spp_df = (
        pd.read_feather(
            data_dir / "species/derived/spp_HUC12.feather",
            columns=["HUC12", "federal", "sgcn", "regional", "trout"],
        )
        .rename(
            columns={
                "federal": "TESpp",
                "sgcn": "StateSGCNSpp",
                "regional": "RegionalSGCNSpp",
                "trout": "Trout",
            }
        )
        .set_index("HUC12")
    )
    df = df.join(spp_df, on="HUC12")
    for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp", "Trout"]:
        df[col] = df[col].fillna(0).astype("uint8")

    return df
