from pathlib import Path
import pyarrow as pa
import warnings

import pandas as pd
import pyarrow.compute as pc
import numpy as np

from api.constants import SPECIES_HABITAT_FIELDS
from analysis.constants import EPA_CAUSE_TO_CODE
from analysis.lib.io import read_arrow_tables
from analysis.rank.lib.metrics import (
    classify_gain_miles,
    classify_mainstem_gain_miles,
    classify_downstream_miles,
    classify_percent_unaltered,
    classify_percent_resilient,
    classify_percent_cold,
    classify_downstream_barriers,
    classify_unaltered_waterbody_area,
    classify_unaltered_wetland_area,
)
from api.lib.tiers import calculate_tiers, METRICS

# TODO: convert some operations to pyarrow instead and then to pandas at the end;
# then remove this filter
warnings.filterwarnings("ignore", message=".*This is usually the result of calling `frame.insert`.*")


NETWORK_COLUMNS = [
    "id",
    # "kind", # not used
    # "HUC2", # not used
    "upNetID",
    "downNetID",
    # upstream / downstream functional network mileage
    "TotalUpstreamMiles",
    "PerennialUpstreamMiles",
    "IntermittentUpstreamMiles",
    "AlteredUpstreamMiles",
    "UnalteredUpstreamMiles",
    "PerennialUnalteredUpstreamMiles",
    "ResilientUpstreamMiles",
    "ColdUpstreamMiles",
    "TotalDownstreamMiles",
    "FreeDownstreamMiles",
    "FreePerennialDownstreamMiles",
    "FreeIntermittentDownstreamMiles",
    "FreeAlteredDownstreamMiles",
    "FreeUnalteredDownstreamMiles",
    # "FreePerennialUnalteredDownstreamMiles", # not used
    "FreeResilientDownstreamMiles",
    "FreeColdDownstreamMiles",
    "GainMiles",
    "FunctionalNetworkMiles",
    "PerennialGainMiles",
    "PerennialFunctionalNetworkMiles",
    # other upstream functional network statistics
    "PercentUnaltered",
    "PercentPerennialUnaltered",
    "PercentResilient",
    "PercentCold",
    "Landcover",
    "SizeClasses",
    "PerennialSizeClasses",
    "UnalteredWaterbodyAcres",
    "UnalteredWetlandAcres",
    "UpstreamDrainageAcres",
    # "FloodplainAcres", # not used
    # "NatFloodplainAcres", # not used
    "HasUpstreamEJTract",
    "HasUpstreamEJTribal",
    # upstream functional and total barrier counts
    "UpstreamWaterfalls",
    "UpstreamDams",
    "UpstreamSmallBarriers",
    "UpstreamRoadCrossings",
    "UpstreamHeadwaters",
    "TotalUpstreamWaterfalls",
    "TotalUpstreamDams",
    "TotalUpstreamSmallBarriers",
    "TotalUpstreamRoadCrossings",
    "TotalUpstreamHeadwaters",
    # upstream / downstream mainstem mileage
    "TotalMainstemUpstreamMiles",
    "PerennialMainstemUpstreamMiles",
    "IntermittentMainstemUpstreamMiles",
    "AlteredMainstemUpstreamMiles",
    "UnalteredMainstemUpstreamMiles",
    "PerennialUnalteredMainstemUpstreamMiles",
    "TotalMainstemDownstreamMiles",
    "FreeMainstemDownstreamMiles",
    "FreePerennialMainstemDownstreamMiles",
    "FreeIntermittentMainstemDownstreamMiles",
    "FreeAlteredMainstemDownstreamMiles",
    "FreeUnalteredMainstemDownstreamMiles",
    "MainstemGainMiles",
    "MainstemNetworkMiles",
    "PerennialMainstemGainMiles",
    "PerennialMainstemNetworkMiles",
    # mainstem upstream / downstream EPA impairments (these will be consolidated into a single upstream field and downstream field)
    "HasMainstemUpstreamTemperature",
    "HasMainstemUpstreamCauseUnknownImpairedBiota",
    "HasMainstemUpstreamOxygenDepletion",
    "HasMainstemUpstreamAlgalGrowth",
    "HasMainstemUpstreamFlowAlterations",
    "HasMainstemUpstreamHabitatAlterations",
    "HasMainstemUpstreamHydrologicAlteration",
    "HasMainstemUpstreamCauseUnknownFishKills",
    "HasMainstemDownstreamTemperature",
    "HasMainstemDownstreamCauseUnknownImpairedBiota",
    "HasMainstemDownstreamOxygenDepletion",
    "HasMainstemDownstreamAlgalGrowth",
    "HasMainstemDownstreamFlowAlterations",
    "HasMainstemDownstreamHabitatAlterations",
    "HasMainstemDownstreamHydrologicAlteration",
    "HasMainstemDownstreamCauseUnknownFishKills",
    # other mainstem stats
    "MainstemSizeClasses",
    "PercentMainstemUnaltered",
    # linear downstream mileage
    "TotalLinearDownstreamMiles",
    "FreeLinearDownstreamMiles",
    "FreePerennialLinearDownstreamMiles",
    "FreeIntermittentLinearDownstreamMiles",
    "FreeAlteredLinearDownstreamMiles",
    "FreeUnalteredLinearDownstreamMiles",
    # other linear downstream stats
    "HasLinearDownstreamEJTract",
    "HasLinearDownstreamEJTribal",
    # statistics for bottom of network
    "HasDownstreamInvasiveBarrier",  # renamed to InvasiveNetwork for backward compatibility
    # "OriginHUC2", # not used
    # "FlowsToOcean",  # not used from networks; uses values from barriers master
    # "FlowsToGreatLakes",  # not used from networks; uses values from barriers master
    "MilesToOutlet",
    # total downstream counts
    "TotalDownstreamWaterfalls",
    "TotalDownstreamDams",
    "TotalDownstreamSmallBarriers",
    "TotalDownstreamRoadCrossings",
    # "TotalDownstreamBarriers", # not used
    # upstream / downstream barrier info
    # "UpstreamBarrierID", # not used
    "UpstreamBarrierMiles",
    "UpstreamBarrier",
    "UpstreamBarrierSARPID",
    # "DownstreamBarrierID", # not used
    "DownstreamBarrier",
    "DownstreamBarrierMiles",
    "DownstreamBarrierSARPID",
] + SPECIES_HABITAT_FIELDS


