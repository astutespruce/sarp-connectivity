from pathlib import Path
import geopandas as gp
from geofeather import from_geofeather
from nhdnet.io import deserialize_df

from analysis.util import spatial_join


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
    huc12 = from_geofeather(boundaries_dir / "HUC12.feather")

    df = spatial_join(df, huc12)

    # Expected: not all barriers fall cleanly within the states dataset
    print(
        "{:,} barriers were not assigned HUC12".format(len(df.loc[df.HUC12.isnull()]))
    )

    # Calculate HUC codes for other levels from HUC12
    df["HUC2"] = df["HUC12"].str.slice(0, 2)  # region
    df["HUC6"] = df["HUC12"].str.slice(0, 6)  # basin
    df["HUC8"] = df["HUC12"].str.slice(0, 8)  # subbasin

    # Read in HUC6 and join in basin name
    huc6 = (
        from_geofeather(boundaries_dir / "HUC6.feather")[["HUC6", "NAME"]]
        .rename(columns={"NAME": "Basin"})
        .set_index("HUC6")
    )
    df = df.join(huc6, on="HUC6")

    print("Joining to counties")
    counties = from_geofeather(boundaries_dir / "counties.feather")[
        ["geometry", "County", "COUNTYFIPS", "STATEFIPS"]
    ]

    df = spatial_join(df, counties)

    # Join in state name based on STATEFIPS from county
    states = deserialize_df(boundaries_dir / "states.feather")[
        ["STATEFIPS", "State"]
    ].set_index("STATEFIPS")
    df = df.join(states, on="STATEFIPS")

    # Expected: not all barriers fall cleanly within the states dataset
    print(
        "{:,} barriers were not assigned states".format(
            len(df.loc[df.STATEFIPS.isnull()])
        )
    )

    ### Level 3 & 4 Ecoregions
    print("Joining to ecoregions")
    # Only need to join in ECO4 dataset since it has both ECO3 and ECO4 codes
    eco4 = from_geofeather(boundaries_dir / "eco4.feather")[
        ["geometry", "ECO3", "ECO4"]
    ]
    df = spatial_join(df, eco4)

    # Expected: not all barriers fall cleanly within the ecoregions dataset
    print(
        "{:,} barriers were not assigned ecoregions".format(
            len(df.loc[df.ECO4.isnull()])
        )
    )

    return df

