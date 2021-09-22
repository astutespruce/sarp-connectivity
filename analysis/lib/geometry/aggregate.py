import geopandas as gp
import pandas as pd
import pygeos as pg
import numpy as np

from analysis.lib.geometry.explode import explode
from analysis.lib.graph import DirectedGraph


def dissolve(df, by, grid_size=None, agg=None, allow_multi=True, op="union"):
    """Dissolve a DataFrame by grouping records using "by".

    Contiguous or overlapping geometries will be unioned together.

    Parameters
    ----------
    df : GeoDataFrame
        geometries must be single-part geometries
    by : str or list-like
        field(s) to dissolve by
    grid_size : float
        precision grid size, will be used in union operation
    agg : dict, optional (default: None)
        If present, is a dictionary of field names in df to agg operations.  Any
        field not aggregated will be set to null in the appended dissolved records.
    allow_multi : bool, optional (default: True)
        If False, geometries will
    op : str, one of {'union', 'coverage_union'}
    """

    if agg is not None:
        if "geometry" in agg:
            raise ValueError("Cannot use user-specified aggregator for geometry")
    else:
        agg = dict()

    agg["geometry"] = lambda g: union_or_combine(
        g.values.data, grid_size=grid_size, op=op
    )

    # Note: this method is 5x faster than geopandas.dissolve (until it is migrated to use pygeos)
    dissolved = gp.GeoDataFrame(
        df.groupby(by).agg(agg).reset_index(), geometry="geometry", crs=df.crs
    )

    if not allow_multi:
        # flatten any multipolygons
        dissolved = explode(dissolved).reset_index(drop=True)

    return dissolved


def union_or_combine(geometries, grid_size=None, op="union"):
    """First does a check for overlap of geometries according to STRtree
    intersects.  If any overlap, then will use union_all on all of them;
    otherwise will return as a multipolygon.

    If only one polygon is present, it will be returned in a MultiPolygon.

    If coverage_union op is provided, geometries must be polygons and
    topologically related or this will produce bad output or fail outright.
    See docs for coverage_union in GEOS.

    Parameters
    ----------
    geometries : ndarray of single part polygons
    grid_size : [type], optional (default: None)
        provided to union_all; otherwise no effect
    op : str, one of {'union', 'coverage_union'}

    Returns
    -------
    MultiPolygon
    """

    geom_types = np.unique(pg.get_type_id(geometries))

    if set(geom_types) - {0, 1, 3}:
        print("Inputs to union or combine must be single-part geometries")

    if geom_types[0] == 0:
        multi_type = pg.points
    elif geom_types[0] == 1:
        multi_type = pg.multilinestrings
    elif geom_types[0] == 3:
        multi_type = pg.multipolygons
    else:
        raise ValueError(
            f"Aggregate geometry type not supported for GeometryType {geom_types[0]}"
        )

    if len(geometries) == 1:
        return multi_type(geometries)

    tree = pg.STRtree(geometries)
    left, right = tree.query_bulk(geometries, predicate="intersects")
    # drop self intersections
    ix = left != right
    left = left[ix]
    right = right[ix]

    # no intersections, just combine parts
    if len(left) == 0:
        return multi_type(geometries)

    # find groups of contiguous geometries and union them together individually
    contiguous = np.sort(np.unique(np.concatenate([left, right])))
    discontiguous = np.setdiff1d(np.arange(len(geometries), dtype="uint"), contiguous)
    groups = DirectedGraph.from_arrays(left, right).components()

    parts = []

    if op == "coverage_union":
        for group in groups:
            parts.extend(pg.get_parts(pg.coverage_union_all(geometries[list(group)])))

    else:
        for group in groups:
            parts.extend(
                pg.get_parts(pg.union_all(geometries[list(group)], grid_size=grid_size))
            )

    parts.extend(pg.get_parts(geometries[discontiguous]))

    return multi_type(parts)


def find_contiguous_groups(geometries):
    """Find all adjacent geometries

    Parameters
    ----------
    geometries : ndarray of pygeos geometries


    Returns
    -------
    DataFrame indexed on the integer index of geometries
    """
    tree = pg.STRtree(geometries)
    left, right = tree.query_bulk(geometries, predicate="intersects")
    # drop self intersections
    ix = left != right
    left = left[ix]
    right = right[ix]

    groups = DirectedGraph.from_arrays(left, right).components()
    groups = (
        pd.DataFrame(
            {i: list(g) for i, g in enumerate(groups)}.items(),
            columns=["group", "index"],
        )
        .explode("index")
        .set_index("index")
    )

    return groups
