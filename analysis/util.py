import geopandas as gp
import pandas as pd
import numpy as np


def spatial_join(left, right):
    left.sindex
    right.sindex

    joined = gp.sjoin(left, right, how="left").drop(columns=["index_right"])

    # WARNING: some places have overlapping areas (e.g., protected areas), this creates extra records!
    # Take the first entry in each case
    grouped = joined.groupby(level=0)
    if grouped.size().max() > 1:
        print(
            "WARNING: multiple target areas returned in spatial join for a single point"
        )

        # extract the right side indexed by the left, and take first record
        right = grouped[
            [c for c in right.columns if not c == right._geometry_column_name]
        ].first()
        joined = left.join(right)

    # pending https://github.com/geopandas/geopandas/issues/846
    # we have to reassign the original index name
    joined.index.name = left.index.name

    return joined


def append(target_df, df):
    """Append df to the end of target_df.

    Intended to be used in a loop where you are appending multiple dataframes
    together.

    Parameters
    ----------
    target_df : GeoDataFrame or DataFrame
        May be none for the first append operation.  If so, the df
        will be returned.
    df : GeoDataFrame or DataFrame
        dataframe to append

    Returns
    -------
    GeoDataFrame or DataFrame
    """

    if target_df is None:
        return df

    return target_df.append(df, ignore_index=True, sort=False)


def flatten_series(series):
    """Convert a series, which may have iterables, into a flattened series,
    repeating index values as necessary.

    Parameters
    ----------
    series : Series

    Returns
    -------
    Series
        index will have duplicate values for each entry in the original iterable for that index
    """
    return pd.Series(
        np.concatenate(series.values), index=np.repeat(series.index, series.apply(len))
    )

