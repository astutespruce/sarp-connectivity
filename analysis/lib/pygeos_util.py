import pandas as pd
import geopandas as gp
import pygeos as pg
import numpy as np


from analysis.lib.network import connected_groups


def sjoin(left, right, predicate="intersects", how="left"):
    """Join data frames on geometry, comparable to geopandas.

    NOTE: left vs right must be determined in advance for best performance, unlike geopandas.

    Parameters
    ----------
    left : GeoDataFrame
    right : GeoDataFrame
    predicate : str, optional (default "intersects")
    how : str, optional (default "left")

    Returns
    -------
    pandas DataFrame
        Includes all columns from left and all columns from right except geometry, suffixed by _right where
        column names overlap.
    """

    # spatial join is inner to avoid recasting indices to float
    joined = sjoin_geometry(
        pd.Series(left.geometry.values.data, index=left.index),
        pd.Series(right.geometry.values.data, index=right.index),
        predicate,
        how="inner",
    )
    joined = left.join(joined, how=how).join(
        right.drop(columns=["geometry"]), on="index_right", rsuffix="_right"
    )
    return joined


def sjoin_geometry(left, right, predicate="intersects", how="inner"):
    """Use pygeos to do a spatial join between 2 series or ndarrays of geometries.

    Parameters
    ----------
    left : Series or ndarray
        left geometries, will form basis of index that is returned
    right : Series or ndarray
        right geometries, their indices will be returned where thy meet predicate
    predicate : str, optional (default: "intersects")
        name of pygeos predicate function (any of the pygeos predicates should work: intersects, contains, within, overlaps, crosses)
    how : str, optional (default: "inner")
        one of "inner" or "left"; "right" is not supported at this time.

    Returns
    -------
    Series
        indexed on index of left, containing values of right index
    """

    if not how in ("inner", "left"):
        raise NotImplementedError("Other join types not implemented")

    if isinstance(left, pd.Series):
        left_values = left.values
        left_index = left.index

    else:
        left_values = left
        left_index = np.arange(0, len(left))

    if isinstance(right, pd.Series):
        right_values = right.values
        right_index = right.index

    else:
        right_values = right
        right_index = np.arange(0, len(right))

    tree = pg.STRtree(right_values)
    # hits are in 0-based indicates of right
    hits = tree.query_bulk(left_values, predicate=predicate)

    if how == "inner":
        index = left_index[hits[0]]
        values = right_index[hits[1]]

    elif how == "left":
        index = left_index.copy()
        values = np.empty(shape=index.shape)
        values.fill(np.nan)
        values[hits[0]] = right_index[hits[1]]

    return pd.Series(values, index=index, name="index_right")


def unique_sjoin(left, right):
    """Perfom a spatial join between left and right, then remove duplicate entries
    for right by left (e.g., feature in left overlaps multiple features in right).

    This is most appropriate where left is composed entirely of point features.

    All joins use a left join and intersects predicate.

    Parameters
    ----------
    left : GeoDataFrame
    right : GeoDataFrame

    Returns
    -------
    GeoDataFrame
        includes non-geometry columns of right joined to left.
    """

    if len(left) >= len(right):
        joined = sjoin(left, right)
    else:
        joined = (
            sjoin(right, left)
            .reset_index(drop=left.index.name in left.columns)
            .set_index(left.index.name or "index")
        )

    joined = joined.drop(columns=["index_right"])

    grouped = joined.groupby(level=0)
    if grouped.size().max() > 1:
        print(
            "WARNING: multiple target areas returned in spatial join for a single point"
        )

        # extract the right side indexed by the left, and take first record
        right = grouped[[c for c in right.columns.drop("geometry")]].first()
        joined = left.join(right)

    return joined