def get_network_results(df, network_type, state_ranks=False):
    """Read network results, calculate derived metric classes, and calculate
    tiers.

    Only barriers that are not unranked (invasive spp barriers, diversions) have
    tiers calculated.

    Parameters
    ----------
    df : DataFrame
        barriers data; must contain State, Unranked, FlowsToOcean, FlowsToGreatLakes
    network_type : {"dams", "combined_barriers", "largefish_barriers", "smallfish_barriers"}
    state_ranks : bool, optional (default: False)
        if True, results will include tiers for the state level

    Returns
    -------
    DataFrame
        Contains network metrics and tiers
    """

    networks = (
        read_arrow_tables(
            [
                Path("data/networks/clean") / huc2 / f"{network_type}_network.feather"
                for huc2 in sorted(df.HUC2.unique())
            ],
            columns=NETWORK_COLUMNS,
        )
        .rename_columns({"HasDownstreamInvasiveBarrier": "InvasiveNetwork"})
        .to_pandas()
        .set_index("id")
    )

    # join back to df using inner join, which limits to barrier types present in df
    networks = networks.join(
        df[df.columns.intersection(["Unranked", "State", "FlowsToOcean", "FlowsToGreatLakes"])], how="inner"
    )

    # sanity check to make sure no duplicate networks
    if networks.groupby(level=0).size().max() > 1:
        raise Exception(f"ERROR: multiple networks found for some {network_type} networks")

    networks["HasNetwork"] = True
    networks["Ranked"] = networks.HasNetwork & (~networks.Unranked)

    # fill species habitat columns; some species are only available for some HUC2s
    spp_cols = [c for c in networks.columns if "Habitat" in c]
    for col in spp_cols:
        networks[col] = networks[col].fillna(0)

    # update data types and calculate total fields
    # calculate size classes GAINED instead of total
    # doesn't apply to those that don't have upstream networks or where size class
    # is unknown for all upstream segments
    for col in ["SizeClasses", "PerennialSizeClasses", "MainstemSizeClasses"]:
        networks[col] = networks[col].astype("int8")
        networks.loc[networks[col] > 0, col] -= 1

    # fill upstream / downstream barrier info
    for col in ["UpstreamBarrier", "UpstreamBarrierSARPID", "DownstreamBarrier", "DownstreamBarrierSARPID"]:
        networks[col] = networks[col].astype("str").fillna("")

    ### Calculate classes used for filtering
    networks["GainMilesClass"] = classify_gain_miles(networks.GainMiles)

    # not available yet for removed barriers, so fill with -1
    if networks.MainstemGainMiles.notnull().sum() > 0:
        networks["MainstemGainMilesClass"] = classify_mainstem_gain_miles(networks.MainstemGainMiles)
    else:
        networks["MainstemGainMilesClass"] = np.int8(-1)

    networks["PercentUnalteredClass"] = classify_percent_unaltered(networks.PercentUnaltered)
    networks["PercentResilientClass"] = classify_percent_resilient(networks.PercentResilient)
    networks["PercentColdClass"] = classify_percent_cold(networks.PercentCold)

    networks["UnalteredWaterbodyClass"] = classify_unaltered_waterbody_area(networks.UnalteredWaterbodyAcres)
    networks["UnalteredWetlandClass"] = classify_unaltered_wetland_area(networks.UnalteredWetlandAcres)

    # NOTE: per guidance from SARP, do not include count of waterfalls
    if network_type == "dams":
        num_downstream = networks.TotalDownstreamDams
    else:
        num_downstream = networks.TotalDownstreamDams + networks.TotalDownstreamSmallBarriers

    # Diadromous related filters - must have FlowsToOcean == True
    networks["DownstreamOceanMilesClass"] = classify_downstream_miles(networks.MilesToOutlet)
    networks["DownstreamOceanBarriersClass"] = classify_downstream_barriers(num_downstream)
    ix = networks.FlowsToOcean == 0
    networks.loc[ix, "DownstreamOceanMilesClass"] = 0
    networks.loc[ix, "DownstreamOceanBarriersClass"] = 0

    # similar for Great Lakes
    networks["DownstreamGreatLakesMilesClass"] = classify_downstream_miles(networks.MilesToOutlet)
    networks["DownstreamGreatLakesBarriersClass"] = classify_downstream_barriers(num_downstream)
    ix = networks.FlowsToGreatLakes == 0
    networks.loc[ix, "DownstreamGreatLakesMilesClass"] = 0
    networks.loc[ix, "DownstreamGreatLakesBarriersClass"] = 0

    # Convert dtypes to allow missing data when joined to barriers later
    # NOTE: upNetID or downNetID may be 0 if there aren't networks on that side, but
    # we set to int dtype instead of uint to allow -1 for missing data later
    for col in ["upNetID", "downNetID"]:
        networks[col] = networks[col].astype("int64")

    for stat_type in [
        "Upstream",
        "TotalUpstream",
        "TotalDownstream",
    ]:
        for t in ["Waterfalls", "Dams", "SmallBarriers", "RoadCrossings"]:
            col = f"{stat_type}{t}"
            networks[col] = networks[col].astype("int32")

    for col in ("Landcover",):
        networks[col] = networks[col].astype("int8")

    # Consolidate upstream / downstream EPA impairments into codes
    # TODO: could probably use bit-packing for this if we can filter by this in UI
    # TODO: convert to coded domain when saving file
    upstream_cols = []
    downstream_cols = []
    for key in EPA_CAUSE_TO_CODE.keys():
        suffix = key.title().replace("_", "")
        upstream_col = f"HasMainstemUpstream{suffix}"
        upstream_cols.append(upstream_col)
        downstream_col = f"HasMainstemDownstream{suffix}"
        downstream_cols.append(downstream_col)
        networks[upstream_col] = networks[upstream_col].map({False: "", True: EPA_CAUSE_TO_CODE[key]})
        networks[downstream_col] = networks[downstream_col].map({False: "", True: EPA_CAUSE_TO_CODE[key]})

    networks["MainstemUpstreamImpairment"] = networks[upstream_cols].apply(
        lambda row: ",".join([x for x in row if x]), axis=1
    )
    networks["MainstemDownstreamImpairment"] = networks[downstream_cols].apply(
        lambda row: ",".join([x for x in row if x]), axis=1
    )
    networks = networks.drop(columns=upstream_cols + downstream_cols)

    if not state_ranks:
        return networks.drop(columns=["Unranked", "State", "FlowsToOcean", "FlowsToGreatLakes"])

    ### Calculate state tiers for each of total and perennial
    # (exclude unranked invasive spp. barriers / no structure diversions)
    # NOTE: tiers are calculated using a pyarrow Table
    to_rank = pa.Table.from_pandas(networks.loc[~networks.Unranked, ["State"] + METRICS].reset_index())

    merged = []
    for state in to_rank["State"].unique():
        subset = to_rank.filter(pc.equal(to_rank["State"], state))
        tiers = calculate_tiers(subset).add_column(0, subset.schema.field("id"), subset["id"])
        merged.append(tiers)

    state_tiers = pa.concat_tables(merged).combine_chunks().to_pandas().set_index("id")
    state_tiers.rename(columns={col: f"State_{col}" for col in state_tiers.columns}, inplace=True)

    networks = networks.join(state_tiers)
    for col in [col for col in networks.columns if col.endswith("_tier")]:
        networks[col] = networks[col].fillna(np.int8(-1)).astype("int8")

    return networks.drop(columns=["Unranked", "State", "FlowsToOcean", "FlowsToGreatLakes"])


