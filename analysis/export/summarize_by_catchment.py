import os
from pathlib import Path

import geopandas as gp
import pandas as pd

from analysis.constants import NETWORK_TYPES


data_dir = Path("data")
network_dir = data_dir / "networks"

out_dir = Path("/tmp/sarp")

if not out_dir.exists():
    os.makedirs(out_dir)

# TODO: expand to full region
huc4_df = pd.read_feather(
    data_dir / "boundaries/sarp_huc4.feather", columns=["HUC2", "HUC4"]
)
# Convert to dict of sorted HUC4s per HUC2
units = huc4_df.groupby("HUC2").HUC4.unique().apply(sorted).to_dict()
huc2s = sorted(units.keys())

# manually subset keys from above for processing
huc2s = ["02", "03"]

network_type = NETWORK_TYPES[1]
for huc2 in huc2s:
    print(f"----- {huc2} ({network_type}) ------")

    working_dir = network_dir / huc2 / network_type

    merged = False
    merged_dir = None

    if os.path.exists(network_dir / "merged" / huc2):
        merged = True
        merged_dir = network_dir / "merged" / huc2 / network_type

    segments = pd.read_feather(
        (merged_dir or working_dir) / "network_segments.feather",
        columns=["networkID", "lineID", "NHDPlusID", "length"],
    )
    segments.lineID = segments.lineID.astype("uint32")
    segments.networkID = segments.networkID.astype("uint32")

    stats = pd.read_feather(
        (merged_dir or working_dir) / "network_stats.feather",
        columns=["networkID", "miles", "sizeclasses"],
    ).set_index("networkID")

    df = segments.join(stats, on="networkID")

    # calculate original length of flowlines before cutting by waterbodies / barriers
    nhd_length = df.groupby("NHDPlusID").length.sum().rename("nhd_length")

    df = df.join(nhd_length, on="NHDPlusID")
    # calculate weighted average of network miles
    df["weight"] = df.length / df.nhd_length
    df["wtd_miles"] = df.weight * df.miles

    # df = df.sort_values(by=['NHDPlusID', 'weight'], ascending=True)

    grouped = df.groupby("NHDPlusID").agg(
        {
            "miles": ["min", "max"],
            "wtd_miles": ["sum"],
            "sizeclasses": ["min", "max"],
            "lineID": "count",
        }
    )

    grouped.columns = [
        "min_miles",
        "max_miles",
        "lwtd_avg_miles",
        "min_sizeclasses",
        "max_sizeclasses",
        "num_networks",
    ]

    df = grouped.reset_index()
    df["id_str"] = df.NHDPlusID.astype("str")

    df.to_csv(
        out_dir / f"region{huc2}_{network_type}_catchment_network_stats.csv",
        index=False,
    )
