import pandas as pd
import numpy as np


def classify_gainmiles(series):
    bins = [-1, 0, 1, 5, 10, 25, 100] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(-1, len(bins) - 2))
    ).astype("int8")


def classify_landcover(series):
    bins = [-1, 0, 50, 75, 90] + [series.max() + 1]
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
