import numpy as np
from numba import njit


@njit("f8[:](f8[:,:], f8[:,:], f8[:,:])")
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
