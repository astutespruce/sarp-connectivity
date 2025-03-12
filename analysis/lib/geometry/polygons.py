import numpy as np
import pandas as pd
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


def unwrap_antimeridian(geometries, ref_long=0):
    """Unwrap geometries that have been split by the antimeridian so that they
    are west of the antimeridian instead of wrapped to positive longitude.

    Parameters
    ----------
    geometries : ndarray of shapely geometries
    ref_long: reference longitude
        geometries with bounds that are beyond this longitude are wrapped to
        the west of the antimeriedian

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


def drop_small_holes(geometries, threshold=1e-6):
    """Drop any interior rings that are smaller in area than threshold.

    NOTE: area is calculated using geodesic methods

    Parameters
    ----------
    geometries : ndarray of shapely Polygons or Multipolygons
    threshold : int, optional (default: 1e-6)
        any interior rings < this area in square meters are dropped

    Returns
    -------
    ndarray of input geometries minus holes that are too small
    """

    parts, index = shapely.get_parts(geometries, return_index=True)

    ix = shapely.get_num_interior_rings(parts) > 0
    ix = np.arange(len(parts))[ix]

    # for each part, keep all rings above area threshold
    for i in ix:
        rings = shapely.get_interior_ring(parts[i], range(shapely.get_num_interior_rings(parts[i])))

        parts[i] = shapely.polygons(
            shapely.get_exterior_ring(parts[i]), rings[shapely.area(shapely.polygons(rings)) >= threshold]
        )

    # aggregate parts back together
    return (
        pd.DataFrame({"geometry": parts}, index=index)
        .groupby(level=0)
        .geometry.apply(np.array)
        .apply(lambda g: shapely.multipolygons(g) if len(g) > 1 else g[0])
        .values
    )
