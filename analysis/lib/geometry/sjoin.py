import pandas as pd
import pygeos as pg
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
