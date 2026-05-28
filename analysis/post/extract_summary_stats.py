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
    columns=[
        "id",
        "HUC2",
        "HasNetwork",
        "Ranked",
        "Removed",
        "YearRemoved",
        "Estimated",
        "State",
        "LowheadDam",
        "Purpose",
        "FERCRegulated",
        "Condition",
        "Hazard",
        "Fatality",
        "TESpp",
        "DiadromousHabitat",
        "TotalUpstreamMiles",
        "TotalDownstreamWaterfalls",
        "TotalDownstreamDams",
        "TotalDownstreamSmallBarriers",
    ],
).set_index("id", drop=False)
# Get recon from master
dams_master = pd.read_feather(
    src_dir / "dams.feather",
    columns=["id", "Recon"],
).set_index("id")
dams = dams.join(dams_master)

# get stats for removed dams
removed_dam_networks = (
    pd.read_feather(
        data_dir / "networks/clean/removed/removed_dams_networks.feather",
        columns=["id", "EffectiveGainMiles", "EffectiveTotalUpstreamMiles", "FreeDownstreamMiles"],
    )
    .set_index("id")
    .rename(
        columns={
            "EffectiveGainMiles": "RemovedGainMiles",
            "EffectiveTotalUpstreamMiles": "RemovedUpstreamMiles",
            "FreeDownstreamMiles": "RemovedDownstreamMiles",
        }
    )
)
dams = dams.join(removed_dam_networks)
for col in ["RemovedGainMiles", "RemovedUpstreamMiles", "RemovedDownstreamMiles"]:
    dams[col] = dams[col].fillna(0)

# fix YearRemoved and bin
dams.loc[~dams.Removed, "YearRemoved"] = np.nan
dams.loc[(dams.YearRemoved > 0) & (dams.YearRemoved < 1900), "YearRemoved"] = np.uint16(0)
dams.loc[(dams.YearRemoved > 0) & (dams.YearRemoved < 2000), "YearRemoved"] = 1
dams["YearRemoved"] = calc_year_removed_bin(dams.YearRemoved)


### Read road-related barriers
barriers = pd.read_feather(
    results_dir / "small_barriers.feather",
    columns=[
        "id",
        "HasNetwork",
        "Ranked",
        "Removed",
        "YearRemoved",
        "State",
        "TotalUpstreamMiles",
        "TotalDownstreamWaterfalls",
        "TotalDownstreamDams",
        "TotalDownstreamSmallBarriers",
    ],
).set_index("id", drop=False)
barriers_master = pd.read_feather(
    "data/barriers/master/small_barriers.feather", columns=["id", "dropped", "excluded"]
).set_index("id")
barriers = barriers.join(barriers_master)

removed_barrier_networks = (
    pd.read_feather(
        data_dir / "networks/clean/removed/removed_combined_barriers_networks.feather",
        columns=["id", "EffectiveGainMiles", "EffectiveTotalUpstreamMiles", "FreeDownstreamMiles"],
    )
    .set_index("id")
    .rename(
        columns={
            "EffectiveGainMiles": "RemovedGainMiles",
            "EffectiveTotalUpstreamMiles": "RemovedUpstreamMiles",
            "FreeDownstreamMiles": "RemovedDownstreamMiles",
        }
    )
)
barriers = barriers.join(removed_barrier_networks)
for col in ["RemovedGainMiles", "RemovedUpstreamMiles", "RemovedDownstreamMiles"]:
    barriers[col] = barriers[col].fillna(0)

barriers.loc[~barriers.Removed, "YearRemoved"] = np.nan
barriers.loc[(barriers.YearRemoved > 0) & (barriers.YearRemoved < 1900), "YearRemoved"] = np.uint16(0)
barriers.loc[(barriers.YearRemoved > 0) & (barriers.YearRemoved < 2000), "YearRemoved"] = 1
barriers["YearRemoved"] = calc_year_removed_bin(barriers.YearRemoved)


