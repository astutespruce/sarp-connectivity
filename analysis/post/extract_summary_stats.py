from pathlib import Path
import json

import pandas as pd

from analysis.constants import STATES, REGION_STATES
from analysis.lib.io import read_feathers


data_dir = Path("data")
src_dir = data_dir / "barriers/master"
api_dir = data_dir / "api"
ui_data_dir = Path("ui/data")


### Read dams
dams = pd.read_feather(
    api_dir / "dams.feather",
    columns=["id", "HUC2", "HasNetwork", "Ranked", "Removed", "State"],
).set_index("id", drop=False)
# Get recon from master
dams_master = pd.read_feather(
    src_dir / "dams.feather", columns=["id", "Recon"]
).set_index("id")
dams = dams.join(dams_master)

# get stats for removed dams
removed_dam_networks = (
    read_feathers(
        [
            Path("data/networks/clean") / huc2 / "removed_dams_network.feather"
            for huc2 in sorted(dams.HUC2.unique())
        ],
        columns=["id", "EffectiveGainMiles"],
    )
    .set_index("id")
    .EffectiveGainMiles.rename("RemovedGainMiles")
)
dams = dams.join(removed_dam_networks)
dams["RemovedGainMiles"] = dams.RemovedGainMiles.fillna(0)

### Read road-related barriers
barriers = pd.read_feather(
    api_dir / "small_barriers.feather",
    columns=["id", "HasNetwork", "Ranked", "Removed", "State"],
).set_index("id", drop=False)
barriers_master = pd.read_feather(
    "data/barriers/master/small_barriers.feather", columns=["id", "dropped", "excluded"]
).set_index("id")

barriers = barriers.join(barriers_master)

removed_barrier_networks = (
    read_feathers(
        [
            Path("data/networks/clean")
            / huc2
            / "removed_combined_barriers_network.feather"
            for huc2 in sorted(dams.HUC2.unique())
        ],
        columns=["id", "EffectiveGainMiles"],
    )
    .set_index("id")
    .EffectiveGainMiles.rename("RemovedGainMiles")
)
barriers = barriers.join(removed_barrier_networks)
barriers["RemovedGainMiles"] = barriers.RemovedGainMiles.fillna(0)

# barriers that were not dropped or excluded are likely to have impacts
barriers["Included"] = ~(barriers.dropped | barriers.excluded)


largefish_barriers = pd.read_feather(
    api_dir / "largefish_barriers.feather",
    columns=["id", "BarrierType", "Ranked"],
)

smallfish_barriers = pd.read_feather(
    api_dir / "smallfish_barriers.feather",
    columns=["id", "BarrierType", "Ranked"],
)


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
        "ranked_largefish_barriers_dams": int(
            (
                largefish_barriers.loc[largefish_barriers.BarrierType == "dams"].Ranked
            ).sum()
        ),
        "ranked_smallfish_barriers_dams": int(
            (
                smallfish_barriers.loc[largefish_barriers.BarrierType == "dams"].Ranked
            ).sum()
        ),
        "removed_dams": int(analysis_dams.Removed.sum()),
        "removed_dams_gain_miles": float(analysis_dams.RemovedGainMiles.sum()),
        "total_small_barriers": len(analysis_barriers),
        "small_barriers": int(analysis_barriers.Included.sum()),
        "ranked_small_barriers": int(analysis_barriers.Ranked.sum()),
        "ranked_largefish_barriers_small_barriers": int(
            (
                largefish_barriers.loc[
                    largefish_barriers.BarrierType == "small_barriers"
                ].Ranked
            ).sum()
        ),
        "ranked_smallfish_barriers_small_barriers": int(
            (
                smallfish_barriers.loc[
                    largefish_barriers.BarrierType == "small_barriers"
                ].Ranked
            ).sum()
        ),
        "removed_small_barriers": int(analysis_barriers.Removed.sum()),
        "removed_small_barriers_gain_miles": float(
            analysis_barriers.RemovedGainMiles.sum()
        ),
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
            "removed_dams": int(region_dams.Removed.sum()),
            "removed_dams_gain_miles": float(region_dams.RemovedGainMiles.sum()),
            "total_small_barriers": len(region_barriers),
            "small_barriers": int(region_barriers.Included.sum()),
            "ranked_small_barriers": int(region_barriers.Ranked.sum()),
            "removed_small_barriers": int(region_barriers.Removed.sum()),
            "removed_small_barriers_gain_miles": float(
                region_barriers.RemovedGainMiles.sum()
            ),
            "crossings": len(region_crossings),
        }
    )

stats["region"] = region_stats


# only extract core counts in states for data download page,
# as other stats are joined to state vector tiles elsewhere
state_stats = []
for state in sorted(STATES.keys()):
    state_dams = dams.loc[dams.State == state]
    state_barriers = barriers.loc[barriers.State == state]

    state_stats.append(
        {
            "id": state,
            "dams": int(len(state_dams)),
            "recon_dams": int((state_dams.Recon > 0).sum()),
            "removed_dams": int(state_dams.Removed.sum()),
            "removed_dams_gain_miles": float(state_dams.RemovedGainMiles.sum()),
            "total_small_barriers": int(len(state_barriers)),
            "small_barriers": int(state_barriers.Included.sum()),
            "removed_small_barriers": int(state_barriers.Removed.sum()),
            "removed_small_barriers_gain_miles": float(
                region_barriers.RemovedGainMiles.sum()
            ),
        }
    )
stats["State"] = state_stats

# Write the summary statistics into the UI directory so that it can be imported at build time
# into the code
with open(ui_data_dir / "summary_stats.json", "w") as outfile:
    outfile.write(json.dumps(stats))
