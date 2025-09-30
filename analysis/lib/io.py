from pathlib import Path
import warnings

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


def read_arrow_tables(paths, columns=None, filter=None, new_fields=None, dict_fields=None, allow_missing_columns=False):
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
        the same order and length as paths
    dict_fields : list-like, optional (default: None)
        if present, is a list of new fields that should be dictionary encoded
        Do not use for existing fields already in the tables
    allow_missing_columns : bool, optional (default: False)
        if True and some of the columns are not present in any of the source files,
        will emit a warning instead of an error

    Returns
    -------
    pyarrow.Table
    """

    # validate requested columns
    if columns is not None:
        detected_columns = []
        for path in paths:
            if Path(path).exists():
                detected_columns.extend(dataset(path, format="feather").schema.names)
        missing = set(columns).difference(set(detected_columns))
        if missing:
            message = f"Columns not present in any of the source paths: {', '.join(missing)}"
            if allow_missing_columns:
                warnings.warn(message)
            else:
                raise ValueError(message)

    merged = None
    for i, path in enumerate(paths):
        if not Path(path).exists():
            warnings.warn(f"{path} does not exist")
            continue

        reader = dataset(path, format="feather")

        # select subset of columns present in this particular dataset
        if columns is not None:
            read_columns = [c for c in reader.schema.names if c in columns]
        else:
            read_columns = None

        table = reader.to_table(columns=read_columns, filter=filter)

        if new_fields is not None:
            for field, values in new_fields.items():
                if dict_fields is not None and field in dict_fields:
                    # uint8 not yet supported for conversion to pandas categoricals
                    index_value = np.int8(i) if len(paths) < 125 else np.uint32(i)
                    new_col = pa.DictionaryArray.from_arrays(np.repeat(index_value, len(table)), new_fields[field])

                else:
                    new_col = pa.array(np.repeat(values[i], len(table)))

                table = table.append_column(field, [new_col])

        merged = pa.concat_tables([merged, table], promote_options="permissive") if merged is not None else table

    # retain geospatial metadata, drop pandas metadata
    out_metadata = {}

    if merged.schema.metadata is not None and "geometry" in (columns or []):
        geo_metadata = merged.schema.metadata.get(b"geo")
        if geo_metadata:
            out_metadata[b"geo"] = geo_metadata

    merged = merged.replace_schema_metadata(out_metadata)

    return merged.combine_chunks()
