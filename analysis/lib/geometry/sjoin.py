import pandas as pd
import shapely
import numpy as np


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
        pd.Series(left.geometry.values, index=left.index),
        pd.Series(right.geometry.values, index=right.index),
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

    tree = shapely.STRtree(right_values)
    # hits are in 0-based indicates of right
    hits = tree.query(left_values, predicate=predicate)

    if how == "inner":
        index = left_index[hits[0]]
        values = right_index[hits[1]]

    elif how == "left":
        index = left_index.copy()
        values = np.empty(shape=index.shape)
        values.fill(np.nan)
        values[hits[0]] = right_index[hits[1]]

    return pd.Series(values, index=index, name="index_right")


def sjoin_points_to_poly(point_df, poly_df):
    """Perfom a spatial join between left and right, then remove duplicate entries
    for right by left (e.g., feature in left overlaps multiple features in right).

    Returns the first spatial join for each point.

    Parameters
    ----------
    point_df : GeoDataFrame
    poly_df : GeoDataFrame

    Returns
    -------
    GeoDataFrame
        all columns of left plus all non-geometry columns from right
    """
    if len(point_df) > len(poly_df):
        tree = shapely.STRtree(point_df.geometry.values)
        poly_ix, pt_ix = tree.query(poly_df.geometry.values, predicate="intersects")

    else:
        tree = shapely.STRtree(poly_df.geometry.values)
        pt_ix, poly_ix = tree.query(point_df.geometry.values, predicate="intersects")

    # reduce to unique poly per pt
    j = pd.DataFrame(
        {"index_right": poly_df.index.values.take(poly_ix)},
        index=point_df.index.values.take(pt_ix),
    )
    grouped = j.groupby(level=0)
    if grouped.size().max() > 1:
        print(
            "WARNING: multiple target areas returned in spatial join for a single point"
        )

        j = grouped.first()

    return (
        point_df.join(j.index_right, how="left")
        .join(poly_df.drop(columns=["geometry"]), on="index_right")
        .drop(columns=["index_right"])
    )
