import asyncio
import os
from pathlib import Path
from time import time

from dotenv import load_dotenv
import httpx
import numpy as np
import pandas as pd
import shapely

from analysis.constants import (
    DAM_FS_COLS,
    CRS,
    SMALL_BARRIER_COLS,
    WATERFALL_COLS,
)
from analysis.prep.barriers.lib.arcgis import download_fs, get_attachments


# Load the token from the .env file in the root of this project
load_dotenv()
TOKEN = os.getenv("AGOL_TOKEN", None)
if not TOKEN:
    raise ValueError("AGOL_TOKEN must be defined in your .env file")


DAMS_URL = "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Dams_National_Aquatic_Barrier_Inventory_Dec_2023/FeatureServer/0"
SNAPPED_URL = (
    "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Dam_Snapping_QA_Dataset_01212020/FeatureServer/0"
)
SMALL_BARRIERS_URL = (
    "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/All_RoadBarriers_01212019/FeatureServer/0"
)
WATERFALLS_URL = (
    "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/SARP_Waterfall_Database_01212020/FeatureServer/0"
)
SMALL_BARRIER_SURVEY_URLS = {
    "Southeast (inland)": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/service_27160a30499e47ad8a33b641b2fb6b97/FeatureServer/0",
    "Southeast (tidal)": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/service_e2b2b49c4126467eac1d77069e33820f/FeatureServer/0",
    "Southeast (pre 2019)": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/SARP_AOP_Road_Crossings_PriorTo2019/FeatureServer/0",
    "Southeast (coarse)": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/service_4b226787a3464f478602431383498138/FeatureServer/0",
    "Western (inland)": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/service_1da663f4b2ff45aeadbf5568829f40f6/FeatureServer/0",
}


async def download_dams(token):
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=60.0), http2=True) as client:
        df = await download_fs(client, DAMS_URL, fields=DAM_FS_COLS, token=token)

        df = df.rename(
            columns={
                "SARPUniqueID": "SARPID",
                "SourceDBID": "SourceID",
                "UNIQUE_ID": "PartnerID",
                "FEDERAL_ID": "NIDFederalID",
                "PotentialFeasibility": "Feasibility",
                "Barrier_Name": "Name",
                "Other_Barrier_Name": "OtherName",
                "DB_Source": "Source",
                "RIVER": "River",
                "YEAR_COMPLETED": "YearCompleted",
                "Year_Removed": "YearRemoved",
                "ConstructionMaterial": "Construction",
                "PurposeCategory": "Purpose",
                "StructureCondition": "Condition",
                "LowheadDam1": "LowheadDam",
                "OwnerType": "BarrierOwnerType",
                "StateAbbreviation": "SourceState",
                "FERC_Dam": "FERCRegulated",
                "Fed_Regulatory_Agency": "FedRegulatoryAgency",
                "STATE_REGULATED": "StateRegulated",
                "Water_Right": "WaterRight",
                "Water_Right_Status": "WaterRightStatus",
                "Beneficial_Use": "BeneficialUse",
                "HEIGHT": "Height",
                "WIDTH": "Width",
                "LENGTH": "Length",
                "Priority_Identified": "IsPriority",
                "NORMSTOR": "StorageVolume",
            }
        )

        print("Projecting dams...")

        df = df.to_crs(CRS)

        return df


async def download_snapped_dams(token):
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=60.0), http2=True) as client:
        df = await download_fs(
            client,
            SNAPPED_URL,
            fields=[
                "SARPID",
                "ManualReview",
                "dropped",
                "excluded",
                "duplicate",
                "snapped",
                "EditDate",
                "Editor",
            ],
            token=token,
        )

        print("Projecting manually snapped dams...")
        df = df.loc[df.geometry.notnull()].to_crs(CRS).reset_index(drop=True)

        # drop any that do not have SARPID
        df = df.dropna(subset=["SARPID"])

        df.ManualReview = df.ManualReview.fillna(0).astype("uint8")

        # dates are either blank or strings MM/DD/YYYY
        df["EditDate"] = df.EditDate.str.strip()

        return df


async def download_small_barriers(token):
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=60.0), http2=True) as client:
        df = await download_fs(client, SMALL_BARRIERS_URL, fields=SMALL_BARRIER_COLS, token=token)

        # fill missing fields
        missing = [c for c in SMALL_BARRIER_COLS if c not in df.columns]
        if len(missing):
            print(f"Download is missing columns: {', '.join(missing)}")
            for col in missing:
                df[col] = np.nan

        df = df.rename(
            columns={
                "LocalID": "SourceID",
                "UNIQUE_ID": "PartnerID",
                "Crossing_Code": "CrossingCode",
                "Potential_Project": "PotentialProject",
                "SARPUniqueID": "SARPID",
                "CrossingTypeId": "CrossingType",
                "RoadTypeId": "RoadType",
                "CrossingConditionId": "Condition",
                "StreamName": "River",
                "Year_Removed": "YearRemoved",
                "OwnerType": "BarrierOwnerType",
                "Protocol_Used": "ProtocolUsed",
            }
        )

        # convert from ESRI format to string
        df["EditDate"] = pd.to_datetime(df.EditDate, unit="ms").dt.strftime("%m/%d/%Y")

        ix = df.geometry.isnull()
        if ix.sum():
            print(f"WARNING: {ix.sum()} small barriers are missing geometry values")
            df = df.loc[~ix].copy()

        df = df.to_crs(CRS).reset_index(drop=True)

        return df


