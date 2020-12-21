"""
Merge network analysis outputs across regions, and join back into the pre-processed barriers inventory datasets.
"""

from pathlib import Path
from time import time
import warnings
import os

import pandas as pd
import geopandas as gp
import pygeos as pg
import numpy as np
from pyogrio import write_dataframe

from analysis.constants import NETWORK_TYPES, CRS
from analysis.network.lib.stats import calculate_network_stats
from analysis.lib.io import read_feathers
from analysis.lib.util import append
from analysis.lib.pygeos_util import explode

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
src_dir = data_dir / "networks"
out_dir = src_dir / "merged"

if not out_dir.exists():
    os.makedirs(out_dir)


# TODO: expand to full region
huc4_df = pd.read_feather(
    data_dir / "boundaries/sarp_huc4.feather", columns=["HUC2", "HUC4"]
)
# Convert to dict of sorted HUC4s per HUC2
units = huc4_df.groupby("HUC2").HUC4.unique().apply(sorted).to_dict()
huc4s = huc4_df.HUC4.unique()
huc2s = huc4_df.HUC2.unique()


# VARY THIS between 0 and 2
network_type = NETWORK_TYPES[1]
print(f"Processing {network_type}")

start = time()


### Find joins between huc2s
# Note: since these are processed by network analysis, they already exclude loops
joins = read_feathers(
    [src_dir / huc2 / network_type / "flowline_joins.feather" for huc2 in huc2s],
)


### TEMP: limit to SARP HUC4s
joins = joins.loc[joins.HUC4.isin(huc4s)].copy()

### END TEMP

joins["HUC2"] = joins.HUC4.str[:2]


### Extract the joins that cross region boundaries, and set new upstream IDs for them
# We can join on the ids we generate (upstream_id, downstream_id) because there are no
# original flowlines split at HUC2 join areas
cross_region = joins.loc[(joins.type == "huc_in") & (joins.upstream_id == 0)]

cross_region = cross_region.rename(columns={"HUC2": "downstream_HUC2"}).join(
    joins.set_index("downstream")[["downstream_id", "HUC2"]].rename(
        columns={"downstream_id": "new_upstream_id", "HUC2": "upstream_HUC2"}
    ),
    on="upstream",
)
cross_region = cross_region.loc[
    cross_region.new_upstream_id.notnull()
].drop_duplicates()
cross_region.upstream_id = cross_region.new_upstream_id.astype("uint64")

# Sanity check
print("{:,} flowlines cross region boundaries".format(len(cross_region)))
print(cross_region[["upstream_HUC2", "downstream_HUC2"]])


connected_huc2 = np.unique(
    np.concatenate(
        [cross_region.upstream_HUC2.unique(), cross_region.downstream_HUC2.unique()]
    )
)
# drop any joins not in these HUC2s
joins = joins.loc[joins.HUC2.isin(connected_huc2)].copy()


### Read in network segments from upstream and downstream regions for regions that cross
print("\nReading network segments...")
network_df = read_feathers(
    [
        data_dir / "networks" / huc2 / network_type / "network_segments.feather"
        for huc2 in connected_huc2
    ],
).set_index("networkID")
network_df.lineID = network_df.lineID.astype("uint32")

### Lookup network ID for downstream segments of HUC2 join
print("Aggregating networks that cross HUC2s...")
tmp = (
    network_df.loc[network_df.lineID.isin(cross_region.downstream_id)]
    .reset_index()
    .set_index("lineID")
    .networkID.rename("downstream_network")
)
cross_region = cross_region.join(tmp, on="downstream_id")

# for all networks that start at the outlet of a HUC2, the upstream_id is the
# networkID of those networks.
cross_region["upstream_network"] = cross_region["upstream_id"]

# Start by assigning the downstream network as the new network for the upstreams.
# This handles any networks that originate in one HUC2 and terminate in another
# but do not cross multiple HUC2s
cross_region["new_network"] = cross_region["downstream_network"]

### Update new_network for any networks that cross regions
# NOTE: this assumes that there is never more than one network that crosses a
# a HUC2.
# Since a given upstream can only have one downstream, build a directed adjacency
# map from upstreams to downstreams, then traverse this to identify cases where
# there are chains of connected regions (any single pairs already handled above)
adj = cross_region.set_index("upstream_network").downstream_network.to_dict()
seen = set()
for upstream_node in adj.keys():
    if upstream_node in seen:
        continue

    next = adj[upstream_node]
    nodes = []

    while True:
        nodes.append(next)
        seen.add(next)

        next = adj.get(next, None)
        if next is None:
            break

    if len(nodes) > 1:
        # the last node visited is the furthest downstream, that becomes the
        # new network for this chain
        new_downstream = nodes[-1]
        ix = nodes[:-1]
        cross_region.loc[
            cross_region.downstream_network.isin(nodes[:-1]), "new_network"
        ] = nodes[-1]
        print(
            f"Network originating at {new_downstream} extends upstream across multiple HUC2s"
        )

