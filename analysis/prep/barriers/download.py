import os
from pathlib import Path
from time import time
from dotenv import load_dotenv
import requests

from nhdnet.io import serialize_gdf, to_shp

from analysis.constants import (
    SARP_STATES,
    RECON_TO_FEASIBILITY,
    DAM_COLS,
    CRS,
    SMALL_BARRIER_COLS,
)
from analysis.prep.barriers.lib.arcgis import download_fs, list_services

# Load the token from the .env file in the root of this project
load_dotenv()
token = os.getenv("AGOL_TOKEN", None)
if not token:
    raise ValueError("AGOL_TOKEN must be defined in your .env file")

# TODO:
# Puerto Rico:  https://arcg.is/1qLnOP

TARGET_WKID = 102003


SNAPPED_URL = "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/All_Dams_Snapped_For_Editing_Feb42019/FeatureServer/0"
SMALL_BARRIERS_URL = "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/All_RoadBarriers_01212019/FeatureServer/0"


### When needed: generate list of dam inventory services
# Root services URL for USFWS R4
# ROOT_URL = "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/"
# services = [
#     s["url"]
#     for s in list_services(ROOT_URL, token=token)
#     if s["type"] == "FeatureServer"
# ]
#
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
}


out_dir = Path("data/barriers/source")

start = time()

# ### Download and merge state feature services
# merged = None
# # Services have varying casing of SNAP2018
# dam_cols = DAM_COLS + ["Snap2018"]
# for state, url in DAM_URLS.items():
#     download_start = time()

#     print("---- Downloading {} ----".format(state))
#     df = download_fs(url, fields=dam_cols, token=token, target_wkid=TARGET_WKID).rename(
#         columns={
#             "Snap2018": "SNAP2018",
#             "PotentialFeasibility": "Feasibility",
#             "Barrier_Name": "Name",
#             "Other_Barrier_Name": "OtherName",
#             "DB_Source": "Source",
#             "Year_Completed": "Year",
#             "ConstructionMaterial": "Construction",
#             "PurposeCategory": "Purpose",
#             "StructureCondition": "Condition",
#         }
#     )
#     df["SourceState"] = state
#     print("Downloaded {:,} dams in {:.2f}s".format(len(df), time() - download_start))

#     # Add feasibility so that we can merge
#     if not "Feasibility" in df.columns:
#         df["Feasibility"] = df.Recon.map(RECON_TO_FEASIBILITY)

#     if merged is None:
#         merged = df
#     else:
#         merged = merged.append(df, ignore_index=True, sort=False)

# df = merged

# print("Projecting dams...")
# # Drop dams without locations and project
# df = df.loc[df.geometry.notnull()].copy().to_crs(CRS)


# print("Merged {:,} dams in SARP states".format(len(df)))
# serialize_gdf(df, out_dir / "sarp_dams.feather")


# ### Download manually snapped dams
# download_start = time()
# print("---- Downloading Snapped Dams ----")
# df = download_fs(SNAPPED_URL, fields=["AnalysisID", "SNAP2018"], token=token, target_wkid=TARGET_WKID)

# print("Projecting manually snapped dams...")
# df = df.loc[df.geometry.notnull()].to_crs(CRS)

# print(
#     "Downloaded {:,} snapped dams in {:.2f}s".format(len(df), time() - download_start)
# )

# df.SNAP2018 = df.SNAP2018.fillna(0).astype("uint8")
# serialize_gdf(df, out_dir / "manually_snapped_dams.feather")

### Download small barriers
download_start = time()
print("---- Downloading Small Barriers ----")
df = download_fs(
    SMALL_BARRIERS_URL, fields=SMALL_BARRIER_COLS, token=token, target_wkid=TARGET_WKID
).rename(
    columns={
        "Crossing_Code": "CrossingCode",
        "OnConservationLand": "ProtectedLand",
        "Potential_Project": "PotentialProject",
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
    }
)

print("Projecting small barriers...")
df = df.loc[df.geometry.notnull()].to_crs(CRS)

print(
    "Downloaded {:,} small barriers in {:.2f}s".format(len(df), time() - download_start)
)

# df.SNAP2018 = df.SNAP2018.fillna(0).astype("uint8")
serialize_gdf(df, out_dir / "sarp_small_barriers.feather")


print("---------------\nAll done in {:.2f}s".format(time() - start))
