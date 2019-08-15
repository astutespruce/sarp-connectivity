"""
Preprocess dams into data needed by API and tippecanoe for creating vector tiles.

Input: 
* Dam inventory from SARP, including all network metrics and summary unit IDs (HUC12, ECO3, ECO4, State, County, etc).

Outputs:
* `dams.feather`: processed dam data for use by the API
* `dams_with_networks.csv`: Dams with networks for creating vector tiles in tippecanoe
* `dams_without_networks.csv`: Dams without networks for creating vector tiles in tippecanoe

"""
from pathlib import Path
from time import time
import csv
import os
import sys
import geopandas as gp
import pandas as pd
from nhdnet.io import deserialize_gdf


# Lazy way to import from calculate tiers from a shared file, this allows us to import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.classify import (
    classify_gainmiles,
    classify_sinuosity,
    classify_landcover,
    classify_rarespp,
    classify_streamorder,
)
from api.domains import RECON_TO_FEASIBILITY
from api.calculate_tiers import calculate_tiers, SCENARIOS


start = time()

src_dir = Path("../data/sarp/derived/final_results")
out_dir = Path("data/derived/")
boundaries_dir = Path("../data/sarp/derived/boundaries")


print("Reading network analysis results")
df = deserialize_gdf(src_dir / "dams.feather")


print("Read {} dams, {} have networks".format(len(df), len(df.loc[df.HasNetwork])))

# Assign an ID.  Note: this is ONLY valid for this exact version of the inventory,
# so this exact same ID needs to be used for the dam vector tiles
df["id"] = df.joinID


### Spatial joins to boundary layers
df.sindex

print("Joining to counties")
counties = deserialize_gdf(boundaries_dir / "counties.feather")[
    ["geometry", "County", "COUNTYFIPS"]
]
counties.sindex
df = gp.sjoin(df, counties, how="left").drop(columns=["index_right"])


print("Joining to ecoregions")
eco4 = deserialize_gdf(boundaries_dir / "eco4.feather")[["geometry", "ECO3", "ECO4"]]
eco4.sindex
df = gp.sjoin(df, eco4, how="left").drop(columns=["index_right"])


### Project to WGS84
print("Projecting to WGS84 and adding lat / lon fields")
df = df.to_crs(epsg=4326)
df["lon"] = df.geometry.x.astype("float32")
df["lat"] = df.geometry.y.astype("float32")

# drop geometry, no longer needed
df = df.drop(columns=["geometry"])


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


# Field fixes
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


### Fill NaN fields and set data types

# TODO: fix once these are consistently provided
df.SARPID = df.SARPID.fillna(-1).astype("int")
# df.SARPID = df.SARPID.astype("uint32")


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


# Calculate derived fields
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

# Read in HUC6 and join in basin name
huc6 = (
    deserialize_gdf(boundaries_dir / "HUC6.feather")[["HUC6", "NAME"]]
    .rename(columns={"NAME": "Basin"})
    .set_index("HUC6")
)
df = df.join(huc6, on="HUC6")


# Calculate feasibility
df["Feasibility"] = df.Recon.map(RECON_TO_FEASIBILITY).astype("uint8")

# Bin metrics
df["GainMilesClass"] = classify_gainmiles(df.GainMiles)
df["SinuosityClass"] = classify_sinuosity(df.Sinuosity)
df["LandcoverClass"] = classify_landcover(df.Landcover)
df["RareSppClass"] = classify_rarespp(df.RareSpp)
df["StreamOrderClass"] = classify_streamorder(df.StreamOrder)

# Drop unnecessary columns
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


# Calculate tiers and scores for the region (None) and State levels
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


# Tiers are used to display the given barrier on a relative scale
# compared to other barriers in the state and region.
# Drop associated raw scores, they are not currently displayed on frontend.
df = df.drop(columns=[c for c in df.columns if c.endswith("_score")])

# Export data for API
print("Writing to output files")
df.reset_index(drop=True).to_feather("data/derived/dams.feather")

# For QA and data exploration only
df.to_csv(out_dir / "dams.csv", index_label="id")


# Export data for tippecanoe
# create duplicate columns for those dropped by tippecanoe
# tippecanoe will use these ones and leave lat / lon
# so that we can use them for display in the frontend
# TODO: can this be replaced with the actual geometry available to mapbox GL?
df["latitude"] = df.lat
df["longitude"] = df.lon

# Drop columns that are not used in vector tiles
df = df.drop(columns=["Sinuosity", "NHDplusVersion", "STATEFIPS"])

# Rename columns for easier use
df.rename(
    columns={
        "County": "CountyName",
        "COUNTYFIPS": "County",
        "SinuosityClass": "Sinuosity",  # Decoded to a label on frontend
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

# Split datasets based on those that have networks
# This is done to control the size of the dam vector tiles, so that those without
# networks are only used when zoomed in further.  Otherwise, the full vector tiles
# get too large, and points that we want to display are dropped by tippecanoe.
df.loc[df.hasnetwork].drop(columns=["hasnetwork"]).to_csv(
    out_dir / "dams_with_networks.csv", index=False
)

# Drop columns we don't need from dams that have no networks, since we do not filter or display
# these fields.
df.loc[~df.hasnetwork].drop(
    columns=[
        "hasnetwork",
        "sinuosity",
        "sizeclasses",
        "upstreammiles",
        "downstreammiles",
        "totalnetworkmiles",
        "gainmiles",
        "landcover",
        "streamorder",
        "gainmilesclass",
        "raresppclass",
        "heightclass",
        "landcoverclass",
        "streamorderclass",
        "County",
        "HUC6",
        "HUC8",
        "HUC12",
        "ECO3",
        "ECO4",
    ]
    + [c for c in df.columns if c.endswith("_tier")]
).to_csv(out_dir / "dams_without_networks.csv", index=False)

print("Done in {:.2f}".format(time() - start))
