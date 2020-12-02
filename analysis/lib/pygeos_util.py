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
    left : DataFrame containing pygeos geometry in "geometry" column
    right : DataFrame containing pygeos geometry in "geometry" column
    predicate : str, optional (default "intersects")
    how : str, optional (default "left")

    Returns
    -------
    pandas DataFrame
        Includes all columns from left and all columns from right except geometry, suffixed by _right where
        column names overlap.
    """

    # spatial join is inner to avoid recasting indices to float
    joined = sjoin_geometry(left.geometry, right.geometry, predicate, how="inner")
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
    df = df.reset_index()
    geometry = pd.Series(df.geometry.values.data, index=df[index_name])
    pairs = sjoin_geometry(geometry, geometry).reset_index()
    pairs = pairs.loc[pairs[index_name] != pairs.index_right].reset_index(drop=True)

    groups = connected_groups(pairs, make_symmetric=False)

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
            else g.values.data[0]
        )

    # Note: this method is 5x faster than geopandas.dissolve (until it is migrated to use pygeos)
    dissolved = (
        df.set_index(index_name).join(groups, how="inner").groupby("group").agg(agg)
    )

    dissolved = gp.GeoDataFrame(dissolved, geometry="geometry", crs=df.crs)
    # flatten any multipolygons
    dissolved = explode(dissolved)

    # extract unmodified (discontiguous) features
    unmodified = df.loc[~df[index_name].isin(groups.index)]

    return unmodified.append(dissolved, sort=False, ignore_index=True).set_index(
        index_name
    )


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
