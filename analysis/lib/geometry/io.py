import geopandas as gp
from pyogrio import write_dataframe


def write_geoms(geometries, path, crs=None):
    """Convenience function to write an ndarray of pygeos geometries to a file

    Parameters
    ----------
    geometries : ndarray of pygeos geometries
    path : str
    crs : CRS object, optional (default: None)
    """
    df = gp.GeoDataFrame({"geometry": geometries}, crs=crs)
    write_dataframe(df, path)
