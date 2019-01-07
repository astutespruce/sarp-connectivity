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
from api.domains import (
    STATE_FIPS_DOMAIN,
    HUC6_DOMAIN,
    BARRIER_CONDITION_TO_DOMAIN,
    POTENTIAL_TO_SEVERITY,
    ROAD_TYPE_TO_DOMAIN,
    CROSSING_TYPE_TO_DOMAIN,
)

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
    },
    inplace=True,
)

# Flag if the field has a network
# TODO: remove no-upstream from network analysis
df["HasNetwork"] = ~(
    df.GainMiles.isnull() | (df.PotentialProject == "No Upstream Channel")
)


######### Fix data issues

# Join in state from FIPS due to data issue with values in State field (many are missing)
df.State = df.STATEFIPS.map(STATE_FIPS_DOMAIN)

# Fix COUNTYFIPS: leading 0's and convert to string
df.COUNTYFIPS = df.COUNTYFIPS.astype("int").astype(str).str.pad(5, fillchar="0")

# Drop ' County' from County field
df.County = df.County.fillna("").str.replace(" County", "")

# Fix mixed casing of values
for column in ("CrossingType", "RoadType", "Stream", "Road"):
    df[column] = df[column].fillna("Unknown").str.title().str.strip()
    df.loc[df[column].str.len() == 0, column] = "Unknown"

# Fix line returns in stream name and road name
df.loc[df.SARPID == "sm7044", "Stream"] = "Unnamed"
df.Road = df.Road.str.replace("\r\n", "")

# Fix issues with RoadType
df.loc[df.RoadType.isin(("No Data", "NoData", "Nodata")), "RoadType"] = "Unknown"

# Fix issues with Condition
df.Condition = df.Condition.fillna("Unknown")
df.loc[
    (df.Condition == "No Data")
    | (df.Condition == "No data")
    | (df.Condition.str.strip().str.len() == 0),
    "Condition",
] = "Unknown"

#########  Fill NaN fields and set data types

for column in ("CrossingCode", "LocalID", "Source"):
    df[column] = df[column].fillna("").str.strip()

for column in ("RareSpp", "ProtectedLand"):
    df[column] = df[column].fillna(0).astype("uint8")

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
print("Calculating derived values")

# Construct a name from Stream and Road
df["Name"] = ""  # "Unknown Crossing"
df.loc[(df.Stream != "Unknown") & (df.Road != "Unknown"), "Name"] = (
    df.Stream + " / " + df.Road + " Crossing"
)
# df.loc[(df.Stream != "Unknown") & (df.Road == "Unknown"), "Name"] = (
#     df.Stream + " / Unknown Road Crossing"
# )
# df.loc[(df.Stream == "Unknown") & (df.Road != "Unknown"), "Name"] = (
#     " Unknown Stream / " + df.Road + " Crossing"
# )


# Calculate HUC and Ecoregion codes
df["HUC6"] = df["HUC12"].str.slice(0, 6)  # basin
df["HUC8"] = df["HUC12"].str.slice(0, 8)  # subbasin
df["Basin"] = df.HUC6.map(HUC6_DOMAIN)

df["ConditionClass"] = df.Condition.map(BARRIER_CONDITION_TO_DOMAIN)
df["SeverityClass"] = df.PotentialProject.map(POTENTIAL_TO_SEVERITY)
df["CrossingTypeClass"] = df.CrossingType.map(CROSSING_TYPE_TO_DOMAIN)
df["RoadTypeClass"] = df.RoadType.map(ROAD_TYPE_TO_DOMAIN)


# Bin metrics
df["GainMilesClass"] = classify_gainmiles(df.GainMiles)
df["SinuosityClass"] = classify_sinuosity(df.Sinuosity)
df["LandcoverClass"] = classify_landcover(df.Landcover)
df["RareSppClass"] = classify_rarespp(df.RareSpp)


########## Drop unnecessary columns
df = df[
    [
        "id",
        "lat",
        "lon",
        # ID and source info
        "SARPID",
        "CrossingCode",
        "LocalID",
        "Source",
        # Basic info
        "Name",
        "County",
        "State",
        "Basin",
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
        "RareSppClass",
        "GainMilesClass",
        "SinuosityClass",
        "LandcoverClass",
        "ConditionClass",
        "SeverityClass",
        "CrossingTypeClass",
        "RoadTypeClass",
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


# Short term: drop scores, they aren't used in the frontend
df = df.drop(columns=[c for c in df.columns if c.endswith("_score")])


print("Writing to files")

# For API
df.reset_index(drop=True).to_feather("data/derived/small_barriers.feather")

# For QA
df.to_csv("data/derived/small_barriers.csv", index=False)


df = df.drop(columns=["Sinuosity", "STATEFIPS", "CrossingCode", "LocalID"])


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

df["latitude"] = df.lat
df["longitude"] = df.lon

df.loc[df.hasnetwork].drop(columns=["hasnetwork"]).to_csv(
    "data/derived/barriers_with_networks.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
)

no_network = df.loc[~df.hasnetwork].drop(
    columns=[
        "hasnetwork",
        "sinuosity",
        "sizeclasses",
        "upstreammiles",
        "downstreammiles",
        "totalnetworkmiles",
        "gainmiles",
        "landcover",
        "gainmilesclass",
        "raresppclass",
        "landcoverclass",
        "conditionclass",
        "severityclass",
        "crossingtypeclass",
        "roadtypeclass",
        "County",
        "HUC6",
        "HUC8",
        "HUC12",
        "ECO3",
        "ECO4",
    ]
    + [c for c in df.columns if c.endswith("_tier")]
)

no_network.to_csv("data/derived/barriers_without_networks.csv", index=False)

# Combine with road crossings
print("Reading stream crossings")
road_crossings = pd.read_csv(
    "data/derived/road_crossings.csv", dtype={"Road": str, "Stream": str, "SARPID": str}
)

road_crossings.Stream = road_crossings.Stream.str.strip()
road_crossings.Road = road_crossings.Road.str.strip()

road_crossings.rename(
    columns={c: c.lower() for c in road_crossings.columns}, inplace=True
)

# Zero out some fields
road_crossings["protectedland"] = 0
road_crossings["rarespp"] = 0
road_crossings["name"] = ""


road_crossings.loc[
    (road_crossings.stream.str.strip().str.len() > 0)
    & (road_crossings.road.str.strip().str.len() > 0),
    "name",
] = (road_crossings.stream + " / " + road_crossings.road)


combined = no_network.append(road_crossings, ignore_index=True, sort=False)
combined["id"] = combined.index.values.astype("uint32")

combined["latitude"] = combined.lat
combined["longitude"] = combined.lon

print("Writing combined file")
combined.to_csv(
    "data/derived/barriers_background.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
)


print("Done in {:.2f}".format(time() - start))
