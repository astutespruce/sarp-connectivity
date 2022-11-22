import pandas as pd
import numpy as np


def classify_gain_miles(series):
    bins = [-1, 0, 1, 5, 10, 25, 100] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(-1, len(bins) - 2))
    ).astype("int8")


def classify_spps(series):
    """classify species counts into 0...4; 0 means 0 instead of missing"""
    bins = [0, 1, 2, 5, 10] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))
    ).astype("uint8")


def classify_streamorder(series):
    """classify stream order into bins 1...6; 0 is reserved for missing values.

    Input values range from -1 for barriers not snapped to network to 1+;
    there are no input 0 values.
    """
    bins = [-1, 1, 2, 3, 4, 5, 6] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))
    ).astype("uint8")


def classify_percent_altered(series):
    """classify percent altered into bins 1...6: 0 is reserved for missing values"""
    bins = [-1, 0, 10, 50, 90] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))
    ).astype("uint8")


def classify_ocean_miles(series):
    """classify ocean miles into bins 1...7; 0 is reserved for missing values"""
    bins = [-1, 0, 1, 5, 10, 25, 100, 250] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))
    ).astype("uint8")


def classify_ocean_barriers(series):
    """classify ocean barriers into bins 1...5; 0 is reserved for missing values"""
    bins = [-1, 0, 1, 2, 5, 10] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))
    ).astype("uint8")
