import geopandas as gp
import numpy as np
import pandas as pd
import shapely

from analysis.lib.graph.speedups import DirectedGraph


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
    first = shapely.get_point(geometries, 0)
    last = shapely.get_point(geometries, -1)
    straight_line_distance = shapely.distance(first, last)

    sinuosity = np.ones((len(geometries),)).astype("float32")

    # if there is no straight line distance there can be no sinuosity
    ix = straight_line_distance > 0

    # by definition, all values must be at least 1, so clip lower bound
    sinuosity[ix] = (shapely.length(geometries[ix]) / straight_line_distance[ix]).clip(
        1
    )

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
    if not shapely.get_type_id(line) == 1:
        raise ValueError("line is not a single linestring")

    vertices = shapely.get_point(line, range(shapely.get_num_points(line)))
    offsets = shapely.line_locate_point(line, vertices)
    cut_offsets = shapely.line_locate_point(line, cut_points)
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
    coords = shapely.get_coordinates(line)
    cut_coords = shapely.get_coordinates(
        shapely.line_interpolate_point(line, cut_offsets)
    )
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
        lines.append(shapely.linestrings(segment))

    return shapely.multilinestrings(lines)


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
            lines[i], shapely.get_parts(points[i]), tolerance=tolerance
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

    # convert to DataFrame, so that we can get at pygeos geometries directly in apply
    tmp = pd.DataFrame(df.copy())
    tmp["geometry"] = tmp.geometry.values.data
    return gp.GeoDataFrame(
        tmp.groupby(by=by, group_keys=False)
        .geometry.apply(shapely.multilinestrings)
        .rename("geometry")
        .reset_index(),
        crs=df.crs,
    )


def merge_lines(df, by):
    """Use GEOS line merge to merge MultiLineStrings into LineStrings (where possible).

    This uses aggregate_lines first to aggregate lines to MultiLineStrings.

    WARNING: this can be a bit slow.

    Parameters
    ----------
    df : GeoDataFrame
    by : string or list-like
        field(s) to aggregate by

    Returns
    -------
    GeoDataFrame of LineStrings or MultiLinestrings (if required)
    """
    agg = aggregate_lines(df, by)
    agg["geometry"] = shapely.line_merge(agg.geometry.values.data)

    geom_type = shapely.get_type_id(agg["geometry"].values.data)
    ix = geom_type == 5
    if ix.sum() > 0:
        agg.loc[~ix, "geometry"] = shapely.multilinestrings(
            agg.loc[~ix].geometry.values.data, np.arange((~ix).sum())
        )

    return agg


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
    ix = cosine_angle > -1
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


def extract_straight_segments(coords, max_angle=10, loops=5):
    index = np.arange(len(coords))

    keep_coords = coords
    keep_ix = index

    for i in range(0, 5):
        angles = np.abs(
            vertex_angle(keep_coords[1:-1], keep_coords[:-2], keep_coords[2:]) - 180
        )
        keep_pts = angles >= max_angle

        # if there are no interior points to drop, then stop
        if (~keep_pts).sum() == 0:
            break

        # Keep the endpoints too
        keep_pts = np.insert(keep_pts, [0, len(keep_coords) - 2], True)
        keep_ix = keep_ix[keep_pts]
        keep_coords = coords[keep_ix]

    return keep_coords, keep_ix


