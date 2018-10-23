"""
Scenarios:
1. Network connectivity: "AbsoluteGainMi" 
2. Watershed condition: "NetworkSinuosity", "PctNatFloodplain", "NumSizeClassGained"  (33% each)
3. Network connectivitiy + watershed condition: (each gets 50%)


watershed condition score which = (0.333 * sinuosity_score + 0.333 * pctnatfloodplain_score + 0.333 * numsizeclass_score)
WatershedConditionTier = above in 5% bins like Eriks old script, tier 1-20
ConnectivityScore = (AbsMiGained_Score)
ConnectivityTier =  above in 5% bins like Eriks old script, tier 1-20
WatershedPlusConnectivityScore = (0.5 * watershedconditionScore + 0.5 * connectivityScore
WatershedPlusConnectivityTier =  above in 5% bins like Eriks old script, tier 1-20
"""

import numpy as np
import pandas as pd


def calculate_score(series, ascending=True):
    """Calculate score based on the rank of a row's value within the sorted array of unique values.
    By default, the smallest unique value receives the lowest score, and the largest unique value
    receives the highest score.
    
    Parameters
    ----------
    series : Pandas.Series
        Data series against which to extract unique values and assign scores.
    ascending : boolean (default: True)
        If True, unique values are sorted in ascending order, meaning that the lowest score is the
        lowest unique value in the series, and the highest score is the length of the unique values.
    
    Returns
    -------
    Pandas.Series, type is float64
        score value for each entry in the series
    """

    unique = series.unique()
    unique.sort()

    if not ascending:
        unique = unique[::-1]

    rank = np.arange(0, unique.size, dtype="float64")
    score = rank / (rank.size - 1)
    lut = {v: score[i] for i, v in enumerate(unique)}
    return series.apply(lambda row: lut.get(row, np.nan))


df = pd.read_csv(
    "data/src/dams.csv",
    dtype={
        "HUC2": str,
        "HUC4": str,
        "HUC8": str,
        "HUC12": str,
        "ECO3": str,
        "ECO4": str,
    },
)


fields = (
    "AbsoluteGainMi",
    "NetworkSinuosity",
    "PctNatFloodplain",
    "NumSizeClassGained",
)
for field in fields:
    score_field = "{}_score".format(field)
    df[score_field] = np.nan
    filter = ~pd.isnull(df[field])
    df.loc[filter, score_field] = calculate_score(df.loc[filter, field])
