"""Summarize dams and small barriers by summary units (HUC6, HUC8, etc).

This creates a summary CSV file for each type of summary unit, with a count of dams,
small barriers, and average gained miles for each summary unit.

It also calculates high-level summary statistics for each region (e.g., Southeast), which
is included in the user interface code at build time for display on the homepage
and elsewhere.

These statistics are based on:
* dams: not dropped or duplicate
* small_barriers: not duplicate (dropped dams are included in stats)

This is run AFTER running `rank_dams.py` and `rank_small_barriers.py`

Inputs:
* `data/api/dams_all.feather`
* `data/api/dams_perennial.feather`
* `data/api/small_barriers_all.feather`
* `data/api/small_barriers_perennial.feather`

"""

from pathlib import Path
import csv
import json
import subprocess

import pandas as pd
import numpy as np

from analysis.constants import STATES, REGION_STATES

# Note: states are identified by name, whereas counties are uniquely identified by
# FIPS code.
# The values from these fields in the dams / small_barriers data must exactly match
# the IDs for those units set when the vector tiles of those units are created, otherwise
# they won't join properly in the frontend.

SUMMARY_UNITS = ["State", "COUNTYFIPS", "HUC6", "HUC8", "HUC12", "ECO3", "ECO4"]

INT_COLS = [
    "dams",
    "barriers",
    "total_barriers",
    "crossings",
    "on_network_dams",
    "on_network_barriers",
    "perennial_dams",
    "perennial_barriers",
]


data_dir = Path("data")
src_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
ui_data_dir = Path("ui/data")
src_tile_dir = data_dir / "tiles"
out_tile_dir = Path("tiles")
tmp_dir = Path("/tmp")


states = (
    pd.read_feather("data/boundaries/states.feather", columns=["id", "State"])
    .set_index("id")
    .State.to_dict()
)


### Read dams
dams = (
    pd.read_feather(
        api_dir / f"dams_all.feather",
        columns=["id", "HasNetwork", "GainMiles"] + SUMMARY_UNITS,
    )
    .set_index("id", drop=False)
    .rename(columns={"HasNetwork": "OnNetwork"})
)
# Set NA so that we don't include these values in our statistics
dams.loc[dams.GainMiles == -1, "GainMiles"] = np.nan

perennial_dams = (
    pd.read_feather(
        api_dir / "dams_perennial.feather",
        # columns=["id", "HasNetwork", "GainMiles"]
    )
    .set_index("id")
    .rename(columns={"HasNetwork": "OnNetwork"})
)
perennial_dams.loc[perennial_dams.GainMiles == -1, "GainMiles"] = np.nan

dams = dams.join(perennial_dams, rsuffix="_perennial")

### Read road-related barriers
barriers = (
    pd.read_feather(
        api_dir / "small_barriers_all.feather",
        columns=["id", "HasNetwork", "GainMiles"] + SUMMARY_UNITS,
    )
    .set_index("id", drop=False)
    .rename(columns={"HasNetwork": "OnNetwork"})
)
perennial_barriers = (
    pd.read_feather(
        api_dir / "small_barriers_perennial.feather", columns=["id", "HasNetwork"]
    )
    .set_index("id")
    .rename(columns={"HasNetwork": "OnNetwork"})
)
barriers_master = pd.read_feather(
    "data/barriers/master/small_barriers.feather", columns=["id", "dropped", "excluded"]
).set_index("id")

barriers = barriers.join(perennial_barriers, rsuffix="_perennial").join(barriers_master)

# barriers that were not dropped or excluded are likely to have impacts
barriers["Included"] = ~(barriers.dropped | barriers.excluded)

### Read road / stream crossings
# NOTE: crossings are already de-duplicated against each other and against
# barriers
crossings = pd.read_feather(
    src_dir / "road_crossings.feather", columns=["id"] + SUMMARY_UNITS
)


# Calculate summary stats for entire analysis area
stats = {
    "total": {
        "dams": len(dams),
        "on_network_dams": dams.OnNetwork.sum(),
        # NOTE: perennial dams are on-network (raw networks) but not on intermittent segments
        "perennial_dams": dams.OnNetwork_perennial.sum(),
        "miles": round(dams.GainMiles.mean().item(), 3),
        "perennial_miles": round(dams.GainMiles_perennial.mean().item(), 3),
        "total_barriers": len(barriers),
        "barriers": barriers.Included.sum(),
        "on_network_barriers": barriers.OnNetwork.sum(),
        "perennial_barriers": barriers.OnNetwork_perennial.sum(),
        "crossings": len(crossings),
    }
}

