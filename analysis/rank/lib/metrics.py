import pandas as pd
import numpy as np


def classify_gain_miles(series):
    bins = [-1, 0, 1, 5, 10, 25, 100] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(-1, len(bins) - 2))
    ).astype("int8")


def classify_ocean_miles(series):
    bins = [-1, 0, 1, 5, 10, 25, 100, 250] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(-1, len(bins) - 2))
    ).astype("int8")


def classify_spps(series):
    bins = [0, 1, 2, 5, 10] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))
    ).astype("uint8")


def classify_streamorder(series):
    bins = [-1, 0, 1, 2, 3, 4, 5, 6] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(-1, len(bins) - 2))
    ).astype("int8")


def classify_percent_altered(series):
    bins = [-1, 0, 10, 50, 90] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(-1, len(bins) - 2))
    ).astype("int8")


def classify_ocean_barriers(series):
    bins = [-1, 0, 1, 2, 5, 10] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(-1, len(bins) - 2))
    ).astype("int8")
