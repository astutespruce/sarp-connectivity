from time import time

import pandas as pd
import geopandas as gp
import networkx as nx
import numpy as np


def dissolve_waterbodies(df, joins):
    """Dissolve waterbodies that overlap, duplicate, or otherwise touch each other.

    WARNING: some adjacent waterbodies are divided by dams, etc.  These will need to be
    accounted for later when snapping dams.

    Parameters
    ----------
    df : GeoDataFrame
        waterbodies
    joins : DataFrame
        waterbody / flowline joins

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
        (waterbodies, waterbody joins)
    """

    ### Join waterbodies to themselves to find overlaps
    # TODO: implment our own alternative to sjoin that avoids self-combinations
    start = time()
    wb = df[["geometry"]].copy()
    wb.sindex
    to_agg = gp.sjoin(wb, wb).join(df[["FType"]])

    # drop the self-intersections
    to_agg = to_agg.loc[to_agg.index != to_agg.index_right].copy()
    print("Found {:,} waterbodies that touch or overlap".format(len(to_agg.index)))

    if len(to_agg):
        # Figure out which polygons are only touching at a single vertex
        # to_agg = to_agg.join(wb.geometry.rename("neighbor"), on="index_right")
        # to_agg["int"] = to_agg.geometry.intersection(gp.GeoSeries(to_agg.neighbor))
        # to_agg["int_type"] = gp.GeoSeries(to_agg["int"]).type

        # Drop any from here that only intersect at a point
        # other touches or overlaps will be LineString, MultiLineString, Polygon, MultiPolygon, GeometryCollection
        # to_agg = to_agg.loc[~to_agg.int_type.isin(["Point", "MultiPoint"])].drop(
        #     columns=["neighbor", "int", "int_type"]
        # )

        # Use network (mathematical, not aquatic) adjacency analysis
        # to identify all sets of waterbodies that touch.
        # Construct an identity map from all wbIDs to their newID (will be new wbID after dissolve)
        grouped = to_agg.groupby(level=0).index_right.unique()
        network = nx.from_pandas_edgelist(
            grouped.explode().rename("wbID").reset_index(), "index", "wbID"
        )
        components = pd.Series(nx.connected_components(network)).apply(list)
        groups = pd.DataFrame(components.explode().rename("wbID"))

        next_id = df.index.max() + 1
        groups["group"] = (next_id + groups.index).astype("uint32")
        groups = groups.set_index("wbID")

        # assign group to polygons to aggregate
        to_agg = to_agg.join(groups).drop(columns=["index_right"]).drop_duplicates()

        ### Dissolve groups
        # Buffer geometries slightly to make sure that any which intersect actually overlap
        print(
            "Buffering {:,} unique waterbodies before dissolving...".format(len(to_agg))
        )
        buffer_start = time()
        to_agg["geometry"] = to_agg.buffer(0.1)
        print("Buffer completed in {:.2f}s".format(time() - buffer_start))

        dissolve_start = time()
        # NOTE: automatically takes the first FType
        dissolved = to_agg.dissolve(by="group").reset_index(drop=True)

        errors = dissolved.type == "MultiPolygon"
        if errors.max():
            print(
                "WARNING: Dissolve created {:,} multipolygons, these will cause errors later!".format(
                    errors.sum()
                )
            )

        # this may create multipolygons if polygons that are dissolved don't sufficiently share overlapping geometries.
        # for these, we want to retain them as individual polygons
        # dissolved = dissolved.explode().reset_index(drop=True)
        # WARNING: this doesn't work with our logic below for figuring out groups associated with original wbIDs
        # since after exploding, we don't know what wbID went into what group

        # assign new IDs and update fields
        next_id = df.index.max() + 1
        dissolved["wbID"] = (next_id + dissolved.index).astype("uint32")
        dissolved["AreaSqKm"] = (dissolved.geometry.area * 1e-6).astype("float32")
        dissolved["NHDPlusID"] = 0
        dissolved.NHDPlusID = dissolved.NHDPlusID.astype("uint64")
        dissolved.wbID = dissolved.wbID.astype("uint32")

        print(
            "Dissolved {:,} adjacent polygons into {:,} new polygons in {:.2f}s".format(
                len(to_agg), len(dissolved), time() - dissolve_start
            )
        )

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

        # NOTE: this mapping will not work if explode() is used above
        joins.loc[ix, "wbID"] = joins.loc[ix].wbID.map(groups.group)

        # Group together ones that were dissolved above
        joins = joins.drop_duplicates().reset_index(drop=True)

    print("Done resolving overlapping waterbodies in {:.2f}s".format(time() - start))

    return df, joins
