import numpy as np
import pyarrow as pa
import pyarrow.compute as pc


SCENARIOS = {
    # NetworkConnectivity
    "NC": ["GainMiles"],
    "PNC": ["PerennialGainMiles"],
    # Watershed Condition
    "WC": ["PercentUnaltered", "Landcover", "SizeClasses"],
    "PWC": ["PercentPerennialUnaltered", "Landcover", "SizeClasses"],
    # Network Connectivity Plus Watershed Condition
    "NCWC": ["NC", "WC"],
    "PNCWC": ["PNC", "PWC"],
}

# Metric fields that are inputs of the above scenarios
METRICS = [
    "GainMiles",
    "PerennialGainMiles",
    "PercentUnaltered",
    "PercentPerennialUnaltered",
    "Landcover",
    "SizeClasses",
]


def calculate_score(column, ascending=True):
    """Calculate score based on the rank of a row's value within the sorted array of unique values.
    By default, the smallest unique value receives the lowest score, and the largest unique value
    receives the highest score.

    Parameters
    ----------
    series : pyarrow ChunkedArray
        Array from which to extract unique values and assign scores.
    ascending : boolean (default: True)
        If True, unique values are sorted in ascending order, meaning that the lowest score is the
        lowest unique value in the series, and the highest score is the length of the unique values.

    Returns
    -------
    numpy.ndarray, dtype is float64
        score value for each entry in the array
    """
    unique = column.unique()
    rank_size = len(unique) - 1 or 1  # to prevent divide by 0

    sort_indices = (
        pc.sort_indices(
            unique, sort_keys=[("", "ascending" if ascending else "descending")]
        )
        .to_numpy()
        .astype("int64")
    )

    # convert position of value within sorted unique values to 0-1 scale
    score = np.searchsorted(unique, column, sorter=sort_indices) / rank_size
    return score


def calculate_composite_score(scores, columns, weights=None):
    """Calculate composite score calculated across columns.

    Parameters
    ----------
    scores : dict
        contains keys corresponding to columns, values are ndarrays
    columns : list-like of column names
    weights : list-like, optional (default: None)
        list-like of weights.  It is up to caller to make sure these sum to 1.  By default,
        if no weights are provided, all columns are weighted equally.  If provided, must
        be same length as dataframe.columns

    Returns
    -------
    numpy.array, dtype is int
        tiers
    """

    num_cols = len(columns)
    if weights is None:
        # all columns weighted equally
        weights = [1.0 / num_cols] * num_cols

    elif not len(weights) == num_cols:
        raise ValueError(
            "weights must be same length as number of columns in input data frame"
        )

    score = np.sum(
        [scores[col] * weight for col, weight in zip(columns, weights)], axis=0
    )

    return score


def calculate_tier(scores):
    """Calculate tiers based on 5% increments of the composite score calculated
    across columns.

    The lowest tier (1) is the highest 95% of the composite score range.

    Parameters
    ----------
    scores : numpy.ndarray

    Returns
    -------
    numpy.ndarray
    """

    min_score, max_score = pc.min_max(scores).as_py().values()
    score_range = (max_score - min_score) or 1  # avoid divide by 0

    # calculate relative score
    relative_score = 100.0 * (scores - min_score) / score_range

    # break into 5% increments, such that tier 0 is in top 95% of the relative scores
    bins = np.arange(95, -5, -5)
    tiers = (np.digitize(relative_score, bins) + 1).astype("uint8")
    return tiers


def calculate_tiers(df):
    """Calculate tiers for each input scenario, which is based on combining scores for
    each scenario's inputs.

    Parameters
    ----------
    df : pyarrow.Table
        Input data frame containing at least all input fields
    group_field: str, optional (default: None)
        Name of a column to use for grouping tier calculation (all scores will be based on values within each group).

    Returns
    -------
    pyarrow.Table
        Table is in same order as input
    """

    scores = {field: calculate_score(df[field]) for field in METRICS}

    tiers = {}
    for scenario, inputs in SCENARIOS.items():
        scores[scenario] = calculate_composite_score(
            scores, columns=[field for field in inputs]
        )
        tiers[f"{scenario}_tier"] = calculate_tier(scores[scenario])

    return pa.Table.from_pydict(tiers)
