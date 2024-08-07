from pathlib import Path

import pandas as pd

src_dir = Path("data/barriers/source")

cost = pd.read_excel(
    src_dir / "sarp_dam_costpred_V2.xlsx",
    engine="calamine",
    usecols=["SARPID", "MeanCost", "95%PredictionInterval_UpperBound", "95%PredictionInterval_LowerBound", "DamHt_m"],
).rename(
    columns={
        "MeanCost": "CostMean",
        "95%PredictionInterval_UpperBound": "CostUpper",
        "95%PredictionInterval_LowerBound": "CostLower",
    }
)

cost.to_feather(src_dir / "sarp_dam_costpred_v2.feather")
