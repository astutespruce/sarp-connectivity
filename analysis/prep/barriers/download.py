import asyncio
import os
from pathlib import Path
from time import time

from dotenv import load_dotenv
import httpx
import pandas as pd
import numpy as np

from analysis.constants import (
    DAM_FS_COLS,
    CRS,
    SMALL_BARRIER_COLS,
    WATERFALL_COLS,
)
from analysis.prep.barriers.lib.arcgis import download_fs


# Load the token from the .env file in the root of this project
load_dotenv()
TOKEN = os.getenv("AGOL_TOKEN", None)
if not TOKEN:
    raise ValueError("AGOL_TOKEN must be defined in your .env file")


SNAPPED_URL = "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Dam_Snapping_QA_Dataset_01212020/FeatureServer/0"
SMALL_BARRIERS_URL = "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/All_RoadBarriers_01212019/FeatureServer/0"
WATERFALLS_URL = "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/SARP_Waterfall_Database_01212020/FeatureServer/0"

# National dams URL
DAMS_URL = "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/National_Aquatic_Barrier_Inventory_Dams_Compilation_03202023/FeatureServer/0"

# Root URLS of feature service
DAM_URLS = {
    "AL": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/Alabama_Dam_Inventory_11_15_2018/FeatureServer/0",
    "AR": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/Arkansas_Dam_Inventory_11122018/FeatureServer/0",
    "AZ": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Arizona_Dam_Inventory_03052021/FeatureServer/1",
    "CO": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Colorado_Dam_Inventory_03052021/FeatureServer/0",
    "FL": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/Florida_Dam_Inventory_Jan112019/FeatureServer/0",
    "GA": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/R4_Georgia_Dam_Inventory_12_14_2018/FeatureServer/0",
    "IA": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Iowa_Dam_Inventory_03052021/FeatureServer/1",
    "ID": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Idaho_Dam_Inventory_03022022/FeatureServer/0",
    "KS": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Kansas_Dam_Inventory_03052021/FeatureServer/1",
    "KY": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/R4_Kentucky_Dam_Inventory_12_01_2018/FeatureServer/0",
    "LA": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/LouisianaDams/FeatureServer/0",
    "MO": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/MissouriDams/FeatureServer/0",
    "MS": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/Mississippi_Dam_Inventory_11192018/FeatureServer/0",
    "MT": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Montana_Dam_Inventory_03052021/FeatureServer/1",
    "NC": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/North_Carolina_Dam_Inventory_03252019/FeatureServer/0",
    "ND": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/North_Dakota_Dam_Inventory_03052021/FeatureServer/0",
    "NE": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Nebraska_Dam_Inventory_03052021/FeatureServer/1",
    "NM": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/New_Mexico_Dam_Inventory_03052021/FeatureServer/1",
    "OK": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/OklahomaDams/FeatureServer/0",
    "OR": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Oregon_Dam_Inventory_03022022/FeatureServer/0",
    "PR": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Puerto_Rico_Dam_Inventory_12202019/FeatureServer/0",
    "SC": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/R4_South_Carolina_Dam_Inventory_2018/FeatureServer/0",
    "SD": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/South_Dakota_Dam_Inventory_03052021/FeatureServer/1",
    "TN": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/Tennessee_Dam_Inventory_11_15_2018/FeatureServer/0",
    "TX": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/TexasDams/FeatureServer/0",
    "UT": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Utah_Dam_Inventory_03052021/FeatureServer/1",
    "VA": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/Virginia_Dam_Inventory_11_12_2018/FeatureServer/0",
    "VI": "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/USVI_Dam_Inventory_01242023/FeatureServer/0",
    "WA": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Washington_Dam_Inventory_03022022/FeatureServer/0",
    "WV": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/WV_Dams_SARP_03142022/FeatureServer/0",
    "WY": "https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Wyoming_Dam_Inventory_03052021/FeatureServer/1",
}


async def download_national_dams(token):
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0, connect=60.0), http2=True
    ) as client:
        df = await download_fs(client, DAMS_URL, fields=DAM_FS_COLS, token=token)

        df = df.rename(
            columns={
                "SARPUniqueID": "SARPID",
                "PotentialFeasibility": "Feasibility",
                "Barrier_Name": "Name",
                "Other_Barrier_Name": "OtherName",
                "DB_Source": "Source",
                "Year_Completed": "YearCompleted",
                "Year_Removed": "YearRemoved",
                "ConstructionMaterial": "Construction",
                "PurposeCategory": "Purpose",
                "StructureCondition": "Condition",
                "LowheadDam1": "LowheadDam",
                "OwnerType": "BarrierOwnerType",
                "StateAbbreviation": "SourceState",
            }
        )

    return df


