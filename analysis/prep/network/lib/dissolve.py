from time import time

import pandas as pd
import pygeos as pg
import geopandas as gp
import networkx as nx
import numpy as np

from analysis.lib.pygeos_util import aggregate_contiguous, sjoin_geometry


def cut_waterbodies_by_dams(df, nhd_lines):
    """Some large waterbody complexes are divided by dams; these breaks
    need to be preserved.  This is done by finding the shared edges between
    adjacent waterbodies that fall near NHD lines (which include dams), and then
    clipping these out of the waterbodies to ensure they do not dissolve together.

    These use a buffer of 0.0001 meters around the shared edges to cut out from
    waterbodies.

    Parameters
    ----------
    df : GeoDataFrame
    nhd_lines : GeoDataFrame

    Returns
    -------
    GeoDataFrame
        Contains waterbodies that have been updated to clip out adjacent edges
        that are close to NHD lines.
    """
    print("Cutting edges of adjacent waterbodies where they overlap with dams")

    start = time()

    index_name = df.index.name
    df = df.reset_index()

    # Find pairs of waterbodies that intersect, using only the outer boundary
    geometry = pd.Series(
        pg.polygons(pg.get_exterior_ring(df.geometry.values.data)), index=df[index_name]
    )
    pairs = sjoin_geometry(geometry, geometry).reset_index()
    pairs = pairs.loc[pairs[index_name] != pairs.index_right].reset_index(drop=True)

    # extract unique pairs (dedup symmetric pairs)
    pairs = pd.DataFrame(
        {index_name: pairs.min(axis=1), "index_right": pairs.max(axis=1)}
    )
    pairs = pairs.groupby(by=[index_name, "index_right"]).first().reset_index()

    tmp = df[[index_name, "geometry"]].set_index(index_name)
    pairs = pairs.join(tmp, how="inner", on=index_name).join(
        tmp, on="index_right", rsuffix="_right"
    )

    i = pg.intersection(pairs.geometry.values.data, pairs.geometry_right.values.data)
    parts = pg.get_parts(pg.get_parts(pg.get_parts(i)))
    # extract only the lines or polygons
    t = pg.get_type_id(parts)
    parts = parts[(t == 1) | (t == 3)].copy()
    # buffer slightly and merge
    split_lines = pg.get_parts(pg.union_all(pg.buffer(parts, 0.0001)))

    # now find the ones that are close to nhd_lines
    # buffer NHD lines by 100m, union, then split into parts for better indexing
    # NOTE: we use "within" predicate here to capture only those split lines that
    # are closely related to NHD lines, instead of partially intersecting.
    ref_lines = pg.get_parts(
        pg.union_all(pg.buffer(nhd_lines.geometry.values.data, 100))
    )

    tree = pg.STRtree(ref_lines)
    ix = tree.query_bulk(split_lines, predicate="within")[0]
    split_lines = split_lines[np.unique(ix)]

    # find the waterbodies that these intersect
    overlap_ix = np.unique(np.concatenate([pairs[index_name], pairs.index_right]))
    subset_ix = df.loc[df[index_name].isin(overlap_ix)].index
    tree = pg.STRtree(df.loc[subset_ix].geometry.values.data)
    w_ix = tree.query_bulk(split_lines, predicate="intersects")[1]

    # apply waterbody index back to original index
    w_ix = subset_ix[np.sort(np.unique(w_ix))]

    # cut the split lines out of the polygons to make sure they don't union together
    cut_lines = pg.union_all(split_lines)
    df.loc[w_ix, "geometry"] = pg.difference(
        df.loc[w_ix].geometry.values.data, cut_lines
    )

    print("Done clipping adjacent waterbodies {:.2f}s".format(time() - start))

    return df.set_index(index_name)


def dissolve_waterbodies(df):
    """Dissolve waterbodies that overlap, duplicate, or otherwise touch each other.

    Parameters
    ----------
    df : GeoDataFrame
        waterbodies

    Returns
    -------
    GeoDataFrame
        updated waterbodies with overlapping ones dissolved together
    """
    print("Dissolving contiguous waterbodies")

    start = time()

    index_name = df.index.name
    df = df.reset_index()

    dissolved = aggregate_contiguous(
        df,
        agg={
            index_name: lambda x: 0,
            "NHDPlusID": lambda x: 0,
            "FType": lambda x: 0,
            "FCode": lambda x: 0,
            "HUC4": "first",
        },
    ).reset_index(drop=True)

    print(f"Dissolved {len(df) - len(dissolved)} adjacent waterbodies")

    # fill in missing data
    ix = dissolved.loc[dissolved.wbID == 0].index
    next_id = df[index_name].max() + 1
    dissolved.loc[ix, index_name] = next_id + np.arange(len(ix), dtype="uint32")
    dissolved[index_name] = dissolved[index_name].astype("uint32")
    dissolved.loc[ix, "AreaSqKm"] = (
        pg.area(dissolved.loc[ix].geometry.values.data) * 1e-6
    ).astype("float32")

    df = dissolved.set_index(index_name)

    print("Done resolving overlapping waterbodies in {:.2f}s".format(time() - start))

    return df