def find_contiguous_groups(df):
    """Finds groups of inputs that are spatially contiguous (intersects predicate).

    Parameters
    ----------
    df : GeoDataFrame

    Returns
    -------
    Series
        indexed on original index of df, contains groups
    """
    index_name = df.index.name or "index"
    df = df.reset_index(drop=df.index.name in df.columns)
    geometry = pd.Series(df.geometry.values.data, index=df[index_name])
    pairs = sjoin_geometry(geometry, geometry).reset_index()
    pairs = pairs.loc[pairs[index_name] != pairs.index_right].reset_index(drop=True)

    groups = connected_groups(pairs, make_symmetric=False).astype("uint32")
    groups.index = groups.index.astype(df[index_name].dtype)
    groups = groups.reset_index()

    # extract unmodified (discontiguous) features
    discontiguous = np.setdiff1d(df[index_name], groups[index_name])
    next_group = groups.group.max().item() + 1 if len(groups) else 0
    groups = groups.append(
        pd.DataFrame(
            {
                index_name: discontiguous,
                "group": np.arange(next_group, next_group + len(discontiguous)),
            }
        ),
        ignore_index=True,
        sort=False,
    )

    return groups.set_index(index_name).group


def aggregate_contiguous(df, agg=None, buffer_size=None):
    """Dissolve contiguous (intersecting) features into singular geometries.

    Returns GeoDataFrame indexed on original index values for features that are
    not contiguous, and appends features from the dissolve operation with null
    indices.

    Parameters
    ----------
    df : GeoDataFrame
    agg : dict, optional (default: None)
        If present, is a dictionary of field names in df to agg operations.  Any
        field not aggregated will be set to null in the appended dissolved records.
    buffer_size : int or float (default: None)
        Amount to buffer polygons by before union to merge together.

    Returns
    -------
    GeoDataFrame
        indexed on original index; index values will be null for new, dissolved
        features.
    """

    index_name = df.index.name or "index"

    if agg is not None:
        if "geometry" in agg:
            raise ValueError("Cannot use user-specified aggregator for geometry")
    else:
        agg = dict()

    # extract singular geometry if not grouped
    if buffer_size is not None:
        agg["geometry"] = (
            lambda g: pg.union_all(
                pg.buffer(
                    g.values.data,
                    buffer_size,
                    quadsegs=1,
                    cap_style="flat",
                    join_style="bevel",
                )
            )
            if len(g.values) > 1
            else g.values.data[0]
        )

    else:
        agg["geometry"] = (
            lambda g: pg.union_all(
                g.values.data,
            )
            if len(g.values) > 1
            else g.values.data[0]  # also picks up any ungrouped features
        )

    # set incoming index to nan when geometries are dissolved
    agg[index_name] = lambda ix: np.nan if len(ix) > 1 else ix

    # df = df.reset_index()

    df = df.join(find_contiguous_groups(df)).reset_index()

    # Note: this method is 5x faster than geopandas.dissolve (until it is migrated to use pygeos)
    dissolved = gp.GeoDataFrame(
        df.groupby("group").agg(agg), geometry="geometry", crs=df.crs
    )
    # flatten any multipolygons
    dissolved = explode(dissolved)

    return dissolved.set_index(index_name)


def explode(df, add_position=False):
    """Explode multipart features to individual geometries

    Note: the fast version of this method will be available in geopandas pending
    https://github.com/geopandas/geopandas/pull/1693

    Parameters
    ----------
    df : GeoDataFrame
    add_position : bool, optional (default: False)
        if True, will add a column indicating position within the original index

    """
    parts, index = pg.get_parts(df.geometry.values.data, return_index=True)
    series = gp.GeoSeries(parts, index=df.index.take(index), name="geometry")
    df = df.drop(columns=["geometry"]).join(series)

    if not add_position:
        return df

    run_start = np.r_[True, index[:-1] != index[1:]]
    counts = np.diff(np.r_[np.nonzero(run_start)[0], len(index)])
    position = (~run_start).cumsum()
    position -= np.repeat(position[run_start], counts)
    df["position"] = position
    return df


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
    # only keep those that are interior to the line
    cut_offsets = cut_offsets[
        (cut_offsets > tolerance) & (cut_offsets < offsets[-1] - tolerance)
    ]

    if len(cut_offsets) == 0:
        # nothing to cut, return original
        return line

    # get coordinates of new vertices from the cut points (interpolated onto the line)
    cut_offsets.sort()
    cut_coords = pg.get_coordinates(pg.line_interpolate_point(line, cut_offsets))

    # split vertices into bins
    bins = np.digitize(offsets, cut_offsets)

    # find the edges of the bins
    breaks = np.r_[True, bins[:-1] != bins[1:]]
    i = np.append(np.arange(len(bins))[breaks], [len(bins)])
    slices = np.column_stack([i[:-1], i[1:]])
    coords = pg.get_coordinates(line)

    num_lines = len(slices)
    lines = []
    for i, ix in enumerate(slices):
        c = coords[slice(*ix)]

        # insert cut coords on both sides of each split
        if i > 0:
            c = np.vstack([cut_coords[i - 1], c])
        if i < num_lines - 1:
            c = np.vstack([c, cut_coords[i]])

        lines.append(pg.linestrings(c))

    return pg.multilinestrings(lines)


