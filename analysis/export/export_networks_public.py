from pathlib import Path

import pandas as pd
import geopandas as gp
from pyogrio import write_dataframe

from analysis.lib.io import read_feathers
from analysis.lib.geometry.lines import merge_lines


src_dir = Path("data/networks")
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True)

scenario = "combined_barriers"  # "dams", "combined_barriers", "largefish_barriers", "smallfish_barriers"
suffix = ""
ext = "gdb"
driver = "OpenFileGDB"

huc2_groups = [
    {"16"},
    {"17"},
    {"18"},
]

huc2s = set()
for group in huc2_groups:
    huc2s = huc2s.union(group)
huc2s = sorted(huc2s)


floodplains = (
    pd.read_feather(
        "data/floodplains/floodplain_stats.feather",
        columns=["NHDPlusID", "nat_floodplain_km2", "floodplain_km2"],
    )
    .set_index("NHDPlusID")
    .rename(columns={"nat_floodplain_km2": "natfldkm2", "floodplain_km2": "fldkm2"})
)
floodplains["natfldpln"] = (100 * floodplains.natfldkm2 / floodplains.fldkm2).astype(
    "float32"
)

for group in huc2_groups:
    segments = (
        read_feathers(
            [src_dir / "clean" / huc2 / "network_segments.feather" for huc2 in group],
            columns=["lineID", scenario],
        )
        .rename(columns={scenario: "networkID"})
        .set_index("lineID")
    )

    stats = read_feathers(
        [
            src_dir / "clean" / huc2 / f"{scenario}_network_stats.feather"
            for huc2 in group
        ],
        columns=[
            "networkID",
            "total_miles",
            "perennial_miles",
            "intermittent_miles",
            "altered_miles",
            "unaltered_miles",
            "perennial_unaltered_miles",
            "free_miles",
            "free_perennial_miles",
            "free_intermittent_miles",
            "free_altered_miles",
            "free_unaltered_miles",
            "free_perennial_unaltered_miles",
            "pct_unaltered",
            "pct_perennial_unaltered",
            "natfldpln",
            "sizeclasses",
            "barrier",
            "flows_to_ocean",
        ],
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

    # create output files by HUC2 based on where the segments occur
    for huc2 in group:
        print(f"Processing {huc2}")

        flowlines = gp.read_feather(
            src_dir / "raw" / huc2 / "flowlines.feather",
            columns=[
                "lineID",
                "geometry",
                "length",
                "intermittent",
                "altered",
                "sizeclass",
                "StreamOrder",
                "NHDPlusID",
                "FCode",
                "FType",
                "TotDASqKm",
                "HUC4",
            ],
        ).set_index("lineID")

        # otherwise doesn't encode properly to FGDB
        for col in ["StreamOrder", "FCode", "FType", "intermittent", "altered"]:
            flowlines[col] = flowlines[col].astype("int32")

        flowlines = (
            flowlines.join(segments)
            .join(floodplains, on="NHDPlusID")
            .join(stats[["sizeclasses", "flows_to_ocean"]], on="networkID")
        )
        flowlines["km"] = flowlines["length"] / 1000.0
        flowlines["miles"] = flowlines["length"] * 0.000621371

        flowlines = flowlines.drop(columns=["length"])

        for col in ["natfldpln", "fldkm2", "natfldkm2"]:
            flowlines[col] = flowlines[col].fillna(-1)

        # serialize raw segments
        print("Serializing undissolved networks...")
        write_dataframe(
            flowlines.reset_index(),
            out_dir / f"region{huc2}_{scenario}_segments.{ext}",
            driver=driver,
        )

        # # aggregate to multilinestrings by combinations of networkID
        # print("Dissolving networks...")
        networks = (
            merge_lines(flowlines[["networkID", "geometry"]], by=["networkID"])
            .set_index("networkID")
            .join(stats, how="inner")
            .reset_index()
        )

        print("Serializing dissolved networks...")
        write_dataframe(
            networks,
            out_dir / f"region{huc2}_{scenario}_networks.{ext}",
            driver=driver,
        )
