import os
import pygeos as pg
import geopandas as gp
import pandas as pd
from pyogrio import read_dataframe

from analysis.lib.flowlines import calculate_sinuosity


FLOWLINE_COLS = [
    "NHDPlusID",
    "FlowDir",
    "FType",
    "FCode",
    "GNIS_ID",
    "GNIS_Name",
    "geometry",
]

VAA_COLS = [
    "NHDPlusID",
    "StreamOrde",
    "StreamLeve",
    "StreamCalc",
    "TotDASqKm",
    "Slope",
    "MinElevSmo",
    "MaxElevSmo",
]

WATERBODY_COLS = [
    "NHDPlusID",
    "FType",
    "FCode",
    "GNIS_ID",
    "GNIS_Name",
    "AreaSqKm",
    "geometry",
]


def extract_flowlines(gdb_path, target_crs, extra_flowline_cols=[]):
    """
    Extracts flowlines data from NHDPlusHR data product.
    Extract flowlines from NHDPlusHR data product, joins to VAA table,
    and filters out coastlines.
    Extracts joins between flowlines, and filters out coastlines.

    Parameters
    ----------
    gdb_path : str
        path to the NHD HUC4 Geodatabase
    target_crs: GeoPandas CRS object
        target CRS to project NHD to for analysis, like length calculations.
        Must be a planar projection.
    extra_cols: list
        List of extra field names to extract from NHDFlowline layer

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
        (flowlines, joins)
    """

    ### Read in flowline data and convert to data frame
    print("Reading flowlines")
    flowline_cols = FLOWLINE_COLS + extra_flowline_cols
    df = read_dataframe(
        gdb_path, layer="NHDFlowline", force_2d=True, columns=[flowline_cols]
    )

    print("Read {:,} flowlines".format(len(df)))

    # Index on NHDPlusID for easy joins to other NHD data
    df.NHDPlusID = df.NHDPlusID.astype("uint64")
    df = df.set_index(["NHDPlusID"], drop=False)

    # convert MultiLineStrings to LineStrings (all have a single linestring)
    df.geometry = pg.get_geometry(df.geometry.values.data, 0)

    ### Read in VAA and convert to data frame
    # NOTE: not all records in Flowlines have corresponding records in VAA
    # we drop those that do not since we need these fields.
    print("Reading VAA table and joining...")
    vaa_df = read_dataframe(gdb_path, layer="NHDPlusFlowlineVAA", columns=[VAA_COLS])

    vaa_df.NHDPlusID = vaa_df.NHDPlusID.astype("uint64")
    vaa_df = vaa_df.set_index(["NHDPlusID"])
    df = df.join(vaa_df, how="inner")
    print("{:,} features after join to VAA".format(len(df)))

    # Simplify data types for smaller files and faster IO
    df.FType = df.FType.astype("uint16")
    df.FCode = df.FCode.astype("uint16")
    df.StreamOrde = df.StreamOrde.astype("uint8")
    df.Slope = df.Slope.astype("float32")
    df.MinElevSmo = df.MinElevSmo.astype("float32")
    df.MaxElevSmo = df.MaxElevSmo.astype("float32")

    ### Read in flowline joins
    print("Reading flowline joins")
    join_df = gp.read_file(gdb_path, layer="NHDPlusFlow")[
        ["FromNHDPID", "ToNHDPID"]
    ].rename(columns={"FromNHDPID": "upstream", "ToNHDPID": "downstream"})
    join_df.upstream = join_df.upstream.astype("uint64")
    join_df.downstream = join_df.downstream.astype("uint64")

    ### Label loops for easier removal later
    # WARNING: loops may be very problematic from a network processing standpoint.
    # Include with caution.
    print("Identifying loops")
    df["loop"] = (df.StreamOrde != df.StreamCalc) | (df.FlowDir.isnull())

    idx = df.loc[df.loop].index
    join_df["loop"] = join_df.upstream.isin(idx) | join_df.downstream.isin(idx)

    ### Filter out coastlines and update joins
    # WARNING: we tried filtering out pipelines (FType == 428).  It doesn't work properly;
    # there are many that go through dams and are thus needed to calculate
    # network connectivity and gain of removing a dam.
    print("Filtering out coastlines...")
    coastline_idx = df.loc[df.FType == 566].index
    df = df.loc[~df.index.isin(coastline_idx)].copy()

    # remove any joins that have coastlines as upstream
    # these are themselves coastline segments
    join_df = join_df.loc[~join_df.upstream.isin(coastline_idx)].copy()

    # set the downstream to 0 for any that join coastlines
    # this will enable us to mark these as downstream terminals in
    # the network analysis later
    join_df.loc[join_df.downstream.isin(coastline_idx), "downstream"] = 0

    # drop any duplicates (above operation sets some joins to upstream and downstream of 0)
    join_df = join_df.drop_duplicates()
    print("{:,} features after removing coastlines".format(len(df)))

    ### Add calculated fields
    # Set our internal master IDs to the original index of the file we start from
    # Assume that we can always fit into a uint32, which is ~400 million records
    # and probably bigger than anything we could ever read in
    df["lineID"] = df.index.values.astype("uint32") + 1
    join_df = (
        join_df.join(df.lineID.rename("upstream_id"), on="upstream")
        .join(df.lineID.rename("downstream_id"), on="downstream")
        .fillna(0)
    )

    for col in ("upstream", "downstream"):
        join_df[col] = join_df[col].astype("uint64")

    for col in ("upstream_id", "downstream_id"):
        join_df[col] = join_df[col].astype("uint32")

    ### Calculate size classes
    print("Calculating size class")
    drainage = df.TotDASqKm
    df.loc[drainage < 10, "sizeclass"] = "1a"
    df.loc[(drainage >= 10) & (drainage < 100), "sizeclass"] = "1b"
    df.loc[(drainage >= 100) & (drainage < 518), "sizeclass"] = "2"
    df.loc[(drainage >= 518) & (drainage < 2590), "sizeclass"] = "3a"
    df.loc[(drainage >= 2590) & (drainage < 10000), "sizeclass"] = "3b"
    df.loc[(drainage >= 10000) & (drainage < 25000), "sizeclass"] = "4"
    df.loc[drainage >= 25000, "sizeclass"] = "5"

    print("projecting to target projection")
    df = df.to_crs(target_crs)

    # Calculate length and sinuosity
    print("Calculating length and sinuosity")
    df["length"] = df.geometry.length.astype("float32")
    df["sinuosity"] = calculate_sinuosity(df.geometry.values.data).astype("float32")

    # set join types to make it easier to track
    join_df["type"] = "internal"  # set default
    join_df.loc[join_df.upstream == 0, "type"] = "origin"
    join_df.loc[join_df.downstream == 0, "type"] = "terminal"
    join_df.loc[(join_df.upstream != 0) & (join_df.upstream_id == 0), "type"] = "huc_in"

    # drop columns not useful for later processing steps
    df = df.drop(columns=["FlowDir", "StreamCalc"])

    return df, join_df


