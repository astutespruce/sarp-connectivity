import numpy as np
import pandas as pd

from analysis.constants import YEAR_REMOVED_BINS


def calc_year_removed_bin(series):
    return pd.cut(series, bins=YEAR_REMOVED_BINS, right=False, labels=np.arange(0, len(YEAR_REMOVED_BINS) - 1))


def pack_year_removed_stats(df, unit=None):
    """Combine year removed counts and gained miles into a single string:
    <year_bin>:<count>|<gainmiles>,...<?>
    adds "?" at end if year includes barriers that do not have networks

    Parameters:
    -----------
    df: DataFrame
        has columns for HasNetwork, YearRemoved, RemovedGainMiles
    unit: str, optional (default: None)
        if present, is used as the top-level grouping of results; otherwise
        a single packed string is returned
    """

    bins = range(len(YEAR_REMOVED_BINS) - 1)

    cols = ["YearRemoved", "RemovedGainMiles", "HasNetwork"]
    group_key = ["YearRemoved"]
    if unit:
        cols.insert(0, unit)
        group_key.insert(0, unit)

    tmp = df[cols].copy().reset_index()
    tmp["NoNetwork"] = (~tmp.HasNetwork).astype("uint8")

    stats = (
        tmp.groupby(group_key, observed=True)
        .agg({"id": "count", "RemovedGainMiles": "sum", "NoNetwork": "sum"})
        .apply(
            lambda row: f"{int(row.id)}{f'/{int(row.NoNetwork)}' if row.NoNetwork>0 else ''}|{row.RemovedGainMiles:.2f}",
            axis=1,
        )
        .rename("packed")
    )

    if unit:
        stats = stats.reset_index()
        # create tuple so we can create dict later in aggregation
        stats["packed"] = stats.apply(lambda row: (row.YearRemoved, row.packed), axis=1)
        return (
            stats.groupby(unit)
            .packed.unique()
            .apply(dict)
            .apply(lambda row: ",".join([row.get(bin, "") for bin in bins]))
        )

    if len(stats) == 0:
        return ""

    stats = stats.to_dict()
    return ",".join([stats.get(bin, "") for bin in bins])
