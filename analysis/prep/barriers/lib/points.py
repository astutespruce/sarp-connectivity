import pygeos as pg
import pandas as pd
import numpy as np


def connect_points(start, end):
    """Convert a series or array of points to an array or series of lines.

    Parameters
    ----------
    start : Series or ndarray
    end : Series or ndarray

    Returns
    -------
    Series or ndarray
    """

    is_series = False

    if isinstance(start, pd.Series):
        is_series = True
        index = start.index
        start = start.values
    if isinstance(end, pd.Series):
        end = end.values

    x1 = pg.get_x(start)
    y1 = pg.get_y(start)
    x2 = pg.get_x(end)
    y2 = pg.get_y(end)

    lines = pg.linestrings(np.array([[x1, x2], [y1, y2]]).T)

    if is_series:
        return pd.Series(lines, index=index)

    return lines


def window(geometries, distance):
    """Return windows around geometries bounds +/- distance

    Parameters
    ----------
    geometries : Series or ndarray
        geometries to window
    distance : number or ndarray
        radius of window
        if ndarry, must match length of geometries

    Returns
    -------
    Series or ndarray
        polygon windows
    """
    minx, miny, maxx, maxy = pg.bounds(geometries).T
    windows = pg.box(minx - distance, miny - distance, maxx + distance, maxy + distance)

    if isinstance(geometries, pd.Series):
        return pd.Series(windows, index=geometries.index)

    return windows
