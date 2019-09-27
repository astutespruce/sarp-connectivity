"""TODO: migrate into prep_dams.py
"""

from pathlib import Path
from time import time
import pandas as pd
import geopandas as gp
import numpy as np

from nhdnet.io import (
    serialize_gdf,
    deserialize_gdf,
    deserialize_sindex,
    deserialize_df,
    to_shp,
)

from analysis.constants import CRS


data_dir = Path("data")
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "src"
dams_filename = "Raw_Featureservice_SARPUniqueID.gdb"
gdb = src_dir / dams_filename


# dams that were manually snapped
snapped_layer = "Snapped_Dataset_for_Edits_09032019"
# dams that fall outside SARP
outside_layer = "Dams_Non_SARP_States_09052019"
# layer for each SARP state
sarp_state_layer = "Dams_{state}"


# Each SARP state will have a layer in the geodatabase below
sarp_states = [
    "AL",
    "AR",
    "FL",
    "GA",
    "KY",
    "LA",
    "MO",
    "MS",
    "NC",
    "OK",
    "PR",  # not currently present but will be coming in late 2019
    "SC",
    "TN",
    "TX",
    "VA",
]


keep_cols = [
    "geometry",
    "SARPUniqueID",
    "AnalysisID",
    "Snap2018",
    "NIDID",
    "SourceDBID",
    "Barrier_Name",
    "Other_Barrier_Name",
    "River",
    "PurposeCategory",
    "Year_Completed",
    "Height",
    "StructureCondition",
    "ConstructionMaterial",
    "ProtectedLand",
    "DB_Source",
    "Off_Network",
    "Mussel_Presence",
    "NumberRareSpeciesHUC12",
    "StreamOrder",
    "Recon",
    "PotentialFeasibility",
    # TODO - network metrics only retained for region 8 barriers
    "AbsoluteGainMi",
    "UpstreamMiles",
    "DownstreamMiles",
    "TotalNetworkMiles",
    "PctNatFloodplain",
    "NetworkSinuosity",
    "NumSizeClassGained",
    "batUSNetID",
    "batDSNetID",
]

### Read in SARP states and merge
merged = None
for state in sarp_states:
    print("Reading dams in {}...".format(state))
    try:
        df = gp.read_file(gdb, layer=sarp_state_layer.format(state=state))
    except:
        print("WARNING: Layer not found for {}".format(state))
        continue

    # drop columns we don't need
    # some states have specific columns
    df = df[df.columns[df.columns.isin(keep_cols)]]

    if merged is None:
        merged = df
    else:
        merged = merged.append(df, ignore_index=True, sort=False)

# Drop dams without locations
merged = merged.loc[merged.geometry.notnull()].copy()


### Read in non-SARP states
# these are for states that overlap with HUC4s that overlap with SARP states
print(
    "Reading dams that fall outside SARP states, but within HUC4s that overlap with SARP states..."
)
outside_df = gp.read_file(gdb, layer=outside_layer)[keep_cols].to_crs(CRS)

# Join to outside states and project to standard projection
print("Merging and projecting data...")
df = merged.to_crs(CRS).append(outside_df, ignore_index=True, sort=False)


### Read in dams that have been manually snapped.
# Join on AnalysisID to merged data above.
# ONLY keep Snap2018 and the location.
print("Reading manually snapped dams...")
snapped_df = gp.read_file(gdb, layer=snapped_layer)[
    ["geometry", "AnalysisID", "SNAP2018", "Editor"]
].set_index("AnalysisID")
snapped_df = snapped_df.loc[snapped_df.geometry.notnull()].to_crs(CRS)

# Join to snapped and bring across updated geometry and SNAP2018
df = df.set_index("AnalysisID").join(snapped_df, rsuffix="_snap").reset_index()
idx = df.loc[df.geometry_snap.notnull()].index
df.loc[idx, "geometry"] = df.loc[idx].geometry_snap
df = df.drop(columns=["geometry_snap"]).reset_index()

