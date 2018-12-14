"""
Preprocess data.
Clean data for creating mbtiles of points

"""

import os
import sys
import csv
from time import time
import pandas as pd
import geopandas as gp

# Lazy way to import from calculate tiers from a shared file, this allows us to import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.calculate_tiers import calculate_tiers, SCENARIOS

from domains import STATE_FIPS_DOMAIN


start = time()

print("Reading source FGDB dataset")
df = gp.read_file(
    "data/src/Road_Related_Barriers_DraftOne_Final.gdb",
    layer="Road_Barriers_WebViewer_DraftOne_ALL_12132018",
)

# Filter out any dams that do not have a HUC12 or State (currently none filtered)
df = df.loc[df.HUC12.notnull() & df.STATE_FIPS.notnull()].copy()

# Per instructions from SARP, drop all Potential_Project=='SRI Only'
df = df.loc[df.Potential_Project != "SRI Only"].copy()

# Assign an ID.  Note: this is ONLY valid for this exact version of the inventory
df["id"] = df.index.values.astype("uint32")


print("Projecting to WGS84 and adding lat / lon fields")

if not df.crs:
    # set projection on the data using Proj4 syntax, since GeoPandas doesn't always recognize it's EPSG Code.
    # It is in Albers (EPSG:102003): https://epsg.io/102003
    df.crs = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

# Project to WGS84
df = df.to_crs(epsg=4326)

# Add lat / lon columns
df["lon"] = df.geometry.x.astype("float32")
df["lat"] = df.geometry.y.astype("float32")

# drop geometry, no longer needed
df = df.drop(columns=["geometry"])


# Rename ecoregion columns
df.rename(columns={"NA_L3CODE": "ECO3", "US_L4CODE": "ECO4"}, inplace=True)

# Rename all columns that have underscores
df.rename(
    columns={c: c.replace("_", "") for c in df.columns[df.columns.str.count("_") > 0]},
    inplace=True,
)

# Rename columns to make them easier to handle
# also rename fields to match dams for consistency
df.rename(
    columns={
        "STATE": "State",
        "OnConservationLand": "ProtectedLand",
        "NumberRareSpeciesHUC12": "RareSpp",
        "TownId": "County",
        # Note re: SARPID - this isn't quite correct but needed for consistency
        "AnalysisId": "SARPID",
        "AbsoluteGainMi": "GainMiles",
        "PctNatFloodplain": "Landcover",
        "NetworkSinuosity": "Sinuosity",
        "NumSizeClassesGained": "SizeClasses",
        "CrossingTypeId": "CrossingType",
        "RoadTypeId": "RoadType",
        "CrossingConditionId": "Condition",
        "StreamName": "Stream",
        "NumberOfStructures": "Structures",
    },
    inplace=True,
)

# Flag if the field has a network
df["HasNetwork"] = ~df.GainMiles.isnull()


######### Fix data issues

# Join in state from FIPS due to data issue with values in State field (many are missing)
df.State = df.STATEFIPS.map(STATE_FIPS_DOMAIN)

# Drop ' County' from County field
df.County = df.County.fillna("").str.replace(" County", "")

# Fix mixed casing of values
for column in ("CrossingType", "RoadType", "Stream", "Road"):
    df[column] = df[column].fillna("Unknown").str.title().str.strip()
    df.loc[df[column].str.len() == 0, column] = "Unknown"

# Fix issues with RoadType
df.loc[df.RoadType.isin(("No Data", "NoData")), "RoadType"] = "Unknown"

# Fix issues with Condition
df.Condition = df.Condition.fillna("Unknown")
df.loc[df.Condition == "No Data", "Condition"] = "Unknown"

# Fix issues with Structures
df.Structures = df.Structures.fillna(-1).astype("int8")

#########  Fill NaN fields and set data types

for column in ("CrossingCode", "LocalID", "Source"):
    df[column] = df[column].fillna("").str.strip()

for column in ("RareSpp", "ProtectedLand"):
    df[column] = df[column].fillna(0).astype("uint8")

for column in ("COUNTYFIPS",):
    df[column] = df[column].fillna(0).astype("uint16")


# Fill metrics with -1
for column in ("Landcover", "SizeClasses"):  # null but with network should be 0
    df[column] = df[column].fillna(-1).astype("int8")

# Round floating point columns to 3 decimals
for column in (
    "Sinuosity",
    "GainMiles",
    "UpstreamMiles",
    "DownstreamMiles",
    "TotalNetworkMiles",
):
    df[column] = df[column].round(3).fillna(-1).astype("float32")


######## Calculate derived fields

# Construct a name from Stream and Road
df["Name"] = "Unknown Crossing"
df.loc[(df.Stream != "Unknown") & (df.Road != "Unknown"), "Name"] = (
    df.Stream + " / " + df.Road + " Crossing"
)
df.loc[(df.Stream != "Unknown") & (df.Road == "Unknown"), "Name"] = (
    df.Stream + " / Unknown Road Crossing"
)
df.loc[(df.Stream == "Unknown") & (df.Road != "Unknown"), "Name"] = (
    " Unknown Stream / " + df.Road + " Crossing"
)


