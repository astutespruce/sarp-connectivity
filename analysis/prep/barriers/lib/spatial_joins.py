from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
from shapely import STRtree

from analysis.lib.geometry import sjoin_points_to_poly


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"


def get_huc2(df):
    """Find the HUC2 that contains each point

    Parameters
    ----------
    df : GeoDataFrame

    Returns
    -------
    pandas.Series
        indexed on index of df
    """

    huc2 = gp.read_feather(boundaries_dir / "huc2.feather", columns=["HUC2", "geometry"]).explode(ignore_index=True)
    tree = STRtree(df.geometry.values)
    left, right = tree.query(huc2.geometry.values, predicate="intersects")
    huc2 = (
        pd.DataFrame({"HUC2": huc2.HUC2.values.take(left)}, index=df.index.values.take(right))
        .groupby(level=0)
        .HUC2.first()
    )

    return huc2


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
        pd.read_feather(boundaries_dir / "HUC8.feather", columns=["HUC8", "name", "coastal"])
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
    df.ProtectedLand = df.ProtectedLand.fillna(0).astype("bool")

    ### Environmental justice layers
    print("Joining to environmental justice disadvantaged communities")
    tracts = gp.read_feather(boundaries_dir / "environmental_justice_tracts.feather")
    tracts["EJTract"] = True
    df = sjoin_points_to_poly(df, tracts)
    df["EJTract"] = df.EJTract.fillna(0).astype("bool")

    tribal_lands = gp.read_feather(boundaries_dir / "tribal_lands.feather")
    tribal_lands["EJTribal"] = True
    df = sjoin_points_to_poly(df, tribal_lands)
    df["EJTribal"] = df.EJTribal.fillna(0).astype("bool")

    # combine into single column for filtering
    labels = np.array(["tract", "tribal"])
    df["DisadvantagedCommunity"] = df[["EJTract", "EJTribal"]].apply(
        lambda row: ",".join(labels[row.values == True]),  # noqa
        axis=1,
    )

    ### Native territories (convert all intersecting territories into comma-delimited list)
    print("Joining to native territories")
    territories = gp.read_feather(boundaries_dir / "native_territories.feather")
    left, right = STRtree(df.geometry.values).query(territories.geometry.values, predicate="intersects")
    territories = (
        pd.DataFrame({"name": territories.name.values.take(left)}, index=df.index.values.take(right))
        .groupby(level=0)
        .name.unique()
        .apply(sorted)
        .apply(", ".join)
        .rename("NativeTerritories")
    )
    df = df.join(territories)
    df["NativeTerritories"] = df.NativeTerritories.fillna("")

    ### Fish Habitat Partnership boundaries
    # NOTE: these include overlapping areas
    fhp = gp.read_feather(boundaries_dir / "fhp_boundary.feather")
    left, right = STRtree(df.geometry.values).query(fhp.geometry.values, predicate="intersects")
    fhp = (
        pd.DataFrame({"name": fhp.FishHabitatPartnership.values.take(left)}, index=df.index.values.take(right))
        .groupby(level=0)
        .name.unique()
        .apply(sorted)
        .apply(",".join)
        .rename("FishHabitatPartnership")
    )
    df = df.join(fhp)
    df["FishHabitatPartnership"] = df.FishHabitatPartnership.fillna("")

    ### Join in species stats
    spp_df = (
        pd.read_feather(
            data_dir / "species/derived/spp_HUC12.feather",
            columns=[
                "HUC12",
                "federal",
                "sgcn",
                "regional",
                "trout",
                "salmonid_esu",
                "salmonid_esu_count",
            ],
        )
        .rename(
            columns={
                "federal": "TESpp",
                "sgcn": "StateSGCNSpp",
                "regional": "RegionalSGCNSpp",
                "trout": "Trout",
                "salmonid_esu": "SalmonidESU",
                "salmonid_esu_count": "SalmonidESUCount",
            }
        )
        .set_index("HUC12")
    )
    df = df.join(spp_df, on="HUC12")
    for col in [
        "TESpp",
        "StateSGCNSpp",
        "RegionalSGCNSpp",
        "Trout",
        "SalmonidESUCount",
    ]:
        df[col] = df[col].fillna(0).astype("uint8")
    df["SalmonidESU"] = df.SalmonidESU.fillna("")

    return df
