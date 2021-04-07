from pathlib import Path

import pandas as pd
import geopandas as gp

from analysis.lib.geometry import unique_sjoin


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"


def add_spatial_joins(df):
    """Add spatial joins of data provided by API, but not needed for network analysis.

    Parameters
    ----------
    df : GeoDataFrame

    Returns
    -------
    GeoDataFrame
        has fields added by spatial joins to other datasets
    """

    ### Protected lands
    print("Joining to protected areas")
    protected = gp.read_feather(boundaries_dir / "protected_areas.feather")
    df = unique_sjoin(df, protected)
    df.OwnerType = df.OwnerType.fillna(-1).astype("int8")
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

    return df
