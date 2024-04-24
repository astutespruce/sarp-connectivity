from pathlib import Path
from time import time

import geopandas as gp
import pandas as pd

from analysis.constants import SEVERITY_TO_PASSABILITY
from analysis.lib.util import get_signed_dtype, append
from analysis.rank.lib.networks import get_network_results, get_removed_network_results
from analysis.rank.lib.metrics import classify_streamorder, classify_spps
from api.constants import (
    GENERAL_API_FIELDS1,
    UNIT_FIELDS,
    DAM_API_FIELDS,
    SB_API_FIELDS,
    COMBINED_API_FIELDS,
    WF_API_FIELDS,
    ROAD_CROSSING_API_FIELDS,
    verify_domains,
)
from analysis.constants import NETWORK_TYPES


start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
api_dir.mkdir(exist_ok=True, parents=True)
results_dir = data_dir / "barriers/networks"
results_dir.mkdir(exist_ok=True, parents=True)


# columns for removed dams API public endpoint
removed_dam_cols = (
    GENERAL_API_FIELDS1
    + [
        "NIDID",
        "YearCompleted",
        "YearRemoved",
        "Height",
        "Construction",
        "Purpose",
    ]
    + UNIT_FIELDS
    + ["duplicate"]
)

rename_cols = {
    "snapped": "Snapped",
    "excluded": "Excluded",
    "removed": "Removed",
    "intermittent": "Intermittent",
    "is_estimated": "Estimated",
    "invasive": "Invasive",
    "unranked": "Unranked",
    "loop": "OnLoop",
    "sizeclass": "StreamSizeClass",
}


def fill_flowline_cols(df):
    # Fill flowline columns with -1 when not available and set to appropriate dtype

    df["NHDPlusID"] = df.NHDPlusID.fillna(-1).astype("int64")
    df["Intermittent"] = df["Intermittent"].astype("int8")
    df.loc[~df.Snapped, "Intermittent"] = -1
    df["AnnualFlow"] = df.AnnualFlow.fillna(-1).astype("float32")
    df["AnnualVelocity"] = df.AnnualVelocity.fillna(-1).astype("float32")
    df["TotDASqKm"] = df.TotDASqKm.fillna(-1).astype("float32")


#######################################################################################
### Read dams and associated networks
print("Reading dams and networks")
dams = gp.read_feather(barriers_dir / "dams.feather").set_index("id").rename(columns=rename_cols)
dams["in_network_type"] = dams.primary_network

fill_flowline_cols(dams)

# add stream order and species classes for filtering
dams["StreamOrderClass"] = classify_streamorder(dams.StreamOrder)
for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    dams[f"{col}Class"] = classify_spps(dams[col])


# export removed dams for separate API endpoint
# NOTE: these don't have network stats for removed dams
pd.DataFrame(dams.loc[dams.Removed, removed_dam_cols].reset_index()).to_feather(api_dir / "removed_dams.feather")

# Drop all dropped / duplicate dams from API / tiles
# NOTE: excluded ones are retained but don't have networks; ones on loops are
# retained but also don't have networks
dams = dams.loc[~(dams.dropped | dams.duplicate)].copy()

nonremoved_dam_networks = get_network_results(dams.loc[~dams.Removed], "dams", state_ranks=True)

# cast so that this gets correctly split out as -1/0/1 values
nonremoved_dam_networks["InvasiveNetwork"] = nonremoved_dam_networks.InvasiveNetwork.fillna(-1).astype("int8")

# NOTE: removed dam networks do not have all fields present or set
removed_dam_networks = get_removed_network_results(dams.loc[dams.Removed], "dams")

dam_networks = pd.concat(
    [
        nonremoved_dam_networks.reset_index(),
        removed_dam_networks.reset_index(),
    ],
    ignore_index=True,
).set_index("id")

dams = dams.join(dam_networks)
for col in ["HasNetwork", "Ranked"]:
    dams[col] = dams[col].fillna(0).astype("bool")

# backfill missing values with 0 for classes and -1 for other network metrics
for col in nonremoved_dam_networks.columns:
    if dams[col].dtype == bool:
        continue

    orig_dtype = nonremoved_dam_networks[col].dtype
    if col.endswith("Class"):
        dams[col] = dams[col].fillna(0).astype(orig_dtype)
    else:
        dams[col] = dams[col].fillna(-1).astype(get_signed_dtype(orig_dtype))

# Convert bool fields to uint8; none of the fields used for filtering can be
# bool because fails on frontend
for col in ["CoastalHUC8"]:
    dams[col] = dams[col].astype("uint8")


print("Saving dams for tiles and API")
# Save full results for tiles, etc
dams.reset_index().to_feather(results_dir / "dams.feather")

# save for API
tmp = dams[DAM_API_FIELDS].reset_index()
verify_domains(tmp)
# downcast id to uint32 or it breaks in UI
tmp["id"] = tmp.id.astype("uint32")
tmp.to_feather(api_dir / "dams.feather")


