import os
from pathlib import Path

import pandas as pd
import geopandas as gp
import pygeos as pg
from pyogrio import write_dataframe

from analysis.constants import CRS
from analysis.lib.io import read_feathers

src_dir = Path("data/networks")
out_dir = Path("/tmp/sarp")

if not out_dir.exists():
    os.makedirs(out_dir)


scenario = "dams_perennial"
ext = "gpkg"

groups_df = pd.read_feather(src_dir / "connected_huc2s.feather")

for group in groups_df.groupby("group").HUC2.apply(set).values:
    segments = (
        read_feathers(
            [src_dir / "clean" / huc2 / "network_segments.feather" for huc2 in group],
            columns=["lineID", scenario],
        )
        .rename(columns={scenario: "networkID"})
        .set_index("lineID")
    )

    # FIXME: remove, debug only
    s = segments.groupby(level=0).size()
    print("dups", s[s > 1])

    stats = read_feathers(
        [
            src_dir / "clean" / huc2 / f"network_stats__{scenario}.feather"
            for huc2 in group
        ]
    ).set_index("networkID")

    # use smaller data types for smaller output files
    for col in ["miles", "free_miles", "sinuosity"]:
        stats[col] = stats[col].round(5).astype("float32")

    # natural floodplain is missing for several catchments; fill with -1
    for col in ["natfldpln", "sizeclasses"]:
        stats[col] = stats[col].fillna(-1).astype("int8")

    stats.segments = stats.segments.astype("uint32")

    # create output files by HUC2 based on where the segments occur
    for huc2 in group:
        print(f"Dissolving networks in {huc2}...")
        flowlines = gp.read_feather(
            src_dir / "raw" / huc2 / "flowlines.feather", columns=["lineID", "geometry", "intermittent", "StreamOrde"]
        ).set_index("lineID")
        flowlines = flowlines.join(segments)

        # aggregate to multilinestrings by networkID
        flowlines = (
            pd.Series(flowlines.geometry.values.data, index=flowlines.networkID)
            .groupby(level=0)
            .apply(pg.multilinestrings)
            .rename("geometry")
        )

        networks = (
            gp.GeoDataFrame(pd.DataFrame(flowlines).join(stats, how="inner"), crs=CRS)
            .reset_index()
            .sort_values(by="networkID")
        )

        print("Serializing dissolved networks...")
        write_dataframe(networks, out_dir / f"region{huc2}_{scenario}_networks.{ext}")

