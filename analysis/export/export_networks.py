import os
from pathlib import Path

import pandas as pd
import geopandas as gp
import pygeos as pg
from pyogrio import write_dataframe

from analysis.constants import CRS
from analysis.lib.io import read_feathers
from analysis.lib.geometry.lines import aggregate_lines

src_dir = Path("data/networks")
out_dir = Path("/tmp/sarp")

if not out_dir.exists():
    os.makedirs(out_dir)


barrier_type = "small_barriers"
ext = "fgb"

# groups_df = pd.read_feather(src_dir / "connected_huc2s.feather")

# for group in groups_df.groupby("group").HUC2.apply(set).values:
for group in [{"02"}]:
    segments = (
        read_feathers(
            [src_dir / "clean" / huc2 / "network_segments.feather" for huc2 in group],
            columns=["lineID", barrier_type],
        )
        .rename(columns={barrier_type: "networkID"})
        .set_index("lineID")
    )

    # FIXME: remove, debug only
    s = segments.groupby(level=0).size()
    print("dups", s[s > 1])

    stats = read_feathers(
        [
            src_dir / "clean" / huc2 / f"{barrier_type}_network_stats.feather"
            for huc2 in group
        ]
    ).set_index("networkID")

    # use smaller data types for smaller output files
    length_cols = [c for c in stats.columns if c.endswith("_miles")]
    for col in length_cols:
        stats[col] = stats[col].round(5).astype("float32")

    for col in [c for c in stats.columns if c.startswith("pct_")]:
        stats[col] = stats[col].fillna(0).astype("int8")

    # natural floodplain is missing for several catchments; fill with -1
    for col in ["natfldpln", "sizeclasses"]:
        stats[col] = stats[col].fillna(-1).astype("int8")

    stats.segments = stats.segments.astype("uint32")

    # create output files by HUC2 based on where the segments occur
    for huc2 in group:
        print(f"Dissolving networks in {huc2}...")
        flowlines = (
            gp.read_feather(
                src_dir / "raw" / huc2 / "flowlines.feather",
                columns=[
                    "lineID",
                    "geometry",
                    "intermittent",
                    "altered",
                    "sizeclass",
                    "StreamOrde",
                ],
            )
            .set_index("lineID")
            .rename(columns={"StreamOrde": "streamorder"})
        )
        flowlines = flowlines.join(segments)

        # aggregate to multilinestrings by combinations of networkID, altered, intermittent
        networks = (
            aggregate_lines(flowlines, by=["networkID", "altered", "intermittent"])
            .set_index("networkID")
            .join(stats, how="inner")
            .reset_index()
            .sort_values(by="networkID")
        )

        # Set plotting symbol
        networks["symbol"] = "normal"
        networks.loc[networks.altered, "symbol"] = "altered"
        # currently overrides altered since both come from NHD (mutually exclusive in source data)
        networks.loc[networks.intermittent, "symbol"] = "intermittent"
        networks.loc[
            networks.intermittent & networks.altered, "symbol"
        ] = "altered_intermittent"

        print("Serializing dissolved networks...")
        write_dataframe(
            networks, out_dir / f"region{huc2}_{barrier_type}_networks.{ext}"
        )

