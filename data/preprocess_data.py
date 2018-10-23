import csv
import pandas as pd
import geopandas as gp

"""
Preprocess data.
Clean data for creating mbtiles of points

"""

# TODO: handle the joins to FGDB domains here instead

print("Reading source FGDB dataset")
df = gp.read_file(
    "data/src/Dams_WebViewer_DraftOne_CBI_fix_HUC12.gdb",
    layer="dams_08172018_fix_huc12",
).drop(columns=["x", "y"])

# set projection on the data using Proj4 syntax, since GeoPandas doesn't properly recognize it's EPSG Code.
# It is in Albers (EPSG:102003): https://epsg.io/102003
df.crs = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

# Project to WGS84 and add x, y columns
print("Projecting to WGS84 and adding lat / lon columns")
df = df.to_crs(epsg=4326)
df["lon"] = df.apply(lambda row: row.geometry.x, axis=1)
df["lat"] = df.apply(lambda row: row.geometry.y, axis=1)
df = pd.DataFrame(df.drop(columns="geometry"))

# Drop unnecessary columns
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
        "Mussel_Presence",  # 0="Unknown", 1="Yes", 2="No"
        "AbsoluteGainMi",
        "UpstreamMiles",
        "DownstreamMiles",
        "TotalNetworkMiles",
        "PctNatFloodplain",
        "NetworkSinuosity",
        "NumSizeClassGained",
        "NumberRareSpeciesHUC12",
        "SpeciesRichness",
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
    # Join to domain values, then drop the domain codes
    df = (
        df.join(domain_df, on=(domain))
        .drop(domain, axis=1)
        .rename(columns={"{}Value".format(domain): domain})
    )
    # set missing data as "Unknown" explicitly
    df[domain] = df.apply(
        lambda row: "Unknown" if pd.isnull(row[domain]) else row[domain], axis=1
    )


# Lookup the simple domains directly
YN_domain = {0: "Unknown", 1: "Yes", 2: "No"}
for domain in ("ProtectedLand", "Mussel_Presence"):
    df[domain] = df.apply(lambda row: YN_domain.get(row[domain], "Unknown"), axis=1)

Off_Network_domain = {0: "Off Network", 1: "On Network"}
df["Off_Network"] = df.apply(
    lambda row: Off_Network_domain.get(row[domain], "Unknown"), axis=1
)

# Filter out any dams that do not have a HUC12 (they are not valid)
# there should only be one.
df = df[df["HUC12"].notnull()].copy()

# Calculate HUC and Ecoregion codes
print("Calculating HUC codes")
df["HUC2"] = df.apply(lambda row: row["HUC12"][:2], axis=1)
df["HUC4"] = df.apply(lambda row: row["HUC12"][:4], axis=1)
df["HUC8"] = df.apply(lambda row: row["HUC12"][:8], axis=1)

df.rename(columns={"Ecoregion3": "ECO3", "Ecoregion4": "ECO4"}, inplace=True)

# Fix name issue - 3 dams have duplicate dam names with line breaks, which breaks tippecanoe
ids = df.UniqueID.isin(["s18605", "s18684", "s18687"])
df.loc[ids, "Barrier_Name"] = df.loc[ids, "Barrier_Name"].apply(
    lambda v: v.split("\r")[0]
)

# Export full set of fields
df.to_csv("data/src/dams.csv", index_label="id")


# Calculate height class
# Height in 10ft increments; -1 (height of 0) indicates null
def calc_height_class(height):
    if pd.isnull(height) or height == 0:
        return -1
    return int(round(height / 10.0))


df["HeightClass"] = df.apply(lambda row: calc_height_class(row.Height), axis=1)


# Export full set of fields
df.to_csv("data/src/dams.csv", index_label="id")


# Export subset of fields for use in mbtiles
df = df[
    [
        "UniqueID",
        # "NIDID",
        # "SourceDBID",
        "Barrier_Name",
        # "Other_Barrier_Name",
        "State",
        "County",
        "River",
        "PurposeCategory",  # value domain
        "Year_Completed",
        "HeightClass",
        "StructureCondition",  # value domain
        "ConstructionMaterial",  # value domain
        "ProtectedLand",  # 0="Unknown", 1="Yes", 2="No"
        # "DB_Source",
        # "Off_Network",  # 0="On Network", 1="Off Network"
        "Mussel_Presence",  # 0="Unknown", 1="Yes", 2="No"
        "AbsoluteGainMi",
        "UpstreamMiles",
        "DownstreamMiles",
        "TotalNetworkMiles",
        "PctNatFloodplain",
        "NetworkSinuosity",
        "NumSizeClassGained",
        # "NumberRareSpeciesHUC12", # FIXME: currently not present
        # "SpeciesRichness", # FIXME: currently not present
        # "batUSNetID",  # FIXME: not currently used
        # "batDSNetID",  # FIXME: not currently used
        "HUC2",
        "HUC4",
        "HUC8",
        "HUC12",
        "ECO3",
        "ECO4",
        # "StreamOrder",
        "lat",
        "lon",
    ]
]


df.to_csv("data/src/dams_mbtiles.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)


# Consider bins of AbsMilesGained for filtering too; log scale


# g = df.groupby(["State", "HeightClass", "PurposeCategory", "ProtectedLand"]).agg({"UniqueID": {"dams": "count"}})


# TODO: calculate regional scores and scores for main units
