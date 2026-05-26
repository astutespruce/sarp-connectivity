from pathlib import Path

import pandas as pd

src_dir = Path("data/barriers/source")

df = pd.read_excel(
    src_dir / "sarp_dam_costpred_V2.xlsx",
    engine="calamine",
    usecols=[
        "SARPID",
        "MeanCost",
        "50%PredictionInterval_UpperBound",
        "50%PredictionInterval_LowerBound",
        "DamHt_m",
        "OutOfBoundPrediction_HtDis",
        "OutOfBoundPrediction_All",
    ],
).rename(
    columns={
        "MeanCost": "CostMean",
        "50%PredictionInterval_UpperBound": "CostUpper",
        "50%PredictionInterval_LowerBound": "CostLower",
    }
)

df["CostOutOfBounds"] = (df.OutOfBoundPrediction_HtDis == "yes") | (df.OutOfBoundPrediction_All == "yes")
df = df.drop(columns=["OutOfBoundPrediction_HtDis", "OutOfBoundPrediction_All"])

df.to_feather(src_dir / "sarp_dam_costpred_v2.feather")
