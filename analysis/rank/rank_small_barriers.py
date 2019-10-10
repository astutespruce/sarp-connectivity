"""
Preprocess small barriers into data needed by API and tippecanoe for creating vector tiles.

This is run AFTER `preprocess_road_crossings.py`.

Inputs:
* Small barriers inventory from SARP, processed through the network analysis
* `road_crossings.feather` created using `preprocess_road_crossings.py`

Outputs:
* `small_barriers.feather`: processed small barriers data for use by the API
* `small_barriers_with_networks.csv`: small barriers with networks for creating vector tiles in tippecanoe
* `dams_without_networks.csv`: small barriers without networks for creating vector tiles in tippecanoe

"""


from pathlib import Path
from time import time
import csv
import sys
import geopandas as gp
import pandas as pd
from geofeather import from_geofeather, to_shp, to_geofeather
from nhdnet.io import deserialize_dfs, deserialize_df, serialize_df
from nhdnet.geometry.points import add_lat_lon


from analysis.constants import REGION_GROUPS
from analysis.network.lib.barriers import DAMS_ID
from analysis.rank.lib import (
    add_spatial_joins,
    update_network_metrics,
    calculate_tiers,
    to_tippecanoe,
)
from analysis.rank.lib.output import BARRIER_FIELDS, SB_FIELDS

start = time()

data_dir = Path("data")
barriers_dir = data_dir / "barriers/master"
out_dir = data_dir / "derived"


### Read in master
print("Reading master...")
df = (
    from_geofeather(barriers_dir / "small_barriers.feather")
    .set_index("id")
    .drop(
        columns=[
            "level_0",
            "index",
            "dup_group",
            "dup_count",
            "snap_dist",
            "snapped",
            "ProtectedLand",
        ],
        errors="ignore",
    )
)

# drop any that should be DROPPED (dropped or duplicate) from the analysis
# NOTE: excluded ones are retained but don't have networks
df = df.loc[~(df.dropped | df.duplicate)].copy()


### Read in network outputs and join to master
print("Reading network outputs")
networks = (
    deserialize_dfs(
        [
            data_dir / "networks" / region / "small_barriers/barriers_network.feather"
            for region in REGION_GROUPS
        ],
        src=[region for region in REGION_GROUPS],
    )
    .drop(columns=["index", "segments"], errors="ignore")
    .rename(
        columns={
            "sinuosity": "Sinuosity",
            "natfldpln": "Landcover",
            "sizeclasses": "SizeClasses",
        }
    )
)

# Select out only dams because we are joining on "id"
# which may have duplicates across barrier types
networks = networks.loc[networks.kind == "small_barrier"].copy()

# All barriers that came out of network analysis have networks
networks["HasNetwork"] = True

### Join in networks and fill N/A
df = df.join(networks.set_index("id"))
df.HasNetwork = df.HasNetwork.fillna(False)


print(
    "Read {:,} small barriers ({:,} have networks)".format(
        len(df), len(df.loc[df.HasNetwork])
    )
)

### Join in T&E Spp stats
spp_df = deserialize_df(data_dir / "species/derived/spp_HUC12.feather").set_index(
    "HUC12"
)
df = df.join(spp_df.NumTEspp.rename("TESpp"), on="HUC12")
df.TESpp = df.TESpp.fillna(0).astype("uint8")


### Update network metrics and calculate classes
df = update_network_metrics(df)


### Add spatial joins to other units
df = add_spatial_joins(df)


### Add lat / lon
print("Adding lat / lon fields")
df = add_lat_lon(df)

### Calculate tiers for the region and by state
df = calculate_tiers(df)

### Output results
print("Writing to output files...")


# Full results for SARP
print("Saving full results to feather")
to_geofeather(df.reset_index(), out_dir / "small_barriers_full.feather")

# drop geometry, not needed from here on out
df = df.drop(columns=["geometry"])

print("Saving full results to CSV")
df.to_csv(out_dir / "small_barriers.csv", index_label="id")


# Drop associated raw scores, they are not currently displayed on frontend.
df = df.drop(columns=[c for c in df.columns if c.endswith("_score")])

# save for API
serialize_df(df.reset_index(), out_dir / "small_barriers.feather")

### Export data for use in tippecanoe to generate vector tiles
to_tippecanoe(df, "small_barriers")


