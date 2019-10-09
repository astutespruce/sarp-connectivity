"""
Merge network analysis outputs across regions, and join back into the pre-processed barriers inventory datasets.
"""

from pathlib import Path
import os
from time import time
from itertools import chain
import pandas as pd
import geopandas as gp
from shapely.geometry import MultiLineString
from geofeather import from_geofeather, to_geofeather

from nhdnet.io import (
    serialize_df,
    deserialize_df,
    to_shp,
    deserialize_dfs,
    deserialize_gdfs,
)

from analysis.constants import REGION_GROUPS, CRS, NETWORK_TYPES, CONNECTED_REGIONS
from analysis.network.lib.stats import calculate_network_stats

data_dir = Path("data")

start = time()

network_type = NETWORK_TYPES[1]
print("Processing {}".format(network_type))

### Read in original joins to find the ones that cross regions
print("Reading joins...")
joins = deserialize_dfs(
    [
        data_dir / "nhd/flowlines" / region / "flowline_joins.feather"
        for region in CONNECTED_REGIONS
    ],
    src=[region for region in CONNECTED_REGIONS],
).rename(columns={"src": "region"})


### Read in network segments from upstream and downstream regions for regions that cross
print("Reading network segments...")
network_df = deserialize_dfs(
    [
        data_dir / "networks" / region / network_type / "raw/network_segments.feather"
        for region in CONNECTED_REGIONS
    ],
    src=[region for region in CONNECTED_REGIONS],
).set_index("networkID")

### Read barrier joins
# WARNING: barrier joins do not reflect networks that were merged together due to multiple upstreams at a barrier
print("Reading barrier joins...")
barrier_joins = deserialize_dfs(
    [
        data_dir / "networks" / region / network_type / "raw/barrier_joins.feather"
        for region in CONNECTED_REGIONS
    ],
    src=[region for region in CONNECTED_REGIONS],
).set_index("barrierID")


### Remove dangling upstream networks
# For any barriers that had multiple upstreams, those were coalesced to a single network above
# So drop any dangling upstream references (those that are not in networks and non-zero)
barrier_joins = barrier_joins.loc[
    barrier_joins.upstream_id.isin(network_df.index) | (barrier_joins.upstream_id == 0)
].copy()


### Extract the joins that cross region boundaries, and set new upstream IDs for them
cross_region = joins.loc[(joins.type == "huc_in") & (joins.upstream_id == 0)]

cross_region = cross_region.join(
    joins.set_index("downstream")[["downstream_id", "region"]].rename(
        columns={"downstream_id": "new_upstream_id", "region": "from_region"}
    ),
    on="upstream",
)
cross_region = cross_region.loc[
    cross_region.new_upstream_id.notnull()
].drop_duplicates()
cross_region.upstream_id = cross_region.new_upstream_id.astype("uint64")

cross_region = cross_region[
    ["upstream", "downstream", "upstream_id", "downstream_id", "region", "from_region"]
].copy()

# Sanity check
print("{:,} flowlines cross region boundaries".format(len(cross_region)))
print(cross_region[["from_region", "region"]].rename(columns={"region": "to_region"}))


### Determine upstream and downstream networkIDs for these joins
# the upstream_id set above should be a networkID in each upstream region's network
# UNLESS there are barriers right at the junction between regions.
cross_region["upstream_network"] = cross_region.upstream_id

# On the downstream side, need to lookup from lineID to networkID
downstream_networks = (
    network_df.loc[network_df.lineID.isin(cross_region.downstream_id)]
    .reset_index()
    .set_index("lineID")
    .networkID
)
cross_region = cross_region.join(
    downstream_networks.rename("downstream_network"), on="downstream_id"
)


### Reassign the upstream networks to the downstream networks
print("------------------- Reassigning networks -----------")

# cross_region.upstream_network is the upstream side of the join
# so for every segment that has that networkID, reassign its networkID
# to the cross_region.downstream_network (the new connected network extending)
# upstream from the downstream regions)
network_df = (
    network_df.join(cross_region.set_index("upstream_network").downstream_network)
    .reset_index()
    .rename(columns={"index": "networkID"})
)
idx = network_df.loc[network_df.downstream_network.notnull()].index
network_df.loc[idx, "networkID"] = network_df.loc[idx, "downstream_network"].astype(
    "uint64"
)
network_df = network_df.drop(columns=["downstream_network"]).set_index("networkID")


### Recalculate network stats for the networks that have been updated
print("------------------- Recalculating network stats -----------")
updated_network = network_df.loc[cross_region.downstream_network]
network_stats = calculate_network_stats(updated_network, barrier_joins)


# NOTE: only extract out the stats we need for the DOWNSTREAM side of barriers
# because there is no barrier at the bottom of the joined network, we never
# need to assign stats on the upstream side of a barrier in this update
cross_region_stats = cross_region.join(network_stats, on="downstream_network")[
    ["downstream_network", "upstream_network", "miles"]
]

