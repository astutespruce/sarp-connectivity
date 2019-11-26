"""
WARNING: due to the way that NHD waterbodies are defined, there may
be multiple drain points from a given waterbody.  Some of these are valid,
e.g., underground pipelines on different flowlines than natural drainage flowline.
"""

from pathlib import Path
from time import time
import pandas as pd
from geofeather import to_geofeather, from_geofeather
import geopandas as gp

from nhdnet.io import serialize_sindex, to_shp, deserialize_gdfs, deserialize_dfs


from analysis.constants import REGION_GROUPS, REGIONS


nhd_dir = Path("data/nhd")

start = time()


print("Reading flowline attributes...")
lineAtts = deserialize_dfs(
    [nhd_dir / "flowlines" / region / "flowline.feather" for region in REGION_GROUPS],
    columns=["lineID", "NHDPlusID", "streamorder", "sizeclass"],
).set_index("lineID")
print("Read {:,} flowlines".format(len(lineAtts)))

print("Reading waterbody drain points...")
drains = deserialize_gdfs(
    [
        nhd_dir / "flowlines" / region / "waterbody_drain_points.feather"
        for region in REGION_GROUPS
    ]
)

print("Read {:,} waterbody drain points".format(len(drains)))

# Add an internal ID, since there may be multiple drain points per waterbody
drains["id"] = drains.index.copy()
drains.id = drains.id.astype("uint32")

# TODO: remove on next full rerun of extract_waterbodies.py
drains.AreaSqKm = drains.AreaSqKm.astype("float32")
drains.numSegments = drains.numSegments.astype("uint16")


# join to line atts to get NHDPlusID, etc
drains = drains.join(lineAtts, on="lineID")


print("Serializing waterbody drain points...")
to_geofeather(drains, nhd_dir / "waterbody_drain_points.feather")
serialize_sindex(drains, nhd_dir / "waterbody_drain_points.sidx")
to_shp(drains, nhd_dir / "waterbody_drain_points.shp")


print("Reading waterbodies...")
wb = deserialize_gdfs(
    [nhd_dir / "flowlines" / region / "waterbodies.feather" for region in REGION_GROUPS]
)
print("Read {:,} waterbodies".format(len(wb)))

# TODO: remove on next full rerun of extract_waterbodies.py
wb.AreaSqKm = wb.AreaSqKm.astype("float32")
wb.FType = wb.FType.astype("uint16")
wb.numSegments = wb.wbSegments.astype("uint16")

print("Serializing waterbodies...")
to_geofeather(wb, nhd_dir / "waterbodies.feather")
to_shp(wb, nhd_dir / "waterbodies.shp")


print("Done in {:.2f}s\n============================".format(time() - start))