#########################################################################################
###
### Read small barriers and associated networks
print("Reading small barriers and networks")
small_barriers = gp.read_feather(barriers_dir / "small_barriers.feather").set_index("id").rename(columns=rename_cols)
small_barriers["in_network_type"] = small_barriers.primary_network

small_barriers = small_barriers.loc[~(small_barriers.dropped | small_barriers.duplicate)].copy()
fill_flowline_cols(small_barriers)

# add stream order and species classes for filtering
small_barriers["StreamOrderClass"] = classify_streamorder(small_barriers.StreamOrder)
for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    small_barriers[f"{col}Class"] = classify_spps(small_barriers[col])


# NOTE: not calculating state ranks, per guidance from SARP
# (not enough barriers to have appropriate ranks)
nonremoved_small_barrier_networks = get_network_results(
    small_barriers.loc[~small_barriers.Removed], "combined_barriers"
)
# cast so that this gets correctly split out as -1/0/1 values
nonremoved_small_barrier_networks["InvasiveNetwork"] = nonremoved_small_barrier_networks.InvasiveNetwork.fillna(
    -1
).astype("int8")

removed_small_barrier_networks = get_removed_network_results(
    small_barriers.loc[small_barriers.Removed], "combined_barriers"
)

small_barrier_networks = pd.concat(
    [
        nonremoved_small_barrier_networks.reset_index(),
        removed_small_barrier_networks.reset_index(),
    ],
    ignore_index=True,
).set_index("id")


small_barriers = small_barriers.join(small_barrier_networks)
for col in ["HasNetwork", "Ranked"]:
    small_barriers[col] = small_barriers[col].fillna(0).astype("bool")

# backfill missing values with 0 for classes and -1 for other network metrics
for col in nonremoved_small_barrier_networks.columns:
    if small_barriers[col].dtype == bool:
        continue

    orig_dtype = nonremoved_small_barrier_networks[col].dtype
    if col.endswith("Class"):
        small_barriers[col] = small_barriers[col].fillna(0).astype(orig_dtype)

    else:
        small_barriers[col] = small_barriers[col].fillna(-1).astype(get_signed_dtype(orig_dtype))

for col in ["CoastalHUC8"]:
    small_barriers[col] = small_barriers[col].astype("uint8")

print("Saving small barriers for tiles and API")
# Save full results for tiles, etc
small_barriers.reset_index().to_feather(results_dir / "small_barriers.feather")

# save for API
tmp = small_barriers[SB_API_FIELDS].reset_index()
verify_domains(tmp)
tmp["id"] = tmp.id.astype("uint32")
tmp.to_feather(api_dir / "small_barriers.feather")

#########################################################################################
###
### Get combined networks
tier_columns = [c for c in dam_networks.columns if c.endswith("_tier")]
dams = dams.drop(columns=dam_networks.columns.tolist() + tier_columns, errors="ignore")
dams["BarrierType"] = "dams"

small_barriers = small_barriers.drop(
    columns=small_barrier_networks.columns.tolist() + tier_columns,
    errors="ignore",
)
small_barriers["BarrierType"] = "small_barriers"

# convert small barriers BarrierSeverity to Passability before merge
small_barriers["Passability"] = small_barriers.BarrierSeverity.map(SEVERITY_TO_PASSABILITY).astype("uint8")


combined = pd.concat(
    [
        dams.reset_index(),
        small_barriers.reset_index(),
    ],
    ignore_index=True,
    sort=False,
).set_index("id")

# fill string columns
dt = combined.dtypes
bool_columns = set(c for c in dams.columns if dams.dtypes[c] == "bool").union(
    set(c for c in small_barriers.columns if small_barriers.dtypes[c] == "bool")
)
for col in bool_columns:
    combined[col] = combined[col].fillna(0).astype("bool")

str_columns = [c for c in dt[dt == object].index if c not in bool_columns]
for col in str_columns:
    combined[col] = combined[col].fillna("")

# fill most domain columns with -1 (not applicable)
fill_columns = [
    # dam columns
    "FERCRegulated",
    "StateRegulated",
    "WaterRight",
    "Hazard",
    "Construction",
    "Diversion",
    "Feasibility",
    "FeasibilityClass",
    "FishScreen",
    "Height",
    "HeightClass",
    "YearCompletedClass",
    "Length",
    "LowheadDam",
    "Purpose",
    "ScreenType",
    "WaterbodyKM2",
    "WaterbodySizeClass",
    "Width",
    "YearCompleted",
    # small barrier columns
    "Constriction",
    "CrossingType",
    "RoadType",
    "SARP_Score",
    "BarrierSeverity",
]

dtypes = (
    pd.concat(
        [dams.dtypes.rename("type").reset_index(), small_barriers.dtypes.rename("type").reset_index()],
        ignore_index=True,
    )
    .drop_duplicates("index")
    .set_index("index")["type"]
)
for col in fill_columns:
    orig_dtype = dtypes[col]
    if col.endswith("Class"):
        combined[col] = combined[col].fillna(0).astype(orig_dtype)

    else:
        combined[col] = combined[col].fillna(-1).astype(get_signed_dtype(orig_dtype))