# all connected networks should now have a new_network of the furthest downstream
print("Updated network connections:")
print(
    cross_region[
        [
            "upstream_HUC2",
            "downstream_HUC2",
            "upstream_network",
            "downstream_network",
            "new_network",
        ]
    ]
)

# assign target HUC2s at the base of each network
new_HUC2 = (
    cross_region.loc[cross_region.downstream_network == cross_region.new_network]
    .groupby("new_network")
    .downstream_HUC2.first()
    .to_dict()
)
cross_region["new_HUC2"] = cross_region.new_network.map(new_HUC2)


### Reassign the upstream networks to the downstream networks
print("\nReassigning networks...")

# cross_region.upstream_network is the upstream side of the join
# so for every segment that has that networkID, reassign its networkID
# to cross_region.new_network
network_df = (
    network_df.join(cross_region.set_index("upstream_network").new_network)
    .reset_index()
    .rename(columns={"index": "networkID"})
)
ix = network_df.loc[network_df.new_network.notnull()].index
network_df.loc[ix, "networkID"] = network_df.loc[ix, "new_network"].astype("uint64")
network_df = network_df.drop(columns=["new_network"]).set_index("networkID")


### Read barrier joins
# WARNING: barrier joins do not reflect networks that were merged together due
# to multiple upstreams at a barrier
print("Reading barrier joins...")
barrier_joins = read_feathers(
    [
        data_dir / "networks" / huc2 / network_type / "barrier_joins.feather"
        for huc2 in connected_huc2
    ],
).set_index("barrierID")


### Remove dangling upstream networks
# For any barriers that had multiple upstreams, those were coalesced to a single network above
# So drop any dangling upstream references (those that are not in networks and non-zero)
barrier_joins = barrier_joins.loc[
    barrier_joins.upstream_id.isin(network_df.index) | (barrier_joins.upstream_id == 0)
].copy()


### Recalculate network stats for the networks that have been updated
print("\nRecalculating network stats...")
updated_network = network_df.loc[cross_region.new_network]

# network stats facing upstream for each functional network
network_stats = calculate_network_stats(updated_network, barrier_joins)
network_stats = cross_region[
    [
        "upstream_HUC2",
        "downstream_HUC2",
        "upstream_network",
        "downstream_network",
        "new_network",
    ]
].join(network_stats, on="new_network")

upstream_stats = (
    network_stats[
        [
            "downstream_network",
            "new_network",
            "miles",
            "free_miles",
            "sinuosity",
            "segments",
            "natfldpln",
            "sizeclasses",
        ]
    ]
    .groupby("downstream_network")
    .first()
)

# stats for networks that terminate in another HUC2 downstream
downstream_stats = (
    network_stats[
        [
            "upstream_network",
            "new_network",
            "miles",
            "free_miles",
        ]
    ]
    .groupby("upstream_network")
    .first()
)

# stats for networks that terminate in the same HUC2
downstream_stats_same_huc2 = (
    network_stats[
        [
            "downstream_network",
            "new_network",
            "miles",
            "free_miles",
        ]
    ]
    .groupby("downstream_network")
    .first()
)