# Calculate HUC and Ecoregion codes
print("Calculating HUC codes")
# df["HUC2"] = df["HUC12"].str.slice(0, 2)  # region
df["HUC6"] = df["HUC12"].str.slice(0, 6)  # basin
df["HUC8"] = df["HUC12"].str.slice(0, 8)  # subbasin

########## Drop unnecessary columns
df = df[
    [
        "id",
        "lat",
        "lon",
        # ID and source info
        "SARPID",
        "CrossingCode",
        "LocalID",  # => source
        # Basic info
        "Name",
        "County",
        "State",
        # Species info
        "RareSpp",
        # Stream info
        "Stream",
        # Road info
        "Road",
        "RoadType",
        # Location info
        "ProtectedLand",
        # "HUC2",
        "HUC6",
        "HUC8",
        "HUC12",
        "ECO3",
        "ECO4",
        # Barrier info
        "CrossingType",
        "Condition",
        "PotentialProject",
        "Structures",
        # Metrics
        "GainMiles",
        "UpstreamMiles",
        "DownstreamMiles",
        "TotalNetworkMiles",
        "Landcover",
        "Sinuosity",
        "SizeClasses",
        # Internal fields
        "COUNTYFIPS",
        "STATEFIPS",
        "HasNetwork",
    ]
].set_index("id", drop=False)


# Calculate tiers
for group_field in (None, "State"):
    print("Calculating tiers for {}".format(group_field or "Region"))

    # Note: some states do not yet have enough inventoried barriers for percentiles to work

    tiers_df = calculate_tiers(
        df.loc[df.HasNetwork],
        SCENARIOS,
        group_field=group_field,
        prefix="SE" if group_field is None else group_field,
        percentiles=group_field is None,
        topn=group_field is None,
    )
    df = df.join(tiers_df)

    # Fill n/a with -1 for tiers and cast columns to integers
    df[tiers_df.columns] = df[tiers_df.columns].fillna(-1)
    for col in tiers_df.columns:
        if col.endswith("_tier") or col.endswith("_p") or col.endswith("_top"):
            df[col] = df[col].astype("int8")
        elif col.endswith("_score"):
            df[col] = df[col].round(3).astype("float32")


print("Writing to files")
df.reset_index(drop=True).to_feather("data/src/small_barriers.feather")
df.to_csv("data/src/small_barriers.csv", index=False)


# # TODO:
# # Export subset of fields for use in mbtiles

# mbtiles_fields = [
#     "UniqueID",
#     # "NIDID",
#     # "SourceDBID",
#     "Barrier_Name",
#     # "Other_Barrier_Name",
#     "State",
#     # "County", # TODO:
#     "River",
#     "PurposeCategory",  # value domain
#     "Year_Completed",
#     "HeightClass",
#     "StructureCondition",  # value domain
#     "ConstructionMaterial",  # value domain
#     "ProtectedLand",  # 0="Unknown", 1="Yes", 2="No"
#     # "DB_Source",
#     # "Off_Network",  # 0="On Network", 1="Off Network"
#     # "Mussel_Presence",  # 0="Unknown", 1="Yes", 2="No"
#     "AbsoluteGainMi",
#     "UpstreamMiles",
#     "DownstreamMiles",
#     "TotalNetworkMiles",
#     "PctNatFloodplain",
#     "NetworkSinuosity",
#     "NumSizeClassGained",
#     # "NumberRareSpeciesHUC12", # FIXME: currently not present
#     # "SpeciesRichness", # FIXME: currently not present
#     # "batUSNetID",  # FIXME: not currently used
#     # "batDSNetID",  # FIXME: not currently used
#     "HUC2",
#     "HUC4",
#     "HUC6",
#     "HUC8",
#     "HUC10",
#     "HUC12",
#     "ECO3",
#     "ECO4",
#     # "StreamOrder",
#     "lat",
#     "lon",
#     # tiers
#     "NC",
#     "WC",
#     "NCWC",
#     "State_NC",
#     "State_WC",
#     "State_NCWC",
#     "HUC2_NC",
#     "HUC2_WC",
#     "HUC2_NCWC",
#     "HUC4_NC",
#     "HUC4_WC",
#     "HUC4_NCWC",
#     "HUC8_NC",
#     "HUC8_WC",
#     "HUC8_NCWC",
# ]


# print("Writing subset of fields to data/src/dams_mbtiles.csv")
# df[mbtiles_fields].to_csv(
#     "data/src/dams_mbtiles.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
# )


# # Query out the highest regional priorities
# # TODO: this needs to be fixed; tippecanoe is having issues with some of the numeric fields
# df.query("NCWC > 0 & (NCWC <=4 | NC <= 4 | WC <=4)").to_csv(
#     "data/src/dams_priority_mbtiles.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
# )


# # Consider bins of AbsMilesGained for filtering too; log scale


# # g = df.groupby(["State", "HeightClass", "PurposeCategory", "ProtectedLand"]).agg({"UniqueID": {"dams": "count"}})


# # TODO: calculate regional scores and scores for main units


print("Done in {:.2f}".format(time() - start))
