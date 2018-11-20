import csv
from time import time
import pandas as pd
import geopandas as gp

from calculate_tiers import calculate_tiers, SCENARIOS

"""
Preprocess data.
Clean data for creating mbtiles of points

"""

start = time()

print("Reading source FGDB dataset")
df = gp.read_file(
    "data/src/Dams_WebViewer_DraftOne_CBI.gdb",
    layer="Dam_Inventory_AllDams_Metrics_Draft_Two_08172018_fix_huc12",
)

print("Projecting to WGS84 and adding lat / lon fields")
# set projection on the data using Proj4 syntax, since GeoPandas doesn't properly recognize it's EPSG Code.
# It is in Albers (EPSG:102003): https://epsg.io/102003
# Project to WGS84
df.crs = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"
df = df.to_crs(epsg=4326)

# Add lat / lon columns
df["lon"] = df.geometry.x
df["lat"] = df.geometry.y

# Drop unnecessary columns, including geometry
df = df[
    [
        "UniqueID",
        "NIDID",
        "SourceDBID",
        "Barrier_Name",
        "Other_Barrier_Name",
        "State",
        "County",
        "River",
        "PurposeCategory",  # value domain
        "Year_Completed",
        "Height",
        "StructureCondition",  # value domain
        "ConstructionMaterial",  # value domain
        "ProtectedLand",  # 0="Unknown", 1="Yes", 2="No"
        "DB_Source",
        "Off_Network",  # 0="On Network", 1="Off Network"
        # "Mussel_Presence",  # 0="Unknown", 1="Yes", 2="No"
        "AbsoluteGainMi",
        "UpstreamMiles",
        "DownstreamMiles",
        "TotalNetworkMiles",
        "PctNatFloodplain",
        "NetworkSinuosity",
        "NumSizeClassGained",
        # "NumberRareSpeciesHUC12", # replaced by newer T&E data
        # "SpeciesRichness",
        "batUSNetID",
        "batDSNetID",
        # "batTotUSDS",
        "HUC12",
        "Ecoregion3",
        "Ecoregion4",
        "StreamOrder",
        "lat",
        "lon",
    ]
]

# TODO: enable domains for specific uses like filtering or download of data
# Lookup state domain codes to state names
# Domains were exported using the ArcGIS Domain to Table tool, with domain name as the key and "value" as the value column
print("Joining in domains")
for domain in (
    "State",
    "StructureCondition",
    "ConstructionMaterial",
    "PurposeCategory",
):
    domain_df = (
        pd.read_csv("data/src/{}_domain.csv".format(domain))
        .set_index([domain])
        .drop("OID", axis=1)
        .rename(columns={"value": "{}Value".format(domain)})
    )
    #     # Join to domain values, then drop the domain codes
    df = (
        df.join(domain_df, on=(domain))
        .drop(domain, axis=1)
        .rename(columns={"{}Value".format(domain): domain})
    )
    # set missing data as "Unknown" explicitly
    # df[domain] = df.apply(
    #     lambda row: "Unknown" if pd.isnull(row[domain]) else row[domain], axis=1
    # )
    df.loc[df[domain].isnull(), domain] = "Unknown"

# # Lookup the simple domains directly
# Not used right now: "Mussel_Presence"
for domain in ("ProtectedLand",):
    df[domain] = df[domain].map({0: "Unknown", 1: "Yes", 2: "No"})

domain = "Off_Network"
df[domain] = df[domain].map({0: "On Network", 1: "Off Network"})

# Filter out any dams that do not have a HUC12 (they are not valid)
# there should only be one.
df = df[df["HUC12"].notnull()].copy()

# Calculate HUC and Ecoregion codes
print("Calculating HUC codes")
df["HUC2"] = df["HUC12"].str.slice(0, 2)
df["HUC4"] = df["HUC12"].str.slice(0, 4)
df["HUC6"] = df["HUC12"].str.slice(0, 6)
df["HUC8"] = df["HUC12"].str.slice(0, 8)
df["HUC10"] = df["HUC12"].str.slice(0, 10)


df.rename(columns={"Ecoregion3": "ECO3", "Ecoregion4": "ECO4"}, inplace=True)

# Fix name issue - 3 dams have duplicate dam names with line breaks, which breaks tippecanoe
ids = df.UniqueID.isin(["s18605", "s18684", "s18687"])
df.loc[ids, "Barrier_Name"] = df.loc[ids, "Barrier_Name"].apply(
    lambda v: v.split("\r")[0]
)

# Calculate height class
# Height in 10ft increments; -1 (height of 0) indicates null
print("Calculating height class")
df["HeightClass"] = -1
row_index = df.Height > 0
df.loc[row_index, "HeightClass"] = (df.loc[row_index, "Height"] / 10).round()
df.HeightClass = df.HeightClass.astype("int8")


# Join T & E species summary
species_df = pd.read_csv(
    "data/summary/species_huc12_summary.csv", dtype={"HUC12": str}
).set_index(["HUC12"])
df = df.join(species_df, on="HUC12").fillna({"NumTEspp": 0})


# Extract the columns we want in the order we want
df = df[
    [
        "UniqueID",
        "lat",
        "lon",
        "NIDID",
        "Barrier_Name",
        "Other_Barrier_Name",
        "Year_Completed",
        "Height",
        "HeightClass",
        "ConstructionMaterial",
        "PurposeCategory",
        "StructureCondition",
        "County",
        "State",
        "River",
        "StreamOrder",
        "HUC2",
        "HUC4",
        "HUC6",
        "HUC8",
        "HUC10",
        "HUC12",
        "ECO3",
        "ECO4",
        "Off_Network",
        "ProtectedLand",
        "NumTEspp",
        "UpstreamMiles",
        "DownstreamMiles",
        "TotalNetworkMiles",
        "AbsoluteGainMi",
        "PctNatFloodplain",
        "NetworkSinuosity",
        "NumSizeClassGained",
    ]
]


# Calculate tiers
for group_field in (None, "State", "HUC8"):  # TODO: "ECO3", "HUC6"?
    if group_field is None:
        print("Calculating regional tiers")
    else:
        print("Calculating tiers for {}".format(group_field))

    is_large_unit = group_field in (None, "State")

    tiers_df = calculate_tiers(
        df,
        SCENARIOS,
        group_field=group_field,
        prefix=group_field,
        percentiles=is_large_unit,
        topn=is_large_unit,
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


# print("Done in {:.2f}".format(time() - start))
