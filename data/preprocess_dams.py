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
    "data/src/Dams_Webviewer_DraftOne_Final.gdb",
    layer="SARP_Dam_Inventory_Prioritization_12132018_D1_ALL",
)

# Filter out any dams that do not have a HUC12 (they are not valid, should be 3)
# Also drop any that do not have a state assigned (there should be 13)
df = df[df.HUC12.notnull() & df.STATE_FIPS.notnull()].copy()


print("Projecting to WGS84 and adding lat / lon fields")


if not df.crs:
    # set projection on the data using Proj4 syntax, since GeoPandas doesn't always recognize it's EPSG Code.
    # It is in Albers (EPSG:102003): https://epsg.io/102003
    df.crs = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

# Project to WGS84
df = df.to_crs(epsg=4326)

# Add lat / lon columns
df["lon"] = df.geometry.x
df["lat"] = df.geometry.y

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
df.rename(
    columns={
        "NumberRareSpeciesHUC12": "RareSpp",
        "YearCompleted": "Year",
        "ConstructionMaterial": "Construction",
        "PurposeCategory": "Purpose",
        "StructureCondition": "Condition",
        "AbsoluteGainMi": "GainMiles",
        "PctNatFloodplain": "Landcover",
        "NetworkSinuosity": "Sinuosity",
        "NumSizeClassGained": "SizeClasses",
    },
    inplace=True,
)

# Flag if the field has a network
df["HasNetwork"] = ~df.GainMiles.isnull()


# Cleanup names
# Standardize the casing of the name
df.BarrierName = df.BarrierName.fillna("").str.title().str.strip()
df.OtherBarrierName = df.OtherBarrierName.fillna("").str.title().str.strip()

# Fix name issue - 3 dams have duplicate dam names with line breaks, which breaks tippecanoe
ids = df.loc[df.BarrierName.str.count("\r") > 0].index
df.loc[ids, "BarrierName"] = df.loc[ids].BarrierName.apply(lambda v: v.split("\r")[0])

# Replace estimated dam names if another name is available
ids = (df.BarrierName.str.count("Estimated Dam") > 0) & (
    df.OtherBarrierName.str.len() > 0
)
df.loc[ids, "BarrierName"] = df.loc[ids].OtherBarrierName


# Calculate HUC and Ecoregion codes
print("Calculating HUC codes")
df["HUC2"] = df["HUC12"].str.slice(0, 2)  # region
df["HUC6"] = df["HUC12"].str.slice(0, 6)  # basin
df["HUC8"] = df["HUC12"].str.slice(0, 8)  # subbasin


# Calculate height class
# Height in 10ft increments; -1 (height of 0) indicates null
print("Calculating height class")

# Round height to nearest foot.  There are no dams between 0 and 1 foot, so fill all
# na as 0
df.Height = df.Height.fillna(0).round().astype("uint16")
df["HeightClass"] = -1
row_index = df.Height > 0
df.loc[row_index, "HeightClass"] = (df.loc[row_index, "Height"] / 10).round()
df.HeightClass = df.HeightClass.astype("int8")

# Join in state from FIPS due to data issue with values in State field (many are missing)
df.State = df.STATEFIPS.map(STATE_FIPS_DOMAIN)

# Drop ' County' from County field
df.County = df.County.fillna("").str.replace(" County", "")


# Fix ProtectedLand: since this was from an intersection, all values should
# either be 1 (intersected) or 0 (did not)
df.loc[df.ProtectedLand != 1, "ProtectedLand"] = 0

# Fix issue with Landcover.  It is null in places where there is a network
# This was due to issues with the catchment floodplains during network processing
df.loc[df.HasNetwork & df.Landcover.isnull(), "Landcover"] = 0
df.Landcover = df.Landcover.round()

#########  Fill NaN fields and set data types

# Fix years between 0 and 100; assume they were in the 1900s
df.loc[(df.Year > 0) & (df.Year < 100), "Year"] = df.Year + 1900


for column in ("River", "NIDID", "DBSource"):
    df[column] = df[column].fillna("").str.strip()

for column in (
    "RareSpp",
    "ProtectedLand",
    "Construction",
    "Condition",
    "Purpose",
    "Recon",
):
    df[column] = df[column].fillna(0).astype("uint8")


for column in ("Year", "COUNTYFIPS"):
    df[column] = df[column].fillna(0).astype("uint16")


# Fill metrics with -1
for column in (
    "StreamOrder",
    "Landcover",  # null but with network should be 0
    "SizeClasses",
):
    df[column] = df[column].fillna(-1).astype("int8")

# Round to 1-3 decimals
for column in (
    "Sinuosity",
    "GainMiles",
    "UpstreamMiles",
    "DownstreamMiles",
    "TotalNetworkMiles",
):
    df[column] = (
        df[column].round(1 if column == "Sinuosity" else 3).fillna(-1).astype("float32")
    )

# Drop unnecessary columns, including geometry
df = df[
    [
        "lat",
        "lon",
        # ID and source info
        "SARPID",  # use as id throughout
        "NIDID",
        "DBSource",  # => source
        # Basic info
        "BarrierName",
        "County",
        "State",
        # Species info
        "RareSpp",
        # River info
        "River",
        "StreamOrder",
        "NHDplusVersion",
        # Location info
        "ProtectedLand",
        "HUC2",
        "HUC6",
        "HUC8",
        "HUC12",
        "ECO3",
        "ECO4",
        # Dam info
        "Height",
        "Year",
        "Construction",
        "Purpose",
        "Condition",
        "Recon",
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
        "HeightClass",
        "HasNetwork",
    ]
].set_index("SARPID", drop=False)


print("Writing to data/src/dams.csv")
df.reset_index(drop=True).to_feather("data/src/dams.feather")
df.to_csv("data/src/dams.csv", index=False)

raise Foo("")


# Calculate tiers
for group_field in (None, "State"):
    print("Calculating tiers")

    tiers_df = calculate_tiers(
        df.loc[df.HasNetwork],
        SCENARIOS,
        group_field=group_field,
        prefix="SE" if group_field is None else group_field,
        percentiles=True,
        topn=True,
    )
    df = df.join(tiers_df)

    # Fill n/a with -1 for tiers and cast columns to integers
    df[tiers_df.columns] = df[tiers_df.columns].fillna(-1)
    for scenario in SCENARIOS:
        int_fields = [scenario] + [
            f for f in tiers_df.columns if f.endswith("_p") or f.endswith("_top")
        ]
        for col in int_fields:
            df[col] = df[col].astype("int8")


# Export full set of fields
print("Writing to data/src/dams.csv")

df.reset_index(drop=True).to_feather("data/src/dams.feather")
df.to_csv("data/src/dams.csv", index_label="id")


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
