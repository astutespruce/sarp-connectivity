from pathlib import Path
import warnings

from pyogrio import read_dataframe, write_dataframe

from analysis.constants import (
    CRS,
    DAM_FS_COLS,
)

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
src_dir = data_dir / "barriers/source"


### Read NID + NE TNC data, and standardize to internal structure
df = (
    read_dataframe(src_dir / "OuterHUC4_Dams_2022.gdb", layer="NEW_NID_OUTERHUC4_2022")
    .to_crs(CRS)
    .set_index("NIDID")
)
cols = [c for c in df.columns if c in DAM_FS_COLS]
df = df[cols + ["geometry"]].rename(
    columns={
        "SARPUniqueID": "SARPID",
        "PotentialFeasibility": "Feasibility",
        "Barrier_Name": "Name",
        "Other_Barrier_Name": "OtherName",
        "DB_Source": "Source",
        "Year_Completed": "Year",
        "Year_Removed": "YearRemoved",
        "ConstructionMaterial": "Construction",
        "PurposeCategory": "Purpose",
        "StructureCondition": "Condition",
    }
)
df["ManualReview"] = 0
df["SourceState"] = df.SARPID.str[:2]

df.to_feather(src_dir / "dams_outer_huc4.feather")
write_dataframe(df, src_dir / "dams_outer_huc4.fgb")