# Calculate stats for regions
# NOTE: these are groupings of states and some states may be in multiple regions
region_stats = []
for region, region_states in REGION_STATES.items():
    region_states = [states[s] for s in region_states]
    region_dams = dams.loc[dams.State.isin(region_states)]
    region_barriers = barriers.loc[barriers.State.isin(region_states)]
    region_crossings = crossings.loc[crossings.State.isin(region_states)]

    region_stats.append(
        {
            "id": region,
            "dams": len(region_dams),
            "on_network_dams": region_dams.OnNetwork.sum(),
            "perennial_dams": region_dams.OnNetwork_perennial.sum(),
            "miles": round(region_dams.GainMiles.mean().item(), 3),
            "perennial_miles": round(region_dams.GainMiles_perennial.mean().item(), 3),
            "total_barriers": len(region_barriers),
            "barriers": region_barriers.Included.sum(),
            "on_network_barriers": region_barriers.OnNetwork.sum(),
            "perennial_barriers": region_barriers.OnNetwork_perennial.sum(),
            "crossings": len(region_crossings),
        }
    )

stats["region"] = region_stats


# only extract core counts in states for data download page,
# as other stats are joined to state vector tiles below
state_stats = []
for state in sorted(STATES.values()):
    state_stats.append(
        {
            "id": state,
            "dams": int((dams.State == state).sum()),
            "total_barriers": int((barriers.State == state).sum()),
        }
    )
stats["State"] = state_stats

# Write the summary statistics into the UI directory so that it can be imported at build time
# into the code
with open(ui_data_dir / "summary_stats.json", "w") as outfile:
    outfile.write(json.dumps(stats))


# Calculate summary statistics for each type of summary unit
# These are joined to vector tiles
mbtiles_files = []
for unit in SUMMARY_UNITS:
    print(f"processing {unit}")

    dam_stats = (
        dams[
            [
                unit,
                "id",
                "OnNetwork",
                "OnNetwork_perennial",
                "GainMiles",
                "GainMiles_perennial",
            ]
        ]
        .groupby(unit)
        .agg(
            {
                "id": "count",
                "OnNetwork": "sum",
                "OnNetwork_perennial": "sum",
                "GainMiles": "mean",
                "GainMiles_perennial": "mean",
            }
        )
        .rename(
            columns={
                "id": "dams",
                "OnNetwork": "on_network_dams",
                "OnNetwork_perennial": "perennial_dams",
                "GainMiles": "miles",
                "GainMiles_perennial": "perennial_miles",
            }
        )
    )

    barriers_stats = (
        barriers[[unit, "id", "Included", "OnNetwork", "OnNetwork_perennial"]]
        .groupby(unit)
        .agg(
            {
                "id": "count",
                "Included": "sum",
                "OnNetwork": "sum",
                "OnNetwork_perennial": "sum",
            }
        )
        .rename(
            columns={
                "id": "total_barriers",
                "Included": "barriers",
                "OnNetwork": "on_network_barriers",
                "OnNetwork_perennial": "perennial_barriers",
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
    merged.perennial_miles = merged.perennial_miles.round(3)

    unit = "County" if unit == "COUNTYFIPS" else unit

    # Write summary CSV for each unit type
    merged.to_csv(
        tmp_dir / f"{unit}.csv", index_label="id", quoting=csv.QUOTE_NONNUMERIC
    )

    # join to tiles
    mbtiles_filename = f"{tmp_dir}/{unit}_summary.mbtiles"
    mbtiles_files.append(mbtiles_filename)
    ret = subprocess.run(
        [
            "tile-join",
            "-f",
            "-pg",
            "-o",
            mbtiles_filename,
            "-c",
            f"{tmp_dir}/{unit}.csv",
            f"{src_tile_dir}/{unit}.mbtiles",
        ]
    )
    ret.check_returncode()


# join all summary tiles together
print("Merging all summary tiles")
ret = subprocess.run(
    [
        "tile-join",
        "-f",
        "-pg",
        "--no-tile-size-limit",
        "-o",
        f"{out_tile_dir}/summary.mbtiles",
        f"{src_tile_dir}/mask.mbtiles",
        f"{src_tile_dir}/boundary.mbtiles",
    ]
    + mbtiles_files
)
ret.check_returncode()
