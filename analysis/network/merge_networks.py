"""
Merge network analysis outputs across regions, and join back into the pre-processed barriers inventory datasets.
"""

from pathlib import Path
import os
import pandas as pd
import geopandas as gp

from nhdnet.io import (
    serialize_df,
    deserialize_gdf,
    deserialize_df,
    to_shp,
    serialize_gdf,
    deserialize_dfs,
    deserialize_gdfs,
)

from analysis.constants import REGION_GROUPS, CRS, NETWORK_TYPES, CONNECTED_REGIONS
from analysis.network.stats import calculate_network_stats

QA = False

data_dir = Path("data")

# out_dir = data_dir / "final_results"
# qa_dir = out_dir / "qa"


# if not os.path.exists(out_dir):
#     os.makedirs(out_dir)

# if QA and not os.path.exists(qa_dir):
#     os.makedirs(qa_dir)


# # FIXME:
# for network_type in NETWORK_TYPES[1:][:1]:
network_type = NETWORK_TYPES[1:][0]

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
# FIXME: raw folder
print("Reading network segments...")
network_df = deserialize_dfs(
    [
        data_dir / "networks" / region / network_type / "network_segments.feather"
        for region in CONNECTED_REGIONS
    ],
    src=[region for region in CONNECTED_REGIONS],
).set_index("networkID")


# Extract the joins that cross region boundaries, and set new upstream IDs for them
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
    .set_index("lineID")
    .networkID
)
cross_region = cross_region.join(
    downstream_networks.rename("downstream_network"), on="downstream_id"
)


### Reassign the upstream networks to the downstream networks
print("------------------- Reassigning networks -----------")
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
network_stats = calculate_network_stats(updated_network)

### Update network geometries
# Cut networks from upstream regions and paste them into downstream regions

