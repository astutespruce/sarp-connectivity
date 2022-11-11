from pathlib import Path
import warnings

from analysis.lib.io import read_feathers
from analysis.rank.lib.metrics import classify_gainmiles, classify_percent_altered
from analysis.rank.lib.tiers import calculate_tiers
from analysis.lib.util import append

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


NETWORK_COLUMNS = [
    "id",
    "kind",
    "upNetID",
    "downNetID",
    "TotalUpstreamMiles",
    "PerennialUpstreamMiles",
    "AlteredUpstreamMiles",
    "UnalteredUpstreamMiles",
    "PerennialUnalteredUpstreamMiles",
    "TotalDownstreamMiles",
    "FreeDownstreamMiles",
    "FreePerennialDownstreamMiles",
    "FreeAlteredDownstreamMiles",
    "FreeUnalteredDownstreamMiles",
    # "FreePerennialUnalteredDownstreamMiles",  # not nused
    "PercentUnaltered",
    "PercentPerennialUnaltered",
    "IntermittentUpstreamMiles",
    "FreeIntermittentDownstreamMiles",
    "natfldpln",
    "sizeclasses",
    # "barrier",  # not used
    "fn_dakm2",
    "fn_waterfalls",
    "fn_dams",
    "fn_small_barriers",
    "fn_road_crossings",
    "fn_headwaters",
    "cat_waterfalls",
    "cat_dams",
    "cat_small_barriers",
    "cat_road_crossings",
    "tot_waterfalls",
    "tot_dams",
    "tot_small_barriers",
    "tot_headwaters",
    "tot_road_crossings",
    "totd_waterfalls",
    "totd_dams",
    "totd_small_barriers",
    "totd_road_crossings",
    "miles_to_outlet",
    "flows_to_ocean",
    "exits_region",
]


NETWORK_COLUMN_NAMES = {
    "natfldpln": "Landcover",
    "sizeclasses": "SizeClasses",
    "fn_dakm2": "UpstreamDrainageArea",
    "fn_dams": "UpstreamDams",
    "fn_small_barriers": "UpstreamSmallBarriers",
    "fn_road_crossings": "UpstreamRoadCrossings",
    "fn_waterfalls": "UpstreamWaterfalls",
    "fn_headwaters": "UpstreamHeadwaters",
    "cat_dams": "UpstreamCatchmentDams",
    "cat_small_barriers": "UpstreamCatchmentSmallBarriers",
    "cat_road_crossings": "UpstreamCatchmentRoadCrossings",
    "cat_waterfalls": "UpstreamCatchmentWaterfalls",
    "tot_dams": "TotalUpstreamDams",
    "tot_small_barriers": "TotalUpstreamSmallBarriers",
    "tot_road_crossings": "TotalUpstreamRoadCrossings",
    "tot_waterfalls": "TotalUpstreamWaterfalls",
    "tot_headwaters": "TotalUpstreamHeadwaters",
    "totd_dams": "TotalDownstreamDams",
    "totd_road_crossings": "TotalDownstreamRoadCrossings",
    "totd_small_barriers": "TotalDownstreamSmallBarriers",
    "totd_waterfalls": "TotalDownstreamWaterfalls",
    "miles_to_outlet": "MilesToOutlet",
    "flows_to_ocean": "FlowsToOcean",
    "exits_region": "ExitsRegion",
}


