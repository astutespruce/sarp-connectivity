import numpy as np
from numba import njit
import pygeos as pg


@njit("f8[:](f8[:,:])")
def segment_length(coords):
    """Calculate the vectorized length between each vertex in coords as an
    alternative to creating geometry objects.

    Parameters
    ----------
    coords : ndarray of shape (n,2)
        x,y pairs

    Returns
    -------
    ndarray of shape(n-1,)
        lengths in units of coordinates
    """
    diff = coords[1:] - coords[:-1]
    return np.sqrt(diff[:, 0] * diff[:, 0] + diff[:, 1] * diff[:, 1])


@njit("f8[:](f8[:,:])")
def vertex_offsets(coords):
    """Calculate the line offset (position) for each vertex in the line.

    Parameters
    ----------
    coords : ndarray of shape (n,2)
        x,y pairs of thecoordinates in the lne

    Returns
    -------
    ndarray of shape(n,)
        offsets of each coordinate along the line
    """
    out = np.empty(coords.shape[0], dtype=coords.dtype)
    out[0] = 0
    out[1:] = np.cumsum(segment_length(coords))
    return out


@njit(", f8[:,:], f8[:,:])")
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
    out = np.zeros(len(points), dtype="float64")
    for i in range(starts.shape[0]):
        ld = np.linalg.norm(left[i])
        rd = np.linalg.norm(right[i])
        x = np.dot(left[i], right[i]) / (ld * rd)

        # cannot calculate arccos of -1
        if x > -1:
            out[i] = np.arccos(x)
        else:
            out[i] = np.pi  # 180 degrees

    return np.degrees(out)


