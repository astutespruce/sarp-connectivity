"""Summarize dams and small barriers by summary units (HUC6, HUC8, etc).

This creates a summary CSV file for each type of summary unit, with a count of dams,
small barriers, and average gained miles for each summary unit.

It also calculates high-level summary statistics for the summary region, which
is included in the user interface code at build time for display on the homepage
and elsewhere.

This is run AFTER running `rank_dams.py` and `rank_small_barriers.py`

Inputs:
* `data/api/dams.feather`
* `data/api/small_barriers.feather`

"""

from pathlib import Path
from collections import defaultdict
import csv
import json
import pandas as pd
import numpy as np
from feather import read_dataframe

from analysis.constants import SARP_STATES

# Bins are manually constructed to give reasonable looking map
# There must be a matching number of colors in the map
PERCENTILES = [20, 40, 60, 75, 80, 85, 90, 95, 100]

# Note: states are identified by name, whereas counties are uniquely identified by
# FIPS code.
# The values from these fields in the dams / small_barriers data must exactly match
# the IDs for those units set when the vector tiles of those units are created, otherwise
# they won't join properly in the frontend.
# TODO: can COUNTYFIPS be renamed as county?

SUMMARY_UNITS = ["State", "COUNTYFIPS", "HUC6", "HUC8", "HUC12", "ECO3", "ECO4"]

INT_COLS = [
    "dams",
    "barriers",
    "total_barriers",
    "crossings",
    "on_network_dams",
    "on_network_barriers",
]


data_dir = Path("data")
src_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
ui_data_dir = Path("ui/data")
tile_dir = data_dir / "tiles"


print("Reading barriers")

# For dams, we want only those that were not dropped or duplicates
# this matches the ones coming out of the ranking
# read in dams with network results
dams = (
    read_dataframe(api_dir / "dams.feather")
    .set_index("id", drop=False)[["id", "HasNetwork", "GainMiles"] + SUMMARY_UNITS]
    .rename(columns={"HasNetwork": "OnNetwork"})
)
dams.OnNetwork = dams.OnNetwork.fillna(False)


# Read in ALL barriers and drop those that are duplicates
barriers = read_dataframe(src_dir / "small_barriers.feather").set_index(
    "id", drop=False
)[["id", "duplicate", "dropped", "excluded"] + SUMMARY_UNITS]
barriers = barriers.loc[~barriers.duplicate].copy()

# read in barriers with network results
barriers_network = read_dataframe(api_dir / "small_barriers.feather").set_index("id")[
    ["HasNetwork"]
]
barriers = barriers.join(barriers_network).rename(columns={"HasNetwork": "OnNetwork"})
barriers.OnNetwork = barriers.OnNetwork.fillna(False)

# any that were not dropped were available for analysis
barriers["Included"] = ~(barriers.dropped | barriers.excluded)

# crossings are already de-duplicated against each other and against
# barriers
crossings = read_dataframe(src_dir / "road_crossings.feather")


# Set NA so that we don't include these values in our statistics
dams.loc[dams.GainMiles == -1, "GainMiles"] = np.nan


stats = defaultdict(defaultdict)

# Calculate summary statistics for the entire region
stats["southeast"] = {
    "dams": len(dams),
    "on_network_dams": len(dams.loc[dams.OnNetwork]),
    "miles": round(dams["GainMiles"].mean().item(), 3),
    "total_barriers": len(barriers),
    "barriers": len(barriers.loc[barriers.Included]),
    "on_network_barriers": len(barriers.loc[barriers.OnNetwork]),
    "crossings": len(crossings),
}

# only extract core counts in states for data download page,
# as other stats are joined to state vector tiles below
states = []
for state in SARP_STATES.values():
    states.append(
        {
            "id": state,
            "dams": int((dams.State == state).sum()),
            "total_barriers": int((barriers.State == state).sum()),
        }
    )
stats["State"] = states

# Write the summary statistics into the UI directory so that it can be imported at build time
# into the code
with open(ui_data_dir / "summary_stats.json", "w") as outfile:
    outfile.write(json.dumps(stats))


# Calculate summary statistics for each type of summary unit
# These are joined to vector tiles
for unit in SUMMARY_UNITS:
    print("processing {}".format(unit))

    dam_stats = (
        dams[[unit, "id", "OnNetwork", "GainMiles"]]
        .groupby(unit)
        .agg({"id": "count", "OnNetwork": "sum", "GainMiles": "mean",})
        .rename(
            columns={
                "id": "dams",
                "OnNetwork": "on_network_dams",
                "GainMiles": "miles",
            }
        )
    )

    barriers_stats = (
        barriers[[unit, "id", "Included", "OnNetwork"]]
        .groupby(unit)
        .agg({"id": "count", "Included": "sum", "OnNetwork": "sum",})
        .rename(
            columns={
                "id": "total_barriers",
                "Included": "barriers",
                "OnNetwork": "on_network_barriers",
            }
        )
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
        tile_dir / "{}.csv".format(unit), index_label="id", quoting=csv.QUOTE_NONNUMERIC
    )

