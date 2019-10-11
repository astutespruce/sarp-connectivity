from pathlib import Path
import geopandas as gp
from geofeather import from_geofeather

from analysis.util import spatial_join


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"


def add_spatial_joins(df):
    ### Spatial joins to boundary layers

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

    ### Protected lands
    print("Joining to protected areas")
    protected = from_geofeather(boundaries_dir / "protected_areas.feather")
    df = spatial_join(df, protected)
    df.OwnerType = df.OwnerType.fillna(-1).astype("int8")
    df.ProtectedLand = df.ProtectedLand.fillna(False).astype("bool")

    # TODO: other spatial joins - priority layers?

    return df

