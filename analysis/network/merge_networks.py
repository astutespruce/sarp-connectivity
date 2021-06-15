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
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import NETWORK_TYPES, CRS
from analysis.lib.graph import DirectedGraph
from analysis.network.lib.stats import calculate_network_stats
from analysis.lib.io import read_feathers
from analysis.lib.util import append
from analysis.lib.geometry import explode

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


PERENNIAL_ONLY = False  # if true, will only build networks from perennial flowlines


data_dir = Path("data")
scenario_dir = "perennial" if PERENNIAL_ONLY else "all"
src_dir = data_dir / "networks" / scenario_dir
out_dir = src_dir / "merged"

if not out_dir.exists():
    os.makedirs(out_dir)


huc4_df = pd.read_feather(
    # data_dir / "boundaries/sarp_huc4.feather",
    data_dir / "boundaries/huc4.feather",
    columns=["HUC2", "HUC4"],
)
huc2s = huc4_df.HUC2.unique()


# VARY THIS between 0 and 2
network_type = NETWORK_TYPES[1]
print(f"Processing {network_type}")

start = time()


### Find joins between huc2s
# Note: since these are processed by network analysis, they already exclude loops
joins = read_feathers(
    [src_dir / huc2 / network_type / "flowline_joins.feather" for huc2 in huc2s],
    new_fields={"HUC2": huc2s},
)


### TEMP: limit to SARP HUC4s
# huc4s = huc4_df.HUC4.unique()
# joins = joins.loc[joins.HUC4.isin(huc4s)].copy()
### END TEMP


### Extract the joins that cross region boundaries, and set new upstream IDs for them
# We can join on the ids we generate (upstream_id, downstream_id) because there are no
# original flowlines split at HUC2 join areas
cross_region = joins.loc[(joins.type == "huc_in") & (joins.upstream_id == 0)]

cross_region = (
    cross_region.drop(columns=["upstream_id"])
    .rename(columns={"HUC2": "downstream_HUC2"})
    .join(
        joins.set_index("downstream")[["downstream_id", "HUC2"]].rename(
            columns={"downstream_id": "upstream_id", "HUC2": "upstream_HUC2"}
        ),
        on="upstream",
        how="inner",
    )
    .drop_duplicates()
)

# Sanity check
print(f"{len(cross_region):,} flowlines cross region boundaries")
print(cross_region[["upstream_HUC2", "downstream_HUC2"]])


connected_huc2 = np.unique(
    cross_region[["upstream_HUC2", "downstream_HUC2"]].values.flatten()
)
# drop any joins not in these HUC2s
joins = joins.loc[joins.HUC2.isin(connected_huc2)].copy()


### Read in network segments from upstream and downstream regions for regions that cross
print("\nReading network segments...")
network_df = read_feathers(
    [
        data_dir
        / "networks"
        / scenario_dir
        / huc2
        / network_type
        / "network_segments.feather"
        for huc2 in connected_huc2
    ],
).set_index("networkID")
network_df.lineID = network_df.lineID.astype("uint32")

### Lookup network ID for downstream segments of HUC2 join
# this finds the networkID that contains this lineID on its upper end
print("Aggregating networks that cross HUC2s...")
tmp = (
    network_df.loc[network_df.lineID.isin(cross_region.downstream_id.unique())]
    .reset_index()
    .set_index("lineID")
    .networkID.rename("downstream_network")
)
cross_region = cross_region.join(tmp, on="downstream_id")

# for all networks that start at the outlet of a HUC2, the upstream_id is the
# networkID of those networks.
cross_region["upstream_network"] = cross_region["upstream_id"]


### Traverse connected regions and determine final networkID
# build a directed graph from upstream to downstream; the last node of this
# is the furthest downstream and the new networkID to assign
g = DirectedGraph(cross_region, source="upstream_network", target="downstream_network")
ids = cross_region.upstream_network.unique()
new_network = pd.Series(
    g.terminal_descendants(ids), index=ids, name="new_network"
).apply(lambda g: list(g)[0])

cross_region = cross_region.join(new_network, on="upstream_network")


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
        data_dir
        / "networks"
        / scenario_dir
        / huc2
        / network_type
        / "barrier_joins.feather"
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
# updated_network = network_df.loc[cross_region.new_network.unique()]

# network stats facing upstream for each functional network
network_stats = calculate_network_stats(network_df, barrier_joins, joins)


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
            # "xmin",
            # "ymin",
            # "xmax",
            # "ymax",
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
            "num_downstream",
            "flows_to_ocean",
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
            "num_downstream",
            "flows_to_ocean",
        ]
    ]
    .groupby("downstream_network")
    .first()
)


