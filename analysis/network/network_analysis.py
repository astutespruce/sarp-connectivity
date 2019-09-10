"""This is the main processing script.

Run this after preparing NHD data for the region group identified below.

"""
from pathlib import Path
import os
from time import time

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

from analysis.constants import REGION_GROUPS

from analysis.network.stats import calculate_network_stats
from analysis.network.barriers import read_barriers

# mode determines the type of network analysis we are doing
# natural: only include waterfalls in analysis
# dams: include waterfalls and dams in analysis
# small_barriers: include waterfalls, dams, and small barriers in analysis
MODES = ("natural", "dams", "small_barriers")

### -------------------------------------------
### START Runtime variables
# These should be the only variables that need to be changed at runtime

QA = True

mode = MODES[1]

region = "02"  # Identifier of region group or region

### END Runtime variables
### -------------------------------------------

data_dir = Path("data")

# INPUT files from merge.py
nhd_dir = data_dir / "nhd/flowlines"
flowline_feather = nhd_dir / region / "flowline.feather"
joins_feather = nhd_dir / region / "flowline_joins.feather"

# INPUT files from prepare_floodplain_stats.py
fp_feather = data_dir / "floodplains" / "floodplain_stats.feather"


# OUTPUT files
out_dir = data_dir / "networks" / region / mode
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# INTERMEDIATE files for QA
if QA:
    qa_dir = out_dir / "qa"
    if not os.path.exists(qa_dir):
        os.makedirs(qa_dir)

# FINAL OUTPUT files
network_feather = out_dir / "network.feather"
network_stats_feather = out_dir / "network_stats.feather"
barrier_network_feather = out_dir / "barriers_network.feather"


#### Start
print("Processing network analysis for {} in region {}".format(mode, region))

start = time()

##################### Read Barrier data #################
print("------------------- Preparing barriers ----------")
barrier_start = time()

print("Reading barriers for analysis...")
barriers = read_barriers(region, mode)
print("Extracted {:,} barriers in this region".format(len(barriers)))

if QA:
    print("Serializing barriers...")
    serialize_gdf(barriers, qa_dir / "barriers.feather", index=False)
    to_shp(barriers, qa_dir / "barriers.shp")

print("Done preparing barriers in {:.2f}s".format(time() - barrier_start))


##################### Read NHD data #################
flowline_start = time()
print("------------------- Reading Flowlines -----------")
print("reading flowlines")
flowlines = (
    deserialize_gdf(flowline_feather)
    .set_index("lineID", drop=False)
    .drop(columns=["HUC2"])
)
joins = deserialize_df(joins_feather)
print("read {:,} flowlines".format(len(flowlines)))

print("Done reading flowlines in {:.2f}s".format(time() - flowline_start))

##################### Cut flowlines #################
cut_start = time()
print("------------------- Cutting flowlines -----------")

# since all other lineIDs use HUC4 prefixes, this should be unique
# Use the first HUC2 for the region group
next_segment_id = int(REGION_GROUPS[region][0]) * 1000000 + 1
flowlines, joins, barrier_joins = cut_flowlines(
    flowlines, barriers, joins, next_segment_id=next_segment_id
)
# barrier_joins.upstream_id = barrier_joins.upstream_id.astype("uint32")
# barrier_joins.downstream_id = barrier_joins.downstream_id.astype("uint32")
# barrier_joins.set_index("joinID", drop=False)

print("Done cutting flowlines in {:.2f}".format(time() - cut_start))

if QA:
    print("serializing cut flowlines")
    serialize_df(joins, qa_dir / "updated_joins.feather", index=False)
    serialize_df(barrier_joins, qa_dir / "barrier_joins.feather", index=False)
    serialize_gdf(flowlines, qa_dir / "split_flowlines.feather", index=False)

    print("Done serializing cut flowlines in {:.2f}".format(time() - cut_start))


##################### Create networks #################
# IMPORTANT: the following analysis allows for multiple upstream networks from an origin or barrier
# this happens when the barrier is perfectly snapped to the junction of >= 2 upstream networks.
# When this is encountered, these networks are merged together and assigned the ID of the first segment
# of the first upstream network.

print("------------------- Creating networks -----------")
network_start = time()

# remove any origin segments ()
barrier_segments = barrier_joins.loc[barrier_joins.upstream_id != 0][["upstream_id"]]

print("generating upstream index")
# Remove origins, terminals, and barrier segments
upstreams = (
    joins.loc[
        (joins.upstream_id != 0)
        & (joins.downstream_id != 0)
        & (~joins.upstream_id.isin(barrier_segments.upstream_id))
    ]
    .groupby("downstream_id")["upstream_id"]
    .apply(list)
    .to_dict()
)

# Create networks from all terminal nodes (have no downstream nodes) up to barriers
# Note: origins are also those that have a downstream_id but are not the upstream_id of another node
origin_idx = (joins.downstream_id == 0) | (
    ~joins.downstream_id.isin(joins.upstream_id.unique())
)
not_barrier_idx = ~joins.upstream_id.isin(barrier_segments.upstream_id)
root_ids = joins.loc[origin_idx & not_barrier_idx][["upstream_id"]].copy()

print(
    "Starting network creation for {} origin points and {} barriers".format(
        len(root_ids), len(barrier_segments)
    )
)

# origin segments are the root of each non-barrier origin point up to barriers
# segments are indexed by the id of the segment at the root for each network
origin_network_segments = generate_networks(root_ids, upstreams)
origin_network_segments["type"] = "origin"

