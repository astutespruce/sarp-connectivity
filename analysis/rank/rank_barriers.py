import os
from pathlib import Path
from time import time
import csv
import warnings

import pandas as pd
import geopandas as gp
import pygeos as pg
from pyogrio import write_dataframe

from analysis.rank.lib import read_networks
from analysis.rank.lib.metrics import update_network_metrics
from analysis.rank.lib.networks import get_network_results
from analysis.rank.lib.tiers import calculate_tiers
from analysis.rank.lib.spatial_joins import add_spatial_joins
from api.constants import DAM_API_FIELDS, UNIT_FIELDS, DAM_CORE_FIELDS


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
network_dir = Path("data/networks")
qa_dir = data_dir / "barriers/qa"
api_dir = data_dir / "api"
tile_dir = data_dir / "tiles"

if not os.path.exists(api_dir):
    os.makedirs(api_dir)

if not os.path.exists(tile_dir):
    os.makedirs(tile_dir)


### Read in master
print("Reading master...")
df = (
    gp.read_feather(barriers_dir / "dams.feather")
    .set_index("id")
    .drop(
        columns=[
            "level_0",
            "index",
            "dup_group",
            "dup_count",
            "dup_sort",
            "dup_log",
            "snap_dist",
            "snap_tolerance",
            "snap_ref_id",
            "snap_log",
            "snap_group",
            "snapped",
            "ProtectedLand",
            "NHDPlusID",
            "lineID",
            "wbID",
            "waterbody",
            "src",
            "kind",
            "log",
        ],
        errors="ignore",
    )
    .rename(
        columns={
            "StreamOrde": "StreamOrder",
            "excluded": "Excluded",
            "intermittent": "Intermittent",
        }
    )
)


### Save dams that were removed, for use in API (they are otherwise dropped below)
removed = df.loc[
    (df.Recon == 7) | (df.ManualReview == 8),
    [
        "geometry",
        "Name",
        "SARPID",
        "NIDID",
        "Source",
        "SourceDBID",
        "River",
        "Year",
        "Height",
        "Construction",
        "Purpose",
        "State",
        "County",
        "HUC8",
        "HUC12",
        "duplicate",
    ],
].to_crs(epsg=4326)
removed["lat"] = pg.get_y(removed.geometry.values.data).astype("float32")
removed["lon"] = pg.get_x(removed.geometry.values.data).astype("float32")
removed = removed.drop(columns=["geometry"])
removed.to_feather(api_dir / "removed_dams.feather")


### drop any that should be DROPPED (dropped or duplicate) from the analysis
# NOTE: excluded ones are retained but don't have networks; ones on loops are retained but also don't have networks
df = df.loc[~(df.dropped | df.duplicate)].copy()

### Join in T&E Spp stats
spp_df = (
    pd.read_feather(
        data_dir / "species/derived/spp_HUC12.feather",
        columns=["HUC12", "federal", "sgcn", "regional"],
    )
    .rename(
        columns={
            "federal": "TESpp",
            "sgcn": "StateSGCNSpp",
            "regional": "RegionalSGCNSpp",
        }
    )
    .set_index("HUC12")
)
df = df.join(spp_df, on="HUC12")
for col in ["TESpp", "StateSGCNSpp", "RegionalSGCNSpp"]:
    df[col] = df[col].fillna(0).astype("uint8")

### Add spatial joins to other units
df = add_spatial_joins(df)

### Add lat / lon
print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(epsg=4326)
geo["lat"] = pg.get_y(geo.geometry.values.data).astype("float32")
geo["lon"] = pg.get_x(geo.geometry.values.data).astype("float32")
df = df.join(geo[["lat", "lon"]])


### Get network results
networks = {
    "all": get_network_results(df, "dams", "all"),
    "perennial": get_network_results(df, "dams", "perennial").drop(
        columns=["FlowsToOcean", "NumBarriersDownstream"], errors="ignore"
    ),
}

# True if the barrier was snapped to a network and has network results in the
# all networks scenario
df["HasNetwork"] = df.index.isin(networks["all"].index)
# intermittent is not applicable if it doesn't have a network
df["Intermittent"] = df["Intermittent"].astype("int8")
df.loc[~df.HasNetwork, "Intermittent"] = -1


### Write out data for API
for network_scenario in ["all", "perennial"]:
    networks = networks[network_scenario]
    tmp = df.join(networks)
    for col in networks.columns:
        tmp[col] = tmp[col].fillna(-1).astype(networks[col].dtype)

    ### Sanity check
    if tmp.groupby(level=0).size().max() > 1:
        raise ValueError(
            "Error - there are duplicate barriers in the results.  Check uniqueness of IDs and joins."
        )

    # Full results for SARP QA/QC
    tmp.reset_index().to_feather(
        qa_dir / f"dams_{network_scenario}__network_results.feather"
    )


### Output results
print("Writing to output files...")


# drop geometry, not needed from here on out
df = df.drop(columns=["geometry"])

# save for API
df[DAM_API_FIELDS].reset_index().to_feather(api_dir / "dams.feather")


# # use smaller data types for smaller output files
# for col in ["miles", "free_miles", "sinuosity"]:
#     stats[col] = stats[col].round(5).astype("float32")

# # natural floodplain is missing for several catchments; fill with -1
# for col in ["natfldpln", "sizeclasses"]:
#     stats[col] = stats[col].fillna(-1).astype("int8")


# TODO: combine scenarios for exporting to tiles