def fill_endpoint_gaps(df, gap_size):
    """Create new line segments that fill gaps below gap_size, and attach
    attributes from one side of the gap.

    A gap is defined as a non-zero (>1e-6) space between the endpoints of a line
    and another line, which is evaluated for all combinations of lines that are
    within gap_size distance of each other.

    IMPORTANT: lines must already be merged / unioned before calling this function;
    calling it repeatedly without merging in the new segments created here will
    create duplicate segments to fill those gaps

    NOTE: this does not fill gaps between endpoints of one line and any interior
    point of the other line.

    Parameters
    ----------
    df : GeoDataFrame
    gap_size : float
        maximum size to fill

    Returns
    -------
    GeoDataFrame
        all records from df plus any new segments that fill gaps between them
    """

    tree = shapely.STRtree(df.geometry.values)
    left, right = tree.query(df.geometry.values, predicate="dwithin", distance=gap_size)

    # drop self intersections
    ix = left != right
    left = left[ix]
    right = right[ix]

    # extract unique pairs (dedup symmetric pairs)
    pairs = np.array([left, right]).T
    pairs = (
        (
            pd.DataFrame({"left": pairs.min(axis=1), "right": pairs.max(axis=1)})
            .groupby(["left", "right"])
            .first()
            .reset_index()
        )
        .join(df.geometry.rename("left_line"), on="left")
        .join(df.geometry.rename("right_line"), on="right")
    )

    # have to do all combinations because segments could be oriented differently
    pairs["left_pt1"] = shapely.get_point(pairs.left_line, 0)
    pairs["left_pt2"] = shapely.get_point(pairs.left_line, -1)
    pairs["right_pt1"] = shapely.get_point(pairs.right_line, 0)
    pairs["right_pt2"] = shapely.get_point(pairs.right_line, -1)
    pairs["d1"] = shapely.distance(pairs.left_pt1, pairs.right_pt1)
    pairs["d2"] = shapely.distance(pairs.left_pt1, pairs.right_pt2)
    pairs["d3"] = shapely.distance(pairs.left_pt2, pairs.right_pt1)
    pairs["d4"] = shapely.distance(pairs.left_pt2, pairs.right_pt2)

    # make sure not to use points that already intersect other points
    # if the min distance across d1 - d4 is < 1e-6, drop that pair
    pairs = pairs.loc[pairs[["d1", "d2", "d3", "d4"]].min(axis=1) > 1e-6]

    new_segments = pd.concat(
        [
            pairs.loc[
                (pairs.d1 > 0) & (pairs.d1 < gap_size),
                ["left", "right", "left_pt1", "right_pt1", "d1"],
            ].rename(columns={"left_pt1": "start", "right_pt1": "end", "d1": "dist"}),
            pairs.loc[
                (pairs.d2 > 0) & (pairs.d2 < gap_size),
                ["left", "right", "left_pt1", "right_pt2", "d2"],
            ].rename(columns={"left_pt1": "start", "right_pt2": "end", "d2": "dist"}),
            pairs.loc[
                (pairs.d3 > 0) & (pairs.d3 < gap_size),
                ["left", "right", "left_pt2", "right_pt1", "d3"],
            ].rename(columns={"left_pt2": "start", "right_pt1": "end", "d3": "dist"}),
            pairs.loc[
                (pairs.d4 > 0) & (pairs.d4 < gap_size),
                ["left", "right", "left_pt2", "right_pt2", "d4"],
            ].rename(columns={"left_pt2": "start", "right_pt2": "end", "d4": "dist"}),
        ]
    ).drop_duplicates(subset=["left", "right"])

    ### find connected components in order to take shortest connection per group
    # (otherwise we create triangles)
    # add back symmetric pairs
    groups = DirectedGraph(
        np.concatenate([new_segments.left, new_segments.right]).astype("int64"),
        np.concatenate([new_segments.right, new_segments.left]).astype("int64"),
    ).components()
    groups = (
        pd.DataFrame(
            {i: list(g) for i, g in enumerate(groups)}.items(),
            columns=["group", "index"],
        )
        .explode("index")
        .set_index("index")
    )
    new_segments = (
        new_segments.join(groups, on="left").sort_values(
            by=["group", "dist"], ascending=[True, False]
        )
        # drop any complete duplicates (e.g., extending a line to a fork)
        .drop_duplicates(subset=["group", "dist"])
    )

    # find any groups with > 2 new segments where the endpoints are shared with
    # the endpoints of other new segments; these will create triangles that
    # we do not want
    g = new_segments.groupby("group").size()
    multi = new_segments.loc[new_segments.group.isin(g[g > 2].index)]

    # iteratively remove new segments where the endpoints are already captured by
    # segments with lower distances
    drop_ids = []
    for index, row in multi.iterrows():
        subset = multi.loc[~multi.index.isin([index] + drop_ids)]
        count = len(
            subset.loc[
                (subset.left == row.left)
                | (subset.right == row.right)
                | (subset.left == row.right)
                | (subset.right == row.left)
            ]
        )
        if count >= 2:
            drop_ids.append(index)

    new_segments = new_segments.loc[~new_segments.index.isin(drop_ids)]

    # attach attributes from left side of pair
    new_segments["geometry"] = new_segments[["start", "end"]].apply(
        lambda row: shapely.LineString([row.start, row.end]), axis=1
    )
    new_segments = gp.GeoDataFrame(
        new_segments.join(df.drop(columns=["geometry"]), on="left")[df.columns],
        geometry="geometry",
        crs=df.crs,
    )
    return pd.concat([df, new_segments], ignore_index=True)
