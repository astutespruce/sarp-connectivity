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
        "Ecoregion3": str,
        "Ecoregion4": str,
    },
)

stats = defaultdict(defaultdict)
cols = ["dams", "connectedmiles"]

geo_join_lut = {
    "State": "NAME",
    "HUC2": "HUC2",
    "HUC4": "HUC4",
    "HUC8": "HUC8",
    "Ecoregion3": "NA_L3CODE",
    "Ecoregion4": "US_L4CODE",
}

# Group by state, HUC level, ecoregion level
for unit in ("State", "HUC2", "HUC4", "HUC8", "Ecoregion3", "Ecoregion4"):
    group_cols = [unit]
    if unit == "HUC4":
        group_cols.append("HUC2")
    elif unit == "HUC8":
        group_cols.extend(["HUC4", "HUC2"])

    g = df.groupby(group_cols).agg(
        {"UniqueID": {"dams": "count"}, "AbsoluteGainMi": {"connectedmiles": "mean"}}
    )

    index_cols = [geo_join_lut[unit]] + group_cols[1:]
    g.to_csv(
        "data/summary/{}.csv".format(unit),
        header=["dams", "connectedmiles"],
        index_label=[geo_join_lut[c] for c in group_cols],
        quoting=csv.QUOTE_NONNUMERIC,
    )

    level_stats = g.agg(["min", "max"])
    level_stats.columns = cols
    for col in cols:
        unit_key = unit.lower() if "Ecoregion" in unit else unit
        stats[unit_key][col] = level_stats[col].tolist()


with open("ui/src/data/summary_stats.json", "w") as outfile:
    outfile.write(json.dumps(stats))