### Update barrier networks with the new IDs and stats
for huc2 in connected_huc2:
    print(f"\nHUC2 {huc2}: updating barrier networks...")
    barrier_networks = pd.read_feather(
        data_dir
        / "networks"
        / scenario_dir
        / huc2
        / network_type
        / "barriers_network.feather"
    )

    if barrier_networks.upNetID.isin(upstream_stats.index).sum() > 0:
        # update any barriers that are at the root of updated networks
        barrier_networks = barrier_networks.join(
            upstream_stats, on="upNetID", rsuffix="_right"
        )
        ix = barrier_networks.new_network.notnull()
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
            columns=["new_network", "miles", "free_miles",]
            + [c for c in barrier_networks.columns if c.endswith("_right")]
        )

    if barrier_networks.downNetID.isin(downstream_stats_same_huc2.index).sum() > 0:
        # Update any records in this HUC2 that have updated networks DOWNSTREAM of them

        barrier_networks = barrier_networks.join(
            downstream_stats_same_huc2, on="downNetID", rsuffix="_right",
        )
        ix = barrier_networks.new_network.notnull()
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
        barrier_networks.loc[ix, "flows_to_ocean"] = barrier_networks.loc[
            ix
        ].flows_to_ocean_right.astype("bool")
        barrier_networks.loc[ix, "num_downstream"] = barrier_networks.loc[
            ix
        ].num_downstream_right.astype("uint16")

        barrier_networks = barrier_networks.drop(
            columns=["new_network", "miles", "free_miles",]
            + [c for c in barrier_networks.columns if c.endswith("_right")]
        )

    if barrier_networks.downNetID.isin(downstream_stats.index).sum() > 0:
        # update any records in UPSTREAM HUC2s that have updated networks DOWNSTREAM of them

        barrier_networks = barrier_networks.join(
            downstream_stats, on="downNetID", rsuffix="_right",
        )
        ix = barrier_networks.new_network.notnull()
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
        barrier_networks.loc[ix, "flows_to_ocean"] = barrier_networks.loc[
            ix
        ].flows_to_ocean_right.astype("bool")
        barrier_networks.loc[ix, "num_downstream"] = barrier_networks.loc[
            ix
        ].num_downstream_right.astype("uint16")

        barrier_networks = barrier_networks.drop(
            columns=["new_network", "miles", "free_miles",]
            + [c for c in barrier_networks.columns if c.endswith("_right")]
        )

    huc2_dir = out_dir / huc2 / network_type
    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    barrier_networks.reset_index(drop=False).to_feather(
        huc2_dir / "barriers_network.feather"
    )


### Update network geometries and barrier networks
# Move networks from upstream HUC2s to downstream HUC2s

# identify HUC2s that will aggregate upstream networks
aggregate_huc2 = (
    cross_region.groupby("new_HUC2").upstream_HUC2.unique().apply(list).to_dict()
)

cross_region[["new_HUC2", "upstream_HUC2"]].reset_index(drop=True).to_feather(
    out_dir / "connected_huc2.feather"
)


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
        "num_downstream",
        "flows_to_ocean",
    ]
].drop_duplicates()
stats.index.name = "networkID"

for huc2 in connected_huc2:
    print(f"\nHUC2 {huc2}: moving networks to base HUC2...")

    network = read_dataframe(
        data_dir / "networks" / scenario_dir / huc2 / network_type / "network.gpkg"
    )

    # first, remove any networks that are now "owned" by another HUC2
    ix = network.networkID.isin(cross_region.upstream_network)
    if ix.sum() > 0:
        print(f"Removing {ix.sum()} networks now owned by a downstream HUC2")
        network = network.loc[~ix].copy()

    # next, for every HUC2 that is at the root of the updated networks, pull in
    # networks upstream
    if huc2 in aggregate_huc2:
        for upstream_huc2 in aggregate_huc2[huc2]:
            upstream_network = read_dataframe(
                data_dir
                / "networks"
                / scenario_dir
                / upstream_huc2
                / network_type
                / "network.gpkg"
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

        s = network.groupby("networkID").size()
        ix = s[s > 1].index

        to_dissolve = network.loc[network.networkID.isin(ix)].copy()

        # TODO: this is empty; it should be bringing in some from upstream

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
            network.append(dissolved).sort_values(by="networkID").reset_index(drop=True)
        )

    print("Serializing updated network...")
    huc2_dir = out_dir / huc2 / network_type
    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    # make sure CRS is set properly
    network = network.set_crs(CRS, allow_override=True)

    # network.to_feather(huc2_dir / "network.feather")
    # Note: this must be a GPKG; FlatGeobuf fails for the larger networks
    # use GPKG as primary data store
    write_dataframe(network, huc2_dir / "network.gpkg")


### Move network segments from upstream HUC2s to downstream HUC2s
# Note: this doesn't move associated flowlines
for huc2 in connected_huc2:
    print(f"\nHUC2 {huc2}: moving network segments to base HUC2...")

    segments = pd.read_feather(
        data_dir
        / "networks"
        / scenario_dir
        / huc2
        / network_type
        / "network_segments.feather"
    )

    # first, remove any segments that are now "owned" by another HUC2
    ix = segments.networkID.isin(cross_region.upstream_network)
    if ix.sum() > 0:
        print(f"Removing {ix.sum()} network segments now owned by a downstream HUC2")
        segments = segments.loc[~ix].copy()

    # next, for every HUC2 that is at the root of the updated networks, pull in
    # network segments upstream
    if huc2 in aggregate_huc2:
        for upstream_huc2 in aggregate_huc2[huc2]:
            upstream_segments = pd.read_feather(
                data_dir
                / "networks"
                / scenario_dir
                / upstream_huc2
                / network_type
                / "network_segments.feather"
            )

            tmp = (
                cross_region.loc[cross_region.new_HUC2 == huc2]
                .set_index("upstream_network")
                .new_network
            )

            # join in new networkID
            upstream_segments = upstream_segments.join(tmp, on="networkID", how="inner")
            upstream_segments.networkID = upstream_segments.new_network
            upstream_segments = upstream_segments.drop(columns=["new_network"])

            print(
                f"Moving {len(upstream_segments)} network segments from {upstream_huc2} into {huc2}"
            )

            segments = append(segments, upstream_segments)

    print("Serializing updated network...")
    huc2_dir = out_dir / huc2 / network_type
    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    segments = segments.reset_index(drop=True)
    segments.to_feather(huc2_dir / "network_segments.feather")
