import numpy as np
import pandas as pd


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
        if len(df) > 0:
            return df
        return None

    if len(df) > 0:
        return pd.concat([target_df, df], ignore_index=True, sort=False)

    return target_df


def flatten_series(series):
    """Convert a series, which may have iterables, into a flattened series,
    repeating index values as necessary.

    NOTE: this can also be done using .explode() on the pandas Series or DataFrame.

    Parameters
    ----------
    series : Series

    Returns
    -------
    Series
        index will have duplicate values for each entry in the original iterable for that index
    """
    return pd.Series(np.concatenate(series.values), index=np.repeat(series.index, series.apply(len)))


def ndarray_append_strings(*args):
    if len(args) < 2:
        raise ValueError("Must have at least 2 values to append per element")

    def get_str(value):
        if (isinstance(value, np.ndarray) or isinstance(value, pd.Series)) and not value.dtype == "O":
            return value.astype("str")
        return str(value)

    result = get_str(args[0]) + get_str(args[1])

    for i in range(2, len(args)):
        result = result + get_str(args[i])

    return result


def get_signed_dtype(dtype):
    """Find the appropriate signed dtype for unsigned integers, allowing others
    to pass through unchanged.

    Parameters
    ----------
    dtype : numpy dtype

    Returns
    -------
    str
        numpy dtype string
    """
    if dtype == object:
        return dtype

    if dtype == bool:
        return "int8"

    if dtype.kind == "u":
        bits = int(str(dtype.name).replace("uint", ""))
        if bits < 64:
            bits *= 2
        return f"int{bits}"

    return dtype
