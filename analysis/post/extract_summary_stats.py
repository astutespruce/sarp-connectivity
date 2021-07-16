"""Summarize statistics for dams and small barriers at overall level, reigonal level,
and state level.

This creates a summary data JSON file in the UI directory for use in the frontend.

These statistics are based on:
* dams: not dropped or duplicate
* small_barriers: not duplicate (dropped barriers are included in stats)
* road crossings

This is run AFTER running `rank_dams.py` and `rank_small_barriers.py`

Inputs:
* `data/api/dams_all.feather`
* `data/api/dams_perennial.feather`
* `data/api/small_barriers_all.feather`
* `data/api/small_barriers_perennial.feather`

Outputs:
* `ui/data/summary_stats.json

"""

from pathlib import Path
import json

import pandas as pd
import numpy as np

from analysis.constants import STATES, REGION_STATES


data_dir = Path("data")
src_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
ui_data_dir = Path("ui/data")

states = (
    pd.read_feather("data/boundaries/states.feather", columns=["id", "State"])
    .set_index("id")
    .State.to_dict()
)


### Read dams
dams = (
    pd.read_feather(
        api_dir / f"dams_all.feather",
        columns=["id", "HasNetwork", "GainMiles", "State"],
    )
    .set_index("id", drop=False)
    .rename(columns={"HasNetwork": "OnNetwork"})
)
# Set NA so that we don't include these values in our statistics
dams.loc[dams.GainMiles == -1, "GainMiles"] = np.nan

perennial_dams = (
    pd.read_feather(api_dir / "dams_perennial.feather",)
    .set_index("id")
    .rename(columns={"HasNetwork": "OnNetwork"})
)
perennial_dams.loc[perennial_dams.GainMiles == -1, "GainMiles"] = np.nan

dams = dams.join(perennial_dams, rsuffix="_perennial")

### Read road-related barriers
barriers = (
    pd.read_feather(
        api_dir / "small_barriers_all.feather",
        columns=["id", "HasNetwork", "GainMiles", "State"],
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
crossings = pd.read_feather(src_dir / "road_crossings.feather", columns=["id", "State"])


# Calculate summary stats for entire analysis area
stats = {
    "total": {
        "dams": len(dams),
        "on_network_dams": int(dams.OnNetwork.sum()),
        # NOTE: perennial dams are on-network (raw networks) but not on intermittent segments
        "perennial_dams": int(dams.OnNetwork_perennial.sum()),
        # TODO: this may not be useful for entire data extent; revisit / remove
        "miles": round(dams.GainMiles.mean().item(), 3),
        "perennial_miles": round(dams.GainMiles_perennial.mean().item(), 3),
        "total_barriers": len(barriers),
        "barriers": int(barriers.Included.sum()),
        "on_network_barriers": int(barriers.OnNetwork.sum()),
        "perennial_barriers": int(barriers.OnNetwork_perennial.sum()),
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
            "on_network_dams": int(region_dams.OnNetwork.sum()),
            "perennial_dams": int(region_dams.OnNetwork_perennial.sum()),
            "miles": round(region_dams.GainMiles.mean().item(), 3),
            "perennial_miles": round(region_dams.GainMiles_perennial.mean().item(), 3),
            "total_barriers": len(region_barriers),
            "barriers": int(region_barriers.Included.sum()),
            "on_network_barriers": int(region_barriers.OnNetwork.sum()),
            "perennial_barriers": int(region_barriers.OnNetwork_perennial.sum()),
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