### Update barrier joins for all regions
print("------------------- Updating barrier networks -----------")
for region in CONNECTED_REGIONS:
    out_dir = data_dir / "networks" / region / network_type

    ### Update barrier networks with the new IDs and stats
    barrier_networks = deserialize_df(
        data_dir / "networks" / region / network_type / "raw/barriers_network.feather"
    )

    # NOTE: We only update barriers that are UPSTREAM of the merged networks
    # because there are no barriers on the lower Mississippi River (downstream part of merged network).
    # (meaning, we don't have to update the upstream networks of any barriers, since there are none)

    if region in cross_region.from_region:
        # In one of the upstream regions, we need to update their downNetID and DownstreamMiles
        # join to the stats based on their original downstream networkID
        barrier_networks = barrier_networks.join(
            cross_region_stats.set_index("upstream_network"), on="downNetID"
        )
        idx = barrier_networks.loc[barrier_networks.downstream_network.notnull()].index
        barrier_networks.loc[idx, "downNetID"] = barrier_networks.loc[
            idx
        ].downstream_network.astype("uint64")
        barrier_networks.loc[idx, "DownstreamMiles"] = barrier_networks.loc[idx].miles

        barrier_networks = barrier_networks.drop(
            columns=["miles", "downstream_network"]
        )

    else:
        # in the same region as the downstream network, but need to update DownstreamMiles

        # Get only the new downstream miles, and drop the multiple incoming records
        # since there is one per upstream_network
        stats = cross_region_stats.set_index(
            "downstream_network"
        ).miles.drop_duplicates()
        barrier_networks = barrier_networks.join(stats, on="downNetID")
        idx = barrier_networks.loc[barrier_networks.miles.notnull()].index
        barrier_networks.loc[idx, "DownstreamMiles"] = barrier_networks.loc[idx].miles
        barrier_networks = barrier_networks.drop(columns=["miles"])

    serialize_df(
        barrier_networks.reset_index(drop=False), out_dir / "barriers_network.feather"
    )


### Update network geometries and barrier networks
# Cut networks from upstream regions and paste them into downstream regions
cut_networks = None
for region in cross_region.from_region.unique():
    out_dir = data_dir / "networks" / region / network_type

    ### Update network geometries
    print("Cutting downstream network from upstream region {}...".format(region))

    network = from_geofeather(
        data_dir / "networks" / region / network_type / "raw/network.feather"
    )

    # select the affected networks
    idx = network.networkID.isin(cross_region.upstream_network)
    cut = network.loc[idx].copy()

    if cut_networks is None:
        cut_networks = cut

    else:
        cut_networks = cut_networks.append(cut, ignore_index=True, sort=False)

    # write the updated network back out
    network = network.loc[~idx].copy()

    print("Serializing updated network...")
    to_geofeather(network.reset_index(drop=True), out_dir / "network.feather")
    # FIXME:
    # to_shp(network, out_dir / "network.shp")

### Update new networkID and stats into cut networks
cut_networks = (
    cut_networks[["geometry", "networkID"]]
    .set_index("networkID")
    .join(cross_region.set_index("upstream_network").downstream_network)
    .reset_index()
    .rename(columns={"index": "networkID"})
)
cut_networks.networkID = cut_networks.downstream_network
cut_networks = (
    cut_networks.drop(columns=["downstream_network"])
    .set_index("networkID")
    .join(network_stats)
)

### Read in downstream networks, remove the original networks that are merged above, and append in merged ones
for region in cross_region.region.unique():
    print("Updating merged network into downstream region {}...".format(region))
    network = from_geofeather(
        data_dir / "networks" / region / network_type / "raw/network.feather"
    )

    # select the affected networks
    idx = network.networkID.isin(cross_region.downstream_network)

    # append those cut from upstream and the original one here
    to_add = (
        cut_networks.loc[
            cut_networks.index.isin(
                cross_region.loc[cross_region.region == region].downstream_network
            )
        ]
        .reset_index()
        .append(network.loc[idx].copy(), ignore_index=True, sort=False)
        .set_index("networkID")
    )

    # dissolve the updated network
    dissolved_lines = (
        # convert back to list of linestrings so we can dissolve them together
        to_add.geometry.apply(lambda g: list(g.geoms))
        .groupby(level=0)
        .apply(list)
        .apply(lambda x: list(chain.from_iterable(x)))
        .apply(MultiLineString)
    )

    # join in stats
    to_add = network_stats.join(dissolved_lines, how="inner").reset_index()

    # remove the previous ones
    network = network.loc[~idx].copy()

    # add in the merged ones
    network = network.append(to_add, ignore_index=True, sort=False)

    # sort by networkID
    network = network.sort_values(by="networkID")

    print("Serializing updated network...")
    out_dir = data_dir / "networks" / region / network_type
    to_geofeather(network.reset_index(drop=True), out_dir / "network.feather")
    # FIXME:
    # to_shp(network, out_dir / "network.shp")

print("All done in {:.2f}s".format(time() - start))
