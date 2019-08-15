import pandas as pd
import numpy as np


GAINMILES_BINS = [-1, 0, 1, 5, 10, 25, 100]
SINUOSITY_BINS = [-1, 0, 1.2, 1.5001]
LANDCOVER_BINS = [-1, 0, 50, 75, 90]
RARESPP_BINS = [0, 1, 2, 5, 10]
STREAMORDER_BINS = [-1, 0, 1, 2, 3, 4, 5, 6]


def classify_gainmiles(series):
    bins = GAINMILES_BINS + [series.max() + 1]
    return pd.cut(
        series, bins, right=False, labels=np.arange(-1, len(bins) - 2)
    ).astype("int8")


def classify_sinuosity(series):
    bins = SINUOSITY_BINS + [series.max() + 1]
    return pd.cut(
        series, bins, right=False, labels=np.arange(-1, len(bins) - 2)
    ).astype("int8")


def classify_landcover(series):
    bins = LANDCOVER_BINS + [series.max() + 1]
    return pd.cut(
        series, bins, right=False, labels=np.arange(-1, len(bins) - 2)
    ).astype("int8")


def classify_rarespp(series):
    bins = RARESPP_BINS + [series.max() + 1]
    return pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1)).astype(
        "uint8"
    )


def classify_streamorder(series):
    bins = STREAMORDER_BINS + [series.max() + 1]
    return pd.cut(
        series, bins, right=False, labels=np.arange(-1, len(bins) - 2)
    ).astype("int8")
