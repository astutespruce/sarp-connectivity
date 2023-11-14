"""Extracts dissolved network and network segments to a shapefile for a single barrier.

TARGET outputs:

<SARPID>_<network_type>_network.shp
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


<SARPID>_<network_type>_network_segments.shp
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
import pyarrow as pa
from pyarrow.dataset import dataset
import pyarrow.compute as pc
from pyogrio import write_dataframe
import shapely

from analysis.constants import CRS
from analysis.lib.io import read_feathers, read_arrow_tables
from analysis.lib.geometry.lines import merge_lines


src_dir = Path("data/networks")
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True)

suffix = ""
ext = "shp"
driver = "ESRI Shapefile"

scenario = "combined_barriers"  # "dams", "combined_barriers", "largefish_barriers", "smallfish_barriers"
barrier_type = "dams"
SARPID = "MN41337"


# resolve SARPID to HUC and upNetID
id, upNetID, HUC2 = (
    dataset(f"data/api/{scenario}.feather", format="feather")
    .to_table(columns=["id", "upNetID", "HUC2"], filter=pc.field("SARPID") == SARPID)
    .to_pandas()
    .iloc[0]
    .values
)

groups_df = pd.read_feather(src_dir / "connected_huc2s.feather")
group = groups_df.loc[groups_df.HUC2 == HUC2].group.iloc[0]
huc2s = sorted(groups_df.loc[groups_df.group == group].HUC2.values)

segments = (
    read_arrow_tables(
        [src_dir / "clean" / huc2 / "network_segments.feather" for huc2 in huc2s],
        columns=["lineID", scenario],
        filter=pc.field(scenario) == upNetID,
    )
    .to_pandas()
    .rename(columns={scenario: "networkID"})
    .set_index("lineID")
)

stats = (
    read_arrow_tables(
        [src_dir / "clean" / huc2 / f"{scenario}_network_stats.feather" for huc2 in huc2s],
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
        filter=pc.field("networkID") == upNetID,
    )
    .to_pandas()
    .set_index("networkID")
)

# use smaller data types for smaller output files
length_cols = [c for c in stats.columns if c.endswith("_miles")]
for col in length_cols:
    stats[col] = stats[col].round(5).astype("float32")

for col in [c for c in stats.columns if c.startswith("pct_")]:
    stats[col] = stats[col].fillna(0).astype("int8")

# natural floodplain is missing for several catchments; fill with -1
for col in ["natfldpln", "sizeclasses"]:
    stats[col] = stats[col].fillna(-1).astype("int8")

flowlines = (
    read_arrow_tables(
        [src_dir / "raw" / huc2 / "flowlines.feather" for huc2 in huc2s],
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
        filter=pc.is_in(pc.field("lineID"), pa.array(segments.index.values)),
    )
    .to_pandas()
    .set_index("lineID")
)
flowlines["geometry"] = shapely.from_wkb(flowlines.geometry.values)
flowlines = gp.GeoDataFrame(flowlines, geometry="geometry", crs=CRS)

floodplains = (
    dataset("data/floodplains/floodplain_stats.feather", format="feather")
    .to_table(
        columns=["NHDPlusID", "nat_floodplain_km2", "floodplain_km2"],
        filter=pc.is_in(pc.field("NHDPlusID"), pa.array(flowlines.NHDPlusID.unique())),
    )
    .to_pandas()
    .set_index("NHDPlusID")
    .rename(columns={"nat_floodplain_km2": "natfldkm2", "floodplain_km2": "fldkm2"})
)
floodplains["natfldpln"] = (100 * floodplains.natfldkm2 / floodplains.fldkm2).astype("float32")

flowlines = flowlines.join(segments).join(floodplains, on="NHDPlusID").join(stats[["flows_to_ocean"]], on="networkID")
flowlines["km"] = flowlines["length"] / 1000.0
flowlines["miles"] = flowlines["length"] * 0.000621371

flowlines = flowlines.drop(columns=["length"])

for col in ["natfldpln", "fldkm2", "natfldkm2"]:
    flowlines[col] = flowlines[col].fillna(-1)


if driver == "ESRI Shapefile":
    # have to shorten fields
    flowlines = flowlines.rename(
        columns={
            "intermittent": "intermit",
            "StreamOrder": "StrOrd",
            "flows_to_ocean": "fl2ocean",
        }
    )

elif driver == "OpenFileGDB":
    # otherwise columns don't encode properly to FGDB
    for col in ["StreamOrder", "FCode", "FType", "intermittent", "altered"]:
        flowlines[col] = flowlines[col].astype("int32")


# serialize raw segments
print("Serializing undissolved networks...")
write_dataframe(
    flowlines.reset_index(),
    out_dir / f"{SARPID}_{scenario}_network_segments.{ext}",
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

if driver == "ESRI Shapefile":
    # have to shorten fields
    networks = networks.rename(
        columns={
            "total_miles": "tot_mi",
            "perennial_miles": "p_mi",
            "intermittent_miles": "int_mi",
            "altered_miles": "a_mi",
            "unaltered_miles": "ua_mi",
            "perennial_unaltered_miles": "pua_mi",
            "free_perennial_miles": "fp_mi",
            "free_intermittent_miles": "fint_mi",
            "free_altered_miles": "fa_mi",
            "free_unaltered_miles": "fua_mi",
            "free_perennial_unaltered_miles": "fpua_mi",
            "pct_unaltered": "pct_ua",
            "pct_perennial_unaltered": "pct_pua",
            "sizeclasses": "sizecl",
            "flows_to_ocean": "fl2ocean",
        }
    )


print("Serializing dissolved networks...")
write_dataframe(
    networks,
    out_dir / f"{SARPID}_{scenario}_networks.{ext}",
    driver=driver,
)
