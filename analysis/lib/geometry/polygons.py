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
