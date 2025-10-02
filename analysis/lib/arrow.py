import pyarrow as pa
import pyarrow.compute as pc
from pyproj import Transformer, CRS as ProjCRS


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


def xy_to_crs(x, y, in_crs, out_crs):
    transformer = Transformer.from_crs(ProjCRS(in_crs), ProjCRS(out_crs), always_xy=True)
    return transformer.transform(x, y)
