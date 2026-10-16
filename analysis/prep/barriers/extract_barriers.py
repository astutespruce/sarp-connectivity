from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import shapely
from pyogrio import list_layers, read_arrow, read_dataframe

from analysis.constants import CRS

# NOTE: where there are different source fields that would be renamed to the same
# target field differently between barrier types, we add barrier type prefix
# below and rename them again for that specific type later
rename_columns = {
    # common fields
    "SARPUniqueID": "SARPID",
    "UNIQUE_ID": "PartnerID",
    "Link": "SourceLink",
    "Barrier_Name": "Name",
    "Other_Barrier_Name": "OtherName",
    "StreamName": "River",
    "ConstructionMaterial": "Construction",
    "PotentialFeasibility": "Feasibility",
    "Year_Removed": "YearRemoved",
    "OwnerType": "BarrierOwnerType",
    "Year_Reconned": "YearSurveyed",
    "Active150": "ActiveList",
    "Priority_Identified": "IsPriority",
    # dam specific fields
    "FEDERAL_ID": "NIDFederalID",
    "FERC_Dam": "FERCRegulated",
    "NRCS_Dam": "NRCSDam",
    "Fed_Regulatory_Agency": "FedRegulatoryAgency",
    "STATE_REGULATED": "StateRegulated",
    "Water_Right": "WaterRight",
    "Water_Right_Status": "WaterRightStatus",
    "Beneficial_Use": "BeneficialUse",
    "HEIGHT": "Height",
    "WIDTH": "Width",
    "LENGTH": "Length",
    "NORMSTOR": "StorageVolume",
    "Dam_EAP": "EmergencyActionPlan",
    "PurposeCategory": "Purpose",
    "LowheadDam1": "LowheadDam",
    "YEAR_COMPLETED": "YearCompleted",
    # waterfall specific fields
    "fall_type": "FallType",
    # crossing specific fields
    "Crossing_Code": "CrossingCode",
    "CrossingTypeId": "CrossingType",
    "RoadTypeId": "RoadType",
    "Potential_Project": "PotentialProject",
    "Protocol_Used": "ProtocolUsed",
}

dam_columns = [
    "SARPID",
    "Source",
    "SourceID",
    "SourceLink",
    "Private",
    "PartnerID",
    "NIDID",
    "NIDFederalID",
    "Name",
    "OtherName",
    "River",
    "Height",
    "Width",
    "Length",
    "StructureCategory",
    "StructureClass",
    "Purpose",
    "BarrierOwnerType",
    "Hazard",
    "ImpoundmentType",
    "BarrierStatus",
    "Condition",
    "Construction",
    "PassageFacility",
    "Feasibility",
    "Recon",
    "Recon2",
    "Recon3",
    "InvasiveSpecies",
    "YearCompleted",
    "YearRemoved",
    "YearFishPass",
    "Diversion",
    "FishScreen",
    "ScreenType",
    "BarrierSeverity",
    "LowheadDam",
    "FERCRegulated",
    "FedRegulatoryAgency",
    "StateRegulated",
    "Regulatory_Agency",
    "WaterRight",
    "WaterRightStatus",
    "BeneficialUse",
    "ManualReview",
    "Last_Updated",
    "IsPriority",
    "StorageVolume",
    "Fatality",
    "NRCSDam",
    "ActiveList",
    "KeepOnActiveList",
    "YearSurveyed",
    "RelicensingDate",
    "EmergencyActionPlan",
    "QAQC_Date",
]

waterfall_columns = [
    "SARPID",
    "Source",
    "SourceID",
    "SourceLink",
    "Private",
    "PartnerID",
    "FallType",
    "River",
    "Name",
    "Recon",
    "ManualReview",
    "BarrierSeverity",
    "YearRemoved",
    "QAQC_Date",
]


small_barrier_columns = [
    "SARPID",
    "Source",
    "SourceID",
    "SourceLink",
    "Private",
    "PartnerID",
    "SurveyID",
    "Recon",
    "ManualReview",
    "CrossingCode",
    "River",
    "Road",
    "RoadType",
    "CrossingType",
    "Condition",
    "PotentialProject",
    "SARP_Score",
    "SE_AOP",
    "ProtocolUsed",
    "YearRemoved",
    "YearFishPass",
    "BarrierOwnerType",
    "Constriction",
    "PassageFacility",
    "IsPriority",
    "ActiveList",
    "KeepOnActiveList",
    "YearSurveyed",
    "Resurveyed",
    "QAQC_Date",
]


data_version = "10_09_2026"


src_dir = Path("data/barriers/source")

