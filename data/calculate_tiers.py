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
    pandas.Series, dtype is float64
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


# TODO: calculate_score_grouped


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
    bins = np.arange(0, 100, 5)[::-1]
    return pd.Series(np.digitize(relative_value, bins) + 1, dtype="uint8")


raw_df = pd.read_csv(
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


fields = [
    "AbsoluteGainMi",
    "NetworkSinuosity",
    "PctNatFloodplain",
    "NumSizeClassGained",
]

# Drop na fields up front, then join back to the original data frame
df = raw_df[fields].dropna()

for field in fields:
    df["{}_score".format(field)] = calculate_score(df[field])


scenarios = [
    ["Connectivity", ["AbsoluteGainMi"]],
    [
        "WatershedCondition",
        ["NetworkSinuosity", "PctNatFloodplain", "NumSizeClassGained"],
    ],
    [
        "ConnectivityPlusWatershedCondition",
        ["NetworkConnectivity", "WatershedCondition"],
    ],
]

for scenario, inputs in scenarios:
    input_scores = ["{}_score".format(field) for field in inputs]
    score_field = "{}_score".format(scenario)
    df[score_field] = calculate_composite_score(df[input_scores])
    df["{}_tier".format(scenario)] = calculate_tier(df[score_field])

