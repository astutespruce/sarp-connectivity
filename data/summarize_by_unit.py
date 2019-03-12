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


dams = read_dataframe("data/derived/dams.feather")
barriers = read_dataframe("data/derived/small_barriers.feather")

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
}

# Calculate summary statistics for each type of summary unit
for unit in SUMMARY_UNITS:
    print("processing {}".format(unit))

    dam_stats = (
        dams[[unit, "id", "OffNetwork", "GainMiles"]]
        .groupby(unit)
        .agg({"id": "count", "OffNetwork": "sum", "GainMiles": "mean"})
        .reset_index()
        .rename(
            columns={
                "id": "dams",
                "OffNetwork": "off_network_dams",
                "GainMiles": "miles",
            }
        )
        .set_index(unit)
    )

    barriers_stats = (
        barriers[[unit, "id", "OffNetwork"]]
        .groupby(unit)
        .agg({"id": "count", "OffNetwork": "sum"})
        .reset_index()
        .rename(columns={"id": "barriers", "OffNetwork": "off_network_barriers"})
        .set_index(unit)
    )
    merged = dam_stats.join(barriers_stats, how="outer").fillna(0)
    merged.dams = merged.dams.astype("uint32")
    merged.barriers = merged.barriers.astype("uint32")
    merged.off_network_dams = merged.off_network_dams.astype("uint32")
    merged.miles = merged.miles.round(3)

    unit = "County" if unit == "COUNTYFIPS" else unit

    # Write summary CSV for each unit type
    merged.to_csv(
        "data/derived/{}.csv".format(unit),
        index_label="id",
        quoting=csv.QUOTE_NONNUMERIC,
    )


# Write the summary statistics into the UI directory so that it can be imported at build time
# into the code
with open("ui/src/data/summary_stats.json", "w") as outfile:
    outfile.write(json.dumps(stats))
