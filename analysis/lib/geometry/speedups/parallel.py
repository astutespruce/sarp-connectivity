import dask.array as da
import dask.dataframe as dd


def apply_parallel(
    function,
    array,
    chunks=4,
    drop_axis=None,
    new_axis=None,
    dtype=float,
    *args,
    **kwargs
):
    """Apply the function in parallel using Dask.

    See https://docs.dask.org/en/latest/array-api.html#dask.array.map_blocks
    for more information.

    Parameters
    ----------
    function
        function to apply
    array : ndarray
        data to apply function against
    chunks : int, optional (default: 4)
        number of chunks to break data into in order to run
    drop_axis : int or list-like, optional (default: None)
        If present, is the number or tuple of numbers of axis to drop
    new_axis : int or list-like, optional (default: None)
        If present, is the axis number or tuple of numbers of axes to add

    dtype : [type], optional (default: float)
        output dtype

    Returns
    -------
    ndarray of dtype
    """

    return (
        da.from_array(array, chunks=chunks, name=False)
        .map_blocks(
            function,
            *args,
            **kwargs,
            dtype=dtype,
            drop_axis=drop_axis,
            new_axis=new_axis,
        )
        .compute()
    )


def apply_parallel_predicate(function, array1, array2, chunks=4, *args, **kwargs):
    """Apply the pygeos predicate function in parallel using Dask.

    See https://docs.dask.org/en/latest/array-api.html#dask.array.map_blocks
    for more information.

    Parameters
    ----------
    function
        predicate function to apply, takes 2 input arrays
    array1 : ndarray
    array2 : ndarray
    chunks : int, optional (default: 4)
        number of chunks to break data into in order to run

    dtype : [type], optional (default: float)
        output dtype

    Returns
    -------
    ndarray(bool)
    """

    return da.map_blocks(
        function,
        da.from_array(array1, chunks=chunks, name=False),
        da.from_array(array2, chunks=chunks, name=False),
        dtype="bool",
    ).compute()


def apply_parallel_dataframe(function, df, partitions=4, *args, **kwargs):
    """Apply the function in parallel using Dask.

    See https://docs.dask.org/en/latest/array-api.html#dask.array.map_blocks
    for more information.

    Parameters
    ----------
    function
        function to apply
    df : DataFrame
        data frame to apply function against
    partitions : int, optional (default: 4)
        number of partitions to break data into in order to run
    drop_axis : int or list-like, optional (default: None)
        If present, is the number or tuple of numbers of axis to drop
    new_axis : int or list-like, optional (default: None)
        If present, is the axis number or tuple of numbers of axes to add

    Returns
    -------
    ndarray of dtype
    """

    return (
        dd.from_pandas(df, npartitions=partitions)
        .map_partitions(function, *args, **kwargs)
        .compute()
    )

