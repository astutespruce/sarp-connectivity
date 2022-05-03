from pathlib import Path

import pandas as pd
import geopandas as gp


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

        if new_fields is not None:
            for field, values in new_fields.items():
                df[field] = values[i]

        merged = (
            pd.concat([merged, df], ignore_index=True, sort=False)
            if merged is not None
            else df
        )

    return merged.reset_index(drop=True)
