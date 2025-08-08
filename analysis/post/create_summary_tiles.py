"""Update summary unit map tiles with summary statistics of dams and small barriers
within them.

Base summary unit map tile are created using `analysis/prep/boundaries/create_map_unit_tiles.py`.

These statistics are based on:
* dams: not dropped or duplicate
* small_barriers: not duplicate (dropped barriers are included in stats)
* road crossings

This is run AFTER running `aggregate_networks.py`

Inputs:
* `data/api/dams.feather`
* `data/api/combined_barriers.feather`
* `data/api/largefish_barriers.feather`
* `data/api/smallfish_barriers.feather`

* `data/api/road_crossings.feather`

Outputs:
* `/tiles/map_units_summary.mbtiles`
* `/data/api/map_units.feather`

"""

from pathlib import Path
import subprocess

import numpy as np
import pandas as pd
import pyarrow as pa
from pyarrow.csv import write_csv

from analysis.constants import REGION_STATES
from analysis.lib.util import append
from analysis.post.lib.removed_barriers import calc_year_removed_bin, pack_year_removed_stats

# Note: states are identified by name, whereas counties are uniquely identified by
# FIPS code.
# The values from these fields in the dams / small_barriers data must exactly match
# the IDs for those units set when the vector tiles of those units are created, otherwise
# they won't join properly in the frontend.

SUMMARY_UNITS = [
    "State",
    "COUNTYFIPS",
    "CongressionalDistrict",
    "HUC2",
    "HUC6",
    "HUC8",
    "HUC10",
    "HUC12",
    "StateWRA",
    # not shown thematically on map (units overlap)
    "FishHabitatPartnership",
]

INT_COLS = [
    "dams",
    "recon_dams",
    "ranked_dams",
    "removed_dams",
    "small_barriers",
    "total_small_barriers",
    "removed_small_barriers",
    "total_road_crossings",
    "unsurveyed_road_crossings",
    "ranked_small_barriers",
    "ranked_largefish_barriers_dams",
    "ranked_largefish_barriers_small_barriers",
    "ranked_smallfish_barriers_dams",
    "ranked_smallfish_barriers_small_barriers",
]


tile_join = "tile-join"

data_dir = Path("data")
api_dir = data_dir / "api"
src_dir = data_dir / "barriers/master"
bnd_dir = data_dir / "boundaries"
results_dir = data_dir / "barriers/networks"
ui_data_dir = Path("ui/data")
src_tile_dir = data_dir / "tiles"
out_tile_dir = Path("tiles")
tmp_dir = Path("/tmp")


### Setup region mapping
# have to aggregate from state to region
# NOTE: some states are in multiple regions, so we split out associated records
state_regions = {}
for region, region_states in REGION_STATES.items():
    for state in region_states:
        if state in state_regions:
            state_regions[state].append(region)
        else:
            state_regions[state] = [region]

### Read dams
dams = pd.read_feather(
    results_dir / "dams.feather",
    columns=["id", "HasNetwork", "Ranked", "Removed", "YearRemoved", "Private"] + SUMMARY_UNITS,
).set_index("id", drop=False)

dams = dams.loc[~dams.Private]

# Get recon from master
dams_master = pd.read_feather(src_dir / "dams.feather", columns=["id", "Recon"]).set_index("id")
dams = dams.join(dams_master)
dams["Recon"] = dams.Recon > 0
dams["FishHabitatPartnership"] = dams.FishHabitatPartnership.str.split(",")
dams["Region"] = dams.State.map(state_regions)

# get stats for removed dams
removed_dam_networks = (
    pd.read_feather(
        data_dir / "networks/clean/removed/removed_dams_networks.feather",
        columns=["id", "EffectiveGainMiles"],
    )
    .set_index("id")
    .rename(columns={"EffectiveGainMiles": "RemovedGainMiles"})
)
dams = dams.join(removed_dam_networks)
dams["RemovedGainMiles"] = dams.RemovedGainMiles.fillna(0)

