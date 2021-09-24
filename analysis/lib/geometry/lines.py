import geopandas as gp
import numpy as np
import pandas as pd
import pygeos as pg


def calculate_sinuosity(geometries):
    """Calculate sinuosity of the line.

    This is the length of the line divided by the distance between the endpoints of the line.
    By definition, it is always >=1.

    Parameters
    ----------
    geometries : Series or ndarray of pygeos geometries

    Returns
    -------
    Series or ndarray
        sinuosity values
    """

    # By definition, sinuosity should not be less than 1
    first = pg.get_point(geometries, 0)
    last = pg.get_point(geometries, -1)
    straight_line_distance = pg.distance(first, last)

    sinuosity = np.ones((len(geometries),)).astype("float32")

    # if there is no straight line distance there can be no sinuosity
    ix = straight_line_distance > 0

    # by definition, all values must be at least 1, so clip lower bound
    sinuosity[ix] = (pg.length(geometries[ix]) / straight_line_distance[ix]).clip(1)

    if isinstance(geometries, pd.Series):
        return pd.Series(sinuosity, index=geometries.index)

    return sinuosity


def cut_line_at_points(line, cut_points, tolerance=1e-6):
    """Cut a pygeos line geometry at points.
    If there are no interior points, the original line will be returned.

    Parameters
    ----------
    line : pygeos Linestring
    cut_points : list-like of pygeos Points
        will be projected onto the line; those interior to the line will be
        used to cut the line in to new segments.
    tolerance : float, optional (default: 1e-6)
        minimum distance from endpoints to consider the points interior
        to the line.

    Returns
    -------
    MultiLineStrings (or LineString, if unchanged)
    """
    if not pg.get_type_id(line) == 1:
        raise ValueError("line is not a single linestring")

    vertices = pg.get_point(line, range(pg.get_num_points(line)))
    offsets = pg.line_locate_point(line, vertices)
    cut_offsets = pg.line_locate_point(line, cut_points)
    # only keep those that are interior to the line and ignore those very close
    # to endpoints or beyond endpoints
    cut_offsets = cut_offsets[
        (cut_offsets > tolerance) & (cut_offsets < offsets[-1] - tolerance)
    ]

    if len(cut_offsets) == 0:
        # nothing to cut, return original
        return line

    # get coordinates of new vertices from the cut points (interpolated onto the line)
    cut_offsets.sort()

    # add in the last coordinate of the line
    cut_offsets = np.append(cut_offsets, offsets[-1])

    # TODO: convert this to a pygos ufunc
    coords = pg.get_coordinates(line)
    cut_coords = pg.get_coordinates(pg.line_interpolate_point(line, cut_offsets))
    lines = []
    orig_ix = 0
    for cut_ix in range(len(cut_offsets)):
        offset = cut_offsets[cut_ix]

        segment = []
        if cut_ix > 0:
            segment = [cut_coords[cut_ix - 1]]
        while offsets[orig_ix] < offset:
            segment.append(coords[orig_ix])
            orig_ix += 1

        segment.append(cut_coords[cut_ix])
        lines.append(pg.linestrings(segment))

    return pg.multilinestrings(lines)


def cut_lines_at_multipoints(lines, points, tolerance=1e-6):
    """Wraps cut_line_at_points to take array inputs.

    Points will be projected onto the line; those interior to the line will be
    used to cut the line in to new segments.

    Parameters
    ----------
    lines : ndarray of pygeos Linestrings
    cut_points : ndarray of pygeos MultiPoints

    tolerance : float, optional (default: 1e-6)
        minimum distance from endpoints to consider the points interior
        to the line.

    Returns
    -------
    ndarray of MultiLineStrings (or LineString, if unchanged)
    """

    out = np.empty(shape=len(lines), dtype="object")
    for i in range(len(lines)):
        new_line = cut_line_at_points(
            lines[i], pg.get_parts(points[i]), tolerance=tolerance
        )
        out[i] = new_line

    return out


def aggregate_lines(df, by):
    """Like dissolve, but aggregates lines to multilinestrings instead of
    unioning them together, which is much slower.

    Parameters
    ----------
    df : GeoDataFrame
    by : string or list-like
        field(s) to aggregate by

    Returns
    -------
    GeoDataFrame of multilinestrings
    """

    tmp = pd.DataFrame(df.copy())
    tmp["geometry"] = tmp.geometry.values.data
    return gp.GeoDataFrame(
        tmp.groupby(by=by)
        .geometry.apply(pg.multilinestrings)
        .rename("geometry")
        .reset_index(),
        crs=df.crs,
    )


def angle(points, starts, ends):
    """Calculate the angle formed at each triple of start, point, end.

    Values close to 180 degrees indicate a relatively straight line.

    Vectorized adaptation of https://github.com/martinfleis/momepy/blob/v0.5.0/momepy/shape.py#L748-L868

    All inputs must be the same shape.

    Parameters
    ----------
    points : ndarray of shape (n, 2)
        array of x,y coordinates for points to calculate angle
    starts : ndarray of shape (n, 2)
        array of x,y coordinates for starting point of each line segment
    ends : ndarray of shape (n, 2)
        array of x,y coordinates for ending point of each line segment

    Returns
    -------
    ndarray of shape (1,)
        angle in degrees
    """

    left = starts - points
    right = ends - points
    cosine_angle = np.diag(np.inner(left, right)) / (
        np.linalg.norm(left, axis=1) * np.linalg.norm(right, axis=1)
    )
    return np.degrees(np.arccos(cosine_angle))


def perpindicular_distance(points, starts, ends):
    """Calculate the perpindicular distance to point in points based on a line
    between starts and ends.

    Vectorized adaptation of https://dougfenstermacher.com/blog/simplification-summarization

    All inputs must be the same shape

    Parameters
    ----------
    points : ndarray of shape (n, 2)
        array of x,y coordinates for points to calculate perpindicular distance
    starts : ndarray of shape (n, 2)
        array of x,y coordinates for starting point of each line segment
    ends : ndarray of shape (n, 2)
        array of x,y coordinates for ending point of each line segment

    Returns
    -------
    ndarray of shape (1,)
        perpindicular distance
    """

    if not (points.shape == starts.shape and points.shape == ends.shape):
        raise ValueError("All inputs must be same shape")

    delta = ends - starts

    return np.abs(np.cross(delta, (points - starts))) / np.linalg.norm(delta, axis=1)


def triangle_area(a, b, c):
    """Calculate the triangular area of the triangle formed between each triple
    of a, b, c.

    Vectorized adaptation of https://dougfenstermacher.com/blog/simplification-summarization

    All inputs must have the same shape.

    Parameters
    ----------
    a : ndarray of shape (n, 2)
    b : ndarray of shape (n, 2)
    c : ndarray of shape (n, 2)

    Returns
    -------
    ndarray of shape (1,)
        area of each triangle
    """
    left = a - b
    right = c - b
    ldist = np.linalg.norm(left, axis=1)
    rdist = np.linalg.norm(right, axis=1)
    cosine_angle = np.diag(np.inner(left, right)) / (ldist * rdist)
    theta = np.arccos(cosine_angle)
    return 0.5 * ldist * rdist * np.sin(theta)
