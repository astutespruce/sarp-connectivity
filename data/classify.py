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


## Old way of doing classes

# Bin gain miles
# df["GainMilesClass"] = -1  # no network
# df.loc[df.HasNetwork & (df.GainMiles < 1), "GainMilesClass"] = 0
# df.loc[df.HasNetwork & (df.GainMiles >= 1) & (df.GainMiles < 5), "GainMilesClass"] = 1
# df.loc[df.HasNetwork & (df.GainMiles >= 5) & (df.GainMiles < 10), "GainMilesClass"] = 2
# df.loc[df.HasNetwork & (df.GainMiles >= 10) & (df.GainMiles < 25), "GainMilesClass"] = 3
# df.loc[
#     df.HasNetwork & (df.GainMiles >= 25) & (df.GainMiles < 100), "GainMilesClass"
# ] = 4
# df.loc[df.HasNetwork & (df.GainMiles >= 100), "GainMilesClass"] = 5
# df.GainMilesClass = df.GainMilesClass.astype("int8")

# Bin sinuosity
# df["SinuosityClass"] = -1  # no network
# df.loc[df.HasNetwork & (df.Sinuosity < 1.2), "SinuosityClass"] = 0
# df.loc[
#     df.HasNetwork & (df.Sinuosity >= 1.2) & (df.Sinuosity <= 1.5), "SinuosityClass"
# ] = 1
# df.loc[df.HasNetwork & (df.Sinuosity > 1.5), "SinuosityClass"] = 2
# df.SinuosityClass = df.SinuosityClass.astype("int8")


# Bin landcover
# df["LandcoverClass"] = -1  # no network
# df.loc[df.HasNetwork & (df.Landcover < 50), "LandcoverClass"] = 0
# df.loc[df.HasNetwork & (df.Landcover >= 50) & (df.Landcover < 75), "LandcoverClass"] = 1
# df.loc[df.HasNetwork & (df.Landcover >= 75) & (df.Landcover < 90), "LandcoverClass"] = 2
# df.loc[df.HasNetwork & (df.Landcover >= 90), "LandcoverClass"] = 3
# df.LandcoverClass = df.LandcoverClass.astype("int8")

# Bin rare species
# df.loc[df.RareSpp == 0, "RareSppClass"] = 0
# df.loc[df.RareSpp == 1, "RareSppClass"] = 1
# df.loc[(df.RareSpp > 1) & (df.RareSpp < 5), "RareSppClass"] = 2
# df.loc[(df.RareSpp >= 5) & (df.RareSpp < 10), "RareSppClass"] = 3
# df.loc[(df.RareSpp >= 10), "RareSppClass"] = 4
# df.RareSppClass = df.RareSppClass.astype("uint8")

# Bin StreamOrder
# df["StreamOrderClass"] = df.StreamOrder
# df.loc[df.StreamOrder >= 6, "StreamOrderClass"] = 6
# df.StreamOrderClass = df.StreamOrderClass.astype("int8")
