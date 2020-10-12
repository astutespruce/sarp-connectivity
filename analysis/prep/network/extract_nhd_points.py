"""Extract NHDPoint to use for the network analysis.

Point types listing: https://prd-wret.s3-us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/NHDv2.2.1_poster_081216.pdf
"""

from pathlib import Path
import os
from time import time
import sys

import geopandas as gp
from geofeather import to_geofeather, from_geofeather
from nhdnet.geometry.points import to2D
from nhdnet.io import serialize_df, deserialize_df, serialize_sindex, to_shp

from analysis.constants import REGIONS, REGION_GROUPS, CRS

KEEP_COLS = ["NHDPlusID", "FType", "FCode", "GNIS_Name", "geometry"]

# Dam, reservoir, waterfall
KEEP_FTYPES = [343, 436, 487]


src_dir = Path("data/nhd/source/huc4")
nhd_dir = Path("data/nhd")


out_dir = nhd_dir / "extra"

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

start = time()

merged = None
for region, HUC2s in list(REGION_GROUPS.items())[-1:]:
    print("\n----- {} ------\n".format(region))

    for HUC2 in HUC2s:
        for i in REGIONS[HUC2]:
            HUC4 = "{0}{1:02d}".format(HUC2, i)

            read_start = time()
            print("\n\n------------------- Reading {} -------------------".format(HUC4))
            gdb = src_dir / HUC4 / "NHDPLUS_H_{HUC4}_HU4_GDB.gdb".format(HUC4=HUC4)

            df = gp.read_file(gdb, layer="NHDPoint")
            df.NHDPlusID = df.NHDPlusID.astype("uint64")

            df = df.loc[df.FType.isin(KEEP_FTYPES)][KEEP_COLS].copy()

            df.FType = df.FType.astype("uint16")
            df.FCode = df.FCode.astype("uint16")
            df["HUC2"] = HUC2

            if not len(df):
                continue

            df.geometry = df.geometry.apply(to2D)
            df = df.to_crs(CRS)

            if merged is None:
                merged = df
            else:
                merged = merged.append(df, ignore_index=True, sort=False)

if merged is None or len(merged) == 0:
    print("No NHD points available in this region, no outputs will be created.")
    sys.exit(0)

print("Extracted {:,} NHD Points".format(len(merged)))
df = merged.reset_index(drop=True)

# add our own ID,
df["id"] = df.index.values.copy()
df.id = (df.id + 1).astype("uint32")

print("Serializing {:,} points...".format(len(df)))
to_geofeather(df, out_dir / "nhd_points.feather")
to_shp(df, out_dir / "nhd_points.shp")

print("Done in {:.2f}s\n============================".format(time() - start))
