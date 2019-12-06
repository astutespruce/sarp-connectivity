from time import time

import pandas as pd
import geopandas as gp
import networkx as nx
import numpy as np

from analysis.util import flatten_series


def dissolve_waterbodies(df, joins, avoid_features):
    """Dissolve waterbodies that overlap, duplicate, or otherwise touch each other.
    Unless they intersect with avoid_features, in which case they are not dissolved.

    Parameters
    ----------
    df : GeoDataFrame
        waterbodies
    joins : DataFrame
        waterbody / flowline joins
    avoid_features : GeoDataFrame
        Features that indicate a given waterbody should not be dissolved with its neighbors.
        May contain features like dams, that represent meaningful breaks between waterbodies.
        WARNING: these will not be spatially deduplicated.
    """
    ### Join waterbodies to themselves to find overlaps
    # TODO: implment our own alternative to sjoin that avoids self-combinations
    start = time()
    print("Identifying overlapping / adjacent waterbodies")
    wb = df[["geometry"]].copy()
    wb.sindex
    to_agg = gp.sjoin(wb, wb).join(df[["FType"]])

    # drop the self-intersections
    to_agg = to_agg.loc[to_agg.index != to_agg.index_right].copy()

    # Skip any poly that intersects one of the NHD Lines (might be a dam or similar)
    # we need these as waterbody exit points later to snap dams
    to_join = to_agg[["geometry"]].copy()
    to_join.sindex
    avoid_features.sindex
    skip = gp.sjoin(to_join, avoid_features, how="inner").index
    to_agg = to_agg.loc[
        ~(to_agg.index.isin(skip) | (to_agg.index_right.isin(skip)))
    ].copy()

    if len(to_agg):
        # Use network (mathematical, not aquatic) adjacency analysis
        # to identify all sets of waterbodies that touch.
        # Construct an identity map from all wbIDs to their newID (will be new wbID after dissolve)
        grouped = to_agg.groupby(level=0).index_right.unique()
        pairs = flatten_series(grouped)
        network = nx.from_pandas_edgelist(pairs.reset_index(), "index", 0)
        components = pd.Series(nx.connected_components(network)).apply(list)
        groups = pd.DataFrame(flatten_series(components)).rename(columns={0: "wbID"})

        next_id = df.index.max() + 1
        groups["group"] = (next_id + groups.index).astype("uint32")
        groups = groups.set_index("wbID").group

        # assign group to polygons to aggregate
        to_agg = to_agg.join(groups).drop(columns=["index_right"])
        to_agg["wbID"] = to_agg.group

        ### Dissolve groups
        # automatically takes the first FType
        print(
            "Dissolving {:,} adjacent polygons into {:,} new polygons, this might take a while...".format(
                len(to_agg), len(groups.unique())
            )
        )
        # Shouldn't need to explode any multipolygons: .explode()
        dissolved = to_agg.dissolve(by="group").reset_index(drop=True)
        dissolved["AreaSqKm"] = (dissolved.geometry.area * 1e-6).astype("float32")
        dissolved["NHDPlusID"] = 0
        dissolved.NHDPlusID = dissolved.NHDPlusID.astype("uint64")
        dissolved.wbID = dissolved.wbID.astype("uint32")

        # remove waterbodies that were dissolved, and append the result
        # of the dissolve
        df = (
            df.loc[~df.index.isin(to_agg.index)]
            .reset_index()
            .append(dissolved, ignore_index=True, sort=False)
            .set_index("wbID")
        )

        # update joins
        ix = joins.loc[joins.wbID.isin(groups.index)].index
        joins.loc[ix, "wbID"] = joins.loc[ix].wbID.map(groups)

        # Just in case
        joins = joins.drop_duplicates().reset_index(drop=True)

    print("Done resolving overlapping waterbodies in {:.2f}s")

    return df, joins
