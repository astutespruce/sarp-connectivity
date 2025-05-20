import pandas as pd
import numpy as np


def classify_gain_miles(series):
    bins = [-1, 0, 1, 5, 10, 25, 100] + [series.max() + 1]
    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(-1, len(bins) - 2))).astype("int8")


def classify_mainstem_gain_miles(series):
    """classify mainstem gain miles.  NOTE: -1 indicates not on a mainstem"""
    bins = [-1, 0, 1, 2, 5, 10, 25]
    last_bin = series.max() + 1
    if last_bin > bins[-1]:
        bins.append(last_bin)

    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(-1, len(bins) - 2))).astype("int8")


def classify_spps(series):
    """classify species counts into 0...4; 0 means 0 instead of missing"""
    bins = [0, 1, 2, 5, 10] + [series.max() + 1]
    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))).astype("uint8")


def classify_streamorder(series):
    """classify stream order into bins 1...6; 0 is reserved for missing values.

    Input values range from -1 for barriers not snapped to network to 1+;
    there are no input 0 values.
    """
    bins = [-1, 1, 2, 3, 4, 5, 6] + [series.max() + 1]
    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))).astype("uint8")


def classify_percent_unaltered(series):
    """classify percent unaltered into bins 1...6: 0 is reserved for missing values"""
    bins = [-1, 0, 10, 50, 90] + [series.max() + 1]
    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))).astype("uint8")


def classify_percent_resilient(series):
    """classify percent resilient into bins 1...6: 0 is reserved for missing values"""
    bins = [-1, 0, 10, 50, 90] + [series.max() + 1]
    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))).astype("uint8")


def classify_percent_cold(series):
    """classify percent cold into bins 1...6: 0 is reserved for missing values"""
    bins = [-1, 0, 10, 50, 90] + [series.max() + 1]
    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))).astype("uint8")


def classify_downstream_miles(series):
    """classify downstream miles to ocean / Great Lakesinto bins 1...7; 0 is reserved for missing values"""
    bins = [-1, 0, 1, 5, 10, 25, 100, 250, 500, 1000]
    max_value = series.max()
    if max_value > bins[-1]:
        bins.append(max_value + 1)

    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))).astype("uint8")


def classify_downstream_barriers(series):
    """classify barriers downstream to ocean / Great Lakes into bins 1...5; 0 is reserved for missing values"""
    bins = [-1, 0, 1, 2, 5, 10] + [series.max() + 1]
    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))).astype("uint8")


def classify_annual_flow(series):
    """classify barriers by the annual flow rate of the flowline where they snapped; 0 indicates missing values"""
    bins = [-1, 0, 1, 3, 5, 10, 50, 100] + [series.max() + 1]
    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))).astype("uint8")


def classify_cost(series):
    """classify dams by CostMean values into bins 1...8; 0 is reserved for missing values (small barriers)"""
    bins = [-1, 0, 100_000, 250_000, 500_000, 750_000, 1_000_000, 2_000_000] + [series.max() + 1]
    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(1, len(bins)))).astype("uint8")


def classify_unaltered_waterbody_area(series):
    bins = [-1, 0, 2.5, 25, 250, 2500] + [series.max() + 1]
    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(-1, len(bins) - 2))).astype("int8")


def classify_unaltered_wetland_area(series):
    bins = [-1, 0, 2.5, 25, 250, 2500] + [series.max() + 1]
    return np.asarray(pd.cut(series, bins, right=False, labels=np.arange(-1, len(bins) - 2))).astype("int8")
