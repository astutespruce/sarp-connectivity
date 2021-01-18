"""Extract undissolved networks with flowline attributes, floodplain stats, etc
for SARP analysis.

Note: this pulls in merged networks where they exist.
"""


from pathlib import Path
import os
from time import time

import geopandas as gp
import pandas as pd
from pyogrio import write_dataframe

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
huc2s = ["05", "06", "07", "08", "10", "11"]

floodplains = (
    pd.read_feather(
        data_dir / "floodplains/floodplain_stats.feather",
        columns=["NHDPlusID", "nat_floodplain_km2", "floodplain_km2"],
    )
    .set_index("NHDPlusID")
    .rename(columns={"nat_floodplain_km2": "natfldkm2", "floodplain_km2": "fldkm2"})
)
floodplains["natfldpln"] = (100 * floodplains.natfldkm2 / floodplains.fldkm2).astype(
    "float32"
)

network_type = NETWORK_TYPES[1]
for huc2 in huc2s:
    print(f"----- {huc2} ({network_type}) ------")

    region_start = time()

    working_dir = network_dir / huc2 / network_type

    merged = False
    merged_dir = None

    if os.path.exists(network_dir / "merged" / huc2):
        merged = True
        merged_dir = network_dir / "merged" / huc2 / network_type

    ### Write barriers to Shapefile
    barriers_network = (
        pd.read_feather((merged_dir or working_dir) / "barriers_network.feather")
        .set_index("barrierID")
        .drop(columns=["id"])
    ).rename(
        columns={
            "TotalUpstreamMiles": "TotUpMi",
            "TotalDownstreamMiles": "TotDownMi",
            "FreeUpstreamMiles": "FreeUpMi",
            "FreeDownstreamMiles": "FreeDownMi",
            "sizeclasses": "numsizes",
        }
    )

    barriers = gp.read_feather(
        network_dir / huc2 / network_type / "barriers.feather",
        columns=["barrierID", "geometry", "NHDPlusID"],
    ).set_index("barrierID")

    barriers = barriers.join(barriers_network)

    barriers.numsizes = barriers.fillna(0).numsizes.astype("uint8")
    # Note: some barriers don't have networks upstream; these are assigned a network of 0
    for col in ["upNetID", "downNetID", "segments"]:
        barriers[col] = barriers[col].fillna(0).astype("uint32")

    for col in barriers.columns[barriers.dtypes == "float64"]:
        barriers[col] = barriers[col].astype("float32")

    barriers.kind = barriers.kind.fillna("")

    write_dataframe(barriers, out_dir / f"region{huc2}_{network_type}_waterfalls.shp")

    ### Extract dissolved networks to shapefile

    networks = gp.read_feather((merged_dir or working_dir) / "network.feather").rename(
        columns={"sizeclasses": "sizes"}
    )

    networks.networkID = networks.networkID.astype("uint32")
    networks.sizes = networks.sizes.astype("uint8")

    for col in networks.columns[networks.dtypes == "float64"]:
        networks[col] = networks[col].astype("float32")

    write_dataframe(networks, out_dir / f"region{huc2}_{network_type}_networks.shp")

    ### Extract undissolved networks to shapefile
    segments = pd.read_feather(
        network_dir / huc2 / network_type / "network_segments.feather",
        columns=["networkID", "lineID"],
    )
    segments.lineID = segments.lineID.astype("uint32")
    segments.networkID = segments.networkID.astype("uint32")
    segments = segments.set_index("lineID")
    # join in barrier type for network
    segments = segments.join(networks.set_index("networkID").barrier)
    segments.barrier = segments.barrier.fillna("")

    flowlines = gp.read_feather(
        network_dir / huc2 / network_type / "flowlines.feather",
        columns=[
            "lineID",
            "NHDPlusID",
            "FCode",
            "FType",
            "GNIS_ID",
            "GNIS_Name",
            "StreamOrde",
            "TotDASqKm",
            "sizeclass",
            "length",
            "sinuosity",
            "geometry",
        ],
    ).rename(
        columns={
            "sizeclass": "size",
            "length": "length_m",
        }
    )
    flowlines.lineID = flowlines.lineID.astype("uint32")
    flowlines.GNIS_ID = flowlines.GNIS_ID.fillna("")
    flowlines.GNIS_Name = flowlines.GNIS_Name.fillna("")

    for col in flowlines.columns[flowlines.dtypes == "float64"]:
        flowlines[col] = flowlines[col].astype("float32")

    flowlines = flowlines.join(floodplains, on="NHDPlusID").join(segments, on="lineID")

    write_dataframe(
        flowlines, out_dir / f"region{huc2}_{network_type}_network_segments.shp"
    )
