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


print("Reading waterbodies...")
wb = (
    deserialize_gdfs(
        [
            nhd_dir / "waterbodies" / region / "waterbodies.feather"
            for region in REGION_GROUPS
        ],
        src=[region for region in REGION_GROUPS],
    )
    .rename(columns={"src": "region"})
    .reset_index(drop=True)
)
print("Read {:,} waterbodies".format(len(wb)))

# Add a new global wbID
wb["id"] = wb.index.copy() + 1
wb.id = wb.id.astype("uint32")


print("Reading flowline attributes...")
lineAtts = deserialize_dfs(
    [nhd_dir / "flowlines" / region / "flowline.feather" for region in REGION_GROUPS],
    columns=["lineID", "NHDPlusID", "streamorder", "sizeclass"],
).set_index("lineID")
print("Read {:,} flowlines".format(len(lineAtts)))

print("Reading waterbody drain points...")
drains = (
    deserialize_gdfs(
        [
            nhd_dir / "waterbodies" / region / "waterbody_drain_points.feather"
            for region in REGION_GROUPS
        ],
        src=[region for region in REGION_GROUPS],
        columns=[
            "geometry",
            "wbID",
            "lineID",
            "flowlineLength",
            "numSegments",
            "AreaSqKm",
        ],
    )
    .rename(
        columns={
            "src": "region",
            "flowlineLength": "wbFlowlineLength",
            "numSegments": "wbSegments",
            "AreaSqKm": "wbAreaKM2",
        }
    )
    .reset_index(drop=True)
)

print("Read {:,} waterbody drain points".format(len(drains)))

# Add an internal ID, since there may be multiple drain points per waterbody
drains["id"] = drains.index.copy() + 1
drains.id = drains.id.astype("uint32")

# join to waterbodies to get global ID
drains = drains.join(
    wb.set_index(["region", "wbID"]).id.rename("wbID"), on=["region", "regionWBID"]
)

# join to line atts to get NHDPlusID, etc
drains = drains.join(lineAtts, on="lineID")


print("Serializing waterbodies...")
to_geofeather(wb, nhd_dir / "waterbodies" / "waterbodies.feather")

print("Serializing waterbody drain points...")
to_geofeather(drains, nhd_dir / "waterbodies" / "waterbody_drain_points.feather")
serialize_sindex(drains, nhd_dir / "waterbodies" / "waterbody_drain_points.sidx")

print("Serializing to shapefiles...")
to_shp(wb, nhd_dir / "waterbodies" / "waterbodies.shp")
to_shp(drains, nhd_dir / "waterbodies" / "waterbody_drain_points.shp")


print("Done in {:.2f}s\n============================".format(time() - start))
