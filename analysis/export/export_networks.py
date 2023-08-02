from pathlib import Path

import geopandas as gp
import pandas as pd
from pyogrio import write_dataframe

from analysis.lib.io import read_feathers
from analysis.lib.geometry.lines import merge_lines

src_dir = Path("data/networks")
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True, parents=True)


scenario = "combined_barriers"  # "dams", "combined_barriers", "largefish_barriers", "smallfish_barriers"
removed = False
ext = "fgb"

groups_df = pd.read_feather(src_dir / "connected_huc2s.feather")

export_hucs = {
    # "01",
    # "02",
    # "04",
    # "05",
    # "06",
    # "07",
    # "08"
    # "09"
    # "21"
}


prefix = "removed_" if removed else ""
segments_prefix = "removed_barriers_" if removed else ""

# for group in groups_df.groupby("group").HUC2.apply(set).values:
for group in [{"01", "02"}]:
    group = sorted(group)

    segments = (
        read_feathers(
            [
                src_dir / "clean" / huc2 / f"{segments_prefix}network_segments.feather"
                for huc2 in group
            ],
            columns=["lineID", scenario],
        )
        .rename(columns={scenario: "networkID"})
        .set_index("lineID")
    )

    stats = read_feathers(
        [
            src_dir / "clean" / huc2 / f"{prefix}{scenario}_network_stats.feather"
            for huc2 in group
        ]
    ).set_index("networkID")

    # use smaller data types for smaller output files
    length_cols = [c for c in stats.columns if c.endswith("_miles")]
    for col in length_cols:
        stats[col] = stats[col].round(5).astype("float32")

    for col in [c for c in stats.columns if c.startswith("pct_")]:
        stats[col] = stats[col].fillna(0).astype("int8")

    for kind in ["waterfalls", "dams", "small_barriers", "road_crossings"]:
        for count_type in ["fn", "tot", "totd", "cat"]:
            col = f"{count_type}_{kind}"
            if col in stats.columns:
                stats[col] = stats[col].fillna(0).astype("uint32")

    for col in ["flows_to_ocean", "flows_to_great_lakes", "exits_region"]:
        if col in stats.columns:
            stats[col] = stats[col].astype("uint8")

    # natural floodplain is missing for several catchments; fill with -1
    for col in ["natfldpln", "sizeclasses"]:
        stats[col] = stats[col].fillna(-1).astype("int8")

    # create output files by HUC2 based on where the segments occur
    for huc2 in group:
        # if huc2 not in export_hucs:
        #     continue

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
                    "StreamOrder",
                ],
            )
            .set_index("lineID")
            .rename(columns={"StreamOrder": "streamorder"})
        )
        flowlines = flowlines.join(segments)

        ### To export larger flowlines only
        # flowlines = flowlines.loc[
        #     flowlines.sizeclass.isin(["1b", "2", "3a", "3b", "4", "5"])
        # ]
        # flowlines = flowlines.loc[flowlines.sizeclass.isin(["2", "3a", "3b", "4", "5"])]

        ### To export dissolved networks
        networks = (
            merge_lines(flowlines, by=["networkID"])
            .set_index("networkID")
            .join(stats, how="inner")
            .reset_index()
            .sort_values(by="networkID")
        )

        # ### To export by plotting symbol
        # networks = (
        #     merge_lines(flowlines, by=["networkID", "altered", "intermittent"])
        #     .set_index("networkID")
        #     .join(stats, how="inner")
        #     .reset_index()
        #     .sort_values(by="networkID")
        # )

        # # Set plotting symbol
        # networks["symbol"] = "normal"
        # networks.loc[networks.altered, "symbol"] = "altered"
        # # currently overrides altered since both come from NHD (mutually exclusive in source data)
        # networks.loc[networks.intermittent, "symbol"] = "intermittent"
        # networks.loc[
        #     networks.intermittent & networks.altered, "symbol"
        # ] = "altered_intermittent"

        print(f"Serializing {len(networks):,} dissolved networks...")
        write_dataframe(
            networks, out_dir / f"region{huc2}_{prefix}{scenario}_networks.{ext}"
        )
