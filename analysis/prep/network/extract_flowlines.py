"""
Extract NHD File Geodatabases (FGDB) for all HUC4s within each region group (set of HUC2s).

Data are downloaded using `nhd/download.py::download_huc4`.

Only the flowlines, joins between flowlines, and specific attributes are extracted for analysis.

Due to data limitations of the FGDB / Shapefile format, NHDPlus IDs are represented natively as float64 data.
However, float64 data are not ideal for indexing, so all IDs are converted to uint64 within this package, and
converted back to float64 only for export to GIS.

These are output as 3 files:
* flowline.feather: serialized flowline geometry and attributes
* flowline.sidx: serialized bounding box data used to reconstruct the spatial index for flowlines
* flowline_joins.feather: serialized joins between adjacent flowlines, with the upstream and downstream IDs of a join

Note: there may be cases where Geopandas is unable to read a FGDB file.  See `nhdnet.nhd.extract` for specific workarounds.
"""

from pathlib import Path
import os
from time import time

from geofeather import to_geofeather
from nhdnet.nhd.extract import extract_flowlines
from nhdnet.io import serialize_df, serialize_sindex, to_shp


from analysis.constants import REGIONS, REGION_GROUPS, CRS, EXCLUDE_IDs


src_dir = Path("data/nhd/source/huc4")
out_dir = Path("data/nhd/flowlines")

start = time()

for region, HUC2s in REGION_GROUPS.items():
    print("\n----- {} ------\n".format(region))

    region_dir = out_dir / region
    if not os.path.exists(region_dir):
        os.makedirs(region_dir)

    if os.path.exists(region_dir / "flowline.feather"):
        print("Skipping existing region {}".format(region))
        continue

    region_start = time()

    merged = None
    merged_joins = None

    for HUC2 in HUC2s:
        for i in REGIONS[HUC2]:
            HUC4 = "{0}{1:02d}".format(HUC2, i)

            read_start = time()
            print("\n\n------------------- Reading {} -------------------".format(HUC4))
            gdb = src_dir / HUC4 / "NHDPLUS_H_{HUC4}_HU4_GDB.gdb".format(HUC4=HUC4)
            flowlines, joins = extract_flowlines(gdb, target_crs=CRS)
            print(
                "Read {:,} flowlines in  {:.0f} seconds".format(
                    len(flowlines), time() - read_start
                )
            )

            # Exclude flowlines as needed
            if HUC4 in EXCLUDE_IDs:
                exclude_ids = EXCLUDE_IDs[HUC4]
                flowlines = flowlines.loc[~flowlines.NHDPlusID.isin(exclude_ids)].copy()

                # update downstream end of joins
                downstream_idx = joins.loc[joins.downstream.isin(exclude_ids)].index
                joins.loc[downstream_idx, "downstream_id"] = 0
                joins.loc[downstream_idx, "downstream"] = 0
                joins.loc[downstream_idx, "type"] = "terminal"

                # remove upstream end of joins
                joins = joins.loc[~joins.upstream.isin(exclude_ids)].copy()

                # reset dtypes
                joins.downstream = joins.downstream.astype("uint64")
                joins.downstream_id = joins.downstream_id.astype("uint32")

                print(
                    "Removed excluded flowlines, now have {:,}".format(len(flowlines))
                )

            flowlines = flowlines[
                [
                    "geometry",
                    "lineID",
                    "NHDPlusID",
                    "FType",
                    "length",
                    "sinuosity",
                    "sizeclass",
                    "streamorder",
                ]
            ]

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

    # Update the missing upstream_ids at the joins between HUCs.
    # These are the segments that are immediately DOWNSTREAM of segments that flow into this HUC4
    # We set a new UPSTREAM id for them based on the segment that is next upstream

    huc_in_idx = merged_joins.loc[merged_joins.type == "huc_in"].index
    cross_huc_joins = merged_joins.loc[huc_in_idx]

    new_upstreams = (
        cross_huc_joins.join(
            merged_joins.set_index("downstream").downstream_id.rename("new_upstream"),
            on="upstream",
        )
        .new_upstream.fillna(0)
        .astype("uint32")
    )
    merged_joins.loc[new_upstreams.index, "upstream_id"] = new_upstreams

    # update new internal joins
    merged_joins.loc[
        (merged_joins.type == "huc_in") & (merged_joins.upstream_id != 0), "type"
    ] = "internal"

    # remove the duplicate downstreams that used to be terminals for their respective HUCs
    merged_joins = merged_joins.loc[
        ~(
            merged_joins.upstream.isin(cross_huc_joins.upstream)
            & (merged_joins.type == "terminal")
        )
    ]

    # remove dead ends
    merged_joins = merged_joins.loc[
        ~((merged_joins.downstream == 0) & (merged_joins.upstream == 0))
    ].copy()

    print("--------------------")

    print("serializing {:,} flowlines to feather".format(len(merged)))
    to_geofeather(merged.reset_index(drop=True), region_dir / "flowline.feather")
    serialize_sindex(merged, region_dir / "flowline.sidx")
    serialize_df(merged_joins, region_dir / "flowline_joins.feather", index=False)

    print("serializing to shp")
    serialize_start = time()
    to_shp(merged.reset_index(drop=True), region_dir / "flowline.shp")
    print("serialize done in {:.0f}s".format(time() - serialize_start))

    print("Region done in {:.0f}s".format(time() - region_start))


print("Done in {:.2f}s\n============================".format(time() - start))
