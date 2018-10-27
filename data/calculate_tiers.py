from collections import OrderedDict
from functools import reduce
from time import time

import numpy as np
import pandas as pd

# Using short labels for scenarios since we will add prefixes / suffixes to them
SCENARIOS = OrderedDict(
    {
        "NC": ["AbsoluteGainMi"],  # NetworkConnectivity
        "WC": [
            "NetworkSinuosity",
            "PctNatFloodplain",
            "NumSizeClassGained",
        ],  # Watershed Condition
    }
)
# Add combination last to ensure it runs last
SCENARIOS["NCWC"] = ["NC", "WC"]  # Network Connectivity Plus Watershed Condition


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
    series = series.copy().round(5)
    unique = series.unique()
    unique.sort()

    if not ascending:
        unique = unique[::-1]

    rank = np.arange(0, unique.size, dtype="float64")
    rank_size = (rank.size - 1) or 1  # to prevent divide by 0 error
    score = rank / rank_size
    lut = {v: score[i] for i, v in enumerate(unique)}
    return series.apply(lambda row: lut.get(row, np.nan))


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

    # TEMP: calculate using percentiles instead, so that there are 5% in each bin.  DOES NOT WORK in all cases (e.g., too many of same value or too few overall dams)
    # percentiles = np.percentile(series, bins)  # no need to make relative first
    # return (np.digitize(series, percentiles) + 1).astype("uint8")


def calculate_tiers(dataframe, scenarios, group_field=None):
    """Calculate tiers for each input scenario, which is based on combining scores for
    each scenario's inputs.

    Calculations will only be performed where all input fields are not null.  Null fields
    will result in null values in output tiers.
    
    Parameters
    ----------
    dataframe : pandas.DataFrame
        Input data frame containing at least all input fields
    scenarios : dict
        Dict mapping name of scenario to input fields
    group_field: str
        Name of a column to use for grouping tier calculation (all scores will be based on values within each group)
    
    Returns
    -------
    pandas.DataFrame
        returns data frame with a tier field (_tier) for each scenario. 
    """

    # extract list of fields based on inputs to scenarios, excluding those that are combinations of other scenarios
    fields = [
        field
        for field in reduce(lambda x, y: set(x).union(y), SCENARIOS.values())
        if not field in SCENARIOS
    ]

    # Drop na fields up front, then join back to the original data frame
    columns = fields.copy()
    if group_field is not None:
        columns.append(group_field)
    df = dataframe[columns].dropna()

    groups = df[group_field].unique() if group_field is not None else [None]

    for group in groups:
        row_index = df[group_field] == group if group is not None else df.index

        # calculate score for each input field
        for field in fields:
            df.loc[row_index, "{}_score".format(field)] = calculate_score(
                df.loc[row_index, field]
            )

        # calculate composite score and tier
        for scenario, inputs in scenarios.items():
            input_scores = ["{}_score".format(field) for field in inputs]
            score_field = "{}_score".format(scenario)
            df.loc[row_index, score_field] = calculate_composite_score(
                df.loc[row_index, input_scores]
            )

            # Tiers are named for the scenario
            tier = calculate_tier(df.loc[row_index, score_field])
            df.loc[row_index, scenario] = tier

    # join back to the original data frame
    # only keep the scenario tier fields
    out_fields = list(scenarios.keys())

    # For adding score fields
    # out_fields = [f for f in df.columns if not f in fields]
    df = df[out_fields]

    if group_field is not None:
        # rename fields based on group prefix
        df.rename(
            columns={
                field: "{0}_{1}".format(group_field, field) for field in out_fields
            },
            inplace=True,
        )

    return df


if __name__ == "__main__":
    start = time()

    df = pd.read_csv(
        "data/src/dams.csv",
        dtype={
            "HUC2": str,
            "HUC4": str,
            "HUC6": str,
            "HUC8": str,
            "HUC10": str,
            "HUC12": str,
            "ECO3": str,
            "ECO4": str,
        },
    ).set_index(["id"])

    df = df.drop(
        columns=[
            c
            for c in df.columns
            if c in {"NCWC", "NC", "WC"} or "_NC" in c or "_WC" in c
        ]
    )

    # for group_field in (None, "State", "HUC2", "HUC4", "HUC8", "ECO3"):
    for group_field in (None,):
        if group_field is None:
            print("Calculating regional tiers")
        else:
            print("Calculating tiers for {}".format(group_field))

        tiers_df = calculate_tiers(df, SCENARIOS, group_field=group_field)
        df = df.join(tiers_df)

        # Fill n/a with -1 for tiers
        df[tiers_df.columns] = df[tiers_df.columns].fillna(-1).astype("int8")

    df.to_csv("data/src/tiers.csv", index_label="id")

    print("Size", len(df))

    print("Done in {:.2f}".format(time() - start))