# barriers that were not excluded are likely to have impacts
# (dropped / duplicates are already removed from above)
barriers["Included"] = ~barriers.excluded


largefish_barriers = pd.read_feather(
    results_dir / "largefish_barriers.feather",
    columns=["id", "BarrierType", "Ranked"],
)

smallfish_barriers = pd.read_feather(
    results_dir / "smallfish_barriers.feather",
    columns=["id", "BarrierType", "Ranked"],
)


### Read road / stream crossings
crossings = pd.read_feather(
    src_dir / "road_crossings.feather",
    columns=[
        "id",
        "State",
        "Surveyed",
        "TESpp",
        "DiadromousHabitat",
    ],
)


### Waterfalls
waterfalls = pd.read_feather(
    src_dir / "waterfalls.feather",
    columns=[
        "id",
        "State",
        "primary_network",
        "Passability",
        "TESpp",
        "DiadromousHabitat",
    ],
)
waterfalls = waterfalls.loc[waterfalls.primary_network].copy()


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
analysis_waterfalls = waterfalls.loc[waterfalls.State.isin(analysis_states)]

stats = {
    "bounds": bounds["total"],
    # dam stats
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
    # special-purpose dam stats
    # true and likely lowhead dams
    "lowhead_dams": int(analysis_dams.LowheadDam.isin([1, 2]).sum()),
    "fatality_dams": int((analysis_dams.Fatality > 0).sum()),
    # hydropower dams
    "hydro_dams": int(((analysis_dams.Purpose == 6) | (dams.FERCRegulated.isin([1, 2, 3, 4]))).sum()),
    # high and significant hazard dams
    "high_hazard_dams": int(analysis_dams.Hazard.isin([1, 2]).sum()),
    "poor_condition_dams": int(analysis_dams.Condition.isin([3, 4]).sum()),
    "te_spp_dams": int((analysis_dams.TESpp > 0).sum()),
    "diadromous_habitat_dams": int((analysis_dams.DiadromousHabitat == 1).sum()),
    "no_downstream_barrier_dams": int(
        (
            (analysis_dams.TotalDownstreamDams == 0)
            & (analysis_dams.TotalDownstreamWaterfalls == 0)
            & (analysis_dams.TotalDownstreamSmallBarriers == 0)
        ).sum()
    ),
    "total_dam_upstream_miles": round(analysis_dams.TotalUpstreamMiles.sum().item(), 1),
    "estimated_dams": int(analysis_dams.Estimated.sum()),
    # surveyed road crossing stats
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
    "total_small_barrier_upstream_miles": round(analysis_barriers.TotalUpstreamMiles.sum().item(), 1),
    "no_downstream_barrier_small_barriers": int(
        (
            (analysis_barriers.TotalDownstreamDams == 0)
            & (analysis_barriers.TotalDownstreamWaterfalls == 0)
            & (analysis_barriers.TotalDownstreamSmallBarriers == 0)
        ).sum()
    ),
    # road crossing stats
    "total_road_crossings": int(len(analysis_crossings)),
    "unsurveyed_road_crossings": int((crossings.Surveyed == 0).sum()),
    "te_spp_road_crossings": int((analysis_crossings.TESpp > 0).sum()),
    "diadromous_habitat_road_crossings": int((analysis_crossings.DiadromousHabitat == 1).sum()),
    # waterfall stats
    "waterfalls": int(len(waterfalls)),
    "passability_waterfalls": int((waterfalls.Passability > 0).sum()),
    "passable_waterfalls": int((waterfalls.Passability >= 2).sum()),
    "te_spp_waterfalls": int((waterfalls.TESpp > 0).sum()),
    "diadromous_habitat_waterfalls": int((waterfalls.DiadromousHabitat == 1).sum()),
}

with open(ui_data_dir / "summary_stats.json", "w") as outfile:
    _ = outfile.write(json.dumps(stats))
