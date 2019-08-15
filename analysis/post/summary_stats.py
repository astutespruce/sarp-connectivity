"""Summarize dams and small barriers by summary units (HUC6, HUC8, etc).

This creates a summary CSV file for each type of summary unit, with a count of dams, 
small barriers, and average gained miles for each summary unit.

It also calculates high-level summary statistics for the summary region, which
is included in the user interface code at build time for display on the homepage
and elsewhere.

This is run AFTER `running preprocess_dams.py` and `preprocess_small_barriers.py`

Inputs:
* `dams.feather`
* `small_barriers.feather`

"""

from pathlib import Path
from collections import defaultdict
import csv
import json
import pandas as pd
import numpy as np
from feather import read_dataframe

# Bins are manually constructed to give reasonable looking map
# There must be a matching number of colors in the map
PERCENTILES = [20, 40, 60, 75, 80, 85, 90, 95, 100]

# Note: states are identified by name, whereas counties are uniquely identified by
# FIPS code.
# The values from these fields in the dams / small_barriers data must exactly match
# the IDs for those units set when the vector tiles of those units are created, otherwise
# they won't join properly in the frontend.
SUMMARY_UNITS = ["State", "HUC6", "HUC8", "HUC12", "ECO3", "ECO4", "COUNTYFIPS"]

INT_COLS = ["dams", "barriers", "crossings", "off_network_dams", "off_network_barriers"]


src_dir = Path("data/derived")
ui_data_dir = Path("ui/data")


print("Reading ranked barriers")
dams = read_dataframe(src_dir / "dams.feather")
barriers = read_dataframe(src_dir / "small_barriers.feather")
crossings = read_dataframe(src_dir / "road_crossings.feather")

# TODO: remove once rerun preprocess_road_crossings.py
crossings["id"] = crossings.index.astype("uint")


# Set NA so that we don't include these values in our statistics
dams.loc[dams.GainMiles == -1, "GainMiles"] = np.nan

# Mark those off network
dams["OffNetwork"] = ~dams.HasNetwork
barriers["OffNetwork"] = ~barriers.HasNetwork

stats = defaultdict(defaultdict)

# Calculate summary statistics for the entire region
stats["southeast"] = {
    "dams": len(dams),
    "off_network_dams": len(dams.loc[dams.OffNetwork]),
    "miles": round(dams["GainMiles"].mean().item(), 3),
    "barriers": len(barriers),
    "off_network_barriers": len(barriers.loc[barriers.OffNetwork]),
    "crossings": len(crossings),
}


# Write the summary statistics into the UI directory so that it can be imported at build time
# into the code
with open(ui_data_dir / "summary_stats.json", "w") as outfile:
    outfile.write(json.dumps(stats))


# Calculate summary statistics for each type of summary unit
# These are joined to vector tiles
for unit in SUMMARY_UNITS:
    print("processing {}".format(unit))

    dam_stats = (
        dams[[unit, "id", "OffNetwork", "GainMiles"]]
        .groupby(unit)
        .agg({"id": "count", "OffNetwork": "sum", "GainMiles": "mean"})
        .rename(
            columns={
                "id": "dams",
                "OffNetwork": "off_network_dams",
                "GainMiles": "miles",
            }
        )
    )

    barriers_stats = (
        barriers[[unit, "id", "OffNetwork"]]
        .groupby(unit)
        .agg({"id": "count", "OffNetwork": "sum"})
        .rename(columns={"id": "barriers", "OffNetwork": "off_network_barriers"})
    )

    crossing_stats = crossings[[unit, "id"]].groupby(unit).size().rename("crossings")

    merged = (
        dam_stats.join(barriers_stats, how="outer")
        .join(crossing_stats, how="outer")
        .fillna(0)
    )
    merged[INT_COLS] = merged[INT_COLS].astype("uint32")
    merged.miles = merged.miles.round(3)

    unit = "County" if unit == "COUNTYFIPS" else unit

    # Write summary CSV for each unit type
    merged.to_csv(
        src_dir / "{}.csv".format(unit), index_label="id", quoting=csv.QUOTE_NONNUMERIC
    )