gdb = src_dir / f"NABI_input_{data_version}.gdb"
layers = list_layers(gdb)[:, 0].tolist()
public_layer = next(l for l in layers if "MASTER" in l)
private_layer = next(l for l in layers if "PRIVATE" in l)

### Extract domains
# to get domains, we have to use the arrow table schema
table = read_arrow(gdb, layer=public_layer, max_features=1)[1]
dict_fields = [f for f in table.schema if pa.types.is_dictionary(f.type)]
domains = {}
for f in dict_fields:
    values = table[f.name].chunk(0).dictionary
    indexes = np.arange(len(values))
    domains[f.name] = dict(np.dstack([indexes, values])[0])


# use_arrow doesn't work because of issues with domains
df = read_dataframe(gdb, layer=public_layer)
df["geometry"] = shapely.force_2d(df.geometry.values)
df = df.to_crs(CRS)
ix = df.geometry.isnull()
if ix.any():
    print(f"WARNING: {ix.sum()} public barriers are missing geometry values")
    df = df.loc[~ix].copy()

s = df.groupby("SARPUniqueID").size()
ids = s[s > 1].index
if len(ids):
    print(f"WARNING: multiple public with same SARPID: {', '.join(ids)}")


private_df = read_dataframe(gdb, layer=private_layer)
private_df["geometry"] = shapely.force_2d(private_df.geometry.values)
private_df = private_df.to_crs(CRS)
ix = private_df.geometry.isnull()
if ix.any():
    print(f"WARNING: {ix.sum()} private barriers are missing geometry values")
    private_df = private_df.loc[~ix].copy()

s = private_df.groupby("SARPUniqueID").size()
ids = s[s > 1].index
if len(ids):
    print(f"WARNING: multiple private barriers with same SARPID: {', '.join(ids)}")


df["Private"] = False
private_df["Private"] = True

df = pd.concat([df, private_df], ignore_index=True).rename(columns=rename_columns)

### Assign barrier type based on SARPID
# dams: <state_abbrev><number>, P_<state_abbrev><number>
# road_crossings: sm<number>, P_sm<number>, P<number>
# waterfalls: f<number>, P_f<number>
dams_ix = df.SARPID.str.match(r"[A-Z][A-Z]\d+|P_[A-Z][A-Z]\d+")
small_barriers_ix = df.SARPID.str.match(r"sm\d+|P\d+|P_sm\d+")
waterfalls_ix = df.SARPID.str.match(r"f\d+|P_f\d+")

df.loc[dams_ix, "BarrierType"] = "dams"
df.loc[small_barriers_ix, "BarrierType"] = "small_barriers"
df.loc[waterfalls_ix, "BarrierType"] = "waterfalls"

missing_ix = df.BarrierType.isnull()
if missing_ix.any():
    raise ValueError(f"did not assign barrier type to SARPIDs: {df.loc[missing_ix].SARPID.values.tolist()[:100]}...")


### cleanup common fields
df["QAQC_Date"] = pd.to_datetime(df.QAQC_Date).dt.strftime("%m/%d/%Y").fillna("")


### Extract dams
dams = (
    df.loc[df.BarrierType == "dams"]
    .reset_index(drop=True)
    .drop(columns=["Source"])
    .rename(columns={"SourceDBID": "SourceID", "DB_Source": "Source", "StructureCondition": "Condition"})
)
missing = [c for c in dam_columns if c not in dams.columns]
if len(missing):
    raise ValueError(f"dams are missing columns: {', '.join(missing)}")

dams[dam_columns + ["geometry"]].to_feather(src_dir / "sarp_dams.feather")

### Extract waterfalls
waterfalls = df.loc[df.BarrierType == "waterfalls"].reset_index(drop=True).rename(columns={"LocalID": "SourceID"})
missing = [c for c in waterfall_columns if c not in waterfalls.columns]
if len(missing):
    raise ValueError(f"waterfalls are missing columns: {', '.join(missing)}")

waterfalls[waterfall_columns + ["geometry"]].to_feather(src_dir / "waterfalls.feather")


### Extract surveyed road crossings
small_barriers = (
    df.loc[df.BarrierType == "small_barriers"]
    .reset_index(drop=True)
    .rename(
        columns={
            "LocalID": "SourceID",
            "CrossingConditionId": "Condition",
        }
    )
)
missing = [c for c in small_barrier_columns if c not in small_barriers.columns]
if len(missing):
    raise ValueError(f"small b arriers are missing columns: {', '.join(missing)}")

small_barriers[small_barrier_columns + ["geometry"]].to_feather(src_dir / "sarp_small_barriers.feather")