# fix YearRemoved and bin
dams.loc[~dams.Removed, "YearRemoved"] = np.nan
dams.loc[(dams.YearRemoved > 0) & (dams.YearRemoved < 1900), "YearRemoved"] = np.uint16(0)
dams.loc[(dams.YearRemoved > 0) & (dams.YearRemoved < 2000), "YearRemoved"] = 1
dams["YearRemoved"] = calc_year_removed_bin(dams.YearRemoved)


### Read road-related barriers
barriers = pd.read_feather(
    results_dir / "small_barriers.feather",
    columns=["id", "HasNetwork", "Ranked", "Removed", "YearRemoved", "Private"] + SUMMARY_UNITS,
).set_index("id", drop=False)

barriers = barriers.loc[~barriers.Private]

barriers_master = pd.read_feather(
    "data/barriers/master/small_barriers.feather",
    columns=["id", "dropped", "excluded", "duplicate"],
).set_index("id")

barriers = barriers.join(barriers_master)

# barriers that were not  excluded are likely to have impacts
# (dropped / duplicates are already removed from above)
barriers["Included"] = ~barriers.excluded
barriers["FishHabitatPartnership"] = barriers.FishHabitatPartnership.str.split(",")
barriers["Region"] = barriers.State.map(state_regions)

removed_barrier_networks = (
    pd.read_feather(
        data_dir / "networks/clean/removed/removed_combined_barriers_networks.feather",
        columns=["id", "EffectiveGainMiles"],
    )
    .set_index("id")
    .rename(columns={"EffectiveGainMiles": "RemovedGainMiles"})
)
barriers = barriers.join(removed_barrier_networks)
barriers["RemovedGainMiles"] = barriers.RemovedGainMiles.fillna(0)

barriers.loc[~barriers.Removed, "YearRemoved"] = np.nan
barriers.loc[(barriers.YearRemoved > 0) & (barriers.YearRemoved < 1900), "YearRemoved"] = np.uint16(0)
barriers.loc[(barriers.YearRemoved > 0) & (barriers.YearRemoved < 2000), "YearRemoved"] = 1
barriers["YearRemoved"] = calc_year_removed_bin(barriers.YearRemoved)

largefish_barriers = pd.read_feather(
    results_dir / "largefish_barriers.feather",
    columns=["id", "BarrierType", "Ranked", "Private"] + SUMMARY_UNITS,
)
largefish_barriers = largefish_barriers.loc[~largefish_barriers.Private]
largefish_barriers["FishHabitatPartnership"] = largefish_barriers.FishHabitatPartnership.str.split(",")
largefish_barriers["Region"] = largefish_barriers.State.map(state_regions)

smallfish_barriers = pd.read_feather(
    results_dir / "smallfish_barriers.feather",
    columns=["id", "BarrierType", "Ranked", "Private"] + SUMMARY_UNITS,
)
smallfish_barriers = smallfish_barriers.loc[~smallfish_barriers.Private]
smallfish_barriers["FishHabitatPartnership"] = smallfish_barriers.FishHabitatPartnership.str.split(",")
smallfish_barriers["Region"] = smallfish_barriers.State.map(state_regions)

### Read road / stream crossings
# NOTE: crossings are already de-duplicated against each other and against
# barriers
crossings = pd.read_feather(src_dir / "road_crossings.feather", columns=["id", "Surveyed"] + SUMMARY_UNITS)
crossings["FishHabitatPartnership"] = crossings.FishHabitatPartnership.str.split(",")
crossings["Region"] = crossings.State.map(state_regions)

