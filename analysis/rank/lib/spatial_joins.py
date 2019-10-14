from pathlib import Path
import geopandas as gp
from geofeather import from_geofeather

from analysis.util import spatial_join


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
    protected = from_geofeather(boundaries_dir / "protected_areas.feather")
    df = spatial_join(df, protected)
    df.OwnerType = df.OwnerType.fillna(-1).astype("int8")
    df.ProtectedLand = df.ProtectedLand.fillna(False).astype("bool")

    # TODO: other spatial joins - priority layers?

    return df

