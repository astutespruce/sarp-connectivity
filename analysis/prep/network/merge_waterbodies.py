"""
WARNING: due to the way that NHD waterbodies are defined, there may
be multiple drain points from a given waterbody.  Some of these are valid,
e.g., underground pipelines on different flowlines than natural drainage flowline.
"""

import os
from pathlib import Path
from time import time
import pandas as pd
from geofeather import to_geofeather, from_geofeather
import geopandas as gp

from nhdnet.io import serialize_sindex, to_shp, deserialize_gdfs, deserialize_dfs


from analysis.constants import (
    REGION_GROUPS,
    REGIONS,
    LARGE_WB_AREA,
    LARGE_WB_FLOWLINE_LENGTH,
)

nhd_dir = Path("data/nhd")
out_dir = nhd_dir / "merged"

if not os.path.exists(out_dir):
    os.makedirs(out_dir)


start = time()


print("Reading waterbodies...")
wb = (
    deserialize_gdfs(
        [
            nhd_dir / "clean" / region / "waterbodies.feather"
            for region in REGION_GROUPS
        ],
        src=[region for region in REGION_GROUPS],
    )
    .rename(columns={"src": "region"})
    .reset_index(drop=True)
)
print("Read {:,} waterbodies".format(len(wb)))


# print("Reading flowline attributes...")
# lineAtts = deserialize_dfs(
#     [nhd_dir / "flowlines" / region / "flowline.feather" for region in REGION_GROUPS],
#     columns=["lineID", "NHDPlusID", "streamorder", "sizeclass", "loop"],
# ).set_index("lineID")
# print("Read {:,} flowlines".format(len(lineAtts)))

print("Reading waterbody drain points...")
drains = deserialize_gdfs(
    [
        nhd_dir / "clean" / region / "waterbody_drain_points.feather"
        for region in REGION_GROUPS
    ],
    src=[region for region in REGION_GROUPS],
).reset_index(drop=True)

print("Read {:,} waterbody drain points".format(len(drains)))

# Add an internal ID, since there may be multiple drain points per waterbody
drains["id"] = drains.index.copy() + 1
drains.id = drains.id.astype("uint32")

print("Serializing waterbodies...")
to_geofeather(wb, out_dir / "waterbodies.feather")

# Extract large waterbodies
# Arbitrary cutoffs, but per visual inspection looks reasonable
large_wb = wb.loc[
    (wb.flowlineLength >= LARGE_WB_FLOWLINE_LENGTH) & (wb.AreaSqKm >= LARGE_WB_AREA)
].reset_index(drop=True)
to_geofeather(large_wb, out_dir / "large_waterbodies.feather")

large_drains = drains.loc[drains.wbID.isin(large_wb.wbID)].reset_index(drop=True)
to_geofeather(large_drains, out_dir / "large_waterbody_drain_points.feather")


print("Serializing waterbody drain points...")
to_geofeather(drains, out_dir / "waterbody_drain_points.feather")

print("Serializing to shapefiles...")
to_shp(wb, out_dir / "waterbodies.shp")
to_shp(large_wb, out_dir / "large_waterbodies.shp")
to_shp(drains, out_dir / "waterbody_drain_points.shp")
to_shp(large_drains, out_dir / "large_waterbody_drain_points.shp")


print("Done in {:.2f}s\n============================".format(time() - start))