# FIXME: in progress
### Combine barriers that don't have networks with road / stream crossings
print("Reading stream crossings")
road_crossings = deserialize_df(out_dir / "road_crossings.feather")
# bring in TESpp
road_crossings = road_crossings.join(spp_df.NumTEspp.rename("TESpp"), on="HUC12")
road_crossings.TESpp = road_crossings.TESpp.fillna(0).astype("uint8")
road_crossings.name = road_crossings.name.fillna("")

keep_cols = BARRIER_FIELDS + SB_FIELDS + ["CountyName", "Basin"]

combined = df.loc[~df.HasNetwork, keep_cols].append(
    road_crossings, ignore_index=True, sort=False
)

print("Now have {:,} combined background barriers".format(len(combined)))

# create a new consolidated ID
combined["id"] = combined.index.values.astype("uint32")
# TODO: is this still in output?
# combined.protectedland = combined.protectedland.fillna(0)


# Duplicate latitude / longitude columns in again
combined["latitude"] = combined.lat
combined["longitude"] = combined.lon

print("Writing combined file")
combined.to_csv(
    "data/derived/barriers_background.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
)


print("Done in {:.2f}".format(time() - start))


# from pathlib import Path
# import sys
# import csv
# from time import time
# import pandas as pd
# import geopandas as gp

# from nhdnet.io import deserialize_gdf, deserialize_df

# from api.calculate_tiers import calculate_tiers, SCENARIOS
# from api.domains import (
#     BARRIER_CONDITION_TO_DOMAIN,
#     POTENTIAL_TO_SEVERITY,
#     ROAD_TYPE_TO_DOMAIN,
#     CROSSING_TYPE_TO_DOMAIN,
# )

# from classify import (
#     classify_gainmiles,
#     classify_sinuosity,
#     classify_landcover,
#     classify_rarespp,
#     classify_streamorder,
# )


# src_dir = Path("../data/sarp/derived/final_results")

# data_dir = Path("data")
# boundaries_dir = data_dir / "boundaries"
# out_dir = data_dir / "derived"

# start = time()

# print("Reading small barriers")
# df = deserialize_gdf(src_dir / "small_barriers.feather").drop(columns=["TownId"])

# print(
#     "Read {} small_barriers, {} have networks".format(
#         len(df), len(df.loc[df.HasNetwork])
#     )
# )

# # Per instructions from SARP, exclude all Potential_Project=='SRI Only'
# # from previous iterations we also dropped Potential_Project=="No Upstream Channel"
# # and noted that we should exclude it from analysis
# # TODO: move to preprocessing step?
# df = df.loc[
#     ~df.Potential_Project.isin(
#         ("SRI Only", "No Upstream Channel", "No Upstream Habitat")
#     )
# ].copy()

# # Assign an ID.  Note: this is ONLY valid for this exact version of the inventory
# df["id"] = df.joinID


# ### Spatial joins to boundary layers
# df.sindex

# print("Joining to counties")
# counties = deserialize_gdf(boundaries_dir / "counties.feather")[
#     ["geometry", "County", "COUNTYFIPS"]
# ]
# counties.sindex
# df = gp.sjoin(df, counties, how="left").drop(columns=["index_right"])


# print("Joining to ecoregions")
# # Only need to join in ECO4 dataset since it has both ECO3 and ECO4 codes
# eco4 = deserialize_gdf(boundaries_dir / "eco4.feather")[["geometry", "ECO3", "ECO4"]]
# eco4.sindex
# df = gp.sjoin(df, eco4, how="left").drop(columns=["index_right"])


# # Obviated by upstream changes
# ### Project to WGS84
# # print("Projecting to WGS84 and adding lat / lon fields")
# # df = df.to_crs(epsg=4326)
# # df["lon"] = df.geometry.x.astype("float32")
# # df["lat"] = df.geometry.y.astype("float32")

# # drop geometry, no longer needed
# df = df.drop(columns=["geometry"])


# # Rename columns to make them easier to handle
# # also rename fields to match dams for consistency
# df.rename(
#     columns={
#         "STATE": "State",
#         "OnConservationLand": "ProtectedLand",
#         "NumberRareSpeciesHUC12": "RareSpp",
#         # Note re: SARPID - this isn't quite correct but needed for consistency
#         "AnalysisID": "SARPID",
#         "AbsoluteGainMi": "GainMiles",
#         "PctNatFloodplain": "Landcover",
#         "NetworkSinuosity": "Sinuosity",
#         "NumSizeClassesGained": "SizeClasses",
#         "CrossingTypeId": "CrossingType",
#         "RoadTypeId": "RoadType",
#         "CrossingConditionId": "Condition",
#         "StreamName": "Stream",
#     },
#     inplace=True,
# )


# ######### Fix data issues