def get_removed_network_results(df, network_type):
    """Read network results for removed barriers.

    Parameters
    ----------
    df : DataFrame
        barriers data; must contain State and Unranked
    network_type : {"dams", "combined_barriers", "largefish_barriers", "smallfish_barriers"}

    Returns
    -------
    DataFrame
        Contains network metrics
    """

    networks = pd.read_feather(f"data/networks/clean/removed/removed_{network_type}_networks.feather").set_index("id")
    # NOTE: many columns are not calculated for removed barriers
    networks = networks[[c for c in NETWORK_COLUMNS if c in networks.columns]].rename(
        columns={"HasDownstreamInvasiveBarrier": "InvasiveNetwork"}
    )

    # join back to df using inner join, which limits to barrier types present in df
    networks = networks.join(df[df.columns.intersection(["Unranked", "State"])], how="inner")

    # sanity check to make sure no duplicate networks
    if networks.groupby(level=0).size().max() > 1:
        raise Exception(f"ERROR: multiple networks found for some {network_type} networks")

    networks["HasNetwork"] = True
    networks["Ranked"] = False

    # fill species habitat columns; some species are only available for some HUC2s
    spp_cols = [c for c in networks.columns if "Habitat" in c]
    for col in spp_cols:
        networks[col] = networks[col].fillna(0)

    # update data types and calculate total fields
    # calculate size classes GAINED instead of total
    # doesn't apply to those that don't have upstream networks
    networks["SizeClasses"] = networks.SizeClasses.astype("int8")
    networks.loc[networks.SizeClasses > 0, "SizeClasses"] = networks.loc[networks.SizeClasses > 0, "SizeClasses"] - 1

    # Convert dtypes to allow missing data when joined to barriers later
    for col in ["upNetID", "downNetID"]:
        # Force to -1 since these aren't part of standard networks
        networks[col] = np.int64(-1)

    for col in ("Landcover",):
        networks[col] = networks[col].astype("int8")

    return networks.drop(columns=["Unranked", "State"])
