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
from nhdnet.nhd.joins import find_joins, index_joins


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

# TEMP: can remove on next full run of prepare_flowlines_waterbodies.feather
wb.wbID = wb.wbID.astype("uint32")


print("Serializing waterbodies...")
to_geofeather(wb, out_dir / "waterbodies.feather")


print("Reading waterbody drain points...")
drains = deserialize_gdfs(
    [
        nhd_dir / "clean" / region / "waterbody_drain_points.feather"
        for region in REGION_GROUPS
    ],
    src=[region for region in REGION_GROUPS],
).reset_index(drop=True)

print("Read {:,} waterbody drain points".format(len(drains)))

### Deduplicate and assign to the next segment downstream where there are multiple segments intersecting
joins = deserialize_dfs(
    [nhd_dir / "clean" / region / "flowline_joins.feather" for region in REGION_GROUPS],
    src=[region for region in REGION_GROUPS],
).reset_index(drop=True)

counts = drains.groupby("wbID").size()
dup_ix = counts.loc[counts > 1].index

# cluster them based on their next downstream ID
# ONLY for those that are not terminals
dups = (
    drains.loc[drains.wbID.isin(dup_ix)]
    .join(
        joins.loc[joins.downstream_id != 0].set_index("upstream_id").downstream_id,
        on="lineID",
    )
    .set_index(["wbID", "downstream_id"])
)
counts = dups.groupby(level=[0, 1]).size()

dups = dups.loc[dups.index.isin(counts.loc[counts > 1].index)]
print("Found {:,} duplicate drains, removing them...".format(len(dups)))

drains = drains.join(
    dups.reset_index().set_index(["lineID", "wbID"]).downstream_id,
    how="left",
    on=["lineID", "wbID"],
).reset_index()
ix = drains.downstream_id.notnull()
# Assign the downstream line ID for the duplicates
drains.loc[ix, "lineID"] = drains.loc[ix].downstream_id.astype("uint32")
drains = drains.drop(columns=["downstream_id"])

# Take the first instance for each duplicate
drains = gp.GeoDataFrame(
    drains.groupby(["lineID", "wbID"]).first().reset_index(), crs=wb.crs
)

# TODO: check if there are multiple identical downstreams
# This is harder to do properly.
# counts = drains.groupby("wbID").size()
# dup_ix = counts.loc[counts > 1].index
# dups = drains.loc[drains.wbID.isin(dup_ix)].join(joins.loc[joins.downstream==0].set_index('upstream_id').downstream_id, on='lineID')
# dups['wkb'] = dups.geometry.apply(lambda g: g.wkb)
# counts = dups.groupby(['wbID', 'downstream_id', 'wkb']).size()
# ix = counts.loc[counts > 1]


# Add an internal ID, since there may be multiple drain points per waterbody
drains["id"] = drains.index.copy() + 1
drains.id = drains.id.astype("uint32")


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
