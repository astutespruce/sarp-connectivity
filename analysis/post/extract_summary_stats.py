from pathlib import Path
import json

import pandas as pd

from analysis.constants import STATES, REGION_STATES


data_dir = Path("data")
src_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
ui_data_dir = Path("ui/data")


### Read dams
dams = pd.read_feather(
    api_dir / "dams.feather",
    columns=["id", "HasNetwork", "Ranked", "State"],
).set_index("id", drop=False)
# Get recon from master
dams_master = pd.read_feather(
    src_dir / "dams.feather", columns=["id", "Recon"]
).set_index("id")
dams = dams.join(dams_master)

### Read road-related barriers
barriers = pd.read_feather(
    api_dir / "small_barriers.feather",
    columns=["id", "HasNetwork", "Ranked", "State"],
).set_index("id", drop=False)
barriers_master = pd.read_feather(
    "data/barriers/master/small_barriers.feather", columns=["id", "dropped", "excluded"]
).set_index("id")

barriers = barriers.join(barriers_master)

# barriers that were not dropped or excluded are likely to have impacts
barriers["Included"] = ~(barriers.dropped | barriers.excluded)

### Read road / stream crossings
# NOTE: crossings are already de-duplicated against each other and against
# barriers
crossings = pd.read_feather(src_dir / "road_crossings.feather", columns=["id", "State"])


# Calculate summary stats for entire analysis area
# NOTE: this is limited to the states fully within the analysis region and excludes
# HUC4s that cross their borders

analysis_states = STATES.keys()
analysis_dams = dams.loc[dams.State.isin(analysis_states)]
analysis_barriers = barriers.loc[barriers.State.isin(analysis_states)]
analysis_crossings = crossings.loc[crossings.State.isin(analysis_states)]

stats = {
    "total": {
        "dams": len(analysis_dams),
        "ranked_dams": int(analysis_dams.Ranked.sum()),
        "recon_dams": int((analysis_dams.Recon > 0).sum()),
        "total_small_barriers": len(analysis_barriers),
        "small_barriers": int(analysis_barriers.Included.sum()),
        "ranked_small_barriers": int(analysis_barriers.Ranked.sum()),
        "crossings": len(analysis_crossings),
    }
}

# Calculate stats for regions
# NOTE: these are groupings of states and some states may be in multiple regions
region_stats = []
for region, region_states in REGION_STATES.items():
    region_dams = dams.loc[dams.State.isin(region_states)]
    region_barriers = barriers.loc[barriers.State.isin(region_states)]
    region_crossings = crossings.loc[crossings.State.isin(region_states)]

    region_stats.append(
        {
            "id": region,
            "dams": len(region_dams),
            "ranked_dams": int(region_dams.Ranked.sum()),
            "recon_dams": int((region_dams.Recon > 0).sum()),
            "total_small_barriers": len(region_barriers),
            "small_barriers": int(region_barriers.Included.sum()),
            "ranked_small_barriers": int(region_barriers.Ranked.sum()),
            "crossings": len(region_crossings),
        }
    )

stats["region"] = region_stats


# only extract core counts in states for data download page,
# as other stats are joined to state vector tiles below
state_stats = []
for state in sorted(STATES.keys()):
    state_stats.append(
        {
            "id": state,
            "dams": int((dams.State == state).sum()),
            "recon_dams": int((dams.loc[dams.State == state].Recon > 0).sum()),
            "total_small_barriers": int((barriers.State == state).sum()),
            "small_barriers": int(region_barriers.Included.sum()),
        }
    )
stats["State"] = state_stats

# Write the summary statistics into the UI directory so that it can be imported at build time
# into the code
with open(ui_data_dir / "summary_stats.json", "w") as outfile:
    outfile.write(json.dumps(stats))