def get_network_results(df, network_type, barrier_types=None, state_ranks=False):
    """Read network results, calculate derived metric classes, and calculate
    tiers.

    Only barriers that are not unranked (invasive spp barriers, diversions) have
    tiers calculated.

    Parameters
    ----------
    df : DataFrame
        barriers data; must contain State and Unranked
    network_type : {"dams", "small_barriers"}
        network scenario; note that small_barriers includes the network already
        cut by dams
    barrier_types : list-like, optional (default: None)
        barrier types to extract from the network data, one or more of "dams",
        "small_barriers", "waterfalls". If omitted, will default to match
        network_type
    state_ranks : bool, optional (default: False)
        if True, results will include tiers for the state level

    Returns
    -------
    DataFrame
        Contains network metrics and tiers
    """

    barrier_types = barrier_types or [network_type]

    networks = (
        read_feathers(
            [
                Path("data/networks/clean") / huc2 / f"{network_type}_network.feather"
                for huc2 in sorted(df.HUC2.unique())
            ],
            columns=NETWORK_COLUMNS,
        )
        .rename(columns=NETWORK_COLUMN_NAMES)
        .set_index("id")
    )

    # select barrier type
    # NOTE: kind is the singular form of barrier type
    kinds = [t[:-1] for t in barrier_types]
    networks = networks.loc[networks.kind.isin(kinds)].drop(columns=["kind"])

    # Convert dtypes to allow missing data when joined to barriers later
    # NOTE: upNetID or downNetID may be 0 if there aren't networks on that side, but
    # we set to int dtype instead of uint to allow -1 for missing data later
    for col in ["upNetID", "downNetID"]:
        networks[col] = networks[col].astype("int")

    for stat_type in [
        "Upstream",
        "UpstreamCatchment",
        "TotalUpstream",
        "TotalDownstream",
    ]:
        for t in ["Waterfalls", "Dams", "SmallBarriers", "RoadCrossings"]:
            col = f"{stat_type}{t}"
            networks[col] = networks[col].astype("int32")

    for col in ("Landcover", "SizeClasses", "FlowsToOcean", "ExitsRegion"):
        networks[col] = networks[col].astype("int8")

    # sanity check to make sure no duplicate networks
    if networks.groupby(level=0).size().max() > 1:
        raise Exception(
            f"ERROR: multiple networks found for some {network_type} networks"
        )

    networks = networks.join(df[df.columns.intersection(["Unranked", "State"])])

    networks["HasNetwork"] = True
    networks["Ranked"] = networks.HasNetwork & (~networks.Unranked)

    # update data types and calculate total fields
    # calculate size classes GAINED instead of total
    # doesn't apply to those that don't have upstream networks
    networks.loc[networks.SizeClasses > 0, "SizeClasses"] = (
        networks.loc[networks.SizeClasses > 0, "SizeClasses"] - 1
    )

    ### Calculate miles GAINED if barrier is removed
    # this is the lesser of the upstream or free downstream lengths.
    # Non-free miles downstream (downstream waterbodies) are omitted from this analysis.
    networks["GainMiles"] = networks[["TotalUpstreamMiles", "FreeDownstreamMiles"]].min(
        axis=1
    )
    networks["PerennialGainMiles"] = networks[
        ["PerennialUpstreamMiles", "FreePerennialDownstreamMiles"]
    ].min(axis=1)

    # For barriers that terminate in marine areas, their GainMiles is only based on the upstream miles
    ix = (networks.MilesToOutlet == 0) & (networks.FlowsToOcean == 1)
    networks.loc[ix, "GainMiles"] = networks.loc[ix].TotalUpstreamMiles
    networks.loc[ix, "PerennialGainMiles"] = networks.loc[ix].PerennialUpstreamMiles

    # TotalNetworkMiles is sum of upstream and free downstream miles
    networks["TotalNetworkMiles"] = networks[
        ["TotalUpstreamMiles", "FreeDownstreamMiles"]
    ].sum(axis=1)
    networks["TotalPerennialNetworkMiles"] = networks[
        ["PerennialUpstreamMiles", "FreePerennialDownstreamMiles"]
    ].sum(axis=1)

    # Round floating point columns to 3 decimals
    for column in [c for c in networks.columns if c.endswith("Miles")]:
        networks[column] = networks[column].round(3).fillna(-1)

    ### Set PercentUnaltered and PercentAltered to integers
    networks["PercentUnaltered"] = networks.PercentUnaltered.round().astype("int8")
    networks["PercentAltered"] = 100 - networks.PercentUnaltered

    ### Calculate classes used for filtering
    networks["GainMilesClass"] = classify_gainmiles(networks.GainMiles)
    networks["PercentAlteredClass"] = classify_percent_altered(networks.PercentAltered)

    if not state_ranks:
        return networks.drop(columns=["Unranked", "State"])

    # only calculate ranks / tiers for ranked barriers
    # (exclude unranked invasive spp. barriers / no structure diversions)
    to_rank = networks.loc[networks.Unranked == 0]

    ### Calculate state tiers for each of total and perennial
    state_tiers = None
    for state in to_rank.State.unique():
        state_tiers = append(
            state_tiers,
            calculate_tiers(to_rank.loc[to_rank.State == state]).reset_index(),
        )

    state_tiers = state_tiers.set_index("id").rename(
        columns={col: f"State_{col}" for col in state_tiers.columns}
    )

    networks = networks.join(state_tiers)
    for col in [col for col in networks.columns if col.endswith("_tier")]:
        networks[col] = networks[col].fillna(-1).astype("int8")

    return networks.drop(columns=["Unranked", "State"])
