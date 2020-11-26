import pandas as pd
import geopandas as gp
import pygeoas as pg
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


def aggregate_contiguous(df, agg=None):
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
    agg["geometry"] = (
        lambda g: pg.union_all(g.values.data) if len(g.values) > 1 else g.values.data[0]
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


def explode(df):
    """Explode multipart features to individual geometries

    Note: the fast version of this method will be available in geopandas pending
    https://github.com/geopandas/geopandas/pull/1693

    Parameters
    ----------
    df : GeoDataFrame

    """
    parts, index = pg.get_parts(df.geometry.values.data, return_index=True)
    series = gp.GeoSeries(parts, index=df.index.take(index), name="geometry")
    return df.drop(columns=["geometry"]).join(series)
