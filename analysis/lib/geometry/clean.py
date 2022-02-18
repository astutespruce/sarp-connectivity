import numpy as np
import pygeos as pg


def make_valid(geometries):
    """Make geometries valid.

    Parameters
    ----------
    geometries : ndarray of pygeos geometries

    Returns
    -------
    ndarray of pygeos geometries
    """

    ix = ~pg.is_valid(geometries)
    if ix.sum():
        geometries = geometries.copy()
        print(f"Repairing {ix.sum()} geometries")
        geometries[ix] = pg.make_valid(geometries[ix])

    return geometries


def to_multipolygon(geometries):
    """Convert single part polygons to multipolygons

    Parameters
    ----------
    geometries : ndarray of pygeos geometries
        can be mixed polygon and multipolygon types

    Returns
    -------
    ndarray of pygeos geometries, all multipolygon types
    """
    ix = pg.get_type_id(geometries) == 3
    if ix.sum():
        geometries = geometries.copy()
        geometries[ix] = np.apply_along_axis(
            pg.multipolygons, arr=(np.expand_dims(geometries[ix], 1)), axis=1
        )

    return geometries
