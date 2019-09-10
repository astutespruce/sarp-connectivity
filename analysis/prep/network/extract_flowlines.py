"""
Extract NHD File Geodatabases (FGDB) for all HUC4s within a region (HUC2).

Data are downloaded using `nhd/download.py::download_huc4`.

Only the flowlines, joins between flowlines, and specific attributes are extracted for analysis.

Due to data limitations of the FGDB / Shapefile format, NHDPlus IDs are represented natively as float64 data.
However, float64 data are not ideal for indexing, so all IDs are converted to uint64 within this package, and
converted back to float64 only for export to GIS.

These are output as 2 files:
* flowlines.feather: serialized flowline geometry and attributes
* flowline_joins.feather: serialized joins between adjacent flowlines, with the upstream and downstream IDs of a join

Note: there may be cases where Geopandas is unable to read a FGDB file.  See `nhdnet.nhd.extract` for specific workarounds.
"""

from pathlib import Path
import os
from time import time

from nhdnet.nhd.extract import extract_flowlines
from nhdnet.nhd.legacy.extract import extract_flowlines_mr
from nhdnet.io import serialize_gdf, serialize_df, to_shp

from analysis.constants import REGIONS, REGION_GROUPS, CRS


src_dir = Path("data/nhd/source/huc4")
out_dir = Path("data/nhd/flowlines")

start = time()

for region, HUC2s in REGION_GROUPS.items():
    print("\n----- {} ------\n".format(region))

    if os.path.exists(region_dir / "flowline.feather"):
        print("Skipping existing region {}".format(region))
        continue


    region_start = time()

    merged = None
    merged_joins = None

    for HUC2 in HUC2s:
        if HUC2 == "08":
            # Skip for now
            continue

        for i in REGIONS[HUC2]:
            HUC4 = "{0}{1:02d}".format(HUC2, i)

            read_start = time()
            print("Reading {}".format(HUC4))
            gdb = src_dir / HUC4 / "NHDPLUS_H_{HUC4}_HU4_GDB.gdb".format(HUC4=HUC4)
            flowlines, joins = extract_flowlines(gdb, target_crs=CRS)
            print("Read {} flowlines in  {:.0f} seconds".format(len(flowlines), time() - read_start))

            flowlines = flowlines[
                [
                    "geometry",
                    "lineID",
                    "NHDPlusID",
                    "length",
                    "sinuosity",
                    "sizeclass",
                    "streamorder",
                ]
            ]
            flowlines["HUC2"] = HUC2
            joins["HUC2"] = HUC2

            # Calculate lineIDs to be unique across the regions
            huc_id = int(HUC4) * 1000000
            flowlines["lineID"] += huc_id
            # Set updated lineIDs with the HUC4 prefix
            joins.loc[joins.upstream_id != 0, "upstream_id"] += huc_id
            joins.loc[joins.downstream_id != 0, "downstream_id"] += huc_id

            if merged is None:
                merged = flowlines
                merged_joins = joins
            else:
                merged = merged.append(flowlines, ignore_index=True)
                merged_joins = merged_joins.append(joins, ignore_index=True)

    # TODO: redo this as a join
    # Update the missing upstream_ids at the joins between HUCs
    huc_in = merged_joins.loc[merged_joins.type == "huc_in"]
    for idx, row in huc_in.iterrows():
        match = merged_joins.loc[merged_joins.downstream == row.upstream].downstream_id
        if len(match):
            merged_joins.loc[idx, "upstream_id"] = match.iloc[0]

    # remove duplicate terminals
    merged_joins = merged_joins.loc[
        ~(
            merged_joins.upstream.isin(huc_in.upstream)
            & (merged_joins.type == "terminal")
        )
    ].copy()

    region_dir = out_dir / region
    if not os.path.exists(region_dir):
        os.makedirs(region_dir)

    print("serializing {} flowlines to feather".format(len(merged)))
    serialize_gdf(merged, region_dir / "flowline.feather")
    serialize_df(merged_joins, region_dir / "flowline_joins.feather", index=False)

    print("serializing to shp")
    serialize_start = time()
    to_shp(merged, region_dir / "flowline.shp")
    print("serialize done in {:.0f}".format(time() - serialize_start))

    print("Region done in {:.0f}".format(time() - region_start))


print("Done in {:.2f}\n============================".format(time() - start))
