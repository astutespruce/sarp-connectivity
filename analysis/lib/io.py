from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gp
import pyarrow as pa
from pyarrow.dataset import dataset

from analysis.constants import CRS


def read_feathers(paths, columns=None, geo=False, new_fields=None):
    """Read multiple feather files into a single DataFrame.

    Parameters
    ----------
    paths : list-like of strings or path objects
    columns : [type], optional (default: None)
        Columns to read from the feather files
    geo : bool, optional (default: False)
        If True, will read as a GeoDataFrame
    new_fields : dict, optional (default: None)
        if present, is a mapping of new field name to add to a list-like of values
        the same length as paths

    Returns
    -------
    (Geo)DataFrame
    """

    read_feather = gp.read_feather if geo else pd.read_feather

    merged = None
    for i, path in enumerate(paths):
        if not Path(path).exists():
            continue

        df = read_feather(path, columns=columns)

        if geo:
            # TEMP: have to explicitly set the CRS to normalize differences between
            # CRS objects generated using different versions of Proj
            df = df.set_crs(CRS)

        if new_fields is not None:
            for field, values in new_fields.items():
                df[field] = values[i]

        merged = pd.concat([merged, df], ignore_index=True, sort=False) if merged is not None else df

    return merged.reset_index(drop=True)


def read_arrow_tables(paths, columns=None, filter=None, new_fields=None):
    """Read multiple feather files into a single pyarrow.Table

    Parameters
    ----------
    paths : list-like of strings or path objects
    columns : [type], optional (default: None)
        Columns to read from the feather files
    filter : pyarrow.compute.Expression
        filter to apply when reading from disk
    new_fields : dict, optional (default: None)
        if present, is a mapping of new field name to add to a list-like of values
        the same length as paths
    Returns
    -------
    pyarrow.Table
    """
    merged = None
    for i, path in enumerate(paths):
        if not Path(path).exists():
            continue

        table = dataset(path, format="feather").to_table(columns=columns, filter=filter)

        if new_fields is not None:
            for field, values in new_fields.items():
                new_col = pa.array(np.repeat(values[i], len(table)))
                table = table.append_column(field, [new_col])

        try:
            merged = pa.concat_tables([merged, table]) if merged is not None else table

        except pa.lib.ArrowInvalid:
            merged = pa.concat_tables([merged, table], promote_options="default") if merged is not None else table

    return merged.combine_chunks()
