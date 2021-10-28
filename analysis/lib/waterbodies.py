import numpy as np
import pandas as pd


def classify_waterbody_size(series):
    bins = [0, 0.01, 0.1, 1, 10] + [series.max() + 1]
    return np.asarray(
        pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1))
    ).astype("uint8")
