from pathlib import Path
import warnings

from analysis.constants import SARP_STATE_NAMES
from analysis.lib.io import read_feathers
from analysis.rank.lib.metrics import classify_gainmiles
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
    "FreePerennialUnalteredDownstreamMiles",
    "PercentUnaltered",
    "PercentPerennialUnaltered",
    "natfldpln",
    "sizeclasses",
    "num_downstream",
    "flows_to_ocean",
]


NETWORK_COLUMN_NAMES = {
    "natfldpln": "Landcover",
    "sizeclasses": "SizeClasses",
    "flows_to_ocean": "FlowsToOcean",
    "num_downstream": "NumBarriersDownstream",
}


def get_network_results(df, network_type, barrier_type=None, rank=True):
    """Read network results, calculate derived metric classes, and calculate
    tiers.

    Only barriers that are not unranked (invasive spp barriers) have tiers calculated.

    Parameters
    ----------
    df : DataFrame
        barriers data; must contain State and unranked
    network_type : {"dams", "small_barriers"}
        network scenario
    barrier_type : {"dams", "small_barriers", "waterfalls"}, optional (default: None)
        if present, used to filter barrier kind from network results
    rank : bool, optional (default: True)
        if True, results will include tiers for the Southeast and state level

    Returns
    -------
    DataFrame
        Contains network metrics and tiers
    """

    barrier_type = barrier_type or network_type

    huc2s = [huc2 for huc2 in df.HUC2.unique() if huc2]

    networks = (
        read_feathers(
            [
                Path("data/networks/clean") / huc2 / f"{network_type}_network.feather"
                for huc2 in huc2s
            ],
            columns=NETWORK_COLUMNS,
        )
        .rename(columns=NETWORK_COLUMN_NAMES)
        .set_index("id")
    )

    # FIXME: temporary fix
    networks.PercentPerennialUnaltered = networks.PercentPerennialUnaltered.fillna(0)

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
            f"ERROR: multiple networks found for some {barrier_type} networks"
        )

    networks = networks.join(df[df.columns.intersection(["unranked", "State"])])

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
    networks["PerennialGainMiles"] = networks[
        ["PerennialUpstreamMiles", "FreePerennialDownstreamMiles"]
    ].min(axis=1)

    # TotalNetworkMiles is sum of upstream and free downstream miles
    networks["TotalNetworkMiles"] = networks[
        ["TotalUpstreamMiles", "FreeDownstreamMiles"]
    ].sum(axis=1)
    networks["TotalPerennialNetworkMiles"] = networks[
        ["PerennialUpstreamMiles", "FreePerennialDownstreamMiles"]
    ].sum(axis=1)

    # Round floating point columns to 3 decimals
    for column in [c for c in networks.columns if c.endswith("Miles")]:
        networks[column] = networks[column].round(3).fillna(-1).astype("float32")

    # Calculate network metric classes
    networks["GainMilesClass"] = classify_gainmiles(networks.GainMiles)
    networks["PerennialGainMilesClass"] = classify_gainmiles(
        networks.PerennialGainMiles
    )

    if not rank:
        return networks.drop(columns=["unranked", "State"], errors="ignore")

    # only calculate ranks / tiers for ranked barriers
    # (exclude unranked invasive spp. barriers)
    to_rank = networks.loc[~networks.unranked]

    ### Calculate regional tiers for SARP (Southeast) region
    # NOTE: this is limited to SARP region; other regions are not ranked at regional level
    # TODO: consider deprecating this
    ix = to_rank.State.isin(SARP_STATE_NAMES)
    sarp_tiers = calculate_tiers(to_rank.loc[ix])
    sarp_tiers = sarp_tiers.rename(
        columns={col: f"SE_{col}" for col in sarp_tiers.columns}
    )

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

    networks = networks.join(sarp_tiers).join(state_tiers)
    for col in [col for col in networks.columns if col.endswith("_tier")]:
        networks[col] = networks[col].fillna(-1).astype("int8")

    return networks.drop(columns=["unranked", "State"])
