from collections import OrderedDict
from functools import reduce
from time import time

import numpy as np
import pandas as pd

# Using short labels for scenarios since we will add prefixes / suffixes to them
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

METRICS = ["GainMiles", "Sinuosity", "Landcover", "SizeClasses"]

PERCENTILES = [99, 95, 90, 75, 50, 25, 0]
# TOP_N = 5  # select the top N from each group
TOP_N = [1000, 500, 100, 50, 10]


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


def calculate_percentile(series, bins):
    """Calculate the percentile value of each element in the series, based on the bins passed in.

    Note: this will fail if the length of unque values in the series is less than the number of bins.
    
    Parameters
    ----------
    series : pandas.Series
        Data series against which to assign relative tiers.
    bins : array-like 
        percentile thresholds to use for calculating percentiles.  Example: [0, 50, 100] would bin values into min, median, and max of the series, and assign 0, 50, 100 to those values
        needs to include either a bin with value of 100 or 0 to work properly.  Example: [99, 95, 90, 75, 50, 25,  0]
    """

    percentiles = np.percentile(series, bins, interpolation="nearest")
    digitized = np.digitize(series, percentiles)
    return np.array(bins)[digitized].astype("uint8")


def calculate_tiers(
    dataframe, scenarios, group_field=None, prefix="", percentiles=False, topn=False
):
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
    group_field: str, optional (default: None)
        Name of a column to use for grouping tier calculation (all scores will be based on values within each group).
    prefix: str, optional (default: "")
        Prefix to add to the resulting score and tier fields.
    percentiles: bool (default: False)
        If True, calculate percentiles.  Note: there must be more values than the PERCENTILES or an exception will occur
    topn: bool (default: False)
        If True, calculate top N bins
    
    Returns
    -------
    pandas.DataFrame
        returns data frame with a tier field (_tier) for each scenario. 
    """

    columns = METRICS.copy()
    if group_field is not None:
        columns.append(group_field)

    df = dataframe[columns].copy()

    groups = df[group_field].unique() if group_field is not None else [None]

    for group in groups:
        row_index = df[group_field] == group if group is not None else df.index
        # calculate score for each input field
        for field in METRICS:

            df.loc[row_index, "{}_score".format(field)] = calculate_score(
                df.loc[row_index, field]
            )

        # calculate composite score and tier
        for scenario, inputs in scenarios.items():
            input_scores = ["{}_score".format(field) for field in inputs]
            score_field = "{}_score".format(scenario)

            df.loc[row_index, score_field] = calculate_composite_score(
                df.loc[row_index][input_scores]
            )

            df.loc[row_index, "{}_tier".format(scenario)] = calculate_tier(
                df.loc[row_index, score_field]
            )

            # Percentiles - only for large areas
            if percentiles:
                percentile = calculate_percentile(
                    df.loc[row_index, score_field], PERCENTILES
                )
                df.loc[row_index, "{}_p".format(scenario)] = percentile

            if topn:
                # Top N - set true if in top N, otherwise false
                topn_field = "{}_top".format(scenario)

                for n in TOP_N:
                    df.loc[
                        df.loc[row_index, score_field].nlargest(n).index, topn_field
                    ] = n

    df = df[df.columns.drop(columns)]

    if prefix:
        df.rename(
            columns={field: "{0}_{1}".format(prefix, field) for field in df.columns},
            inplace=True,
        )

    return df


if __name__ == "__main__":
    from feather import read_dataframe

    start = time()

    print("reading data")
    df = read_dataframe("data/src/dams.feather").set_index("id", drop=False)

    # keep only those on the network
    df = df.loc[df.HasNetwork].copy()

    for group_field in (None, "State"):
        print("Calculating tiers for: {}".format(group_field or "Region"))

        tiers_df = calculate_tiers(
            df,
            SCENARIOS,
            group_field=group_field,
            prefix="SE" if group_field is None else group_field,
            percentiles=True,
            topn=True,
        )
        df = df.join(tiers_df)

        # Fill n/a with -1 for tiers
        df[tiers_df.columns] = df[tiers_df.columns].fillna(-1)
        for col in tiers_df.columns:
            if col.endswith("_tier") or col.endswith("_p") or col.endswith("_top"):
                df[col] = df[col].astype("int8")
            elif col.endswith("_score"):
                df[col] = df[col].round(3).astype("float32")

    print("saving to CSV")
    df.to_csv("data/src/tiers.csv", index_label="id")

    print("Done in {:.2f}".format(time() - start))