# # Fix mixed casing of values
# for column in ("CrossingType", "RoadType", "Stream", "Road"):
#     df[column] = df[column].fillna("Unknown").str.title().str.strip()
#     df.loc[df[column].str.len() == 0, column] = "Unknown"

# # Fix line returns in stream name and road name
# df.loc[df.SARPID == "sm7044", "Stream"] = "Unnamed"
# df.Road = df.Road.str.replace("\r\n", "")

# # Fix issues with RoadType
# df.loc[df.RoadType.isin(("No Data", "NoData", "Nodata")), "RoadType"] = "Unknown"

# # Fix issues with Condition
# df.Condition = df.Condition.fillna("Unknown")
# df.loc[
#     (df.Condition == "No Data")
#     | (df.Condition == "No data")
#     | (df.Condition.str.strip().str.len() == 0),
#     "Condition",
# ] = "Unknown"

# #########  Fill NaN fields and set data types

# for column in ("CrossingCode", "LocalID", "Source"):
#     df[column] = df[column].fillna("").str.strip()

# # for column in ("RareSpp", "ProtectedLand"):
# #     df[column] = df[column].fillna(0).astype("uint8")

# # # Fill metrics with -1
# # for column in ("Landcover", "SizeClasses"):  # null but with network should be 0
# #     df[column] = df[column].fillna(-1).astype("int8")

# # Round floating point columns to 3 decimals
# # for column in (
# #     "Sinuosity",
# #     "GainMiles",
# #     "UpstreamMiles",
# #     "DownstreamMiles",
# #     "TotalNetworkMiles",
# # ):
# #     df[column] = df[column].round(3).fillna(-1).astype("float32")


# ######## Calculate derived fields
# print("Calculating derived values")

# # Construct a name from Stream and Road
# df["Name"] = ""  # "Unknown Crossing"
# df.loc[(df.Stream != "Unknown") & (df.Road != "Unknown"), "Name"] = (
#     df.Stream + " / " + df.Road + " Crossing"
# )

# # Calculate HUC and Ecoregion codes
# #

# # # Read in HUC6 and join in basin name
# # huc6 = (
# #     deserialize_gdf(boundaries_dir / "HUC6.feather")[["HUC6", "NAME"]]
# #     .rename(columns={"NAME": "Basin"})
# #     .set_index("HUC6")
# # )
# # df = df.join(huc6, on="HUC6")

# # Calculate classes
# df["ConditionClass"] = df.Condition.map(BARRIER_CONDITION_TO_DOMAIN)
# df["SeverityClass"] = df.PotentialProject.map(POTENTIAL_TO_SEVERITY)
# df["CrossingTypeClass"] = df.CrossingType.map(CROSSING_TYPE_TO_DOMAIN)
# df["RoadTypeClass"] = df.RoadType.map(ROAD_TYPE_TO_DOMAIN)


# # # Bin metrics
# # df["GainMilesClass"] = classify_gainmiles(df.GainMiles)
# # df["SinuosityClass"] = classify_sinuosity(df.Sinuosity)
# # df["LandcoverClass"] = classify_landcover(df.Landcover)
# # df["RareSppClass"] = classify_rarespp(df.RareSpp)


# ########## Drop unnecessary columns
# df = df[
#     [
#         "id",
#         "lat",
#         "lon",
#         # ID and source info
#         "SARPID",
#         "CrossingCode",
#         "LocalID",
#         "Source",
#         # Basic info
#         "Name",
#         "County",
#         "State",
#         "Basin",
#         # Species info
#         "RareSpp",
#         # Stream info
#         "Stream",
#         # Road info
#         "Road",
#         "RoadType",
#         # Location info
#         "ProtectedLand",
#         # "HUC2",
#         "HUC6",
#         "HUC8",
#         "HUC12",
#         "ECO3",
#         "ECO4",
#         # Barrier info
#         "CrossingType",
#         "Condition",
#         "PotentialProject",
#         # Metrics
#         "GainMiles",
#         "UpstreamMiles",
#         "DownstreamMiles",
#         "TotalNetworkMiles",
#         "Landcover",
#         "Sinuosity",
#         "SizeClasses",
#         # Internal fields
#         "COUNTYFIPS",
#         "STATEFIPS",
#         "HasNetwork",
#         "RareSppClass",
#         "GainMilesClass",
#         "SinuosityClass",
#         "LandcoverClass",
#         "ConditionClass",
#         "SeverityClass",
#         "CrossingTypeClass",
#         "RoadTypeClass",
#     ]
# ].set_index("id", drop=False)


