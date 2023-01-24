from pathlib import Path
import warnings
import pyarrow as pa

import pyarrow.compute as pc
import numpy as np

from analysis.lib.io import read_feathers
from analysis.rank.lib.metrics import (
    classify_gain_miles,
    classify_ocean_miles,
    classify_percent_altered,
    classify_ocean_barriers,
)
from api.lib.tiers import calculate_tiers, METRICS


NETWORK_COLUMNS = [
    "id",
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


def get_network_results(df, network_type, state_ranks=False):
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
    state_ranks : bool, optional (default: False)
        if True, results will include tiers for the state level

    Returns
    -------
    DataFrame
        Contains network metrics and tiers
    """

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

    # join back to df using inner join, which limits to barrier types present in df
    networks = networks.join(
        df[df.columns.intersection(["Unranked", "State"])], how="inner"
    )

    # sanity check to make sure no duplicate networks
    if networks.groupby(level=0).size().max() > 1:
        raise Exception(
            f"ERROR: multiple networks found for some {network_type} networks"
        )

    networks["HasNetwork"] = True
    networks["Ranked"] = networks.HasNetwork & (~networks.Unranked)

    # update data types and calculate total fields
    # calculate size classes GAINED instead of total
    # doesn't apply to those that don't have upstream networks
    networks["SizeClasses"] = networks.SizeClasses.astype("int8")
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
    networks["GainMilesClass"] = classify_gain_miles(networks.GainMiles)
    networks["PercentAlteredClass"] = classify_percent_altered(networks.PercentAltered)

    # Diadromous related filters - must have FlowsToOcean == True
    networks["DownstreamOceanMilesClass"] = classify_ocean_miles(networks.MilesToOutlet)

    # NOTE: per guidance from SARP, do not include count of waterfalls
    if network_type == "dams":
        num_downstream = networks.TotalDownstreamDams
    elif network_type == "small_barriers":
        num_downstream = (
            +networks.TotalDownstreamDams + networks.TotalDownstreamSmallBarriers
        )

    networks["DownstreamOceanBarriersClass"] = classify_ocean_barriers(num_downstream)

    ix = ~networks.FlowsToOcean
    networks.loc[ix, "DownstreamOceanMilesClass"] = 0
    networks.loc[ix, "DownstreamOceanBarriersClass"] = 0

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

    for col in ("Landcover", "FlowsToOcean", "ExitsRegion"):
        networks[col] = networks[col].astype("int8")

    if not state_ranks:
        return networks.drop(columns=["Unranked", "State"])

    ### Calculate state tiers for each of total and perennial
    # (exclude unranked invasive spp. barriers / no structure diversions)
    # NOTE: tiers are calculated using a pyarrow Table
    to_rank = pa.Table.from_pandas(
        networks.loc[~networks.Unranked, ["State"] + METRICS].reset_index()
    )

    merged = []
    for state in to_rank["State"].unique():
        subset = to_rank.filter(pc.equal(to_rank["State"], state))
        tiers = calculate_tiers(subset).add_column(
            0, subset.schema.field("id"), subset["id"]
        )
        merged.append(tiers)

    state_tiers = pa.concat_tables(merged).combine_chunks().to_pandas().set_index("id")
    state_tiers.rename(
        columns={col: f"State_{col}" for col in state_tiers.columns}, inplace=True
    )

    networks = networks.join(state_tiers)
    for col in [col for col in networks.columns if col.endswith("_tier")]:
        networks[col] = networks[col].fillna(np.int8(-1)).astype("int8")

    return networks.drop(columns=["Unranked", "State"])