### Update barrier networks with the new IDs and stats
for huc2 in connected_huc2:
    print(f"\nHUC2 {huc2}: updating barrier networks...")
    barrier_networks = pd.read_feather(
        data_dir / "networks" / huc2 / network_type / "barriers_network.feather"
    )

    # update any barriers that are at the root of updated networks
    barrier_networks = barrier_networks.join(
        upstream_stats, on="upNetID", rsuffix="_right"
    )
    ix = barrier_networks.new_network.notnull()

    if ix.sum() > 0:
        print(f"updating {ix.sum()} barriers that have updated upstream networks")
        barrier_networks.loc[ix, "upNetID"] = barrier_networks.loc[
            ix
        ].new_network.astype("uint32")
        barrier_networks.loc[ix, "TotalUpstreamMiles"] = barrier_networks.loc[
            ix
        ].miles.astype("float32")
        barrier_networks.loc[ix, "FreeUpstreamMiles"] = barrier_networks.loc[
            ix
        ].free_miles.astype("float32")
        barrier_networks.loc[ix, "sinuosity"] = barrier_networks.loc[
            ix
        ].sinuosity_right.astype("float32")
        barrier_networks.loc[ix, "segments"] = barrier_networks.loc[
            ix
        ].segments_right.astype("uint32")
        barrier_networks.loc[ix, "sizeclasses"] = barrier_networks.loc[
            ix
        ].sizeclasses_right.astype("uint8")

    barrier_networks = barrier_networks.drop(
        columns=[
            "new_network",
            "miles",
            "free_miles",
            "sinuosity_right",
            "segments_right",
            "natfldpln_right",
            "sizeclasses_right",
        ]
    )

    # Update any records in this HUC2 that have updated networks DOWNSTREAM of them
    barrier_networks = barrier_networks.join(
        downstream_stats_same_huc2,
        on="downNetID",
        rsuffix="_right",
    )
    ix = barrier_networks.new_network.notnull()

    if ix.sum() > 0:
        print(
            f"updating {ix.sum()} barriers that have updated downstream networks in this HUC2"
        )
        barrier_networks.loc[ix, "downNetID"] = barrier_networks.loc[
            ix
        ].new_network.astype("uint32")
        barrier_networks.loc[ix, "TotalDownstreamMiles"] = barrier_networks.loc[
            ix
        ].miles.astype("float32")
        barrier_networks.loc[ix, "FreeDownstreamMiles"] = barrier_networks.loc[
            ix
        ].free_miles.astype("float32")

    barrier_networks = barrier_networks.drop(
        columns=[
            "new_network",
            "miles",
            "free_miles",
        ]
    )

    # update any records in UPSTREAM HUC2s that have updated networks DOWNSTREAM of them
    barrier_networks = barrier_networks.join(
        downstream_stats,
        on="downNetID",
        rsuffix="_right",
    )
    ix = barrier_networks.new_network.notnull()

    if ix.sum() > 0:
        print(
            f"updating {ix.sum()} barriers that have updated dowstream networks from other HUC2"
        )
        barrier_networks.loc[ix, "downNetID"] = barrier_networks.loc[
            ix
        ].new_network.astype("uint32")
        barrier_networks.loc[ix, "TotalDownstreamMiles"] = barrier_networks.loc[
            ix
        ].miles.astype("float32")
        barrier_networks.loc[ix, "FreeDownstreamMiles"] = barrier_networks.loc[
            ix
        ].free_miles.astype("float32")

    barrier_networks = barrier_networks.drop(
        columns=[
            "new_network",
            "miles",
            "free_miles",
        ]
    )

    huc2_dir = out_dir / huc2 / network_type
    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    barrier_networks.reset_index(drop=False).to_feather(
        huc2_dir / "barriers_network.feather"
    )


### Update network geometries and barrier networks
# identify HUC2s that will aggregate upstream networks
aggregate_huc2 = cross_region.groupby("new_HUC2").upstream_HUC2.unique().to_dict()

stats = network_stats.set_index("new_network")[
    [
        "miles",
        "free_miles",
        "sinuosity",
        "segments",
        "natfldpln",
        "sizeclasses",
        "up_ndams",
        "up_nwfs",
        "barrier",
    ]
]


for huc2 in connected_huc2:
    print(f"\nHUC2 {huc2}: moving network segments to base HUC2...")

    network = gp.read_feather(
        data_dir / "networks" / huc2 / network_type / "network.feather"
    )

    # first, remove any segments that are now "owned" by another HUC2
    ix = network.networkID.isin(cross_region.upstream_network)
    if ix.sum() > 0:
        print(f"Removing {ix.sum()} networks now owned by a downstream HUC2")
        network = network.loc[~ix].copy()

    # next, for every HUC2 that is at the root of the updated networks, pull in
    # network segments upstream
    if huc2 in aggregate_huc2:
        for upstream_huc2 in aggregate_huc2[huc2]:
            upstream_network = gp.read_feather(
                data_dir / "networks" / upstream_huc2 / network_type / "network.feather"
            )

            tmp = (
                cross_region.loc[cross_region.new_HUC2 == huc2]
                .set_index("upstream_network")
                .new_network
            )

            # join in new networkID
            upstream_network = upstream_network.join(tmp, on="networkID", how="inner")
            upstream_network.networkID = upstream_network.new_network
            upstream_network = upstream_network.drop(columns=["new_network"])

            print(
                f"Moving {len(upstream_network)} networks from {upstream_huc2} into {huc2}"
            )

            network = append(network, upstream_network)

        # network = network.set_index('networkID')

        s = network.groupby("networkID").size()
        ix = s[s > 1].index

        to_dissolve = network.loc[network.networkID.isin(ix)].copy()

        # remove these, dissolve, then add back
        network = network.loc[~network.networkID.isin(ix)].copy()

        to_dissolve = explode(to_dissolve)

        # Dissolve geometries by networkID
        dissolved_lines = (
            pd.Series(to_dissolve.geometry.values.data, index=to_dissolve.networkID)
            .groupby(level=0)
            .apply(pg.multilinestrings)
            .rename("geometry")
        )

        dissolved = stats.join(dissolved_lines, how="inner").reset_index()

        network = (
            network.append(dissolved)
            .sort_values(by="networkID")
            .reset_index(drop=True)
            .set_crs(CRS)
        )

    print("Serializing updated network...")
    huc2_dir = out_dir / huc2 / network_type
    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    network.to_feather(huc2_dir / "network.feather")
    write_dataframe(network, huc2_dir / "network.gpkg")
