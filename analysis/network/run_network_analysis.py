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
import warnings

import geopandas as gp
import pygeos as pg
import pandas as pd
import numpy as np
from pyogrio import write_dataframe


from analysis.constants import NETWORK_TYPES

from analysis.network.lib.stats import calculate_network_stats
from analysis.network.lib.barriers import read_barriers, save_barriers
from analysis.lib.flowlines import cut_flowlines_at_barriers, save_cut_flowlines
from analysis.network.lib.networks import create_networks

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
nhd_dir = data_dir / "nhd/clean"


# TODO: expand to full region
huc4_df = pd.read_feather(
    data_dir / "boundaries/sarp_huc4.feather", columns=["HUC2", "HUC4"]
)
# Convert to dict of sorted HUC4s per HUC2
units = huc4_df.groupby("HUC2").HUC4.unique().apply(sorted).to_dict()

# manually subset keys from above for processing
huc2s = [
    "02",
    # "03", "05", "06", "07", "08", "10", "11", "12", "13", "21"
]


start = time()

for huc2, network_type in product(huc2s, NETWORK_TYPES[1:2]):
    region_start = time()

    print(f"----- {huc2} ({network_type}) ------")

    out_dir = data_dir / "networks" / huc2 / network_type

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    ##################### Read Barrier data #################
    barriers = read_barriers(huc2, network_type)
    save_barriers(out_dir, barriers)

    ##################### Cut flowlines at barriers #################
    print("------------------- Cutting Flowlines -----------")
    ### Read NHD flowlines and joins
    print("Reading flowlines...")
    flowline_start = time()
    flowlines = (
        gp.read_feather(nhd_dir / huc2 / "flowlines.feather")
        .set_index("lineID", drop=False)
        .drop(columns=["HUC2"], errors="ignore")
    )
    joins = pd.read_feather(nhd_dir / huc2 / "flowline_joins.feather")

    ### TEMP: limit flowlines and joins to HUC4s in SARP region above
    flowlines = flowlines.loc[flowlines.huc4.isin(units[huc2])].copy()
    joins = joins.loc[joins.huc4.isin(units[huc2])].copy()

    # limit barriers to these flowlines
    barriers = barriers.loc[barriers.lineID.isin(flowlines.index)].copy()

    ### END TEMP

    # drop all loops from the analysis
    ix = flowlines.loop == True
    print("Found {:,} loops, dropping...".format(ix.sum()))
    flowlines = flowlines.loc[~ix].copy()
    joins = joins.loc[~joins.loop].copy()
    flowlines = flowlines.drop(columns=["loop"])
    joins = joins.drop(columns=["loop"])

    print(f"Read {len(flowlines):,} flowlines in {time() - flowline_start:.2f}s")

    # since all other lineIDs use HUC4 prefixes, this should be unique
    # Use the first HUC2 for the region group
    next_segment_id = int(huc2) * 1000000 + 1

    flowlines, joins, barrier_joins = cut_flowlines_at_barriers(
        flowlines, joins, barriers, next_segment_id=next_segment_id
    )

    barrier_joins = barrier_joins.join(barriers.kind)

    save_cut_flowlines(out_dir, flowlines, joins, barrier_joins)

    ##################### Create networks #################
    # IMPORTANT: the following analysis allows for multiple upstream networks from an origin or barrier
    # this happens when the barrier is perfectly snapped to the junction of >= 2 upstream networks.
    # When this is encountered, these networks are merged together and assigned the ID of the first segment
    # of the first upstream network.

    print("------------------- Creating networks -----------")
    network_start = time()

    network_df = create_networks(flowlines, joins, barrier_joins)

    # For any barriers that had multiple upstreams, those were coalesced to a single network above
    # So drop any dangling upstream references (those that are not in networks and non-zero)
    # NOTE: these are not persisted because we want the original barrier_joins to reflect multiple upstreams
    barrier_joins = barrier_joins.loc[
        barrier_joins.upstream_id.isin(network_df.index)
        | (barrier_joins.upstream_id == 0)
    ].copy()

    print(
        f"{len(network_df.index.unique()):,} networks created in {time() - network_start:.2f}s"
    )

    print("Serializing network segments")
    pd.DataFrame(network_df.drop(columns=["geometry"])).reset_index().to_feather(
        out_dir / "network_segments.feather"
    )

    ##################### Network stats #################
    print("------------------- Calculating network stats -----------")

    stats_start = time()

    network_stats = calculate_network_stats(network_df, barrier_joins)
    # WARNING: because not all flowlines have associated catchments, they are missing
    # natfldpln

    print(f"done calculating network stats in {time() - stats_start:.2f}")

    network_stats.reset_index().to_feather(out_dir / "network_stats.feather")

    #### Calculate up and downstream network attributes for barriers

    print("calculating upstream and downstream networks for barriers")

    upstream_networks = (
        barrier_joins[["upstream_id"]]
        .join(network_stats, on="upstream_id")
        .rename(
            columns={
                "upstream_id": "upNetID",
                "miles": "TotalUpstreamMiles",
                "free_miles": "FreeUpstreamMiles",
            }
        )
    )

    downstream_networks = (
        barrier_joins[["downstream_id"]]
        .join(
            network_df.reset_index().set_index("lineID").networkID, on="downstream_id"
        )
        .join(
            network_stats[["free_miles", "miles"]].rename(
                columns={
                    "free_miles": "FreeDownstreamMiles",
                    "miles": "TotalDownstreamMiles",
                }
            ),
            on="networkID",
        )
        .rename(columns={"networkID": "downNetID"})
        .drop(columns=["downstream_id"])
    )

    # Note: the join creates duplicates if there are multiple upstream or downstream
    # networks for a given barrier, so we drop these duplicates after the join just to be sure.
    barrier_networks = (
        upstream_networks.join(downstream_networks)
        .join(barriers[["id", "kind"]])
        .drop(columns=["barrier", "up_ndams", "up_nwfs", "up_sbs"], errors="ignore")
        .fillna(0)
        .drop_duplicates()
    )

    # Fix data types after all the joins
    for col in ["upNetID", "downNetID", "segments"]:
        barrier_networks[col] = barrier_networks[col].astype("uint32")

    for col in [
        "TotalUpstreamMiles",
        "FreeUpstreamMiles",
        "TotalDownstreamMiles",
        "FreeDownstreamMiles",
        "sinuosity",
        "natfldpln",
    ]:
        barrier_networks[col] = barrier_networks[col].astype("float32")

    barrier_networks.sizeclasses = barrier_networks.sizeclasses.astype("uint8")

    barrier_networks.reset_index().to_feather(out_dir / "barriers_network.feather")

    # TODO: if downstream network extends off this HUC, it will be null in the above and AbsoluteGainMin will be wrong

    ##################### Dissolve networks on networkID ########################
    print("Dissolving networks")
    dissolve_start = time()

    dissolved_lines = (
        pd.Series(network_df.geometry.values.data, index=network_df.index)
        .groupby(level=0)
        .apply(pg.multilinestrings)
    )

    networks = (
        gp.GeoDataFrame(network_stats.join(dissolved_lines), crs=flowlines.crs)
        .reset_index()
        .sort_values(by="networkID")
    )

    print(f"Network dissolve done in {time() - dissolve_start:.2f}")

    print("Serializing network")
    networks = networks.reset_index(drop=True)
    networks.to_feather(out_dir / "network.feather")
    write_dataframe(networks, out_dir / "network.gpkg")

    print(f"Region done in {time() - region_start:.2f}s")

print("All done in {:.2f}s".format(time() - start))
