"""Extract NHDPoint to use for the network analysis.

Point types listing: https://prd-wret.s3-us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/NHDv2.2.1_poster_081216.pdf
"""

from pathlib import Path
import os
from time import time

import geopandas as gp
import numpy as np
from geofeather import to_geofeather, from_geofeather
from nhdnet.geometry.lines import to2D
from nhdnet.io import serialize_df, deserialize_df, serialize_sindex, to_shp

from analysis.constants import REGIONS, REGION_GROUPS, CRS, EXCLUDE_IDs

KEEP_COLS = ["NHDPlusID", "FType", "FCode", "GNIS_Name", "geometry"]

# Dam, Gate, Lock Chamber, Waterfall
KEEP_FTYPES = [343, 369, 398, 487]


src_dir = Path("data/nhd/source/huc4")
nhd_dir = Path("data/nhd")


out_dir = nhd_dir / "extra"

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

start = time()

merged = None
for region, HUC2s in REGION_GROUPS.items():
    print("\n----- {} ------\n".format(region))

    for HUC2 in HUC2s:
        for i in REGIONS[HUC2]:
            HUC4 = "{0}{1:02d}".format(HUC2, i)

            read_start = time()
            print("\n\n------------------- Reading {} -------------------".format(HUC4))
            gdb = src_dir / HUC4 / "NHDPLUS_H_{HUC4}_HU4_GDB.gdb".format(HUC4=HUC4)

            df = gp.read_file(gdb, layer="NHDLine")
            df.NHDPlusID = df.NHDPlusID.astype("uint64")

            df = df.loc[df.FType.isin(KEEP_FTYPES)][KEEP_COLS].copy()

            # convert to LineString from MultiLineString
            idx = df.loc[df.geometry.type == "MultiLineString"].index
            df.loc[idx, "geometry"] = df.loc[idx].geometry.apply(lambda g: g[0])

            df.geometry = df.geometry.apply(to2D)
            df = df.to_crs(CRS)

            df.FType = df.FType.astype("uint16")
            df.FCode = df.FCode.astype("uint16")

            if merged is None:
                merged = df
            else:
                merged = merged.append(df, ignore_index=True)


print("Extracted {:,} NHD lines".format(len(merged)))
df = merged.reset_index(drop=True)

# add our own ID,
df["id"] = df.index.values.copy()
df.id = (df.id + 1).astype("uint32")

print("Serializing {:,} lines...".format(len(df)))
to_geofeather(df, out_dir / "nhd_lines.feather")
to_shp(df, out_dir / "nhd_lines.shp")

print("Done in {:.2f}s\n============================".format(time() - start))
