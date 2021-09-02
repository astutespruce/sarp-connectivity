"""Update summary unit map tiles with summary statistics of dams and small barriers
within them.

Base summary unit map tile are created using `analysis/prep/boundaries/generate_region_tiles.py`.

These statistics are based on:
* dams: not dropped or duplicate
* small_barriers: not duplicate (dropped barriers are included in stats)
* road crossings

This is run AFTER running `rank_dams.py` and `rank_small_barriers.py`

Inputs:
* `data/api/dams.feather`
* `data/api/small_barriers.feather`

Outputs:
* `/tiles/summary.mbtiles

"""

from pathlib import Path
import csv
import subprocess

import pandas as pd
import numpy as np
from pyogrio import read_dataframe

# Note: states are identified by name, whereas counties are uniquely identified by
# FIPS code.
# The values from these fields in the dams / small_barriers data must exactly match
# the IDs for those units set when the vector tiles of those units are created, otherwise
# they won't join properly in the frontend.

SUMMARY_UNITS = ["State", "COUNTYFIPS", "HUC6", "HUC8", "HUC12", "ECO3", "ECO4"]

INT_COLS = [
    "dams",
    "small_barriers",
    "total_small_barriers",
    "crossings",
    "on_network_dams",
    "on_network_small_barriers",
]


data_dir = Path("data")
src_dir = data_dir / "barriers/master"
bnd_dir = data_dir / "boundaries"
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
        api_dir / f"dams.feather",
        columns=["id", "HasNetwork", "GainMiles", "PerennialGainMiles"] + SUMMARY_UNITS,
    )
    .set_index("id", drop=False)
    .rename(columns={"HasNetwork": "OnNetwork"})
)
# Set NA so that we don't include these values in our statistics
dams.loc[dams.GainMiles == -1, "GainMiles"] = np.nan
dams.loc[dams.PerennialGainMiles == -1, "PerennialGainMiles"] = np.nan


### Read road-related barriers
barriers = (
    pd.read_feather(
        api_dir / "small_barriers.feather",
        columns=["id", "HasNetwork"] + SUMMARY_UNITS,
    )
    .set_index("id", drop=False)
    .rename(columns={"HasNetwork": "OnNetwork"})
)
barriers_master = pd.read_feather(
    "data/barriers/master/small_barriers.feather", columns=["id", "dropped", "excluded"]
).set_index("id")

barriers = barriers.join(barriers_master)

# barriers that were not dropped or excluded are likely to have impacts
barriers["Included"] = ~(barriers.dropped | barriers.excluded)

### Read road / stream crossings
# NOTE: crossings are already de-duplicated against each other and against
# barriers
crossings = pd.read_feather(
    src_dir / "road_crossings.feather", columns=["id"] + SUMMARY_UNITS
)


# Calculate summary statistics for each type of summary unit
# These are joined to vector tiles
mbtiles_files = []
for unit in SUMMARY_UNITS:
    print(f"processing {unit}")

    if unit == "State":
        units = read_dataframe(
            bnd_dir / "region_states.gpkg", columns=["id"], read_geometry=False
        ).set_index("id")
    elif unit == "COUNTYFIPS":
        units = read_dataframe(
            bnd_dir / "region_counties.gpkg", columns=["id"], read_geometry=False
        ).set_index("id")
    else:
        units = pd.read_feather(bnd_dir / f"{unit}.feather", columns=[unit]).set_index(
            unit
        )

    dam_stats = (
        dams[[unit, "id", "OnNetwork", "GainMiles", "PerennialGainMiles",]]
        .groupby(unit)
        .agg(
            {
                "id": "count",
                "OnNetwork": "sum",
                "GainMiles": "mean",
                "PerennialGainMiles": "mean",
            }
        )
        .rename(
            columns={
                "id": "dams",
                "OnNetwork": "on_network_dams",
                "GainMiles": "miles",
                "PerennialGainMiles": "perennial_miles",
            }
        )
    )

    barriers_stats = (
        barriers[[unit, "id", "Included", "OnNetwork"]]
        .groupby(unit)
        .agg({"id": "count", "Included": "sum", "OnNetwork": "sum",})
        .rename(
            columns={
                "id": "total_small_barriers",
                "Included": "small_barriers",
                "OnNetwork": "on_network_small_barriers",
            }
        )
    )

    crossing_stats = crossings[[unit, "id"]].groupby(unit).size().rename("crossings")

    merged = (
        units.join(dam_stats, how="left")
        .join(barriers_stats, how="left")
        .join(crossing_stats, how="left")
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
