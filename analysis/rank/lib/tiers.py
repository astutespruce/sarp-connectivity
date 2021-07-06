from collections import OrderedDict
from functools import reduce
from time import time

import numpy as np
import pandas as pd


SCENARIOS = OrderedDict(
    {
        # NetworkConnectivity
        "NC": ["GainMiles"],
        # Watershed Condition
        "WC": ["Sinuosity", "Landcover", "SizeClasses"],
        # Network Connectivity Plus Watershed Condition
        "NCWC": ["NC", "WC"],
    }
)

# Metric fields that are inputs of the above scenarios
METRICS = ["GainMiles", "Sinuosity", "Landcover", "SizeClasses"]


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
    pandas.Series, dtype is float64
        score value for each entry in the series
    """

    # Round to 3 decimal places to avoid unnecessary precision and extract unique values
    series = series.copy().round(3)
    unique = series.unique()
    unique.sort()

    if not ascending:
        unique = unique[::-1]

    rank = np.arange(0, unique.size, dtype="float64")
    rank_size = (rank.size - 1) or 1  # to prevent divide by 0 error
    score = rank / rank_size  # on a 0-1 scale
    lut = {v: score[i] for i, v in enumerate(unique)}
    return series.map(lut)


def calculate_composite_score(dataframe, weights=None):
    """Calculate composite, weighted score across one or more columns.
    The lowest tier (1) is the highest 95% of the composite score range.

    Parameters
    ----------
    dataframe : DataFrame
        data frame of score fields to combine for calculating tier
    weights : list-like, optional (default: None)
        list-like of weights.  It is up to caller to make sure these sum to 1.  By default,
        if no weights are provided, all columns are weighted equally.  If provided, must
        be same length as dataframe.columns

    Raises
    ------
    ValueError
        raised if weights are not the same length as number of columns in dataframe

    Returns
    -------
    pandas.Series, dtype is float64
        composite score
    """

    if weights is None:
        numcols = len(dataframe.columns)
        weights = [1.0 / numcols] * numcols

    elif not len(weights) == len(dataframe.columns):
        raise ValueError(
            "weights must be same length as number of columns in input data frame"
        )

    dataframe = dataframe.copy()  # copy so that we can modify in place
    for i, col in enumerate(dataframe.columns):
        dataframe[col] = dataframe[col] * weights[i]

    return dataframe.sum(axis=1)


def calculate_tier(series):
    """Calculate tiers based on 5% increments of the score range.
    The lowest tier (1) is the highest 95% of the composite score range.

    Parameters
    ----------
    series : pandas.Series
        Data series against which to assign relative tiers.

    Returns
    -------
    pandas.Series, dtype is int
        tiers
    """

    # calculate relative score
    series_min = max(series.min(), 0)
    series_range = (series.max() - series_min) or 1  # to avoid divide by 0
    relative_value = 100.0 * (series - series_min) / series_range

    # break into 5% increments, such that tier 0 is in top 95% of the relative scores
    bins = np.arange(95, -5, -5)
    return (np.digitize(relative_value, bins) + 1).astype("uint8")


def calculate_tiers(df):
    """Calculate tiers for each input scenario, which is based on combining scores for
    each scenario's inputs.

    Parameters
    ----------
    df : pandas.DataFrame
        Input data frame containing at least all input fields
    group_field: str, optional (default: None)
        Name of a column to use for grouping tier calculation (all scores will be based on values within each group).

    Returns
    -------
    pandas.DataFrame
        returns data frame indexed on original index, with a score field (_score)
        and tier field (_tier) for each scenario. Scores are on a 0-100 (percent)
        scale.
    """

    # calculate scores for individual fields
    results = pd.DataFrame(
        {f"{field}_score": calculate_score(df[field]) for field in METRICS},
        index=df.index,
    )

    # calculate composite score and tier
    for scenario, inputs in SCENARIOS.items():
        input_scores = [f"{field}_score" for field in inputs]
        results[f"{scenario}_score"] = calculate_composite_score(results[input_scores])
        results[f"{scenario}_tier"] = calculate_tier(results[f"{scenario}_score"])

    # only return tier columns
    return results[[col for col in results.columns if col.endswith("_tier")]]

