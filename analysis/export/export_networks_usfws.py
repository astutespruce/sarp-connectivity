"""Extracts dam & waterfall dissolved networks, network segments, and barriers
for HUC2s that overlap SARP states.

TARGET outputs:
region<region>_dams_waterfalls.shp
These are the dams and waterfalls that were used for the network analysis

Attributes:
- NHDPlusID: original segment ID where this barrier snapped
- upNetID: upstream network ID (0 if no network upstream)
- downNetID: downstream network ID (0 if no network downstream)
- TotUpMi: total upstream miles
- TotDownMi: total downstream miles
- FreeUpMi: free upstream miles
- FreeDownMi: free downstream miles
- sinuosity: network length averaged sinuosity (all segments)
- segments: number of cut flowline segments within this network
- numsizes: number of unique size classes in upstream network
- natfldpln: total percent of floodplain that is in natural landcover classes for the entire network
- kind: type of barrier: dam, waterfall, etc



region<region>_dams_network.shp
These are the dissolved networks with associated functional network metrics.

Attributes:
- networkID: network identifier from this run of network analysis
- miles: total upstream network length
- free_miles: total upstream network length minus the length contained within NHD waterbodies
- segments: number of cut flowline segments within this network
- sizes: number of unique size classes in upstream network
- natfldpln: total percent of floodplain that is in natural landcover classes for the entire network
- up_ndams: number of dams that are immediately upstream of this network (i.e., this network is the downstream network of each of these dams)
- barrier: type of barrier that created this network (i.e., this network is upstream of what kind of barrier); blank for networks with no downstream barriers


region<region>_dams_network_segments.shp
These are cut flowlines for this barriers type (dams or small barriers) with additional attributes

Attributes:
- lineID (unique flowline identifier AFTER cutting flowlines by barriers and waterbodies)
- NHDPlusID (original flowline identifier BEFORE cutting flowlines)
- FCode / FType / GNIS_ID / GNIS_Name / StreamOrde (NHD stream order) / TotDASqKM (total drainage area in km2 of original flowline): original values from NHD
- size: TNC sizeclass
- length (in km)
- sinuosity (for this flowline)
- length_m: length in meters
- natfldkm2: area of natural landcover in floodplain (in km2); for the catchment associated with the original NHDPlusID segments, applied to all flowlines cut from original segments (i.e., joined on NHDPlusID)
- fldkm2: area of floodplain (in km2) for this catchment
- natfldpln: percent of floodplain in natural landcover for this catchment
- networkID: network identifier from this run of network analysis
- barrier: type of barrier that created this network (i.e., this network is upstream of what kind of barrier); blank for networks with no downstream barriers

"""

from pathlib import Path

import pandas as pd
import geopandas as gp
from pyogrio import write_dataframe

from analysis.lib.io import read_feathers
from analysis.lib.geometry.lines import merge_lines


src_dir = Path("data/networks")
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True)

suffix = ""
ext = "gdb"
driver = "OpenFileGDB"

# specific HUC2 groups that overlap with SECAS area
huc2_groups = [
    {"02"},
    {"03"},
    {
        "05",
        "06",
        "07",
        "08",
        "10",
        "11",
    },
    {"12"},
    {"13"},
    {"21"},
]

huc2s = set()
for group in huc2_groups:
    huc2s = huc2s.union(group)
huc2s = sorted(huc2s)


df = pd.read_feather(
    "data/api/dams.feather",
    columns=[
        "HasNetwork",
        "id",
        "SARPID",
        "State",
        "lon",
        "lat",
        "HUC12",
        "Estimated",
        "Intermittent",
        "upNetID",
        "downNetID",
        "TotalUpstreamMiles",
        "PerennialUpstreamMiles",
        "AlteredUpstreamMiles",
        "UnalteredUpstreamMiles",
        "PerennialUnalteredUpstreamMiles",
        "TotalDownstreamMiles",
        "FreeDownstreamMiles",
        "FreePerennialDownstreamMiles",
        "FreeAlteredDownstreamMiles",
        "FreeUnalteredDownstreamMiles",
        "PercentUnaltered",
        "PercentPerennialUnaltered",
        "Landcover",
        "SizeClasses",
        "FlowsToOcean",
        "FlowsToGreatLakes",
        "Ranked",
    ],
).set_index("id")

master = pd.read_feather(
    "data/barriers/master/dams.feather",
    columns=["id", "NHDPlusID"],
).set_index("id")
df = df.loc[df.HasNetwork].join(master).drop(columns=["HasNetwork"])
df.NHDPlusID = df.NHDPlusID.astype("uint64")

df["HUC2"] = df.HUC12.str[:2]
df = df.loc[df.HUC2.isin(huc2s)].copy()


floodplains = (
    pd.read_feather(
        "data/floodplains/floodplain_stats.feather",
        columns=["NHDPlusID", "nat_floodplain_km2", "floodplain_km2"],
    )
    .set_index("NHDPlusID")
    .rename(columns={"nat_floodplain_km2": "natfldkm2", "floodplain_km2": "fldkm2"})
)
floodplains["natfldpln"] = (100 * floodplains.natfldkm2 / floodplains.fldkm2).astype("float32")


# HUC2s that specifically overlap SECAS states (SARP states + VI & WV)
for group in huc2_groups:
    segments = (
        read_feathers(
            [src_dir / "clean" / huc2 / "network_segments.feather" for huc2 in group],
            columns=["lineID", "dams"],
        )
        .rename(columns={"dams": "networkID"})
        .set_index("lineID")
    )

    stats = read_feathers(
        [src_dir / "clean" / huc2 / "dams_network_stats.feather" for huc2 in group],
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
            out_dir / f"region{huc2}_dams_segments.{ext}",
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
            out_dir / f"region{huc2}_dams_networks.{ext}",
            driver=driver,
        )
