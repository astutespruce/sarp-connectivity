from pathlib import Path
import pyarrow as pa

import pandas as pd
import pyarrow.compute as pc
import numpy as np

from analysis.lib.io import read_arrow_tables
from analysis.rank.lib.metrics import (
    classify_gain_miles,
    classify_downstream_miles,
    classify_percent_altered,
    classify_downstream_barriers,
)
from api.lib.tiers import calculate_tiers, METRICS


NETWORK_COLUMNS = [
    "id",
    "upNetID",
    "downNetID",
    "GainMiles",
    "PerennialGainMiles",
    "TotalNetworkMiles",
    "TotalPerennialNetworkMiles",
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
    # "FreePerennialUnalteredDownstreamMiles",  # not used
    "PercentAltered",
    "PercentPerennialAltered",
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
    "flows_to_great_lakes",
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
    "flows_to_great_lakes": "FlowsToGreatLakes",
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
        .to_pandas()
        .rename(columns=NETWORK_COLUMN_NAMES)
        .set_index("id")
    )

    # join back to df using inner join, which limits to barrier types present in df
    networks = networks.join(df[df.columns.intersection(["Unranked", "State"])], how="inner")

    # sanity check to make sure no duplicate networks
    if networks.groupby(level=0).size().max() > 1:
        raise Exception(f"ERROR: multiple networks found for some {network_type} networks")

    networks["HasNetwork"] = True
    networks["Ranked"] = networks.HasNetwork & (~networks.Unranked)

    # update data types and calculate total fields
    # calculate size classes GAINED instead of total
    # doesn't apply to those that don't have upstream networks
    networks["SizeClasses"] = networks.SizeClasses.astype("int8")
    networks.loc[networks.SizeClasses > 0, "SizeClasses"] = networks.loc[networks.SizeClasses > 0, "SizeClasses"] - 1

    ### Calculate classes used for filtering
    networks["GainMilesClass"] = classify_gain_miles(networks.GainMiles)
    networks["PercentAlteredClass"] = classify_percent_altered(networks.PercentAltered)

    # NOTE: per guidance from SARP, do not include count of waterfalls
    if network_type == "dams":
        num_downstream = networks.TotalDownstreamDams
    else:
        num_downstream = networks.TotalDownstreamDams + networks.TotalDownstreamSmallBarriers

    # Diadromous related filters - must have FlowsToOcean == True
    networks["DownstreamOceanMilesClass"] = classify_downstream_miles(networks.MilesToOutlet)
    networks["DownstreamOceanBarriersClass"] = classify_downstream_barriers(num_downstream)
    ix = ~networks.FlowsToOcean
    networks.loc[ix, "DownstreamOceanMilesClass"] = 0
    networks.loc[ix, "DownstreamOceanBarriersClass"] = 0

    # similar for Great Lakes
    networks["DownstreamGreatLakesMilesClass"] = classify_downstream_miles(networks.MilesToOutlet)
    networks["DownstreamGreatLakesBarriersClass"] = classify_downstream_barriers(num_downstream)
    ix = ~networks.FlowsToGreatLakes
    networks.loc[ix, "DownstreamGreatLakesMilesClass"] = 0
    networks.loc[ix, "DownstreamGreatLakesBarriersClass"] = 0

    # Convert dtypes to allow missing data when joined to barriers later
    # NOTE: upNetID or downNetID may be 0 if there aren't networks on that side, but
    # we set to int dtype instead of uint to allow -1 for missing data later
    for col in ["upNetID", "downNetID"]:
        networks[col] = networks[col].astype("int")

    for stat_type in [
        "Upstream",
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

    return networks.drop(columns=["Unranked", "State"])


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
    networks = networks[[c for c in NETWORK_COLUMNS if c in networks.columns]].rename(columns=NETWORK_COLUMN_NAMES)

    # join back to df using inner join, which limits to barrier types present in df
    networks = networks.join(df[df.columns.intersection(["Unranked", "State"])], how="inner")

    # sanity check to make sure no duplicate networks
    if networks.groupby(level=0).size().max() > 1:
        raise Exception(f"ERROR: multiple networks found for some {network_type} networks")

    networks["HasNetwork"] = True
    networks["Ranked"] = False

    # update data types and calculate total fields
    # calculate size classes GAINED instead of total
    # doesn't apply to those that don't have upstream networks
    networks["SizeClasses"] = networks.SizeClasses.astype("int8")
    networks.loc[networks.SizeClasses > 0, "SizeClasses"] = networks.loc[networks.SizeClasses > 0, "SizeClasses"] - 1

    # Convert dtypes to allow missing data when joined to barriers later
    for col in ["upNetID", "downNetID"]:
        # Force to -1 since these aren't part of standard networks
        networks[col] = -1

    for col in ("Landcover", "FlowsToOcean", "ExitsRegion"):
        networks[col] = networks[col].astype("int8")

    return networks.drop(columns=["Unranked", "State"])