# # Calculate tiers and scores for the region (None) and State levels
# for group_field in (None, "State"):
#     print("Calculating tiers for {}".format(group_field or "Region"))

#     # Note: some states do not yet have enough inventoried barriers for percentiles to work

#     tiers_df = calculate_tiers(
#         df.loc[df.HasNetwork],
#         SCENARIOS,
#         group_field=group_field,
#         prefix="SE" if group_field is None else group_field,
#         percentiles=False,
#         topn=False,
#     )
#     df = df.join(tiers_df)

#     # Fill n/a with -1 for tiers and cast columns to integers
#     df[tiers_df.columns] = df[tiers_df.columns].fillna(-1)
#     for col in tiers_df.columns:
#         if col.endswith("_tier") or col.endswith("_p"):
#             df[col] = df[col].astype("int8")
#         elif col.endswith("_top"):
#             df[col] = df[col].astype("int16")
#         elif col.endswith("_score"):
#             # Convert to a 100% scale
#             df[col] = (df[col] * 100).round().astype("uint16")


# # Tiers are used to display the given barrier on a relative scale
# # compared to other barriers in the state and region.
# # Drop associated raw scores, they are not currently displayed on frontend.
# df = df.drop(columns=[c for c in df.columns if c.endswith("_score")])


# ######## Export data for API
# print("Writing to files")
# df.reset_index(drop=True).to_feather("data/derived/small_barriers.feather")

# # For QA and data exploration only
# df.to_csv("data/derived/small_barriers.csv", index=False)


# ######## Export data for tippecanoe
# # create duplicate columns for those dropped by tippecanoe
# # tippecanoe will use these ones and leave lat / lon
# # so that we can use them for display in the frontend
# df["latitude"] = df.lat
# df["longitude"] = df.lon

# # Drop columns that are not used in vector tiles
# df = df.drop(columns=["Sinuosity", "STATEFIPS", "CrossingCode", "LocalID"])

# # Rename columns for easier use
# df.rename(
#     columns={
#         "County": "CountyName",
#         "COUNTYFIPS": "County",
#         "SinuosityClass": "Sinuosity",
#     },
#     inplace=True,
# )

# # lowercase all fields except those for unit IDs
# df.rename(
#     columns={
#         k: k.lower()
#         for k in df.columns
#         if k not in ("State", "County", "HUC6", "HUC8", "HUC12", "ECO3", "ECO4")
#     },
#     inplace=True,
# )

# # Split datasets based on those that have networks
# # This is done to control the size of the dam vector tiles, so that those without
# # networks are only used when zoomed in further.  Otherwise, the full vector tiles
# # get too large, and points that we want to display are dropped by tippecanoe.
# # Road / stream crossings are particularly large, so those are merged in below.
# df.loc[df.hasnetwork].drop(columns=["hasnetwork"]).to_csv(
#     "data/derived/barriers_with_networks.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
# )

# # Drop columns we don't need from dams that have no networks, since we do not filter or display
# # these fields.
# no_network = df.loc[~df.hasnetwork].drop(
#     columns=[
#         "hasnetwork",
#         "sinuosity",
#         "sizeclasses",
#         "upstreammiles",
#         "downstreammiles",
#         "totalnetworkmiles",
#         "gainmiles",
#         "landcover",
#         "gainmilesclass",
#         "raresppclass",
#         "landcoverclass",
#         "conditionclass",
#         "severityclass",
#         "crossingtypeclass",
#         "roadtypeclass",
#         # "County",
#         # "HUC6",
#         # "HUC8",
#         # "HUC12",
#         # "ECO3",
#         # "ECO4",
#     ]
#     + [c for c in df.columns if c.endswith("_tier")]
# )

# # Combine barriers that don't have networks with road / stream crossings
# print("Reading stream crossings")
# road_crossings = deserialize_df(out_dir / "road_crossings.feather")

# combined = no_network.append(road_crossings, ignore_index=True, sort=False)

# print("Now have {} combined background barriers".format(len(combined)))

# combined["id"] = combined.index.values.astype("uint32")
# combined.protectedland = combined.protectedland.fillna(0)
# combined.rarespp = combined.rarespp.fillna(0)
# combined.name = combined.name.fillna("")


# # Duplicate latitude / longitude columns in again
# combined["latitude"] = combined.lat
# combined["longitude"] = combined.lon

# print("Writing combined file")
# combined.to_csv(
#     "data/derived/barriers_background.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
# )


# print("Done in {:.2f}".format(time() - start))