# Calculate summary statistics for each type of summary unit
# These are joined to vector tiles
stats = None
for unit in SUMMARY_UNITS + ["Region"]:
    print(f"processing {unit}")

    dams_by_unit = dams.copy()
    barriers_by_unit = barriers.copy()
    largefish_barriers_by_unit = largefish_barriers.copy()
    smallfishbarriers_by_unit = smallfish_barriers.copy()
    crossings_by_unit = crossings.copy()

    if unit == "State":
        units = pd.read_feather(bnd_dir / "region_states.feather", columns=["id"]).set_index("id")
    elif unit == "COUNTYFIPS":
        units = pd.read_feather(bnd_dir / "region_counties.feather", columns=["id"]).set_index("id")
    elif unit == "CongressionalDistrict":
        units = pd.read_feather(bnd_dir / "region_congressional_districts.feather", columns=["id"]).set_index("id")
    elif unit == "StateWRA":
        units = pd.read_feather(bnd_dir / "state_water_resource_areas.feather", columns=["id"]).set_index("id")
    elif unit == "FishHabitatPartnership":
        units = pd.read_feather(bnd_dir / "fhp_boundary.feather", columns=["id"]).set_index("id")
    elif unit == "Region":
        units = pd.read_feather(bnd_dir / "region_boundary.feather", columns=["id"]).set_index("id")
        # ignore total; that is handled via JSON
        units = units.loc[units.index != "total"].copy()
    else:
        units = pd.read_feather(bnd_dir / f"{unit}.feather", columns=[unit]).set_index(unit)

    if unit in {"FishHabitatPartnership", "Region"}:
        # have to split unit list values into individual records
        dams_by_unit = dams_by_unit.explode(unit)
        barriers_by_unit = barriers_by_unit.explode(unit)
        largefish_barriers_by_unit = largefish_barriers_by_unit.explode(unit)
        smallfishbarriers_by_unit = smallfishbarriers_by_unit.explode(unit)
        crossings_by_unit = crossings_by_unit.explode(unit)

    dam_stats = (
        dams_by_unit[[unit, "id", "Ranked", "Recon", "Removed", "RemovedGainMiles"]]
        .groupby(unit)
        .agg(
            {
                "id": "count",
                "Ranked": "sum",
                "Recon": "sum",
                "Removed": "sum",
                "RemovedGainMiles": "sum",
            }
        )
        .rename(
            columns={
                "id": "dams",
                "Ranked": "ranked_dams",
                "Recon": "recon_dams",
                "Removed": "removed_dams",
                "RemovedGainMiles": "removed_dams_gain_miles",
            }
        )
        .join(
            pack_year_removed_stats(
                dams_by_unit[[unit, "HasNetwork", "YearRemoved", "RemovedGainMiles"]], unit=unit
            ).rename("removed_dams_by_year")
        )
    )
    dam_stats["removed_dams_by_year"] = dam_stats.removed_dams_by_year.fillna("")

    barriers_stats = (
        barriers_by_unit[[unit, "id", "Included", "Ranked", "Removed", "RemovedGainMiles"]]
        .groupby(unit)
        .agg(
            {
                "id": "count",
                "Included": "sum",
                "Ranked": "sum",
                "Removed": "sum",
                "RemovedGainMiles": "sum",
            }
        )
        .rename(
            columns={
                "id": "total_small_barriers",
                "Included": "small_barriers",
                "Ranked": "ranked_small_barriers",
                "Removed": "removed_small_barriers",
                "RemovedGainMiles": "removed_small_barriers_gain_miles",
            }
        )
        .join(
            pack_year_removed_stats(
                barriers_by_unit[[unit, "HasNetwork", "YearRemoved", "RemovedGainMiles"]], unit=unit
            ).rename("removed_small_barriers_by_year")
        )
    )
    barriers_stats["removed_small_barriers_by_year"] = barriers_stats.removed_small_barriers_by_year.fillna("")

    # have to split out stats by barrier type because this is how it is handled in UI
    largefish_stats = (
        largefish_barriers_by_unit.loc[largefish_barriers_by_unit.Ranked]
        .groupby([unit, "BarrierType"])
        .size()
        .rename("count")
        .reset_index()
        .pivot(columns=["BarrierType"], index=unit)
        .fillna(0)
    )
    largefish_stats.columns = [f"ranked_largefish_barriers_{c}" for _, c in largefish_stats.columns]

    smallfish_stats = (
        smallfishbarriers_by_unit.loc[smallfishbarriers_by_unit.Ranked]
        .groupby([unit, "BarrierType"])
        .size()
        .rename("count")
        .reset_index()
        .pivot(columns=["BarrierType"], index=unit)
        .fillna(0)
    )
    smallfish_stats.columns = [f"ranked_smallfish_barriers_{c}" for _, c in smallfish_stats.columns]

    total_crossing_stats = crossings_by_unit[[unit, "id"]].groupby(unit).size().rename("total_road_crossings")
    unsurveyed_crossing_stats = (
        crossings_by_unit.loc[crossings_by_unit.Surveyed == 0][[unit, "id"]]
        .groupby(unit)
        .size()
        .rename("unsurveyed_road_crossings")
    )

    merged = (
        units.join(dam_stats, how="left")
        .join(barriers_stats, how="left")
        .join(largefish_stats, how="left")
        .join(smallfish_stats, how="left")
        .join(total_crossing_stats, how="left")
        .join(unsurveyed_crossing_stats, how="left")
    )
    merged[INT_COLS] = merged[INT_COLS].fillna(0).astype("uint32")

    for col in ["removed_dams_by_year", "removed_small_barriers_by_year"]:
        merged[col] = merged[col].fillna("")

    merged = merged.fillna(0)

    if unit == "COUNTYFIPS":
        unit = "County"

    merged.index.name = "id"
    merged["layer"] = unit
    stats = append(stats, merged.reset_index())


