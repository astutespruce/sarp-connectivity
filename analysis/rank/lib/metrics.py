import pandas as pd
import numpy as np


GAINMILES_BINS = [-1, 0, 1, 5, 10, 25, 100]
SINUOSITY_BINS = [-1, 0, 1.2, 1.5001]
LANDCOVER_BINS = [-1, 0, 50, 75, 90]
TESPP_BINS = [0, 1, 2, 5, 10]
STREAMORDER_BINS = [-1, 0, 1, 2, 3, 4, 5, 6]


# call after join to master
def update_network_metrics(df):

    # calculate size classes GAINED instead of total
    # doesn't apply to those that don't have upstream networks
    idx = df.loc[df.SizeClasses > 0].index
    df.loc[idx, "SizeClasses"] = df.loc[idx].SizeClasses - 1

    # Calculate miles GAINED if barrier is removed
    # this is the lesser of the upstream or free downstream lengths.
    # Non-free miles downstream (downstream waterbodies) are omitted from this analysis.
    df["GainMiles"] = df[["TotalUpstreamMiles", "FreeDownstreamMiles"]].min(axis=1)

    # TotalNetworkMiles is sum of upstream and free downstream miles
    df["TotalNetworkMiles"] = df[["TotalUpstreamMiles", "FreeDownstreamMiles"]].sum(
        axis=1
    )

    for column in ("StreamOrder", "Landcover", "SizeClasses"):
        df[column] = df[column].fillna(-1).astype("int8")

    # Round floating point columns to 3 decimals
    for column in (
        "Sinuosity",
        "GainMiles",
        "TotalUpstreamMiles",
        "FreeUpstreamMiles",
        "TotalDownstreamMiles",
        "FreeDownstreamMiles",
        "GainMiles",
        "TotalNetworkMiles",
    ):
        df[column] = df[column].round(3).fillna(-1).astype("float32")

    # Calculate derived fields
    print("Calculating derived attributes")

    # Bin metrics
    df["GainMilesClass"] = classify_gainmiles(df.GainMiles)
    df["SinuosityClass"] = classify_sinuosity(df.Sinuosity)
    df["LandcoverClass"] = classify_landcover(df.Landcover)
    df["TESppClass"] = classify_te_spp(df.TESpp)
    df["StreamOrderClass"] = classify_streamorder(df.StreamOrder)

    return df


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


def classify_te_spp(series):
    bins = TESPP_BINS + [series.max() + 1]
    return pd.cut(series, bins, right=False, labels=np.arange(0, len(bins) - 1)).astype(
        "uint8"
    )


def classify_streamorder(series):
    bins = STREAMORDER_BINS + [series.max() + 1]
    return pd.cut(
        series, bins, right=False, labels=np.arange(-1, len(bins) - 2)
    ).astype("int8")