async def download_small_barrier_survey_photo_urls(token):
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=60.0), http2=True) as client:
        merged = None
        for id, survey_url in SMALL_BARRIER_SURVEY_URLS.items():
            print(f"Downloading attachments from: {id}")
            df = await download_fs(
                client,
                survey_url,
                fields=["OBJECTID" if id == "Southeast (pre 2019)" else "objectid", "Crossing_Code", "DateObserved"],
                token=token,
            )

            df = df.rename(columns={"OBJECTID": "objectid"})

            # convert from ESRI format to string
            df["DateObserved"] = pd.to_datetime(df.DateObserved, unit="ms").dt.strftime("%m/%d/%Y")

            # drop duplicates
            df = df.loc[df.geometry != shapely.Point(0, 0)].drop_duplicates(subset="geometry")

            attachments = await get_attachments(client, survey_url, token)
            df = df.join(attachments, on="objectid", how="inner").drop(columns=["objectid"])
            df["source"] = id

            if merged is None:
                merged = df
            else:
                merged = pd.concat([merged, df], ignore_index=True)

        return merged.to_crs(CRS)


async def download_waterfalls(token):
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=60.0), http2=True) as client:
        df = await download_fs(client, WATERFALLS_URL, fields=WATERFALL_COLS, token=token)
        df = df.rename(
            columns={
                "SARPUniqueId": "SARPID",
                "LocalID": "SourceID",
                "UNIQUE_ID": "PartnerID",
                "gnis_name_": "GNIS_Name",
                "watercours": "River",
                "name": "Name",
                "Year_Removed": "YearRemoved",
            }
        )
        df = df.loc[df.geometry.notnull()].to_crs(CRS).reset_index(drop=True)

        # gnis_name_ may be completely null and thus dropped during download,
        # but GNIS_Name is used during prep and needs to be present
        if "GNIS_Name" not in df.columns:
            df["GNIS_Name"] = ""

        return df


out_dir = Path("data/barriers/source")

start = time()

### Download national dams
print("\n---- Downloading National Dams ----")
download_start = time()
df = asyncio.run(download_dams(TOKEN))
print(f"Downloaded {len(df):,} dams in {time() - download_start:.2f}s")

ix = df.SARPID.isnull() | (df.SARPID == "")
if ix.any():
    print(f"--------------------------\nWARNING: {ix.sum():,} dams are missing SARPID\n----------------------------")
    print(df.loc[ix].groupby("SourceState", dropna=False).size())

# DEBUG ONLY - SARPID must be present; follow up with SARP if not
df.SARPID = df.SARPID.fillna("").astype("str")


s = df.groupby("SARPID").size()
if s.max() > 1:
    print("WARNING: multiple dams with same SARPID")
    print(s[s > 1])

# convert from ESRI format to string
df["EditDate"] = pd.to_datetime(df.EditDate, unit="ms").dt.strftime("%m/%d/%Y")

df.to_feather(out_dir / "sarp_dams.feather")


# ### Download manually snapped dams
print("\n---- Downloading Snapped Dams ----")
download_start = time()
df = asyncio.run(download_snapped_dams(TOKEN))
print(f"Downloaded {len(df):,} snapped dams in {time() - download_start:.2f}s")

s = df.groupby("SARPID").size()
if s.max() > 1:
    print("WARNING: multiple dams with same SARPID in snapped dataset")
    print(s[s > 1])

df.to_feather(out_dir / "manually_snapped_dams.feather")

### Download small barriers
print("\n---- Downloading Small Barriers ----")
download_start = time()
df = asyncio.run(download_small_barriers(TOKEN))
print(f"Downloaded {len(df):,} small barriers in {time() - download_start:.2f}s")

ix = df.SARPID.isnull() | (df.SARPID == "")
if ix.max():
    print(
        f"--------------------------\nWARNING: {ix.sum():,} small barriers are missing SARPID\n----------------------------"
    )

# # DEBUG ONLY - SARPID must be present; follow up with SARP if not
df.SARPID = df.SARPID.fillna("").astype("str")

s = df.groupby("SARPID").size()
if s.max() > 1:
    print("WARNING: multiple small barriers with same SARPID")
    print(s[s > 1])

df.to_feather(out_dir / "sarp_small_barriers.feather")


### Download small barrier survey photo URLs
download_start = time()
df = asyncio.run(download_small_barrier_survey_photo_urls(TOKEN))
print(f"Downloaded {len(df):,} small records with photo URLs in {time() - download_start:.2f}s")

df.to_feather(out_dir / "sarp_small_barrier_survey_urls.feather")


### Download waterfalls
download_start = time()
print("\n---- Downloading waterfalls ----")
df = asyncio.run(download_waterfalls(TOKEN))
print(f"Downloaded {len(df):,} waterfalls in {time() - download_start:.2f}s")

ix = df.SARPID.isnull() | (df.SARPID == "")
if ix.max():
    print(
        f"--------------------------\nWARNING: {ix.sum():,} waterfalls are missing SARPID\n----------------------------"
    )

df.SARPID = df.SARPID.fillna("").astype("str")

s = df.groupby("SARPID").size()
if s.max() > 1:
    print(f"WARNING: {len(s[s > 1])} waterfalls with same SARPID")


df.to_feather(out_dir / "waterfalls.feather")


print(f"---------------\nAll done in {time() - start:.2f}s")
