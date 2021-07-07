from pathlib import Path
from time import time
import warnings

from analysis.constants import SARP_STATES
from analysis.lib.io import read_feathers
from analysis.rank.lib.metrics import (
    classify_gainmiles,
    classify_sinuosity,
    classify_landcover,
)
from analysis.rank.lib.tiers import calculate_tiers
from analysis.lib.util import append

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


NETWORK_COLUMNS = [
    "id",
    "kind",
    "upNetID",
    "downNetID",
    "TotalUpstreamMiles",
    "TotalDownstreamMiles",
    "FreeUpstreamMiles",
    "FreeDownstreamMiles",
    "sinuosity",
    "natfldpln",
    "sizeclasses",
    "num_downstream",
    "flows_to_ocean",
]


NETWORK_COLUMN_NAMES = {
    "sinuosity": "Sinuosity",
    "natfldpln": "Landcover",
    "sizeclasses": "SizeClasses",
    "flows_to_ocean": "FlowsToOcean",
    "num_downstream": "NumBarriersDownstream",
}


def get_network_results(df, barrier_type, network_scenario="all"):
    """Read network results, calculate derived metric classes, and calculate
    tiers.

    Only barriers that are not unranked (invasive spp barriers) have tiers calculated.

    Parameters
    ----------
    df : DataFrame
        barriers data; must contain State and unranked
    barrier_type : {"dams", "small_barriers"}
    network_scenario : {"all", "perennial"}, optional (default: "all")

    Returns
    -------
    DataFrame
        Contains network metrics and tiers
    """

    huc2s = [huc2 for huc2 in df.HUC2.unique() if huc2]

    networks = (
        read_feathers(
            [
                Path("data/networks/clean")
                / huc2
                / f"barriers_network__{barrier_type}_{network_scenario}.feather"
                for huc2 in huc2s
            ],
            columns=NETWORK_COLUMNS,
        )
        .rename(columns=NETWORK_COLUMN_NAMES)
        .set_index("id")
    )

    # select barrier type
    networks = networks.loc[networks.kind == barrier_type[:-1]].drop(columns=["kind"])

    # Convert dtypes to allow missing data when joined to barriers later
    # NOTE: upNetID or downNetID may be 0 if there aren't networks on that side, but
    # we set to int dtype instead of uint to allow -1 for missing data later
    for col in ["upNetID", "downNetID"]:
        networks[col] = networks[col].astype("int")

    for col in ["NumBarriersDownstream"]:
        networks[col] = networks[col].astype("int16")

    for column in ("Landcover", "SizeClasses", "FlowsToOcean"):
        networks[column] = networks[column].astype("int8")

    # sanity check to make sure no duplicate networks
    if networks.groupby(level=0).size().max() > 1:
        raise Exception(
            f"ERROR: multiple networks found for some {barrier_type} in {network_scenario} networks"
        )

    # join in source state (provided by SARP, not spatial state)
    networks = networks.join(df[["unranked", "State"]])

    # update data types and calculate total fields
    # calculate size classes GAINED instead of total
    # doesn't apply to those that don't have upstream networks
    networks.loc[networks.SizeClasses > 0, "SizeClasses"] -= 1

    # Calculate miles GAINED if barrier is removed
    # this is the lesser of the upstream or free downstream lengths.
    # Non-free miles downstream (downstream waterbodies) are omitted from this analysis.
    networks["GainMiles"] = networks[["TotalUpstreamMiles", "FreeDownstreamMiles"]].min(
        axis=1
    )

    # TotalNetworkMiles is sum of upstream and free downstream miles
    networks["TotalNetworkMiles"] = networks[
        ["TotalUpstreamMiles", "FreeDownstreamMiles"]
    ].sum(axis=1)

    # Round floating point columns to 3 decimals
    for column in (
        "Sinuosity",
        "GainMiles",
        "TotalUpstreamMiles",
        "FreeUpstreamMiles",
        "TotalDownstreamMiles",
        "FreeDownstreamMiles",
        "TotalNetworkMiles",
    ):
        networks[column] = networks[column].round(3).fillna(-1).astype("float32")

    # Calculate network metric classes
    networks["GainMilesClass"] = classify_gainmiles(networks.GainMiles)
    networks["SinuosityClass"] = classify_sinuosity(networks.Sinuosity)
    networks["LandcoverClass"] = classify_landcover(networks.Landcover)

    # only calculate ranks / tiers for ranked barriers
    # (exclude unranked invasive spp. barriers)
    to_rank = networks.loc[~networks.unranked]

    ### Calculate regional tiers for SARP (Southeast) region
    # NOTE: this is limited to SARP region; other regions are not ranked at regional level
    # TODO: consider deprecating this
    ix = to_rank.State.isin(SARP_STATES)
    sarp_tiers = calculate_tiers(to_rank.loc[ix])
    sarp_tiers = sarp_tiers.rename(
        columns={col: f"SE_{col}" for col in sarp_tiers.columns}
    )

    ### Calculate state tiers
    state_tiers = None
    for state in to_rank.State.unique():
        state_tiers = append(
            state_tiers,
            calculate_tiers(to_rank.loc[to_rank.State == state]).reset_index(),
        )

    state_tiers = state_tiers.set_index("id").rename(
        columns={col: f"State_{col}" for col in state_tiers.columns}
    )

    networks = networks.join(sarp_tiers).join(state_tiers)
    for col in [col for col in networks.columns if col.endswith("_tier")]:
        networks[col] = networks[col].fillna(-1).astype("int8")

    return networks.drop(columns=["unranked", "State"])
