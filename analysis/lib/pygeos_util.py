import pandas as pd
import geopandas as gp
import pygeos as pg
import numpy as np
from pyogrio import write_dataframe

from analysis.lib.graph import find_adjacent_groups
from analysis.lib.util import append


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

        joined = sjoin_geometry(
            pd.Series(left.geometry.values.data, index=left.index),
            pd.Series(right.geometry.values.data, index=right.index),
            predicate="intersects",
            how="inner",
        )

    else:
        # optimize for the case where the right side is smaller
        # and restructure so that this is equivalent to above
        left_index_name = left.index.name or "index"
        joined = (
            sjoin_geometry(
                pd.Series(right.geometry.values.data, index=right.index),
                pd.Series(left.geometry.values.data, index=left.index),
                predicate="intersects",
                how="inner",
            )
            .rename(left_index_name)
            .reset_index()
            .set_index(left_index_name)
        )
        joined = joined[joined.columns[0]].rename("index_right")

    joined = left.join(joined, how="left").join(
        right.drop(columns=["geometry"]), on="index_right", rsuffix="_right"
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


def explode(df):
    """Explode a GeoDataFrame containing multi* geometries into single parts.

    Note: GeometryCollections of Multi* may need to be exploded a second time.

    Parameters
    ----------
    df : GeoDataFrame

    Returns
    -------
    GeoDataFrame
    """
    join_cols = [c for c in df.columns if not c == "geometry"]
    geom, index = pg.get_parts(df.geometry.values.data, return_index=True)
    return gp.GeoDataFrame(df[join_cols].take(index), geometry=geom, crs=df.crs)


def dissolve(df, by, grid_size=None, agg=None, allow_multi=True, op="union"):
    """Dissolve a DataFrame by grouping records using "by".

    Contiguous or overlapping geometries will be unioned together.

    Parameters
    ----------
    df : GeoDataFrame
        geometries must be single-part geometries
    by : str or list-like
        field(s) to dissolve by
    grid_size : float
        precision grid size, will be used in union operation
    agg : dict, optional (default: None)
        If present, is a dictionary of field names in df to agg operations.  Any
        field not aggregated will be set to null in the appended dissolved records.
    allow_multi : bool, optional (default: True)
        If False, geometries will
    op : str, one of {'union', 'coverage_union'}
    """

    if agg is not None:
        if "geometry" in agg:
            raise ValueError("Cannot use user-specified aggregator for geometry")
    else:
        agg = dict()

    agg["geometry"] = lambda g: union_or_combine(
        g.values.data, grid_size=grid_size, op=op
    )

    # Note: this method is 5x faster than geopandas.dissolve (until it is migrated to use pygeos)
    dissolved = gp.GeoDataFrame(
        df.groupby(by).agg(agg).reset_index(), geometry="geometry", crs=df.crs
    )

    if not allow_multi:
        # flatten any multipolygons
        dissolved = explode(dissolved).reset_index(drop=True)

    return dissolved


def union_or_combine(geometries, grid_size=None, op="union"):
    """First does a check for overlap of geometries according to STRtree
    intersects.  If any overlap, then will use union_all on all of them;
    otherwise will return as a multipolygon.

    If only one polygon is present, it will be returned in a MultiPolygon.

    If coverage_union op is provided, geometries must be polygons and
    topologically related or this will produce bad output or fail outright.
    See docs for coverage_union in GEOS.

    Parameters
    ----------
    geometries : ndarray of single part polygons
    grid_size : [type], optional (default: None)
        provided to union_all; otherwise no effect
    op : str, one of {'union', 'coverage_union'}

    Returns
    -------
    MultiPolygon
    """

    if not (pg.get_type_id(geometries) == 3).all():
        print("Inputs to union or combine must be single-part geometries")

    if len(geometries) == 1:
        return pg.multipolygons(geometries)

    tree = pg.STRtree(geometries)
    left, right = tree.query_bulk(geometries, predicate="intersects")
    # drop self intersections
    ix = left != right
    left = left[ix]
    right = right[ix]

    # no intersections, just combine parts
    if len(left) == 0:
        return pg.multipolygons(geometries)

    # find groups of contiguous geometries and union them together individually
    contiguous = np.sort(np.unique(np.concatenate([left, right])))
    discontiguous = np.setdiff1d(np.arange(len(geometries), dtype="uint"), contiguous)
    groups = find_adjacent_groups(left, right)

    parts = []

    if op == "coverage_union":
        for group in groups:
            parts.extend(pg.get_parts(pg.coverage_union_all(geometries[list(group)])))

    else:
        for group in groups:
            parts.extend(
                pg.get_parts(pg.union_all(geometries[list(group)], grid_size=grid_size))
            )

    parts.extend(pg.get_parts(geometries[discontiguous]))

    return pg.multipolygons(parts)


def find_contiguous_groups(geometries):
    """Find all adjacent geometries

    Parameters
    ----------
    geometries : ndarray of pygeos geometries


    Returns
    -------
    DataFrame indexed on the integer index of geometries
    """
    tree = pg.STRtree(geometries)
    left, right = tree.query_bulk(geometries, predicate="intersects")
    # drop self intersections
    ix = left != right
    left = left[ix]
    right = right[ix]

    groups = find_adjacent_groups(left, right)
    groups = (
        pd.DataFrame(
            {i: list(g) for i, g in enumerate(groups)}.items(),
            columns=["group", "index"],
        )
        .explode("index")
        .set_index("index")
    )

    return groups


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

    out = []
    for i in range(len(lines)):
        new_line = cut_line_at_points(
            lines[i], pg.get_parts(points[i]), tolerance=tolerance
        )
        out.append(new_line)

    return np.array(out)


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


def nearest(source, target, max_distance, keep_all=False):
    """Find the nearest target geometry for each record in source, if one
    can be found within distance.

    Parameters
    ----------
    source : Series
        contains pygeos geometries
    target : Series
        contains target pygeos geometries to search against
    max_distance : number or ndarray
        radius within which to find target geometries
        If ndarray, must be equal length to source.
    keep_all : bool (default: False)
        If True, will keep all equidistant results

    Returns
    -------
    DataFrame
        indexed by original index of source, has index of target for each
        nearest target geom.
        Includes distance
    """

    left_index_name = source.index.name or "index"
    right_index_name = target.index.name or "index_right"

    tree = pg.STRtree(target.values.data)

    if np.isscalar(max_distance):
        (left_ix, right_ix), distance = tree.nearest_all(
            source.values.data, max_distance=max_distance, return_distance=True
        )

        # Note: there may be multiple equidistant or intersected results, so we take the first
        df = pd.DataFrame(
            {right_index_name: target.index.take(right_ix), "distance": distance,},
            index=source.index.take(left_ix),
        )

    else:  # array
        merged = None
        for d in np.unique(max_distance):
            ix = max_distance == d
            left = source.loc[ix]
            (left_ix, right_ix), distance = tree.nearest_all(
                left.values.data, max_distance=d, return_distance=True
            )
            merged = append(
                merged,
                pd.DataFrame(
                    {
                        left_index_name: left.index.take(left_ix),
                        right_index_name: target.index.take(right_ix),
                        "distance": distance,
                    },
                ),
            )
        df = merged.set_index(left_index_name)

    if keep_all:
        df = df.reset_index().drop_duplicates().set_index(left_index_name)
    else:
        df = df.groupby(level=0).first()

    df.index.name = source.index.name

    return df


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

    # TODO: update to latest API
    groups = find_adjacent_groups(pairs).astype("uint32")

    return groups


def write_geoms(geometries, path, crs=None):
    """Convenience function to write an ndarray of pygeos geometries to a file

    Parameters
    ----------
    geometries : ndarray of pygeos geometries
    path : str
    crs : CRS object, optional (default: None)
    """
    df = gp.GeoDataFrame({"geometry": geometries}, crs=crs)
    write_dataframe(df, path)


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
