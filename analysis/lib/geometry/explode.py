import geopandas as gp
import numpy as np
import pygeos as pg


def explode(df, add_position=False):
    """Explode a GeoDataFrame containing multi* geometries into single parts.

    Note: GeometryCollections of Multi* may need to be exploded a second time.

    Parameters
    ----------
    df : GeoDataFrame
    add_position : bool, optional (default: False)
        if True, adds inner index within original geometries

    Returns
    -------
    GeoDataFrame
    """
    join_cols = [c for c in df.columns if not c == "geometry"]
    crs = df.crs
    geom, outer_index = pg.get_parts(df.geometry.values.data, return_index=True)

    if not add_position:
        return gp.GeoDataFrame(
            df[join_cols].take(outer_index), geometry=geom, crs=df.crs
        )

    if len(outer_index):
        # generate inner index as a range per value of outer_idx

        # identify the start of each run of values in outer_idx
        run_start = np.r_[True, outer_index[:-1] != outer_index[1:]]

        # count the number of values in each run
        counts = np.diff(np.r_[np.nonzero(run_start)[0], len(outer_index)])

        # increment values for each value in each run after run start
        inner_index = (~run_start).cumsum()
        # decrement these so that each run is a range that starts at 0
        inner_index -= np.repeat(inner_index[run_start], counts)

    else:
        inner_index = []

    df = df[join_cols].take(outer_index)
    df["position"] = inner_index

    return gp.GeoDataFrame(df, geometry=geom, crs=crs)
