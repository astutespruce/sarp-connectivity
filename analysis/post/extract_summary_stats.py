from pathlib import Path
import json

import geopandas as gp
import numpy as np
import pandas as pd

from analysis.constants import STATES
from analysis.post.lib.removed_barriers import calc_year_removed_bin, pack_year_removed_stats


data_dir = Path("data")
src_dir = data_dir / "barriers/master"
results_dir = data_dir / "barriers/networks"
ui_data_dir = Path("ui/data")

# Outputs are written to the UI directory so they can be imported at build time
# into the UI code


### Read dams
dams = pd.read_feather(
    results_dir / "dams.feather",
    columns=["id", "HUC2", "HasNetwork", "Ranked", "Removed", "YearRemoved", "Private", "State"],
).set_index("id", drop=False)
# Get recon from master
dams_master = pd.read_feather(src_dir / "dams.feather", columns=["id", "Recon"]).set_index("id")
dams = dams.join(dams_master)


# do not include private barriers in top-level stats
dams = dams.loc[~dams.Private].copy()

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
    columns=["id", "HasNetwork", "Ranked", "Removed", "YearRemoved", "Private", "State"],
).set_index("id", drop=False)
barriers_master = pd.read_feather(
    "data/barriers/master/small_barriers.feather", columns=["id", "dropped", "excluded"]
).set_index("id")
barriers = barriers.join(barriers_master)

barriers = barriers.loc[~barriers.Private].copy()

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


# barriers that were not excluded are likely to have impacts
# (dropped / duplicates are already removed from above)
barriers["Included"] = ~barriers.excluded


largefish_barriers = pd.read_feather(
    results_dir / "largefish_barriers.feather",
    columns=["id", "BarrierType", "Ranked", "Private"],
)
largefish_barriers = largefish_barriers.loc[~largefish_barriers.Private].copy()

smallfish_barriers = pd.read_feather(
    results_dir / "smallfish_barriers.feather",
    columns=["id", "BarrierType", "Ranked", "Private"],
)
smallfish_barriers = smallfish_barriers.loc[~smallfish_barriers.Private].copy()


### Read road / stream crossings
crossings = pd.read_feather(src_dir / "road_crossings.feather", columns=["id", "State", "Surveyed"])

bounds = (
    gp.read_feather(data_dir / "boundaries/region_boundary.feather")
    .set_index("id")
    .bounds.round(2)
    .apply(list, axis=1)
    .rename("bbox")
    .to_dict()
)


### Calculate summary stats for entire analysis area
# NOTE: this is limited to the states fully within the analysis region and excludes
# HUC4s that cross their borders

analysis_states = STATES.keys()
analysis_dams = dams.loc[dams.State.isin(analysis_states)]
analysis_barriers = barriers.loc[barriers.State.isin(analysis_states)]
analysis_crossings = crossings.loc[crossings.State.isin(analysis_states)]

stats = {
    "bounds": bounds["total"],
    "dams": len(analysis_dams),
    "ranked_dams": int(analysis_dams.Ranked.sum()),
    "recon_dams": int((analysis_dams.Recon > 0).sum()),
    "ranked_largefish_barriers_dams": int(
        (largefish_barriers.loc[largefish_barriers.BarrierType == "dams"].Ranked).sum()
    ),
    "ranked_smallfish_barriers_dams": int(
        (smallfish_barriers.loc[largefish_barriers.BarrierType == "dams"].Ranked).sum()
    ),
    "removed_dams": int(analysis_dams.Removed.sum()),
    "removed_dams_gain_miles": round(analysis_dams.RemovedGainMiles.sum().item(), 1),
    "removed_dams_by_year": pack_year_removed_stats(analysis_dams),
    "total_small_barriers": len(analysis_barriers),
    "small_barriers": int(analysis_barriers.Included.sum()),
    "ranked_small_barriers": int(analysis_barriers.Ranked.sum()),
    "ranked_largefish_barriers_small_barriers": int(
        (largefish_barriers.loc[largefish_barriers.BarrierType == "small_barriers"].Ranked).sum()
    ),
    "ranked_smallfish_barriers_small_barriers": int(
        (smallfish_barriers.loc[largefish_barriers.BarrierType == "small_barriers"].Ranked).sum()
    ),
    "removed_small_barriers": int(analysis_barriers.Removed.sum()),
    "removed_small_barriers_gain_miles": round(analysis_barriers.RemovedGainMiles.sum().item(), 1),
    "removed_small_barriers_by_year": pack_year_removed_stats(analysis_barriers),
    "total_road_crossings": int(len(analysis_crossings)),
    "unsurveyed_road_crossings": int((crossings.Surveyed == 0).sum()),
}

with open(ui_data_dir / "summary_stats.json", "w") as outfile:
    _ = outfile.write(json.dumps(stats))
