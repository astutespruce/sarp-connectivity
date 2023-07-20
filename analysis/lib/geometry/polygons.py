import numpy as np
import shapely


def get_interior_rings(polygons):
    """Return array of inner rings for all polygons.

    Parameters
    ----------
    polygons : ndarray
        All items must be Polygon geometry type

    Returns
    -------
    (outer_index, inner_index, rings)
    """
    num_rings = shapely.get_num_interior_rings(polygons)
    outer_index = []
    inner_index = []
    rings = []
    for i in range(len(polygons)):
        if num_rings[i]:
            ix = np.arange(num_rings[i])
            rings.extend(shapely.get_interior_ring(polygons[i], ix))
            inner_index.extend(ix)
            outer_index.extend([i] * num_rings[i])

    return outer_index, inner_index, rings


def unwrap_antimeridian(geometries, ref_long=0, grid_size=None):
    """Unwrap geometries that have been split by the antimeriedian so that they
    are west of the antimeridian instead of wrapped to positive longitude.

    Parameters
    ----------
    geometries : ndarray of shapely geometries
    ref_long: reference longitude
        geometries with bounds that are beyond this longitude are wrapped to
        the west of the antimeriedian
    grid_size : precision grid size to use for union

    Returns
    -------
    ndarray of shapely geometries
    """
    bounds = shapely.bounds(geometries)
    out_geometries = geometries.copy()
    ix = bounds[:, 0] >= ref_long

    if ix.sum():
        # subtract 360 degrees
        out_geometries[ix] = shapely.transform(geometries[ix], lambda g: g - [360, 0])

    return out_geometries
