from pathlib import Path

import geopandas as gp
import pandas as pd
from pyogrio import write_dataframe

from analysis.lib.io import read_feathers
from analysis.lib.geometry.lines import merge_lines

src_dir = Path("data/networks")
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True, parents=True)


# full network scenarios are: "dams", "combined_barriers", "largefish_barriers", "smallfish_barriers", "road_crossings"
scenario = "dams"
mainstem = False
ext = "fgb"
driver = "FlatGeobuf"
# ext = "gdb"
# driver = "OpenFileGDB"


# Doesn't appear to work in QGIS
# layer_options = {"TARGET_ARCGIS_VERSION": "ARCGIS_PRO_3_2_OR_LATER"} if driver == "OpenFileGDB" else None
layer_options = None

scenario_suffix = "_mainstem" if mainstem else ""

groups_df = pd.read_feather(src_dir / "connected_huc2s.feather")

export_hucs = {
    # "01",
    # "02",
    # "03",
    # "04",
    # "05",
    # "06",
    # "07",
    # "08",
    # "09",
    # "10",
    # "11",
    # "12",
    # "13",
    # "14",
    # "15",
    # "16",
    # "17",
    "18",
    # "21",
}

# FIXME: remove
groups_df = groups_df.loc[groups_df.HUC2.isin(export_hucs)]


floodplains = (
    pd.read_feather(
        "data/floodplains/floodplain_stats.feather",
        columns=["NHDPlusID", "nat_floodplain_km2", "floodplain_km2"],
    )
    .set_index("NHDPlusID")
    .rename(columns={"nat_floodplain_km2": "natfldkm2", "floodplain_km2": "fldkm2"})
)
floodplains["natfldpln"] = (100 * floodplains.natfldkm2 / floodplains.fldkm2).astype("float32")

for group in groups_df.groupby("group").HUC2.apply(set).values:
    group = sorted(group)

    networkID_col = f"{scenario}{scenario_suffix}"
    segments = (
        read_feathers(
            [src_dir / "clean" / huc2 / "network_segments.feather" for huc2 in group],
            columns=["lineID", networkID_col],
        )
        .rename(columns={networkID_col: "networkID"})
        .set_index("lineID")
    )
    if mainstem:
        segments = segments.loc[segments.networkID != -1]

    stats = read_feathers(
        [src_dir / "clean" / huc2 / f"{scenario}_network_stats.feather" for huc2 in group],
        columns=[
            "networkID",
            # full functional network miles
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
            "resilient_miles",
            "pct_resilient",
            "pct_cold",
            "natfldpln",
            "sizeclasses",
            "barrier",
            "upstream_barrier_id",
            "upstream_barrier",
            "upstream_barrier_miles",
            "downstream_barrier_id",
            "downstream_barrier",
            "downstream_barrier_miles",
            "invasive_network",  # true if upstream of an invasive barrier
            "has_ej_tract",
            "has_ej_tribal",
            # upstream mainstem
            "total_upstream_mainstem_miles",
            "perennial_upstream_mainstem_miles",
            "intermittent_upstream_mainstem_miles",
            "altered_upstream_mainstem_miles",
            "unaltered_upstream_mainstem_miles",
            "perennial_unaltered_upstream_mainstem_miles",
            "pct_upstream_mainstem_unaltered",
            "upstream_mainstem_impairment",
            # downstream mainstem
            "total_downstream_mainstem_miles",
            "free_downstream_mainstem_miles",
            "free_perennial_downstream_mainstem_miles",
            "free_intermittent_downstream_mainstem_miles",
            "free_altered_downstream_mainstem_miles",
            "free_unaltered_downstream_mainstem_miles",
            "downstream_mainstem_impairment",
            # downstream linear network miles (downstream to next barrier / outlet)
            "total_linear_downstream_miles",
            "free_linear_downstream_miles",
            "free_perennial_linear_downstream_miles",
            "free_intermittent_linear_downstream_miles",
            "free_altered_linear_downstream_miles",
            "free_unaltered_linear_downstream_miles",
            # downstream linear network to outlet
            "miles_to_outlet",
            "flows_to_ocean",
            "flows_to_great_lakes",
        ],
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

    for col in ["flows_to_ocean", "flows_to_great_lakes", "invasive_network", "has_ej_tract", "has_ej_tribal"]:
        if col in stats.columns:
            stats[col] = stats[col].astype("uint8")

    # natural floodplain is missing for several catchments; fill with -1
    for col in ["natfldpln", "sizeclasses"]:
        stats[col] = stats[col].fillna(-1).astype("int8")

    # create output files by HUC2 based on where the segments occur
    for huc2 in group:
        if huc2 not in export_hucs:
            continue

        print(f"Dissolving networks in {huc2}...")
        flowlines = gp.read_feather(
            src_dir / "raw" / huc2 / "flowlines.feather",
            columns=[
                "lineID",
                "geometry",
                "length",
                "intermittent",
                "altered",
                "waterbody",
                "sizeclass",
                "StreamOrder",
                "NHDPlusID",
                "FCode",
                "FType",
                "TotDASqKm",
            ],
        ).set_index("lineID")

        # temporary, not useful
        other = pd.read_feather(
            Path("data/nhd/clean") / huc2 / "flowlines.feather",
            columns=[
                "lineID",
                "Slope",
                "MinElev",
                "MaxElev",
            ],
        ).set_index("lineID")
        flowlines = flowlines.join(other)

        flowlines = (
            flowlines.join(segments, how="inner")
            .join(floodplains, on="NHDPlusID")
            .join(stats[["flows_to_ocean", "flows_to_great_lakes", "invasive_network"]], on="networkID")
        )

        flowlines["km"] = flowlines["length"] / 1000.0
        flowlines["miles"] = flowlines["length"] * 0.000621371

        flowlines = flowlines.drop(columns=["length"])

        for col in ["natfldpln", "fldkm2", "natfldkm2"]:
            flowlines[col] = flowlines[col].fillna(-1)

        if ext == "gdb":
            # otherwise doesn't encode properly to FGDB
            for col in ["StreamOrder", "FCode", "FType", "intermittent", "altered"]:
                flowlines[col] = flowlines[col].astype("int32")

        ### To export larger flowlines only
        # flowlines = flowlines.loc[
        #     flowlines.sizeclass.isin(["1b", "2", "3a", "3b", "4", "5"])
        # ]
        # flowlines = flowlines.loc[flowlines.sizeclass.isin(["2", "3a", "3b", "4", "5"])]

        ### To export flowline segments
        print(f"Serializing {len(flowlines):,} network segments...")
        write_dataframe(
            flowlines,
            out_dir / f"region{huc2}_{scenario}{scenario_suffix}_network_segments.{ext}",
            driver=driver,
            layer_options=layer_options,
        )

        ### To export dissolved networks
        networks = (
            merge_lines(flowlines[["networkID", "geometry"]], by=["networkID"])
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

        # NOTE: this breaks when networks have a very large number of segments dissolved together into a multilinestring
        # (in the millions) and simply won't be displayed in QGIS

        print(f"Serializing {len(networks):,} dissolved networks...")
        write_dataframe(
            networks,
            out_dir / f"region{huc2}_{scenario}{scenario_suffix}_networks.{ext}",
            driver=driver,
            layer_options=layer_options,
        )
