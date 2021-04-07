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