async def download_dams_for_state(client, state, token):
    df = await download_fs(client, DAM_URLS[state], fields=DAM_FS_COLS, token=token)

    df = df.rename(
        columns={
            "SARPUniqueID": "SARPID",
            "Snap2018": "Snap2018",
            "SNAP2018": "Snap2018",
            "PotentialFeasibility": "Feasibility",
            "Barrier_Name": "Name",
            "Other_Barrier_Name": "OtherName",
            "DB_Source": "Source",
            "Year_Completed": "YearCompleted",
            "Year_Removed": "YearRemoved",
            "ConstructionMaterial": "Construction",
            "PurposeCategory": "Purpose",
            "StructureCondition": "Condition",
            "LowheadDam1": "LowheadDam",
            "OwnerType": "BarrierOwnerType",
        }
    )

    # NC only has SNAP2018 and ManualReview; only use ManualReview
    if "ManualReview" in df.columns and "Snap2018" in df.columns:
        df = df.drop(columns=["Snap2018"])

    df = df.rename(columns={"Snap2018": "ManualReview"})

    df["SourceState"] = state

    # Add feasibility so that we can merge
    if "Feasibility" not in df.columns:
        # we backfill this later
        df["Feasibility"] = np.nan

    return df


async def download_state_dams(token):
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0, connect=60.0),
        http2=True,
    ) as client:
        tasks = [
            asyncio.ensure_future(download_dams_for_state(client, state, token))
            for state in DAM_URLS
        ]
        completed = await asyncio.gather(*tasks)

        merged = None
        for df in completed:
            if merged is None:
                merged = df
            else:
                merged = pd.concat([merged, df], ignore_index=True, sort=False)

        return merged.to_crs(CRS)


async def download_snapped_dams(token):
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0, connect=60.0), http2=True
    ) as client:
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
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0, connect=60.0), http2=True
    ) as client:
        df = await download_fs(
            client, SMALL_BARRIERS_URL, fields=SMALL_BARRIER_COLS, token=token
        )

        df = df.rename(
            columns={
                "Crossing_Code": "CrossingCode",
                "Potential_Project": "PotentialProject",
                "SARPUniqueID": "SARPID",
                "CrossingTypeId": "CrossingType",
                "RoadTypeId": "RoadType",
                "CrossingConditionId": "Condition",
                "StreamName": "Stream",
                "Year_Removed": "YearRemoved",
                "OwnerType": "BarrierOwnerType",
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


async def download_waterfalls(token):
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0, connect=60.0), http2=True
    ) as client:
        df = await download_fs(
            client, WATERFALLS_URL, fields=WATERFALL_COLS, token=token
        )
        df = df.rename(
            columns={
                "SARPUniqueId": "SARPID",
                "gnis_name_": "GNIS_Name",
                "watercours": "Stream",
                "name": "Name",
            }
        )
        df = df.loc[df.geometry.notnull()].to_crs(CRS).reset_index(drop=True)

        return df


out_dir = Path("data/barriers/source")

start = time()

### Download national dams
print("\n---- Downloading National Dams ----")
download_start = time()
natl_df = asyncio.run(download_national_dams(TOKEN))
print(f"Downloaded {len(natl_df):,} dams in {time() - download_start:.2f}s")


## Download and merge state feature services
print("\n---- Downloading State Dams ----")
download_start = time()
state_df = asyncio.run(download_state_dams(TOKEN))
print(
    f"Downloaded {len(state_df):,} state-level dams in {time() - download_start:.2f}s"
)

ix = state_df.geometry.isnull()
if ix.sum():
    print(f"WARNING: {ix.sum()} dams are missing geometry values")
    print(state_df.loc[ix].groupby("SourceState").size())
    print("SARPIDs:", state_df.loc[ix].SARPID.unique().tolist())
    df = state_df.loc[~ix].copy()
    print("\n")

print("Merging and projecting dams...")
df = pd.concat(
    [natl_df.to_crs(CRS), state_df.to_crs(CRS)], ignore_index=True, sort=False
).reset_index(drop=True)

ix = df.SARPID.isnull() | (df.SARPID == "")
if ix.max():
    print(
        f"--------------------------\nWARNING: {ix.sum():,} dams are missing SARPID\n----------------------------"
    )
    print(df.loc[ix].groupby("SourceState").size())

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


# ### Download waterfalls
download_start = time()
print("\n---- Downloading waterfalls ----")
df = asyncio.run(download_waterfalls(TOKEN))
print(f"Downloaded {len(df):,} waterfalls in {time() - download_start:.2f}s")

df.to_feather(out_dir / "waterfalls.feather")


print(f"---------------\nAll done in {time() - start:.2f}s")
