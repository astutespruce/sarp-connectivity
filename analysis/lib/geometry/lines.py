import geopandas as gp
import numpy as np
import pandas as pd
import pygeos as pg
from numba import njit


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


def vertex_angle(points, starts, ends):
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

    # fill with value of np.degrees(np.pi), which is equivalent to np.degrees(np.arccos(-1))
    out = np.ones(len(points), dtype="float64") * 180

    # cannot calculate arccos of -1
    ix = ~np.isclose(cosine_angle, -1)
    out[ix] = np.degrees(np.arccos(cosine_angle[ix]))

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
    out = np.zeros(len(b), dtype="float64")

    # cannot calculate arccos of -1
    ix = cosine_angle > -1
    theta = np.arccos(cosine_angle[ix])
    out[ix] = 0.5 * ldist[ix] * rdist[ix] * np.sin(theta)
    return out


@njit("f8[:](f8[:,:], f8[:,:], f8[:,:])")
def triangle_area_numba(a, b, c):
    """Calculate the triangular area of the triangle formed between each triple
    of a, b, c.

    About 2x faster than regular version above.

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
    out = np.zeros(len(b), dtype="float64")
    for i in range(a.shape[0]):
        ld = np.linalg.norm(left[i])
        rd = np.linalg.norm(right[i])
        x = np.dot(left[i], right[i]) / (ld * rd)

        # cannot calculate arccos of -1
        if x > -1:
            out[i] = 0.5 * ld * rd * np.sin(np.arccos(x))
    return out


def segment_length(coords):
    """Calculate the vectorized length between each vertex in coords as an
    alternative to creating geometry objects.

    Parameters
    ----------
    coords : ndarray of shape (n,2)
        x,y pairs

    Returns
    -------
    ndarray of shape(n,)
        lengths in units of coordinates
    """
    return np.linalg.norm((coords[1:] - coords[:-1]), axis=1)


def simplify_vw(coords, epsilon):
    """Vectorized Visvalingam-Whyatt simplification.

    This repeatedly recalculates area after removing vertices and is less
    performant than simplify_vw_numba below.

    Parameters
    ----------
    coords : ndarray of shape (n,2)
        x,y pairs
    epsilon : float
        min area required to retain a triangle

    Returns
    -------
    (indexes, simplified_coords)
        tuple of indexes of the retained coordinates and the simplified coordinates
    """
    mask = np.ones(len(coords), dtype="bool")
    index = np.arange(len(mask))

    while mask.sum() > 2:
        keep_coords = coords[mask]
        a = keep_coords[:-2]
        b = keep_coords[1:-1]
        c = keep_coords[2:]
        area = triangle_area(a, b, c)

        min_area = np.nanmin(area)
        if min_area >= epsilon:
            break

        drop_index = index[mask][1:-1][np.isclose(area, min_area)]
        mask[drop_index] = False

    return coords[mask], index[mask]


@njit("b1[:](f8[:], f8)")
def is_min_area(a, b):
    # np.isclose is not currently available in numba
    return np.abs(a - b) <= 1e-5


@njit("Tuple((f8[:,:], i8[:]))(f8[:,:], f8)")
def simplify_vw_numba(coords, epsilon):
    """Vectorized Visvalingam-Whyatt simplification.

    Parameters
    ----------
    coords : ndarray of shape (n,2)
        x,y pairs
    epsilon : float
        min area required to retain a triangle

    Returns
    -------
    (indexes, simplified_coords)
        tuple of indexes of the retained coordinates and the simplified coordinates
    """

    mask = np.ones(len(coords), dtype="bool")
    index = np.arange(len(mask))
    area = triangle_area_numba(coords[:-2], coords[1:-1], coords[2:])

    min_area = np.nanmin(area)
    # NOTE: drop_index is in absolute position
    drop_index = index[1:-1][is_min_area(area, min_area)]
    mask[drop_index] = False

    while min_area < epsilon and mask.sum() > 2:
        # set area for drop_index to nan to exclude from min
        # NOTE: this is shifted left to correct position
        area[drop_index - 1] = np.nan

        # update areas for all new triangles formed after dropping vertices at
        # drop_index
        for i in drop_index:
            keep_index = index[mask]
            left_index = keep_index[keep_index < i][-2:]
            right_index = keep_index[keep_index > i][:2]

            if len(left_index) == 2 and len(right_index) > 0:
                far_left, left = left_index
                right = right_index[0]
                area[left - 1] = triangle_area_numba(
                    coords[far_left : far_left + 1],
                    coords[left : left + 1],
                    coords[right : right + 1],
                )[0]

            if len(right_index) == 2 and len(left_index) > 0:
                left = left_index[-1]
                right, far_right = right_index
                area[right - 1] = triangle_area_numba(
                    coords[left : left + 1],
                    coords[right : right + 1],
                    coords[far_right : far_right + 1],
                )[0]

        # find next smallest area
        min_area = np.nanmin(area)
        if min_area >= epsilon:
            break

        drop_index = index[1:-1][is_min_area(area, min_area) & mask[1:-1]]
        if len(drop_index) == 0:
            break

        mask[drop_index] = False

    return coords[mask], index[mask]