# barrier segments are the root of each upstream network from each barrier
# segments are indexed by the id of the segment at the root for each network
barrier_network_segments = generate_networks(barrier_segments, upstreams)
barrier_network_segments["type"] = "barrier"

# In Progress - multiple upstreams
upstream_count = barrier_joins.groupby(level=0).size()
multiple_upstreams = barrier_joins.loc[
    barrier_joins.index.isin(upstream_count.loc[upstream_count > 1].index)
]

if len(multiple_upstreams):
    print(
        "Merging multiple upstream networks for barriers at network junctions, affects {} networks".format(
            len(multiple_upstreams)
        )
    )

    # For each barrier with multiple upstreams, coalesce their networkIDs
    for joinID in multiple_upstreams.index.unique():
        upstream_ids = multiple_upstreams.loc[joinID].upstream_id

        # Set all upstream networks for this barrier to the ID of the first
        barrier_network_segments.loc[
            barrier_network_segments.networkID.isin(upstream_ids), ["networkID"]
        ] = upstream_ids.iloc[0]

# Append network types back together
network_df = origin_network_segments.append(
    barrier_network_segments, sort=False, ignore_index=False
)

# Join back to flowlines, dropping anything that didn't get networks
network_df = flowlines.join(network_df, how="inner")

print(
    "{0} networks done in {1:.2f}".format(
        len(network_df.networkID.unique()), time() - network_start
    )
)

if QA:
    print("Serializing network segments")
    serialize_gdf(network_df, qa_dir / "network_segments.feather", index=False)


##################### Network stats #################
print("------------------- Aggregating network info -----------")

# Read in associated floodplain info and join
fp_stats = deserialize_df(fp_feather)
fp_stats = fp_stats.loc[fp_stats.HUC2.isin(REGION_GROUPS[region])].set_index(
    "NHDPlusID"
)

network_df = network_df.join(fp_stats, on="NHDPlusID")

print("calculating network stats")
stats_start = time()
network_stats = calculate_network_stats(network_df)
print("done calculating network stats in {0:.2f}".format(time() - stats_start))

serialize_df(network_stats.reset_index(), network_stats_feather)
network_stats.to_csv(
    str(network_stats_feather).replace(".feather", ".csv"), index_label="networkID"
)

# Drop columns we don't need later
network_stats = network_stats[
    ["miles", "NetworkSinuosity", "NumSizeClassGained", "PctNatFloodplain"]
]


print("calculating upstream and downstream networks for barriers")
# join to upstream networks
barriers = barriers.set_index("joinID")[["kind"]]
barrier_joins.set_index("joinID", inplace=True)

# Join upstream networks, dropping any that don't have networks
upstream_stats = barrier_joins.join(network_stats, on="upstream_id").dropna()
upstream_networks = (
    barriers.join(upstream_stats)
    .fillna(0)
    .rename(columns={"upstream_id": "upNetID", "miles": "UpstreamMiles"})
)

network_by_lineID = network_df[["lineID", "networkID"]].set_index("lineID")
downstream_networks = (
    barrier_joins.join(network_by_lineID, on="downstream_id")
    .join(network_stats, on="networkID")
    .fillna(0)
    .rename(columns={"networkID": "downNetID", "miles": "DownstreamMiles"})[
        ["downNetID", "DownstreamMiles"]
    ]
)

# Note: the join creates duplicates if there are multiple upstream or downstream
# networks for a given barrier, so we drop these duplicates after the join.
barrier_networks = upstream_networks.join(downstream_networks).drop_duplicates()

barrier_networks.UpstreamMiles = barrier_networks.UpstreamMiles.astype("float32")
barrier_networks.DownstreamMiles = barrier_networks.DownstreamMiles.astype("float32")

# Absolute gain is minimum of upstream or downstream miles
barrier_networks["AbsoluteGainMi"] = (
    barrier_networks[["UpstreamMiles", "DownstreamMiles"]].min(axis=1).astype("float32")
)

# TotalNetworkMiles is sum of upstream and downstream miles
barrier_networks["TotalNetworkMiles"] = (
    barrier_networks[["UpstreamMiles", "DownstreamMiles"]].sum(axis=1).astype("float32")
)
barrier_networks.upNetID = barrier_networks.upNetID.fillna(0).astype("uint32")
barrier_networks.downNetID = barrier_networks.downNetID.fillna(0).astype("uint32")
barrier_networks.NumSizeClassGained = barrier_networks.NumSizeClassGained.fillna(
    0
).astype("uint8")

serialize_df(barrier_networks.reset_index(), barrier_network_feather)
barrier_networks.to_csv(
    str(barrier_network_feather).replace(".feather", ".csv"), index_label="joinID"
)


# TODO: if downstream network extends off this HUC, it will be null in the above and AbsoluteGainMin will be wrong

##################### Dissolve networks on networkID ########################
print("Dissolving networks")
dissolve_start = time()

network_df = network_df.set_index("networkID", drop=False)

dissolved = (
    network_df[["geometry"]]
    .groupby(network_df.index)
    .geometry.apply(list)
    .apply(MultiLineString)
)

networks = gp.GeoDataFrame(network_stats.join(dissolved), crs=flowlines.crs)

# add networkID back
networks["networkID"] = networks.index.values.astype("uint32")

print("Network dissolve done in {0:.2f}".format(time() - dissolve_start))

print("Writing dissolved network shapefile")
serialize_gdf(networks, network_feather, index=False)
to_shp(networks, str(network_feather).replace(".feather", ".shp"))

print("All done in {:.2f}".format(time() - start))