@njit("f8[:](f8[:,:], f8[:,:], f8[:,:])")
def triangle_area(a, b, c):
    """Calculate the triangular area of the triangle formed between each triple
    of a, b, c.

    About 2x faster than regular above.

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


@njit("b1[:](f8[:], f8)")
def is_min_area(a, b):
    # np.isclose is not currently available in numba
    return np.abs(a - b) <= 1e-5


@njit("Tuple((f8[:,:], i8[:]))(f8[:,:], f8)")
def simplify_vw(coords, epsilon):
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
    area = triangle_area(coords[:-2], coords[1:-1], coords[2:])

    min_area = np.nanmin(area)
    # nothing to simplify
    if min_area >= epsilon:
        return coords[mask], index[mask]

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
                area[left - 1] = triangle_area(
                    coords[far_left : far_left + 1],
                    coords[left : left + 1],
                    coords[right : right + 1],
                )[0]

            if len(right_index) == 2 and len(left_index) > 0:
                left = left_index[-1]
                right, far_right = right_index
                area[right - 1] = triangle_area(
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


@njit("Tuple((f8[:,:], i8[:]))(f8[:,:], f8, i8)")
def extract_straight_segments(coords, max_angle=10, loops=5):
    """Extracts coordinates and indices of the significant vertices by
    repeatedly dropping any vertices that are less than 180° +/- max_angle.

    Parameters
    ----------
    coords : ndarray of shape (n,2)
        x,y pairs
    max_angle : int or float, optional (default: 10)
        maximum difference from 180° that an angle can still be considered
        "straight" enough
    loops : int, optional (default: 5)
        number of times to repeatedly drop low angles, by default 5

    Returns
    -------
    (array of retained coordinates, array of integer indexes of retained coordinates)
    """
    mask = np.ones(len(coords), dtype="bool")
    index = np.arange(len(mask))

    for i in range(0, loops):
        keep_coords = coords[mask]
        angles = np.abs(
            vertex_angle(keep_coords[1:-1], keep_coords[:-2], keep_coords[2:]) - 180
        )

        drop_pts = angles < max_angle
        # if there are no interior points to drop, then stop
        if drop_pts.sum() == 0:
            break

        mask[index[mask][1:-1][drop_pts]] = False

    return coords[mask], index[mask]


@njit("Tuple((f8[:,:], i8[:]))(f8[:,:],f8[:])")
def split_coords(coords, cut_offsets):
    """Split coordinates representing a single line at cut_offsets.

    Parameters
    ----------
    coords : ndarray of shape (n, 2)
        coordinates
    cut_offsets : ndarray of shape (m,)
        offsets along line to cut into line

    Returns
    -------
    (coords, line_ix)
        tuple of split coords of shape (n, 2), index of new lines in coords of
        shape (n,)
    """
    offsets = vertex_offsets(coords)
    # get the index of the existing vertex to the right of the cut point
    segment_ix = np.digitize(cut_offsets, offsets, right=True)
    # only add 1 extra vertex for each existing vertex, otherwise we add 2
    existing_vertex = np.abs(offsets[segment_ix] - cut_offsets) < 1e-5

    # interpolate coordinates for cut_offsets
    p = (cut_offsets - offsets[segment_ix - 1]) / (
        offsets[segment_ix] - offsets[segment_ix - 1]
    )
    # Note: p.expand_dims reshapes p to allow elementwise multiplication along axis
    new_coords = (
        np.expand_dims(p, 1) * (coords[segment_ix] - coords[segment_ix - 1])
    ) + coords[segment_ix - 1]

    # make one array of indexes and one array of coordinates so that we can
    # create multilinestring ix-2 corresponds to last value of bin add closing
    # coord for prev line and starting coord of next
    out_len = len(coords) + 2 * len(cut_offsets) - existing_vertex.sum()
    out_coords = np.empty(shape=(out_len, 2), dtype="float64")
    out_ix = np.empty(out_len, dtype="int64")
    prev_ix = 0
    prev_offset = 0
    cur_offset = 0
    for i in range(len(segment_ix)):
        cur_ix = segment_ix[i]
        width = cur_ix - prev_ix
        cur_offset = prev_offset + width

        if width:
            out_coords[prev_offset:cur_offset] = coords[prev_ix:cur_ix]
            out_ix[prev_offset:cur_offset] = i

        out_coords[cur_offset] = new_coords[i]

        if existing_vertex[i]:
            # closing coordinate already exists, starting coordinate already added above
            out_ix[cur_offset] = i
            prev_offset = cur_offset + 1
        else:
            # insert starting coodinate of next line
            out_coords[cur_offset + 1] = new_coords[i]
            out_ix[cur_offset] = i
            out_ix[cur_offset + 1] = i + 1
            prev_offset = cur_offset + 2

        prev_ix = cur_ix

    out_coords[prev_offset:] = coords[prev_ix:]
    out_ix[prev_offset:] = len(segment_ix)

    return out_coords, out_ix


def cut_line_at_points(coords, cut_offsets):
    """Cut a pygeos line geometry at points.  The points must be interior
    to the line.

    Parameters
    ----------
    coords : ndarray of shape (2,n)
        line coordinates
    cut_points : list-like of offsets projected onto the line

    Returns
    -------
    MultiLineStrings
    """
    new_coords, line_ix = split_coords(coords, cut_offsets)
    return pg.multilinestrings(pg.linestrings(new_coords, indices=line_ix))


def cut_lines_at_points(coords, cut_offsets):
    """Cut lines represented by coords at cut_offsets

    Parameters
    ----------
    coords : list-like
        coordinates for each line
    cut_offsets : list-like
        offset of cut points on their corresponding lines

    Returns
    -------
    (outer_ix, inner_ix, lines)
        tuple of arrays of outer index, inner index of split line within original
        line, and pygeos LineString.
    """

    outer_ix = []
    inner_ix = []
    lines = []
    for i in range(len(coords)):
        new_coords, line_ix = split_coords(coords[i], cut_offsets[i])
        outer_ix.append(i)
        l = pg.linestrings(new_coords, indices=line_ix)  # multiple lines
        outer_ix.extend([i] * (len(l) - 1))
        inner_ix.extend(np.arange(len(l)))
        lines.extend(l)

    return outer_ix, inner_ix, lines
