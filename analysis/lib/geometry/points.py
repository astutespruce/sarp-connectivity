from geopandas.tools.hilbert_curve import _encode as _encode_hilbert
import numpy as np
import shapely


def encode_hilbert(geometries, level=16):
    """Encode geoseries to Hilbert curve index

    Parameters
    ----------
    geometries : geopandas GeoSeries or array of shapely geometries
    level : int, optional (default 16)
        level of detail in Hilbert encoding; e.g., 16 = 16 bit range for each of
        x and y

    Returns
    -------
    1d array of Hilbert indices
    """
    level = 16
    side_length = (2**level) - 1
    total_bounds = shapely.total_bounds(geometries)
    x, y = shapely.get_coordinates(geometries).T
    x = np.round((x - total_bounds[0]) * (side_length / (total_bounds[2] - total_bounds[0])))
    y = np.round((y - total_bounds[1]) * (side_length / (total_bounds[3] - total_bounds[1])))

    return _encode_hilbert(level, x, y)