cut_networks = None
for region in cross_region.from_region.unique():
    print("Cutting downstream network from upstream region...")

    network = deserialize_gdf(
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
    out_dir = data_dir / "networks" / region / network_type

    print("Serializing updated network...")
    serialize_gdf(network, out_dir / "network.feather", index=None)

    # FIXME: re-enable
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


# FIXME:
# for network_type in NETWORK_TYPES[1:][:1]:
# data_dir / "networks" / region / filename
# network_type / "network_segments.feather"
# )

# extract those that are connected to the networks in the upstream regions


cross_region = cross_region.join(
    df.set_index("lineID").networkID.rename("downstream_network"), on="downstream_id"
)

# Cut the connected networks from the upstream regions, and merge them into the dowstream regions
# print(
#     "Reading upstream region networks and cutting out networks joined to downstream regions..."
# )
# merged = None
# for region in upstream_regions:
#     print("------- {} -------".format(region))

#     df = deserialize_gdf(
#         data_dir / "networks" / region / network_type / "network.feather"
#     )

#     # select the affected networks
#     idx = df.networkID.isin(cross_region.upstream_network)
#     cut_networks = df.loc[idx].copy()

#     if merged is None:
#         merged = cut_networks

#     else:
#         merged = merged.append(cut_networks, ignore_index=True, sort=False)

#     # write the updated network back out
#     df = df.loc[~idx].copy()
#     out_dir = merged_dir / region / network_type

#     print("Serializing updated network...")
#     serialize_gdf(df, out_dir / "network.feather")
#     to_shp(df, out_dir / "network.shp")

# cut_networks = merged


# Merge the cut networks into the downstream region
print("Reading downstream region and merging in networks from upstream ")
for region in downstream_regions:
    print("------- {} -------".format(region))

    df = deserialize_gdf(
        data_dir / "networks" / region / network_type / "network.feather"
    )

    idx = df.loc[df.networkID.isin(cross_region.downstream_network)]

# # FIXME:
# for network_type in NETWORK_TYPES[1:][:1]:

#     print("Processing networks for {}".format(network_type))

#     kind = network_type[:-1]  # strip off trailing "s"

#     merged_network = None
#     merged_barrier_network = None
#     for region in regions:
#         print("------- {} -------".format(region))

#         # Barrier networks
#         df = deserialize_df(
#             data_dir / "networks" / region / network_type / "barriers_network.feather"
#         )

#         # Only keep the barrier type from this analysis
#         df = df.loc[df.kind == kind].copy()

#         if not len(df):
#             print("No {} in region {}".format(network_type, region))
#             continue

#         if merged_barrier_network is None:
#             merged_barrier_network = df

#         else:
#             merged_barrier_network = merged_barrier_network.append(df, ignore_index=True, sort=False)

# df = merged_barrier_network

# # update the barriers on the upstream side of the join
# idx = df.loc[df.]


# for network_type in NETWORK_TYPES[1:]:

#     print("Processing networks for {}".format(network_type))

#     kind = network_type[:-1]  # strip off trailing "s"

#     merged = None
#     for region in REGION_GROUPS:
#         print("------- {} -------".format(region))

#         df = deserialize_df(
#             data_dir / "networks" / region / network_type / "barriers_network.feather"
#         )

#         # Only keep the barrier type from this analysis
#         df = df.loc[df.kind == kind].copy()

#         if not len(df):
#             print("No {} in region {}".format(network_type, region))
#             continue

#         if merged is None:
#             merged = df
#         else:
#             merged = merged.append(df, ignore_index=True, sort=False)

#     results_df = merged.set_index("barrierID", drop=False)

#     results_df = results_df[
#         [
#             "upNetID",
#             "UpstreamMiles",
#             "NetworkSinuosity",
#             "NumSizeClassGained",
#             "PctNatFloodplain",
#             "downNetID",
#             "DownstreamMiles",
#             "AbsoluteGainMi",
#             "TotalNetworkMiles",
#         ]
#     ]

#     ### Read in pre-processed barriers
#     print("Reading pre-processed barriers")
#     # drop prioritization columns
#     # TODO: move this to prep_*.py step
#     barriers_df = (
#         deserialize_gdf(data_dir / "inputs" / "{}.feather".format(network_type))
#         .set_index("joinID")
#         .drop(
#             columns=[
#                 "x",
#                 "y",
#                 "xy",
#                 "NHDplus_Version",
#                 "PctNatFloodplain_Score",
#                 "PctNatFloodplain_Rank",
#                 "AbsoluteGainMi_Rank",
#                 "AbsoluteGainMi_Score",
#                 "NetworkSinuosity_Score",
#                 "NetworkSinuosity_Rank",
#                 "NumSizeClass_Score",
#                 "NumSizeClassesGained_Rank",
#                 "NumSizeClassGained_Rank",
#                 "NumSizeClassGained_Score",
#                 "WatershedCondition_CompositeScore",
#                 "WatershedCondition_tier",
#                 "ConnectivityPlusWatershedCondition_CompositeScore",
#                 "ConnectivityPlusWatershedCondition_tier",
#                 "Connectivity_CompositeScore",
#                 "Connectivity_tier",
#             ],
#             errors="ignore",
#         )
#         .rename(columns={"batDSNetId": "batDSNetID", "batUSNetId": "batUSNetID"})
#     )

#     # Set region 8 aside, since the network analysis is done separately
#     r8 = barriers_df.loc[barriers_df.HUC2 == "08"].copy()
#     r8["NHDplusVersion"] = "Medium"

#     # Drop region 8 and columns that come from network analysis
#     barriers_df = barriers_df.loc[barriers_df.HUC2 != "08"].drop(
#         columns=[c for c in results_df if c in barriers_df.columns]
#     )

#     ### Join network analysis results to barriers
#     print("Joining network analysis results to barriers")

#     results_df = barriers_df.join(results_df, how="left").reset_index()
#     results_df["NHDplusVersion"] = "High"

#     # Run some quick tests to make sure that nothing unexpected happened
#     # Have to check before merging in region 8 since those were not snapped in same way
#     snapped_no_network = results_df.loc[
#         results_df.snapped & results_df.AbsoluteGainMi.isnull()
#     ]
#     if len(snapped_no_network):
#         print(
#             "WARNING: {} barriers were snapped but did not get network assigned".format(
#                 len(snapped_no_network)
#             )
#         )
#         print(
#             "These are most likely at the upstream terminals of networks, but should double check"
#         )

#         if QA:
#             to_shp(
#                 snapped_no_network,
#                 qa_dir / "{}_snapped_no_network.shp".format(network_type),
#             )

#     # Join region 8 back in
#     results_df = results_df.append(
#         r8.reset_index(drop=False), sort=False, ignore_index=True
#     )

#     ### Temporary: Extract join info for networks that cross in to region 8
#     # TODO: remove this once region 8 is released
#     print("Updating network stats from region 8")
#     r8_joins = [
#         [514171383, 2219],  # 5 => 8
#         [714015373, 2219],  # 7 => 8
#         [1114058628, 2109],  # 11 => 8
#     ]

#     for downNetID, batNetID in r8_joins:
#         idx = results_df.downNetID == downNetID
#         r8idx = results_df.batDSNetID == batNetID

#         if r8idx.max():
#             # find the length of this network based on other barriers that already had this downstream ID
#             length = results_df.loc[r8idx].iloc[0].DownstreamMiles

#             # Add this to the lengths already present
#             results_df.loc[idx, "DownstreamMiles"] += length
#             results_df.loc[idx, "TotalNetworkMiles"] += length
#             results_df.loc[idx, "AbsoluteGainMi"] = results_df.loc[
#                 idx, ["UpstreamMiles", "DownstreamMiles"]
#             ].min(axis=1)

#     # TODO: simplify field names for downstream processing

#     results_df["HasNetwork"] = ~results_df.AbsoluteGainMi.isnull()

#     serialize_gdf(results_df, out_dir / "{}.feather".format(network_type), index=False)
#     results_df.drop(columns=["geometry"]).to_csv(out_dir / "dams.csv", index=False)

#     if QA:
#         print("Serializing barriers to shapefile")
#         to_shp(
#             results_df, qa_dir / "{}_network_analysis_results.shp".format(network_type)
#         )