for col in ["CoastalHUC8"]:
    combined[col] = combined[col].astype("uint8")

for network_type in [
    "combined_barriers",
    "largefish_barriers",
    "smallfish_barriers",
]:
    nonremoved_networks = get_network_results(
        combined.loc[~combined.Removed],
        network_type=network_type,
        state_ranks=False,
    )
    # cast so that this gets correctly split out as -1/0/1 values
    nonremoved_networks["InvasiveNetwork"] = nonremoved_networks.InvasiveNetwork.fillna(-1).astype("int8")

    removed_networks = get_removed_network_results(
        combined.loc[combined.Removed],
        network_type=network_type,
    )
    networks = pd.concat(
        [
            nonremoved_networks.reset_index(),
            removed_networks.reset_index(),
        ],
        ignore_index=True,
    ).set_index("id")

    scenario_results = combined.join(networks)
    scenario_results["in_network_type"] = (
        scenario_results.primary_network
        if network_type == "combined_barriers"
        else scenario_results[f"{network_type.split('_')[0]}_network"]
    )

    for col in nonremoved_networks.columns:
        orig_dtype = nonremoved_networks[col].dtype

        if orig_dtype == bool or col.endswith("Class"):
            scenario_results[col] = scenario_results[col].fillna(0).astype(orig_dtype)

        else:
            scenario_results[col] = scenario_results[col].fillna(-1).astype(get_signed_dtype(orig_dtype))

    print(f"Saving {network_type} networks for tiles and API")
    # Save full results for tiles, etc
    scenario_results.reset_index().to_feather(results_dir / f"{network_type}.feather")

    # save for API
    tmp = scenario_results[COMBINED_API_FIELDS].reset_index()
    verify_domains(tmp)
    tmp["id"] = tmp.id.astype("uint32")

    if network_type == "combined_barriers":
        # create search key for search by name
        tmp["search_key"] = (tmp["Name"] + " " + tmp["River"]).str.strip().str.replace("  ", " ", regex=False)

    tmp.to_feather(api_dir / f"{network_type}.feather")

########################################################################################
##
## Read waterfalls and associated networks
# NOTE: this creates one record per network type in a single file

print("Reading waterfalls and networks")
waterfalls = gp.read_feather(barriers_dir / "waterfalls.feather").set_index("id").rename(columns=rename_cols)
waterfalls = waterfalls.loc[~(waterfalls.dropped | waterfalls.duplicate)].copy()
fill_flowline_cols(waterfalls)

# backfill Unranked for compatibility (this is needed when getting networks)
waterfalls["Unranked"] = False

merged = None
for network_type in NETWORK_TYPES.keys():
    networks = get_network_results(waterfalls, network_type=network_type, state_ranks=False)

    # cast so that this gets correctly split out as -1/0/1 values
    networks["InvasiveNetwork"] = networks.InvasiveNetwork.astype("int8")

    scenario_results = waterfalls.join(networks)
    for col in networks.columns:
        orig_dtype = networks[col].dtype

        if orig_dtype == bool or col.endswith("Class"):
            scenario_results[col] = scenario_results[col].fillna(0).astype(orig_dtype)

        else:
            scenario_results[col] = scenario_results[col].fillna(-1).astype(get_signed_dtype(orig_dtype))

    # copy to defragment DataFrame
    scenario_results = scenario_results.copy()

    scenario_results["network_type"] = network_type
    scenario_results["in_network_type"] = (
        scenario_results[f"{network_type.split('_')[0]}_network"]
        if network_type in {"largefish_barriers", "smallfish_barriers"}
        else scenario_results.primary_network
    )

    merged = append(merged, scenario_results.reset_index()).copy()

waterfalls = merged

print("Saving waterfalls networks for tiles and API")

waterfalls.to_feather(results_dir / "waterfalls.feather")

tmp = waterfalls[["id"] + WF_API_FIELDS].copy()
verify_domains(tmp)
tmp["id"] = tmp.id.astype("uint32")

tmp.to_feather(api_dir / "waterfalls.feather")


#########################################################################################
###
### Read road crossings and create files for API / tiles
# NOTE: these don't currently have network data, but share logic with above
print("Processing road crossings")
crossings = gp.read_feather(barriers_dir / "road_crossings.feather").set_index("id").rename(columns=rename_cols)
fill_flowline_cols(crossings)

# cast intermittent to int to match other types
crossings["StreamOrderClass"] = classify_streamorder(crossings.StreamOrder)
for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    crossings[f"{col}Class"] = classify_spps(crossings[col])

print("Saving crossings for tiles and API")
# Save full results for tiles, etc
crossings[ROAD_CROSSING_API_FIELDS + ["offnetwork_flowline", "geometry"]].reset_index().to_feather(
    results_dir / "road_crossings.feather"
)

tmp = crossings[ROAD_CROSSING_API_FIELDS].reset_index()
verify_domains(tmp)

# downcast id to uint32 or it breaks in UI
tmp["id"] = tmp.id.astype("uint32")
tmp.to_feather(api_dir / "road_crossings.feather")
