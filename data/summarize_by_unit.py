from collections import defaultdict
import csv
import json
import pandas as pd
import geopandas as gp


# TODO: derive other HUCs from HUC12 if they don't already exist
df = pd.read_csv(
    "data/src/sarp_dams.csv",
    dtype={
        "HUC2": str,
        "HUC4": str,
        "HUC8": str,
        "HUC12": str,
        "ECO3": str,
        "ECO4": str,
    },
)

stats = defaultdict(defaultdict)
cols = ["dams", "connectedmiles"]

# Group by state, HUC level, ecoregion level
for unit in ("State", "HUC2", "HUC4", "HUC8", "ECO3", "ECO4"):
    group_cols = [unit]
    if unit == "HUC4":
        group_cols.append("HUC2")
    elif unit == "HUC8":
        group_cols.extend(["HUC4", "HUC2"])
    elif unit == "ECO4":
        group_cols.append("ECO3")

    g = df.groupby(group_cols).agg(
        {"UniqueID": {"dams": "count"}, "AbsoluteGainMi": {"connectedmiles": "mean"}}
    )

    g.to_csv(
        "data/summary/{}.csv".format(unit),
        header=["dams", "connectedmiles"],
        index_label=["id"] + group_cols[1:],
        quoting=csv.QUOTE_NONNUMERIC,
    )

    level_stats = g.agg(["min", "max"])
    level_stats.columns = cols
    for col in cols:
        stats[unit][col] = level_stats[col].tolist()


with open("ui/src/data/summary_stats.json", "w") as outfile:
    outfile.write(json.dumps(stats))
