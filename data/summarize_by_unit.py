from collections import defaultdict
import csv
import json
import pandas as pd
import geopandas as gp


# TODO: derive other HUCs from HUC12 if they don't already exist
df = pd.read_csv(
    "data/src/dams.csv",
    dtype={
        "HUC2": str,
        "HUC4": str,
        "HUC6": str,
        "HUC8": str,
        "HUC10": str,
        "HUC12": str,
        "ECO3": str,
        "ECO4": str,
    },
)

stats = defaultdict(defaultdict)

# Group by state, HUC level, ecoregion level
for unit in ("State", "HUC2", "HUC4", "HUC6", "HUC8", "HUC10", "ECO3", "ECO4"):
    group_cols = [unit]
    # TODO: only needed if we are extracting out subregions based on some higher order ID
    # if unit == "HUC4":
    #     group_cols.append("HUC2")
    # elif unit == "HUC8":
    #     group_cols.extend(["HUC4", "HUC2"])
    # elif unit == "ECO4":
    #     group_cols.append("ECO3")

    g = (
        df.groupby(group_cols)
        .agg({"UniqueID": "count", "AbsoluteGainMi": "mean"})
        .rename(columns={"UniqueID": "dams", "AbsoluteGainMi": "connectedmiles"})
    )

    g.to_csv(
        "data/summary/{}.csv".format(unit),
        index_label=["id"] + group_cols[1:],
        quoting=csv.QUOTE_NONNUMERIC,
    )

    level_stats = g.agg(["min", "max"])
    for col in g.columns:
        stats[unit][col] = {"range": level_stats[col].tolist(), "mean": g[col].mean()}

stats["sarp"] = {"dams": len(df), "connectedmiles": df["AbsoluteGainMi"].mean()}

with open("ui/src/data/summary_stats.json", "w") as outfile:
    outfile.write(json.dumps(stats))
