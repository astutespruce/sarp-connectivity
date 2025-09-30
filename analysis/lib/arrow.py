import pyarrow as pa
import pyarrow.compute as pc
from pyproj import Transformer, CRS as ProjCRS
import geoarrow.pyarrow as ga


def map_values(arr, dict_values, dtype=None):
    """Map array values to new values based on dictionary

    Parameters
    ----------
    arr : pyarrow Array
        input values
    dict_values : dict
        input dictionary

    Returns
    -------
    pyarrow Array
    """
    keys = pa.array(list(dict_values.keys()))
    values = pa.array(list(dict_values.values()), type=dtype)
    return pc.take(values, pc.index_in(arr, keys))


def points_to_crs(points, crs):
    """Convert geoarrow-encoded points to a different CRS

    Parameters
    ----------
    points : geoarrow GeometryExtensionArray:PointType
    crs : crs
        output CRS

    Returns
    -------
    geoarrow GeometryExtensionArray:PointType
    """
    if points.type.extension_name != "geoarrow.point":
        raise ValueError("Requires geoarrow PointType")

    transformer = Transformer.from_crs(points.type.crs, ProjCRS(crs), always_xy=True)
    x, y = transformer.transform(*ga.point_coords(points))
    return ga.with_crs(ga.point().from_geobuffers(None, x, y), crs)
