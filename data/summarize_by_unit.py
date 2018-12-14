from collections import defaultdict
import csv
import json
import pandas as pd
import numpy as np
from feather import read_dataframe

# Bins are manually constructed to give reasonable looking map
# There must be a matching number of colors in the map
PERCENTILES = [20, 40, 60, 75, 80, 85, 90, 95, 100]


dams = read_dataframe("data/src/dams.feather")
sb = read_dataframe("data/src/small_barriers.feather")

stats = defaultdict(defaultdict)
stats["southeast"] = {
    "dams": len(dams),
    "miles": round(dams["GainMiles"].mean().item(), 3),
    "barriers": len(sb),
}

# Group by state, HUC level, ecoregion level
for unit in ("State", "HUC6", "HUC8", "HUC12", "ECO3", "ECO4"):
    print("processing {}".format(unit))

    dam_stats = (
        dams[[unit, "id", "GainMiles"]]
        .groupby(unit)
        .agg({"id": "count", "GainMiles": "mean"})
        .reset_index()
        .rename(columns={"id": "dams", "GainMiles": "miles"})
        .set_index(unit)
    )

    sb_stats = (
        sb[[unit, "id"]]
        .groupby(unit)
        .size()
        .reset_index()
        .rename(columns={0: "barriers"})
        .set_index(unit)
    )
    merged = dam_stats.join(sb_stats, how="outer").fillna(0)
    merged.dams = merged.dams.astype("uint32")
    merged.barriers = merged.barriers.astype("uint32")
    merged.miles = merged.miles.round(3)

    merged.to_csv(
        "data/summary/{}.csv".format(unit),
        index_label="id",
        quoting=csv.QUOTE_NONNUMERIC,
    )

    level_stats = merged.agg(["min", "max"])
    for col in ("dams", "miles", "barriers"):
        stats[unit][col] = {
            "range": level_stats[col].round(3).tolist(),
            "mean": round(merged[col].mean().item(), 3),
        }
        if col in ("dams", "barriers"):
            stats[unit][col]["bins"] = (
                np.percentile(merged[col], PERCENTILES).round().astype("uint").tolist()
            )

with open("ui/src/data/summary_stats.json", "w") as outfile:
    outfile.write(json.dumps(stats))
