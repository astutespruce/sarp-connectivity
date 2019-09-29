"""Generate list of NHDPlusIDs that intersect with Chesapeake Bay so that we can remove them"""


from pathlib import Path
import os
import pandas as pd
import geopandas as gp

from nhdnet.io import (
    serialize_df,
    deserialize_gdf,
    deserialize_df,
    to_shp,
    serialize_gdf,
)


HUC4 = "0208"


src_dir = Path("data/nhd/source/huc4")
gdb = src_dir / HUC4 / "NHDPLUS_H_{HUC4}_HU4_GDB.gdb".format(HUC4=HUC4)

flowlines = gp.read_file(gdb, layer="NHDFlowline")[["geometry", "NHDPlusID", "FType"]]
flowlines.NHDPlusID = flowlines.NHDPlusID.astype("uint64")

# Filter out artificial paths only
flowlines = flowlines.loc[flowlines.FType == 558].copy()
flowlines.sindex


wb = gp.read_file(gdb, layer="NHDWaterbody")[["geometry", "GNIS_Name"]]

# Extract out Chesapeake Bay
wb = wb.loc[wb.GNIS_Name == "Chesapeake Bay"].copy()
wb.sindex


# get the IDs of the segments that are within the bay
in_cb = gp.sjoin(flowlines, wb, op="within")

