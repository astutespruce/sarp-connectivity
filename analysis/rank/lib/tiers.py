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
    }
)
# Add combination last to ensure it runs last
SCENARIOS["NCWC"] = ["NC", "WC"]  # Network Connectivity Plus Watershed Condition

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


def calculate_tiers(df, group_field=None, prefix=""):
    """Calculate tiers for each input scenario, which is based on combining scores for
    each scenario's inputs.

    Calculations will only be performed where the "HasNetwork" field is true; otherwise results will be -1.
    
    Parameters
    ----------
    df : pandas.DataFrame
        Input data frame containing at least all input fields
    group_field: str, optional (default: None)
        Name of a column to use for grouping tier calculation (all scores will be based on values within each group).
    prefix: str, optional (default: "")
        Prefix to add to the resulting score and tier fields.
    
    Returns
    -------
    pandas.DataFrame
        returns data frame with a score field (_score) and tier field (_tier) for each scenario. 
        Scores are on a 0-100 (percent) scale.
    """

    columns = METRICS.copy()
    if group_field is not None:
        columns.append(group_field)

    # Subset just the metrics fields for just those records with networks
    results = df.loc[df.HasNetwork, columns].copy()

    groups = results[group_field].unique() if group_field is not None else [None]

    for group in groups:
        row_index = (
            results[group_field] == group if group is not None else results.index
        )
        # calculate score for each input field
        for field in METRICS:
            results.loc[row_index, "{}_score".format(field)] = calculate_score(
                results.loc[row_index, field]
            )

        # calculate composite score and tier
        for scenario, inputs in SCENARIOS.items():
            input_scores = ["{}_score".format(field) for field in inputs]
            score_field = "{}_score".format(scenario)

            results.loc[row_index, score_field] = calculate_composite_score(
                results.loc[row_index][input_scores]
            )
            results.loc[row_index, "{}_tier".format(scenario)] = calculate_tier(
                results.loc[row_index, score_field]
            )

    results_fields = results.columns.drop(columns)
    score_fields = [c for c in results_fields if c.endswith("_score")]

    # convert scores to percent scale
    results[score_fields] = (results[score_fields] * 100).round()

    # join back to original and fill N/A and fix dtypes
    df = df.join(results[results_fields])
    df[results_fields] = df[results_fields].fillna(-1).astype("int8")

    if prefix:
        df = df.rename(
            columns={field: "{0}_{1}".format(prefix, field) for field in results_fields}
        )

    return df

