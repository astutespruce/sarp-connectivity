import numpy as np
import shapely
from pyproj.transformer import Transformer

from analysis.constants import CRS, GEO_CRS


def to_crs(geometries, src_crs, target_crs):
    """Convert coordinates from one CRS to another CRS.

    Parameters
    ----------
    geometries : ndarray of pygeos geometries
    src_crs : CRS or params to create it
    target_crs : CRS or params to create it
    """

    if src_crs == target_crs:
        return geometries.copy()

    transformer = Transformer.from_crs(src_crs, target_crs, always_xy=True)
    coords = shapely.get_coordinates(geometries)
    new_coords = transformer.transform(coords[:, 0], coords[:, 1])
    result = shapely.set_coordinates(geometries.copy(), np.array(new_coords).T)
    return result


def geo_bounds(geometries):
    """Calculate bounds in WGS84 coordinates for each geometry.

    As a faster approximation, only the the bounding coordinates are projected
    to WGS84 before calculating the outer bounds.

    Coordinates are rounded to 5 decimal places.

    Parameters
    ----------
    flowlines : ndarray of pygeos geometries

    Returns
    -------
        ndarray of (xmin, ymin, xmax, ymax) for each geometry
    """

    transformer = Transformer.from_crs(CRS, GEO_CRS, always_xy=True)

    xmin, ymin, xmax, ymax = shapely.bounds(geometries).T

    # transform all 4 corners then take min/max
    x1, y1 = transformer.transform(xmin, ymin)
    x2, y2 = transformer.transform(xmin, ymax)
    x3, y3 = transformer.transform(xmax, ymin)
    x4, y4 = transformer.transform(xmax, ymax)

    return (
        np.array(
            [
                np.min([x1, x2], axis=0),
                np.min([y1, y3], axis=0),
                np.max([x3, x4], axis=0),
                np.max([y2, y4], axis=0),
            ]
        )
        .round(5)
        .astype("float32")
        .T
    )
