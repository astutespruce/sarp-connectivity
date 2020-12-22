import os
from pathlib import Path
from time import time
import warnings


from dotenv import load_dotenv
import requests


from analysis.constants import (
    SARP_STATES,
    RECON_TO_FEASIBILITY,
    DAM_FS_COLS,
    CRS,
    SMALL_BARRIER_COLS,
    WATERFALL_COLS,
)
from analysis.prep.barriers.lib.arcgis import download_fs, list_services

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


# Load the token from the .env file in the root of this project
load_dotenv()
token = os.getenv("AGOL_TOKEN", None)
if not token:
    raise ValueError("AGOL_TOKEN must be defined in your .env file")


SNAPPED_URL = "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Dam_Snapping_QA_Dataset_01212020/FeatureServer/0"
SMALL_BARRIERS_URL = "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/All_RoadBarriers_01212019/FeatureServer/0"
WATERFALLS_URL = "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/SARP_Waterfall_Database_01212020/FeatureServer/0"

### When needed: generate list of dam inventory services
# Root services URL for USFWS R4
# ROOT_URL = "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/"
# services = [
#     s["url"]
#     for s in list_services(ROOT_URL, token=token)
#     if s["type"] == "FeatureServer"
# ]

# DAM_URLS = dict()
# for id, state in SARP_STATES.items():
#     state = state.replace(" ", "_")
#     url = next(
#         (
#             "{}/0".format(s)
#             for s in services
#             if "{}_Dam_Inventory".format(state) in s or "{}Dams".format(state) in s
#         ),
#         None,
#     )
#     if url:
#         DAM_URLS[id] = url
#     else:
#         print("WARNING: {} service not found".format(state))


# Root URLS of feature service
# Note: PR is not yet available
DAM_URLS = {
    "FL": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/Florida_Dam_Inventory_Jan112019/FeatureServer/0",
    "NC": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/North_Carolina_Dam_Inventory_03252019/FeatureServer/0",
    "LA": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/LouisianaDams/FeatureServer/0",
    "GA": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/R4_Georgia_Dam_Inventory_12_14_2018/FeatureServer/0",
    "AL": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/Alabama_Dam_Inventory_11_15_2018/FeatureServer/0",
    "TX": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/TexasDams/FeatureServer/0",
    "SC": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/R4_South_Carolina_Dam_Inventory_2018/FeatureServer/0",
    "OK": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/OklahomaDams/FeatureServer/0",
    "TN": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/Tennessee_Dam_Inventory_11_15_2018/FeatureServer/0",
    "KY": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/R4_Kentucky_Dam_Inventory_12_01_2018/FeatureServer/0",
    "AR": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/Arkansas_Dam_Inventory_11122018/FeatureServer/0",
    "MS": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/Mississippi_Dam_Inventory_11192018/FeatureServer/0",
    "MO": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/MissouriDams/FeatureServer/0",
    "VA": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/Virginia_Dam_Inventory_11_12_2018/FeatureServer/0",
    "PR": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Puerto_Rico_Dam_Inventory_12202019/FeatureServer/0",
}


out_dir = Path("data/barriers/source")

start = time()

### Download and merge state feature services
merged = None
# Services have varying casing of SNAP2018
# TODO: update snap2018??
dam_cols = DAM_FS_COLS
for state, url in DAM_URLS.items():
    download_start = time()

    print("---- Downloading {} ----".format(state))
    df = download_fs(url, fields=dam_cols, token=token).rename(
        columns={
            "SARPUniqueID": "SARPID",
            "Snap2018": "ManualReview",
            "SNAP2018": "ManualReview",
            "PotentialFeasibility": "Feasibility",
            "Barrier_Name": "Name",
            "Other_Barrier_Name": "OtherName",
            "DB_Source": "Source",
            "Year_Completed": "Year",
            "ConstructionMaterial": "Construction",
            "PurposeCategory": "Purpose",
            "StructureCondition": "Condition",
        }
    )
    df["SourceState"] = state
    print("Downloaded {:,} dams in {:.2f}s".format(len(df), time() - download_start))

    ix = df.SARPID.isnull()
    if ix.max():
        print(f"WARNING: {ix.sum():,} dams are missing SARPID")

    # Add feasibility so that we can merge
    if not "Feasibility" in df.columns:
        df["Feasibility"] = df.Recon.map(RECON_TO_FEASIBILITY)

    if merged is None:
        merged = df
    else:
        merged = merged.append(df, ignore_index=True, sort=False)

df = merged

print("Projecting dams...")
# Drop dams without locations and project
df = df.loc[df.geometry.notnull()].copy().to_crs(CRS).reset_index(drop=True)

print("Merged {:,} dams in SARP states".format(len(df)))

ix = df.SARPID.isnull()
if ix.max():
    print(
        "--------------------------\nWARNING: {:,} dams are missing SARPID\n----------------------------".format(
            ix.sum()
        )
    )

# DEBUG ONLY - SARPID must be present; follow up with SARP if not
df.SARPID = df.SARPID.fillna("").astype("str")

df.to_feather(out_dir / "sarp_dams.feather")


### Download manually snapped dams
download_start = time()
print("---- Downloading Snapped Dams ----")
df = download_fs(
    SNAPPED_URL,
    fields=["SARPID", "ManualReview"],
    token=token,
)

print("Projecting manually snapped dams...")
df = df.loc[df.geometry.notnull()].to_crs(CRS).reset_index(drop=True)

print(
    "Downloaded {:,} snapped dams in {:.2f}s".format(len(df), time() - download_start)
)

df.ManualReview = df.ManualReview.fillna(0).astype("uint8")
df.to_feather(out_dir / "manually_snapped_dams.feather")

### Download small barriers
download_start = time()
print("---- Downloading Small Barriers ----")
df = download_fs(SMALL_BARRIERS_URL, fields=SMALL_BARRIER_COLS, token=token).rename(
    columns={
        "Crossing_Code": "CrossingCode",
        "Potential_Project": "PotentialProject",
        "SARPUniqueID": "SARPID",
        "CrossingTypeId": "CrossingType",
        "RoadTypeId": "RoadType",
        "CrossingConditionId": "Condition",
        "StreamName": "Stream",
    }
)

print("Projecting small barriers...")
df = df.loc[df.geometry.notnull()].to_crs(CRS).reset_index(drop=True)

print(
    "Downloaded {:,} small barriers in {:.2f}s".format(len(df), time() - download_start)
)

ix = df.SARPID.isnull()
if ix.max():
    print(
        "--------------------------\nWARNING: {:,} small barriers are missing SARPID\n----------------------------".format(
            ix.sum()
        )
    )

# DEBUG ONLY - SARPID must be present; follow up with SARP if not
df.SARPID = df.SARPID.fillna("").astype("str")

df.to_feather(out_dir / "sarp_small_barriers.feather")


### Download waterfalls
download_start = time()
print("---- Downloading waterfalls ----")
df = download_fs(WATERFALLS_URL, fields=WATERFALL_COLS, token=token)

print("Projecting waterfalls.")
df = df.loc[df.geometry.notnull()].to_crs(CRS).reset_index(drop=True)

df = df.rename(
    columns={"gnis_name_": "GNIS_Name", "watercours": "Stream", "name": "Name"}
)


print("Downloaded {:,} waterfalls in {:.2f}s".format(len(df), time() - download_start))


df.to_feather(out_dir / "waterfalls.feather")


print("---------------\nAll done in {:.2f}s".format(time() - start))