### output unit stats with bounds for API
units = pd.read_feather(bnd_dir / "unit_bounds.feather").set_index(["layer", "id"])
out = units.join(stats.set_index(["layer", "id"]))

out.reset_index().to_feather(api_dir / "map_units.feather")

### Output minimal subset and join to tiles

# create bitset field based on number of barriers present per unit; where false for a given barrier type,
# this is used to color the unit grey (see priority/Map.jsx for decoding)
# Can rank if:
# dams: ranked_dams > 0
# small_barriers: ranked_small_barriers > 0 AND total_small_barriers >= 10
# other *_barriers: dams ranked in scenario > 0 AND total_small_barriers >= 10 (may need to revisit this)

can_prioritize_dams = (stats.ranked_dams > 0).values.astype("uint8")
can_prioritize_small_barriers = ((stats.ranked_small_barriers > 0) & (stats.total_small_barriers >= 10)).values.astype(
    "uint8"
)
can_prioritize_combined_barriers = ((stats.ranked_dams > 0) & (stats.total_small_barriers >= 10)).values.astype("uint8")
can_prioritize_largefish_barriers = (
    (stats.ranked_largefish_barriers_dams > 0) & (stats.total_small_barriers >= 10)
).values.astype("uint8")
can_prioritize_smallfish_barriers = (
    (stats.ranked_smallfish_barriers_dams > 0) & (stats.total_small_barriers >= 10)
).values.astype("uint8")
can_select_road_crossings = (stats.total_road_crossings > 0).values.astype("uint8")

stats["has_data"] = (
    can_prioritize_dams
    | (can_prioritize_small_barriers << 1)
    | (can_prioritize_combined_barriers << 2)
    | (can_prioritize_largefish_barriers << 3)
    | (can_prioritize_smallfish_barriers << 4)
    | (can_select_road_crossings << 5)
)

# only write the fields used for rendering map units by color in the frontend
stats = stats[["id", "dams", "small_barriers", "removed_dams", "removed_small_barriers", "has_data"]]

csv_filename = tmp_dir / "map_units_summary.csv"
write_csv(pa.Table.from_pandas(stats), csv_filename)

print("Joining to tiles...")

# join to tiles
mbtiles_filename = f"{out_tile_dir}/map_units_summary.mbtiles"
ret = subprocess.run(
    [
        tile_join,
        "-f",
        "-pg",
        "--no-tile-size-limit",
        "-o",
        mbtiles_filename,
        "-c",
        f"{tmp_dir}/map_units_summary.csv",
        f"{data_dir}/tiles/map_units.mbtiles",
    ]
)
ret.check_returncode()

csv_filename.unlink()

print("All done!")
