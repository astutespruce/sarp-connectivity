from pathlib import Path
from time import time
import warnings

import geopandas as gp
import pandas as pd

from analysis.lib.util import pack_bits, get_signed_dtype
from analysis.rank.lib.networks import get_network_results
from analysis.rank.lib.metrics import (
    classify_streamorder,
    classify_spps,
)
from api.constants import (
    GENERAL_API_FIELDS1,
    UNIT_FIELDS,
    DOMAINS,
    DAM_API_FIELDS,
    DAM_TILE_FIELDS,
    DAM_PACK_BITS,
    SB_API_FIELDS,
    SB_TILE_FIELDS,
    SB_PACK_BITS,
    WF_CORE_FIELDS,
    WF_TILE_FIELDS,
    WF_PACK_BITS,
    unique,
)

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
api_dir.mkdir(exist_ok=True, parents=True)
results_dir = data_dir / "barriers/networks"
results_dir.mkdir(exist_ok=True, parents=True)


removed_dam_cols = (
    GENERAL_API_FIELDS1
    + [
        "NIDID",
        "SourceDBID",
        "River",
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
    "excluded": "Excluded",
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
    df.loc[~df.snapped, "Intermittent"] = -1
    df["AnnualFlow"] = df.AnnualFlow.fillna(-1).astype("float32")
    df["AnnualVelocity"] = df.AnnualVelocity.fillna(-1).astype("float32")
    df["TotDASqKm"] = df.TotDASqKm.fillna(-1).astype("float32")


def verify_domains(df):
    failed = False
    for col in df.columns.intersection(DOMAINS.keys()):
        diff = set(df[col].unique()).difference(DOMAINS[col].keys())
        if diff:
            print(f"Missing values from domain lookup: {col}: {diff}")
            failed = True

    if failed:
        raise ValueError(
            "ERROR: stopping; one or more domain fields includes values not present in domain lookup"
        )


### Read dams and associated networks
print("Reading dams and networks")
dams = (
    gp.read_feather(barriers_dir / "dams.feather")
    .set_index("id")
    .rename(columns=rename_cols)
)
dams["BarrierType"] = "dam"
fill_flowline_cols(dams)

# add stream order and species classes for filtering
dams["StreamOrderClass"] = classify_streamorder(dams.StreamOrder)
for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    dams[f"{col}Class"] = classify_spps(dams[col])


# export removed dams for separate API endpoint
pd.DataFrame(dams.loc[dams.removed, removed_dam_cols].reset_index()).to_feather(
    api_dir / "removed_dams.feather"
)

# Drop all dropped / duplicate dams from API / tiles
# NOTE: excluded ones are retained but don't have networks; ones on loops are retained but also don't have networks
# NOTE: removed dams are retained for download per direction from Kat
dams = dams.loc[~(dams.dropped | dams.duplicate)].copy()

dam_networks = get_network_results(dams, "dams", state_ranks=True)

# TODO: limit to API + TILE fields
dams = dams.join(dam_networks)
for col in ["HasNetwork", "Ranked"]:
    dams[col] = dams[col].fillna(False)

# Pack bits for categorical fields not used for filtering
# IMPORTANT: this needs to happen here, before backfilling fields with -1
pack_cols = [e["field"] for e in DAM_PACK_BITS]
tmp = dams[pack_cols].copy()
# recode streamorder -1 to 0 for packing
tmp.loc[tmp.StreamOrder == -1, "StreamOrder"] = 0
dams["packed"] = pack_bits(tmp, DAM_PACK_BITS)

# fill other network columns and set to signed dtypes
for col in dam_networks.columns:
    if dams[col].dtype == bool:
        continue

    dams[col] = dams[col].fillna(-1).astype(get_signed_dtype(dam_networks[col].dtype))

dams = dams[unique(["geometry", "Unranked"] + DAM_API_FIELDS + DAM_TILE_FIELDS)]
verify_domains(dams)

print("Saving dams for tiles and API")
# Save full results for tiles, etc
dams.reset_index().to_feather(results_dir / "dams.feather")

# save for API
dams[DAM_API_FIELDS].reset_index().to_feather(api_dir / f"dams.feather")


### Read small barriers and associated networks
print("Reading small barriers and networks")
small_barriers = (
    gp.read_feather(barriers_dir / "small_barriers.feather")
    .set_index("id")
    .rename(columns=rename_cols)
)
small_barriers["BarrierType"] = "Inventoried road-related barrier"
small_barriers = small_barriers.loc[
    ~(small_barriers.dropped | small_barriers.duplicate)
].copy()
fill_flowline_cols(small_barriers)

# add stream order and species classes for filtering
small_barriers["StreamOrderClass"] = classify_streamorder(small_barriers.StreamOrder)
for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    small_barriers[f"{col}Class"] = classify_spps(small_barriers[col])


# NOTE: not calculating state ranks, per guidance from SARP
# (not enough barriers to have appropriate ranks)
small_barrier_networks = get_network_results(small_barriers, "small_barriers")
small_barriers = small_barriers.join(small_barrier_networks)
for col in ["HasNetwork", "Ranked"]:
    small_barriers[col] = small_barriers[col].fillna(False)

pack_cols = [e["field"] for e in SB_PACK_BITS]
tmp = small_barriers[pack_cols].copy()
tmp.loc[tmp.StreamOrder == -1, "StreamOrder"] = 0
small_barriers["packed"] = pack_bits(tmp, SB_PACK_BITS)

# set -1 when network not available for barrier
for col in small_barrier_networks.columns:
    if small_barriers[col].dtype == bool:
        continue

    small_barriers[col] = (
        small_barriers[col]
        .fillna(-1)
        .astype(get_signed_dtype(small_barrier_networks[col].dtype))
    )


small_barriers = small_barriers[
    unique(["geometry", "Unranked"] + SB_API_FIELDS + SB_TILE_FIELDS)
]
verify_domains(small_barriers)

print("Saving small barriers for tiles and API")
# Save full results for tiles, etc
small_barriers.reset_index().to_feather(results_dir / "small_barriers.feather")

# save for API
small_barriers[SB_API_FIELDS].reset_index().to_feather(
    api_dir / f"small_barriers.feather"
)


### Get combined networks
combined = pd.concat(
    [
        dams.drop(columns=dam_networks.columns, errors="ignore").reset_index(),
        small_barriers.drop(
            columns=small_barrier_networks.columns, errors="ignore"
        ).reset_index(),
    ],
    ignore_index=True,
    sort=False,
).set_index("id")

combined_networks = get_network_results(
    combined,
    network_type="small_barriers",
    state_ranks=True,
)
combined = combined.join(combined_networks)
for col in ["HasNetwork", "Ranked", "Estimated"]:
    combined[col] = combined[col].fillna(False)

for col in combined_networks.columns:
    if combined[col].dtype == bool:
        continue

    combined[col] = (
        combined[col].fillna(-1).astype(get_signed_dtype(combined_networks[col].dtype))
    )

# fill string columns
dt = combined.dtypes
str_columns = dt[dt == object].index
for col in str_columns:
    combined[col] = combined[col].fillna("")

# fill most domain columns with -1 (not applicable)
fill_columns = [
    # dam columns
    "Construction",
    "Diversion",
    "Feasibility",
    "FishScreen",
    "Height",
    "HeightClass",
    "Length",
    "LowheadDam",
    "PassageFacility",
    "PassageFacilityClass",
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
]

dtypes = pd.concat([dams.dtypes, small_barriers.dtypes])
for col in fill_columns:
    combined[col] = combined[col].fillna(-1).astype(get_signed_dtype(dtypes[col]))


verify_domains(combined)


print("Saving combined networks for tiles and API")
# Save full results for tiles, etc
combined.reset_index().to_feather(results_dir / "combined.feather")

# save for API
combined[unique(DAM_API_FIELDS + SB_API_FIELDS)].reset_index().to_feather(
    api_dir / f"combined.feather"
)


### Read waterfalls and associated networks
print("Reading waterfalls and networks")
waterfalls = (
    gp.read_feather(barriers_dir / "waterfalls.feather")
    .set_index("id")
    .rename(columns=rename_cols)
)
waterfalls = waterfalls.loc[~(waterfalls.dropped | waterfalls.duplicate)].copy()
fill_flowline_cols(waterfalls)

# add stream order and species classes for filtering
waterfalls["StreamOrderClass"] = classify_streamorder(waterfalls.StreamOrder)
for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    waterfalls[f"{col}Class"] = classify_spps(waterfalls[col])

# backfill Unranked for compatibility
waterfalls["Unranked"] = False

wf_dam_networks = get_network_results(
    waterfalls, network_type="dams", state_ranks=False
)
wf_dam_networks.columns = [f"{c}_dams" for c in wf_dam_networks.columns]
wf_dam_networks = wf_dam_networks.rename(
    columns={"HasNetwork_dams": "HasNetwork", "Ranked_dams": "Ranked"}
)

wf_sb_networks = get_network_results(
    waterfalls, network_type="small_barriers", state_ranks=False
).drop(columns=["HasNetwork", "Ranked"])
wf_sb_networks.columns = [f"{c}_small_barriers" for c in wf_sb_networks.columns]

waterfalls = waterfalls.join(wf_dam_networks).join(wf_sb_networks).copy()
for col in ["HasNetwork", "Ranked"]:
    waterfalls[col] = waterfalls[col].fillna(False)

pack_cols = [e["field"] for e in WF_PACK_BITS]
tmp = waterfalls[pack_cols].copy()
tmp.loc[tmp.StreamOrder == -1, "StreamOrder"] = 0
waterfalls["packed"] = pack_bits(tmp, WF_PACK_BITS)

network_cols = wf_dam_networks.columns.tolist() + wf_sb_networks.columns.tolist()
dtypes = pd.concat([wf_dam_networks.dtypes, wf_sb_networks.dtypes])
for col in network_cols:
    if waterfalls[col].dtype == bool:
        continue

    waterfalls[col] = waterfalls[col].fillna(-1).astype(get_signed_dtype(dtypes[col]))

waterfalls = waterfalls[
    unique(["geometry", "packed"] + unique(WF_CORE_FIELDS + WF_TILE_FIELDS))
]

print("Saving waterfalls for tiles")
waterfalls.reset_index().to_feather(results_dir / "waterfalls.feather")
