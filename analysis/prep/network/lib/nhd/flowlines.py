import warnings

import numpy as np
import pandas as pd
import shapely
from pyogrio import read_dataframe

from analysis.lib.geometry import make_valid
from analysis.prep.network.lib.nhd.util import get_column_names

warnings.filterwarnings("ignore", message=".*geometry types are not supported*")


FLOWLINE_COLS = [
    "NHDPlusID",
    "ReachCode",  # theoretically this can be used to join to NHD Plus Med Res
    "FlowDir",
    "FType",
    "FCode",
    "GNIS_ID",
    "GNIS_Name",
    "InNetwork",  # flowlines are only useful for InNetwork = 1
]

VAA_COLS = [
    "NHDPlusID",
    "StreamOrde",
    "StreamLeve",
    "StreamCalc",
    "AreaSqKm",
    "TotDASqKm",
    "Slope",
    "MinElevSmo",
    "MaxElevSmo",
    "Divergence",
    "LevelPathI",
    "TerminalPa",
]

EROMMA_COLS = ["NHDPlusID", "QAMA", "VAMA"]


def extract_flowlines(gdb, target_crs):
    """
    Extracts flowlines data from NHDPlusHR data product.
    Extract flowlines from NHDPlusHR data product, joins to VAA table,
    and filters out coastlines.
    Extracts joins between flowlines, and filters out coastlines.

    Parameters
    ----------
    gdb : str
        path to the NHD HUC4 Geodatabase
    target_crs: GeoPandas CRS object
        target CRS to project NHD to for analysis, like length calculations.
        Must be a planar projection.

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
        (flowlines, joins)
    """

    ### Read in flowline data and convert to data frame
    print("Reading flowlines")
    layer = "NHDFlowline"
    read_cols, col_map = get_column_names(gdb, layer, FLOWLINE_COLS)

    df = read_dataframe(gdb, layer=layer, columns=read_cols, use_arrow=True).rename(columns=col_map)

    df["geometry"] = shapely.force_2d(df.geometry.values)

    # Index on NHDPlusID for easy joins to other NHD data
    df.NHDPlusID = df.NHDPlusID.astype("uint64")
    df = df.set_index(["NHDPlusID"], drop=False)

    df["offnetwork"] = ~df.InNetwork.fillna(0).astype("bool")
    # drop any that are offnetwork and pipelines / underground connectors
    df = df.loc[~(df.offnetwork & df.FType.isin([420, 428]))]

    # convert MultiLineStrings to LineStrings (all have a single linestring)
    df.geometry = shapely.get_geometry(df.geometry.values, 0)

    print("making valid and projecting to target projection")
    df.geometry = make_valid(df.geometry.values)
    df = df.to_crs(target_crs)
    print(f"Read {len(df):,} flowlines")

    ### Read in VAA and convert to data frame
    # NOTE: these are only valid where offnetwork is False
    print("Reading VAA table and joining...")
    layer = "NHDPlusFlowlineVAA"
    read_cols, col_map = get_column_names(gdb, layer, VAA_COLS)

    vaa_df = (
        read_dataframe(gdb, layer=layer, columns=read_cols, read_geometry=False, use_arrow=True)
        .rename(columns=col_map)
        .rename(
            columns={
                "StreamOrde": "StreamOrder",
                "StreamLeve": "StreamLevel",
                "MinElevSmo": "MinElev",
                "MaxElevSmo": "MaxElev",
                "LevelPathI": "LevelPathID",
                "TerminalPa": "TerminalID",
            }
        )
    )

    vaa_df.NHDPlusID = vaa_df.NHDPlusID.astype("uint64")
    df = df.join(vaa_df.set_index(["NHDPlusID"]))

    # Simplify data types for smaller files and faster IO
    for field in ["StreamOrder", "StreamCalc", "StreamLevel", "Divergence"]:
        # Note: value 0 signals it is not valid
        # -9 values are invalid coming in (e.g., coastlines)
        df.loc[df[field] == -9, field] = 0
        df[field] = df[field].fillna(0).astype("uint8")

    for field in ["FType", "FCode"]:
        df[field] = df[field].astype("uint16")

    for field in ["Slope", "MinElev", "MaxElev"]:
        df[field] = df[field].fillna(-9998.0).astype("float32")

    for field in ["LevelPathID", "TerminalID"]:
        df[field] = df[field].fillna(0).astype("uint64")

    for field in ["AreaSqKm", "TotDASqKm"]:
        # Note: 0 values signal not valid
        df[field] = df[field].fillna(0).astype("float32")

    ### Read in EROMMA_COLS
    # NOTE: these are only valid where offnetwork is False
    layer = "NHDPlusEROMMA"
    read_cols, col_map = get_column_names(gdb, layer, EROMMA_COLS)
    flow_df = (
        read_dataframe(gdb, layer=layer, columns=read_cols, read_geometry=False, use_arrow=True)
        .rename(columns=col_map)
        .rename(columns={"QAMA": "AnnualFlow", "VAMA": "AnnualVelocity"})
    )
    flow_df.NHDPlusID = flow_df.NHDPlusID.astype("uint64")
    flow_df = flow_df.set_index("NHDPlusID")
    df = df.join(flow_df)

    for field in ["AnnualFlow", "AnnualVelocity"]:
        df[field] = df[field].fillna(-9998.0).astype("float32")

    ### Read in flowline joins
    # NOTE: these are only present for flowlines where offnetwork is False
    print("Reading flowline joins")
    layer = "NHDPlusFlow"
    read_cols, col_map = get_column_names(gdb, layer, ["FromNHDPID", "ToNHDPID"])
    join_df = (
        read_dataframe(gdb, layer=layer, columns=read_cols, read_geometry=False, use_arrow=True)
        .rename(columns=col_map)
        .rename(columns={"FromNHDPID": "upstream", "ToNHDPID": "downstream"})
    )
    join_df.upstream = join_df.upstream.astype("uint64")
    join_df.downstream = join_df.downstream.astype("uint64")

    ### Fix errors in NHD
    # some valid joins are marked as terminals (downstream==0) in NHD; we need
    # to backfill the missing join info.
    # To do this, we intersect all terminals back with flowlines dropping any
    # that are themselves terminals.  Then we calculate the distance to the upstream
    # point of the intersected line, and the upstream point of the next segment
    # downstream.  We use the ID of whichever one is closer (must be within 100m).
    ix = join_df.loc[join_df.downstream == 0].upstream.unique()
    # get last point, is furthest downstream
    tmp = df.loc[df.index.isin(ix), ["geometry"]].copy()
    tmp["geometry"] = shapely.get_point(tmp.geometry.values, -1)

    target = df.loc[~df.index.isin(ix)]

    # only search against other flowlines
    tree = shapely.STRtree(target.geometry.values)
    # search within a tolerance of 0.001, these are very very close
    left, right = tree.query_nearest(tmp.geometry.values, max_distance=0.001)

    pairs = pd.DataFrame(
        {
            "left": tmp.index.take(left),
            "right": target.index.take(right),
            "source": tmp.geometry.values.take(left),
            # take upstream / downstream points of matched lines
            "upstream_target": shapely.get_point(df.geometry.values.take(right), 0),
        }
    )

    # drop any pairs where the other side is also a terminal (these appear as
    # V shaped tiny networks that need to be left as is)
    pairs = pairs.loc[~pairs.right.isin(ix)]

    # calculate the next segment downstream (only keep the first if multiple; possible logic issue)
    next_downstream = (
        join_df.loc[(join_df.upstream != 0) & (join_df.downstream != 0)].groupby("upstream").downstream.first()
    )
    pairs["next_downstream"] = pairs.right.map(next_downstream)
    pairs.loc[pairs.next_downstream.notnull(), "downstream_target"] = shapely.get_point(
        df.loc[pairs.loc[pairs.next_downstream.notnull()].next_downstream].geometry.values,
        0,
    )

    pairs["upstream_dist"] = shapely.distance(pairs.source, pairs.upstream_target)
    ix = pairs.next_downstream.notnull()
    pairs.loc[ix, "downstream_dist"] = shapely.distance(pairs.loc[ix].source, pairs.loc[ix].downstream_target)

    # this ignores any nan
    pairs["dist"] = pairs[["upstream_dist", "downstream_dist"]].min(axis=1)
    # discard any that are too far (>100m)
    pairs = pairs.loc[pairs.dist <= 100].copy()

    # sort by distance to upstream point of matched flowline; this allows us
    # to sort on those then dedup to calculate a new downstream ID for this source line
    pairs = pairs.sort_values(by=["left", "dist"])

    # set the right value to the next downstream if it is closer
    # this also ignores na
    ix = pairs.downstream_dist < pairs.upstream_dist
    pairs.loc[ix, "right"] = pairs.loc[ix].next_downstream.astype("uint64")

    ids = pairs.groupby("left").right.first()

    if len(ids):
        # save to send to NHD
        pd.DataFrame({"NHDPlusID": ids.index.unique()}).to_csv(f"/tmp/{gdb.stem}_bad_joins.csv", index=False)

        ix = join_df.upstream.isin(ids.index)
        join_df.loc[ix, "downstream"] = join_df.loc[ix].upstream.map(ids)

        print(f"Repaired {len(ids):,} joins marked by NHD as terminals but actually joined to flowlines")

    ### Filter out coastlines and update joins
    # WARNING: we tried filtering out pipelines (FType == 428).  It doesn't work properly;
    # there are many that go through dams and are thus needed to calculate
    # network connectivity and gain of removing a dam.
    print("Filtering out coastlines...")
    coastline_idx = df.loc[df.FType == 566].index
    df = df.loc[~df.index.isin(coastline_idx)].copy()
    print(f"{len(df):,} features after removing coastlines")

    # remove any joins that have coastlines as upstream
    # these are themselves coastline segments
    join_df = join_df.loc[~join_df.upstream.isin(coastline_idx)].copy()

    # set the downstream to 0 for any that join coastlines
    # this will enable us to mark these as downstream terminals in
    # the network analysis later
    join_df["marine"] = join_df.downstream.isin(coastline_idx)
    join_df.loc[join_df.marine, "downstream"] = 0

    # drop any duplicates (above operation sets some joins to upstream and downstream of 0)
    join_df = join_df.drop_duplicates(subset=["upstream", "downstream"])

    ### set join types to make it easier to track
    join_df["type"] = "internal"  # set default
    # upstream-most origin points
    join_df.loc[join_df.upstream == 0, "type"] = "origin"
    # downstream-most termination points
    join_df.loc[join_df.downstream == 0, "type"] = "terminal"

    ### Label loops for easier removal later
    print("Identifying loops")
    df["loop"] = (df.StreamOrder != df.StreamCalc) | (df.FlowDir.isnull())

    idx = df.loc[df.loop].index
    join_df["loop"] = join_df.upstream.isin(idx) | join_df.downstream.isin(idx)

    # drop columns not useful for later processing steps
    df = df.drop(columns=["FlowDir", "StreamCalc", "InNetwork"])

    # Cleanup invalid joins
    join_df = join_df.loc[(join_df.upstream != 0) | (join_df.downstream != 0)].copy()

    ### Add calculated fields
    # lineIDs are 1-based because join==0 indicates endpoints of network
    df["lineID"] = np.arange(1, len(df) + 1, dtype="uint32")
    # add in 0 so that joining on NHDPlusID==0 works properly
    tmp = pd.concat([df.lineID, pd.Series(np.uint32([0]), index=np.uint64([0]))])
    join_df = join_df.join(tmp.rename("upstream_id"), on="upstream").join(tmp.rename("downstream_id"), on="downstream")

    # calculate incoming joins (have valid upstream, but not in this HUC4)
    join_df.loc[(join_df.upstream != 0) & (join_df.upstream_id.isnull()), "type"] = "huc_in"

    join_df = join_df.fillna(0)

    for col in ("upstream", "downstream"):
        join_df[col] = join_df[col].astype("uint64")

    for col in ("upstream_id", "downstream_id"):
        join_df[col] = join_df[col].astype("uint32")

    ### Calculate size classes
    print("Calculating size class")
    drainage = df.TotDASqKm
    df.loc[drainage == 0, "sizeclass"] = ""  # not valid
    df.loc[(drainage > 0) & (drainage < 10), "sizeclass"] = "1a"
    df.loc[(drainage >= 10) & (drainage < 100), "sizeclass"] = "1b"
    df.loc[(drainage >= 100) & (drainage < 518), "sizeclass"] = "2"
    df.loc[(drainage >= 518) & (drainage < 2590), "sizeclass"] = "3a"
    df.loc[(drainage >= 2590) & (drainage < 10000), "sizeclass"] = "3b"
    df.loc[(drainage >= 10000) & (drainage < 25000), "sizeclass"] = "4"
    df.loc[drainage >= 25000, "sizeclass"] = "5"

    # Calculate length
    print("Calculating length")
    df["length"] = df.geometry.length.astype("float32")

    return df, join_df
