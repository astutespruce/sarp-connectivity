import geopandas as gp
import pygeos as pg


def explode(df):
    """Explode a GeoDataFrame containing multi* geometries into single parts.

    Note: GeometryCollections of Multi* may need to be exploded a second time.

    Parameters
    ----------
    df : GeoDataFrame

    Returns
    -------
    GeoDataFrame
    """
    join_cols = [c for c in df.columns if not c == "geometry"]
    geom, index = pg.get_parts(df.geometry.values.data, return_index=True)
    return gp.GeoDataFrame(df[join_cols].take(index), geometry=geom, crs=df.crs)
