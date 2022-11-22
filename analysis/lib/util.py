import pandas as pd
import numpy as np


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
    return pd.Series(
        np.concatenate(series.values), index=np.repeat(series.index, series.apply(len))
    )


def ndarray_append_strings(*args):
    if len(args) < 2:
        raise ValueError("Must have at least 2 values to append per element")

    def get_str(value):
        if (
            isinstance(value, np.ndarray) or isinstance(value, pd.Series)
        ) and not value.dtype == "O":
            return value.astype("str")
        return str(value)

    result = get_str(args[0]) + get_str(args[1])

    for i in range(2, len(args)):
        result = result + get_str(args[i])

    return result


def pack_bits(df, field_bits):
    """Pack categorical values into a single integer.

    All values must fit within a uint32.

    `value_shift` is optional (default: 0); if present it is the amount that
    is added to 0 to reach minimum value of value range for unpacked value.

    Parameters
    ----------
    df : DataFrame or pyarrow.Table
    field_bits : list-like of dicts
        {"field": <field>, "bits": <num bits>, "value_shift": <shift>} for each field

    Returns
    -------
    ndarray of dtype large enough to hold all values
    """

    is_pandas = isinstance(df, pd.DataFrame)

    tot_bits = sum([f["bits"] for f in field_bits])
    dtype = "uint32"
    if tot_bits <= 8:
        dtype = "uint8"
    elif tot_bits <= 16:
        dtype = "uint16"
    elif tot_bits > 32:
        raise ValueError(f"Packing requires {tot_bits} bits; needs to be less than 32")

    first = field_bits[0]
    values = df[first["field"]].values if is_pandas else df[first["field"]].to_numpy()
    values = values - first.get("value_shift", 0)
    if values.min() < 0:
        raise ValueError(f"Values for {first['field']} must be >= 0")

    values = values.astype(dtype)
    if values.max() > (2 ** first["bits"]) - 1:
        raise ValueError(
            f"Values for {first['field']} cannot be stored in {first['bits']} bits"
        )

    sum_bits = first["bits"]
    for entry in field_bits[1:]:
        field_values = (
            df[entry["field"]].values if is_pandas else df[entry["field"]].to_numpy()
        )
        field_values = field_values - entry.get("value_shift", 0)
        if field_values.min() < 0:
            raise ValueError(f"Values for {entry['field']} must be >= 0")

        if field_values.max() > (2 ** entry["bits"]) - 1:
            raise ValueError(
                f"Values for {first['field']} cannot be stored in {entry['bits']} bits"
            )

        values = values | field_values.astype(dtype) << sum_bits
        sum_bits += entry["bits"]

    return values


def unpack_bits(arr, field_bits):
    """Unpack bits in a packed integer to a DataFrame.

    `value_shift` is optional (default: 0); if present it is the amount that
    is added to 0 to reach minimum value of value range for unpacked value.

    Parameters
    ----------
    arr : ndarray or Series
    field_bits : list-like of dicts
        {"field": <field>, "bits": <num bits>, "value_shift": <shift>} for each field

    Returns
    -------
    DataFrame
        contains each field in field_bits; dtype is same as arr.dtype and
        may need to be adjusted for each field
    """
    if isinstance(arr, pd.Series):
        arr = arr.values

    out = {}
    sum_bits = 0
    for entry in field_bits:
        out[entry["field"]] = (
            (arr >> sum_bits) & ((2 ** entry["bits"]) - 1)
        ) + entry.get("value_shift", 0)
        sum_bits += entry["bits"]

    return pd.DataFrame(out)


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
