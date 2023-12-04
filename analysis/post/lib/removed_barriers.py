import numpy as np
import pandas as pd

from analysis.constants import YEAR_REMOVED_BINS


def calc_year_removed_bin(series):
    return pd.cut(series, bins=YEAR_REMOVED_BINS, right=False, labels=np.arange(0, len(YEAR_REMOVED_BINS) - 1))


def pack_year_removed_stats(df, unit=None):
    """Combine year removed counts and gained miles into a single string:
    <year_bin>:<count>|<gainmiles>,...

    Parameters:
    -----------
    df: DataFrame
        has columns for YearRemoved and RemovedGainMiles
    unit: str, optional (default: None)
        if present, is used as the top-level grouping of results; otherwise
        a single packed string is returned
    """

    bins = range(len(YEAR_REMOVED_BINS) - 1)

    cols = ["YearRemoved", "RemovedGainMiles"]
    group_key = ["YearRemoved"]
    if unit:
        cols.insert(0, unit)
        group_key.insert(0, unit)

    stats = (
        df[cols]
        .reset_index()
        .groupby(group_key, observed=True)
        .agg({"id": "count", "RemovedGainMiles": "sum"})
        .apply(lambda row: f"{int(row.id)}|{row.RemovedGainMiles:.2f}", axis=1)
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
