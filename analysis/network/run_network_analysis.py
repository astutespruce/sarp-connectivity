"""Create networks by first cutting flowlines at barriers, then traversing upstream to
determine upstream networks to upstream-most endpoints or upstream barriers.

After networks are created, summary statistics are calculated.

The final outputs of this process are a set of network-related files for each region
and network type (dams or small barriers):

data/networks/<region>/<network type>/*
"""

from pathlib import Path
import os
from time import time
from itertools import product

import geopandas as gp
import pandas as pd
import numpy as np
from shapely.geometry import MultiLineString

from nhdnet.nhd.cut import cut_flowlines
from nhdnet.nhd.network import generate_networks
from nhdnet.io import (
    deserialize_df,
    deserialize_gdf,
    to_shp,
    serialize_df,
    serialize_gdf,
)

from analysis.constants import REGION_GROUPS, NETWORK_TYPES

from analysis.network.stats import calculate_network_stats
from analysis.network.barriers import read_barriers, save_barriers
from analysis.network.flowlines import cut_flowlines_at_barriers, save_cut_flowlines
from analysis.network.networks import create_networks

QA = True
# Set to True to save intermediate files

data_dir = Path("data")

start = time()
for region, network_type in product(REGION_GROUPS.keys(), NETWORK_TYPES[1:]):
    print(
        "\n\n###### Processing region {0}: {1} networks #####".format(
            region, network_type
        )
    )

    out_dir = data_dir / "networks" / region / network_type
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if QA:
        qa_dir = out_dir / "qa"
        if not os.path.exists(qa_dir):
            os.makedirs(qa_dir)

    region_start = time()

    ##################### Read Barrier data #################
    print("------------------- Preparing Barriers ----------")

    barriers = read_barriers(region, network_type)

    if QA:
        save_barriers(qa_dir, barriers)

    ##################### Cut flowlines at barriers #################
    print("------------------- Cutting Flowlines -----------")
    flowlines, joins, barrier_joins = cut_flowlines_at_barriers(region, barriers)

    if QA:
        save_cut_flowlines(qa_dir, flowlines, joins, barrier_joins)

    ##################### Create networks #################
    # IMPORTANT: the following analysis allows for multiple upstream networks from an origin or barrier
    # this happens when the barrier is perfectly snapped to the junction of >= 2 upstream networks.
    # When this is encountered, these networks are merged together and assigned the ID of the first segment
    # of the first upstream network.

    # FIXME
    print("------------------- Creating networks -----------")
    network_start = time()

    network_df = create_networks(flowlines, joins, barrier_joins)

    print(
        "{0:,} networks created in {1:.2f}s".format(
            len(network_df.index.unique()), time() - network_start
        )
    )

    if QA:
        serialize_start = time()
        print("Serializing network segments")
        serialize_gdf(network_df, qa_dir / "network_segments.feather", index=False)
        print(
            "Done serializing network segments in {:.2f}s".format(
                time() - serialize_start
            )
        )

    ##################### Network stats #################
    print("------------------- Calculating network stats -----------")

    stats_start = time()

    network_stats = calculate_network_stats(network_df)
    # WARNING: because not all flowlines have associated catchments, they are missing
    # PctNatFloodplain

    print("done calculating network stats in {0:.2f}".format(time() - stats_start))

    serialize_df(network_stats.reset_index(), out_dir / "network_stats.feather")
    network_stats.to_csv(out_dir / "network_stats.csv", index_label="networkID")

    #### Calculate up and downstream network attributes for barriers

    print("calculating upstream and downstream networks for barriers")

    upstream_networks = (
        barrier_joins[["upstream_id"]]
        .join(network_stats, on="upstream_id")
        .rename(columns={"upstream_id": "upNetID", "miles": "UpstreamMiles"})
    )

    downstream_networks = (
        barrier_joins[["downstream_id"]]
        .join(
            network_df.reset_index().set_index("lineID").networkID, on="downstream_id"
        )
        .join(network_stats.miles.rename("DownstreamMiles"), on="networkID")
        .rename(columns={"networkID": "downNetID"})
        .drop(columns=["downstream_id"])
    )

    # Note: the join creates duplicates if there are multiple upstream or downstream
    # networks for a given barrier, so we drop these duplicates after the join.
    barrier_networks = (
        upstream_networks.join(downstream_networks).join(barriers.kind).fillna(0)
    )

    # Fix data types after all the joins
    for col in ["upNetID", "downNetID", "NumSegments"]:
        barrier_networks[col] = barrier_networks[col].astype("uint32")

    for col in [
        "UpstreamMiles",
        "DownstreamMiles",
        "NetworkSinuosity",
        "PctNatFloodplain",
    ]:
        barrier_networks[col] = barrier_networks[col].astype("float32")

    barrier_networks.NumSizeClassGained = barrier_networks.NumSizeClassGained.astype(
        "uint8"
    )

    # Absolute gain is minimum of upstream or downstream miles
    barrier_networks["AbsoluteGainMi"] = (
        barrier_networks[["UpstreamMiles", "DownstreamMiles"]]
        .min(axis=1)
        .astype("float32")
    )

    # TotalNetworkMiles is sum of upstream and downstream miles
    barrier_networks["TotalNetworkMiles"] = (
        barrier_networks[["UpstreamMiles", "DownstreamMiles"]]
        .sum(axis=1)
        .astype("float32")
    )

    serialize_df(barrier_networks.reset_index(), out_dir / "barriers_network.feather")
    barrier_networks.to_csv(out_dir / "barriers_network.csv", index_label="barrierID")

    # TODO: if downstream network extends off this HUC, it will be null in the above and AbsoluteGainMin will be wrong

    ##################### Dissolve networks on networkID ########################
    print("Dissolving networks")
    dissolve_start = time()

    dissolved_lines = (
        network_df[["geometry"]]
        .groupby(level=0)
        .geometry.apply(list)
        .apply(MultiLineString)
    )

    networks = gp.GeoDataFrame(
        network_stats.join(dissolved_lines), crs=flowlines.crs
    ).reset_index()

    print("Network dissolve done in {0:.2f}".format(time() - dissolve_start))

    print("Writing dissolved network shapefile")
    serialize_gdf(networks, out_dir / "network.feather")
    to_shp(networks, out_dir / "network.shp")

    print("Region done in {:.2f}s".format(time() - region_start))

print("All done in {:.2f}s".format(time() - start))

