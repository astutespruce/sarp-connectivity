import pandas as pd
import geopandas as gp


def read_feathers(paths, columns=None, geo=False):
    """Read multiple feather files into a single DataFrame.

    Parameters
    ----------
    paths : list-like of strings or path objects
    columns : [type], optional (default: None)
        Columns to read from the feather files
    geo : bool, optional
        If True, will read as a GeoDataFrame

    Returns
    -------
    (Geo)DataFrame
    """

    read_feather = gp.read_feather if geo else pd.read_feather

    merged = None
    for path in paths:
        df = read_feather(path, columns=columns)

        merged = (
            merged.append(df, ignore_index=True, sort=False)
            if merged is not None
            else df
        )

    return merged.reset_index(drop=True)