def extract_waterbodies(gdb_path, target_crs, exclude_ftypes=[], min_area=0):
    """Extract waterbodies from NHDPlusHR data product.

    Parameters
    ----------
    gdb_path : str
        path to the NHD HUC4 Geodatabase
    target_crs: GeoPandas CRS object
        target CRS to project NHD to for analysis, like length calculations.
        Must be a planar projection.
    exclude_ftypes : list, optional (default: [])
        list of FTypes to exclude.
    min_area : int, optional (default: 0)
        If provided, only waterbodies that are >= this value are retained

    Returns
    -------
    GeoDataFrame
    """
    print("Reading waterbodies")
    df = read_dataframe(
        gdb_path, layer="NHDWaterbody", columns=[WATERBODY_COLS], force_2d=True
    )
    print("Read {:,} waterbodies".format(len(df)))

    df = df.loc[
        (df.AreaSqKm >= min_area) & (~df.FType.isin(exclude_ftypes))
    ].reset_index(drop=True)
    print(
        "Retained {:,} waterbodies after dropping those below size threshold or in exclude FTypes".format(
            len(df)
        )
    )

    # Convert multipolygons to polygons
    # those we checked that are true multipolygons are errors
    df.geometry = pg.get_geometry(df.geometry.values.data, 0)

    print("projecting to target projection")
    df = df.to_crs(target_crs)

    df.NHDPlusID = df.NHDPlusID.astype("uint64")
    df.AreaSqKm = df.AreaSqKm.astype("float32")
    df.FType = df.FType.astype("uint16")

    ### Add calculated fields
    df["wbID"] = df.index.values.astype("uint32") + 1

    return df