def dissolve(df, by, agg=None, allow_multi=True):
    """Dissolve a DataFrame by grouping records using "by".

    Contiguous or overlapping geometries will be unioned together.

    Parameters
    ----------
    df : GeoDataFrame
    by : str
        field to dissolve by
    agg : dict, optional (default: None)
        If present, is a dictionary of field names in df to agg operations.  Any
        field not aggregated will be set to null in the appended dissolved records.
    allow_multi : bool, optional (default: True)
        If False, geometries will
    """

    if agg is not None:
        if "geometry" in agg:
            raise ValueError("Cannot use user-specified aggregator for geometry")
    else:
        agg = dict()

    agg["geometry"] = (
        lambda g: pg.union_all(
            g.values.data,
        )
        if len(g.values) > 1
        else g.values.data[0]  # also picks up any ungrouped features
    )

    # Note: this method is 5x faster than geopandas.dissolve (until it is migrated to use pygeos)
    dissolved = gp.GeoDataFrame(
        df.groupby(by).agg(agg).reset_index(), geometry="geometry", crs=df.crs
    )

    if not allow_multi:
        # flatten any multipolygons
        dissolved = explode(dissolved).reset_index(drop=True)

    return dissolved


def near(source, target, distance):
    """Return target geometries within distance of source geometries.

    Only returns records from source that intersected at least one feature in target.

    Parameters
    ----------
    source : Series
        contains pygeos geometries
    target : Series
        contains target pygeos geometries to search against
    distance : number or ndarray
        radius within which to find target geometries.
        If ndarray, must be equal length to source.

    Returns
    -------
    DataFrame
        indexed on original index of source
        includes distance
    """

    # Get all indices from target_values that intersect buffers of input geometry
    idx = sjoin_geometry(pg.buffer(source, distance), target)
    hits = (
        pd.DataFrame(idx)
        .join(source.rename("geometry"), how="inner")
        .join(target.rename("geometry_right"), on="index_right", how="inner")
    )
    # this changes the index if hits is empty, causing downstream problems
    if not len(hits):
        hits.index.name = idx.index.name

    hits["distance"] = pg.distance(hits.geometry, hits.geometry_right).astype("float32")

    return (
        hits.drop(columns=["geometry", "geometry_right"])
        .rename(columns={"index_right": target.index.name or "index_right"})
        .sort_values(by="distance")
    )


def nearest(source, target, distance):
    """Find the nearest target geometry for each record in source, if one
    can be found within distance.

    Parameters
    ----------
    source : Series
        contains pygeos geometries
    target : Series
        contains target pygeos geometries to search against
    distance : number or ndarray
        radius within which to find target geometries
        If ndarray, must be equal length to source.

    Returns
    -------
    DataFrame
        indexed by original index of source, has index of target for each
        nearest target geom.
        Includes distance
    """

    # results coming from near() already sorted by distance, just take the first
    # since this will be the nearest

    return near(source, target, distance).groupby(level=0).first()


def neighborhoods(source, tolerance=100):
    """Find the neighborhoods for a given set of geometries.
    Neighborhoods are those where geometries overlap by distance; this gets
    at the outer neighborhood: if A,B; A,C; and C,D are each neighbors
    the neighborhood is A,B,C,D.

    WARNING: not all neighbors within a neighborhood are within distance of each other.

    Parameters
    ----------
    source : Series
        contains pygeos geometries
    tolerance : int, optional (default 100)
        max distance between pairs of geometries
    Returns
    -------
    Series
        returns neighborhoods ("group") indexed by original series index
    """
    index_name = source.index.name or "index"

    pairs = near(source, source, distance=tolerance)

    # drop self-intersections
    pairs = (
        pairs.loc[pairs.index != pairs[index_name]]
        .rename(columns={index_name: "index_right"})
        .index_right.reset_index()
    )

    groups = connected_groups(pairs, make_symmetric=False).astype("uint32")

    return groups
