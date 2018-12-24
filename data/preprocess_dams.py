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
from api.domains import STATE_FIPS_DOMAIN, HUC6_DOMAIN, RECON_TO_FEASIBILITY

from classify import (
    classify_gainmiles,
    classify_sinuosity,
    classify_landcover,
    classify_rarespp,
    classify_streamorder,
)

start = time()

print("Reading source FGDB dataset")
df = gp.read_file(
    "data/src/Dams_Webviewer_DraftOne_Final.gdb",
    layer="SARP_Dam_Inventory_Prioritization_12132018_D1_ALL",
)

# Filter out any dams that do not have a HUC12 (they are not valid, should be 3)
# Also drop any that do not have a state assigned (there should be 13)
df = df.loc[df.HUC12.notnull() & df.STATE_FIPS.notnull()].copy()

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
df.rename(
    columns={
        "BarrierName": "Name",
        "DBSource": "Source",
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


########## Field fixes
# Round height to nearest foot.  There are no dams between 0 and 1 foot, so fill all
# na as 0
df.Height = df.Height.fillna(0).round().astype("uint16")

# Cleanup names
# Standardize the casing of the name
df.Name = df.Name.fillna("").str.title().str.strip()
df.OtherBarrierName = df.OtherBarrierName.fillna("").str.title().str.strip()

# Fix name issue - 3 dams have duplicate dam names with line breaks, which breaks tippecanoe
ids = df.loc[df.Name.str.count("\r") > 0].index
df.loc[ids, "Name"] = df.loc[ids].Name.apply(lambda v: v.split("\r")[0])

# Replace estimated dam names if another name is available
ids = (df.Name.str.count("Estimated Dam") > 0) & (df.OtherBarrierName.str.len() > 0)
df.loc[ids, "Name"] = df.loc[ids].OtherBarrierName

# Fill any remaining ones that are missing
# df.loc[df.Name.str.len() == 0, "Name"] = "Unknown Dam"


# Join in state from FIPS due to data issue with values in State field (many are missing)
df.State = df.STATEFIPS.map(STATE_FIPS_DOMAIN)

# Fix COUNTYFIPS: leading 0's and convert to string
df.COUNTYFIPS = df.COUNTYFIPS.astype("int").astype(str).str.pad(5, fillchar="0")

# Drop ' County' from County field
df.County = df.County.fillna("").str.replace(" County", "")

# Fix ProtectedLand: since this was from an intersection, all values should
# either be 1 (intersected) or 0 (did not)
df.loc[df.ProtectedLand != 1, "ProtectedLand"] = 0

# Fix issue with Landcover.  It is null in places where there is a network
# This was due to issues with the catchment floodplains during network processing
df.loc[df.HasNetwork & df.Landcover.isnull(), "Landcover"] = 0
df.Landcover = df.Landcover.round()

# Fix years between 0 and 100; assume they were in the 1900s
df.loc[(df.Year > 0) & (df.Year < 100), "Year"] = df.Year + 1900
df.loc[df.Year == 20151, "Year"] = 2015
df.loc[df.Year == 9999, "Year"] = 0

df.River = df.River.str.title()


#########  Fill NaN fields and set data types
df.SARPID = df.SARPID.astype("uint32")

for column in ("River", "NIDID", "Source"):
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


for column in ("Year",):
    df[column] = df[column].fillna(0).astype("uint16")


# Fill metrics with -1
for column in (
    "StreamOrder",
    "Landcover",  # null but with network should be 0
    "SizeClasses",
):
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
print("Calculating derived attributes")

# Calculate height class
df["HeightClass"] = 0  # Unknown
df.loc[(df.Height > 0) & (df.Height < 5), "HeightClass"] = 1
df.loc[(df.Height >= 5) & (df.Height < 10), "HeightClass"] = 2
df.loc[(df.Height >= 10) & (df.Height < 25), "HeightClass"] = 3
df.loc[(df.Height >= 25) & (df.Height < 50), "HeightClass"] = 4
df.loc[(df.Height >= 50) & (df.Height < 100), "HeightClass"] = 5
df.loc[df.Height >= 100, "HeightClass"] = 6
df.HeightClass = df.HeightClass.astype("uint8")

# Calculate HUC and Ecoregion codes
df["HUC6"] = df["HUC12"].str.slice(0, 6)  # basin
df["HUC8"] = df["HUC12"].str.slice(0, 8)  # subbasin
df["Basin"] = df.HUC6.map(HUC6_DOMAIN)

# Calculate feasibility
df["Feasibility"] = df.Recon.map(RECON_TO_FEASIBILITY).astype("uint8")

# Bin metrics
df["GainMilesClass"] = classify_gainmiles(df.GainMiles)
df["SinuosityClass"] = classify_sinuosity(df.Sinuosity)
df["LandcoverClass"] = classify_landcover(df.Landcover)
df["RareSppClass"] = classify_rarespp(df.RareSpp)
df["StreamOrderClass"] = classify_streamorder(df.StreamOrder)


######## Drop unnecessary columns
df = df[
    [
        "id",
        "lat",
        "lon",
        # ID and source info
        "SARPID",
        "NIDID",
        "Source",  # => source
        # Basic info
        "Name",
        "County",
        "State",
        "Basin",
        # Species info
        "RareSpp",
        # River info
        "River",
        "StreamOrder",
        "NHDplusVersion",
        # Location info
        "ProtectedLand",
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
        "Feasibility",
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
        "HeightClass",
        "RareSppClass",
        "GainMilesClass",
        "SinuosityClass",
        "LandcoverClass",
        "StreamOrderClass",
    ]
].set_index("id", drop=False)


# Calculate tiers
for group_field in (None, "State"):
    print("Calculating tiers for {}".format(group_field or "Region"))

    tiers_df = calculate_tiers(
        df.loc[df.HasNetwork],
        SCENARIOS,
        group_field=group_field,
        prefix="SE" if group_field is None else group_field,
        percentiles=False,
        topn=False,
    )
    df = df.join(tiers_df)

    # Fill n/a with -1 for tiers and cast columns to integers
    df[tiers_df.columns] = df[tiers_df.columns].fillna(-1)
    for col in tiers_df.columns:
        if col.endswith("_tier") or col.endswith("_p"):
            df[col] = df[col].astype("int8")
        elif col.endswith("_top"):
            df[col] = df[col].astype("int16")
        elif col.endswith("_score"):
            # Convert to a 100% scale
            df[col] = (df[col] * 100).round().astype("uint16")


# Export full set of fields
print("Writing to output files")

# For use in API
df.reset_index(drop=True).to_feather("data/derived/dams.feather")

# For QA
df.to_csv("data/derived/dams.csv", index_label="id")


# Split datasets based on those that have networks

# create duplicate columns for those dropped by tippecanoe
# tippecanoe will use these ones and leave lat / lon
df["latitude"] = df.lat
df["longitude"] = df.lon

df = df.drop(columns=["Sinuosity", "Source", "NHDplusVersion", "STATEFIPS"])

# convert HasNetwork so that it encodes into tiles properly
df.HasNetwork = df.HasNetwork.astype("uint8")


df.rename(
    columns={
        "County": "CountyName",
        "COUNTYFIPS": "County",
        "SinuosityClass": "Sinuosity",
    },
    inplace=True,
)

# lowercase all fields except those for unit IDs
df.rename(
    columns={
        k: k.lower()
        for k in df.columns
        if k not in ("State", "County", "HUC6", "HUC8", "HUC12", "ECO3", "ECO4")
    },
    inplace=True,
)


df.to_csv("data/derived/dams_mbtiles.csv", index_label="id")


print("Done in {:.2f}".format(time() - start))
