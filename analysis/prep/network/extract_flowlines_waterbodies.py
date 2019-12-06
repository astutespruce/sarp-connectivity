"""
Extract NHD File Geodatabases (FGDB) for all HUC4s within each region group (set of HUC2s).

Data are downloaded using `nhd/download.py::download_huc4`.

Only the flowlines, joins between flowlines, and specific attributes are extracted for analysis.

Due to data limitations of the FGDB / Shapefile format, NHDPlus IDs are represented natively as float64 data.
However, float64 data are not ideal for indexing, so all IDs are converted to uint64 within this package, and
converted back to float64 only for export to GIS.

These are output as 4 files:
* flowlines.feather: serialized flowline geometry and attributes
* flowline_joins.feather: serialized joins between adjacent flowlines, with the upstream and downstream IDs of a join
* waterbodies.feather: serialized waterbody geometry and attributes
* waterbody_flowline_joins.feather: serialized joins between waterbodies and any intersecting flowlines.  NOTE: may include flowlines that touch but do not overlap with waterbodies.

Note: there may be cases where Geopandas is unable to read a FGDB file.  See `nhdnet.nhd.extract` for specific workarounds.
"""

from pathlib import Path
import os
from time import time
import geopandas as gp

from geofeather import to_geofeather
from nhdnet.nhd.extract import extract_flowlines, extract_waterbodies
from nhdnet.io import serialize_df, serialize_sindex, to_shp


from analysis.constants import (
    REGIONS,
    REGION_GROUPS,
    CRS,
    WATERBODY_EXCLUDE_FTYPES,
    WATERBODY_MIN_SIZE,
)
from analysis.util import append


src_dir = Path("data/nhd/source/huc4")
out_dir = Path("data/nhd/raw")

start = time()

# useful slices are :3, 3:5, 5:
for region, HUC2s in list(REGION_GROUPS.items()):
    print("\n----- {} ------\n".format(region))

    region_dir = out_dir / region
    if not os.path.exists(region_dir):
        os.makedirs(region_dir)

    # if os.path.exists(region_dir / "flowline.feather"):
    #     print("Skipping existing region {}".format(region))
    #     continue

    region_start = time()

    merged_flowlines = None
    merged_joins = None
    merged_waterbodies = None
    merged_waterbody_joins = None

    for HUC2 in HUC2s:
        for i in REGIONS[HUC2]:
            HUC4 = "{0}{1:02d}".format(HUC2, i)
            print("\n\n------------------- Reading {} -------------------".format(HUC4))

            huc_id = int(HUC4) * 1000000

            gdb = src_dir / HUC4 / "NHDPLUS_H_{HUC4}_HU4_GDB.gdb".format(HUC4=HUC4)

            ### Read flowlines and joins
            read_start = time()
            flowlines, joins = extract_flowlines(gdb, target_crs=CRS)
            print(
                "Read {:,} flowlines in  {:.0f} seconds".format(
                    len(flowlines), time() - read_start
                )
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
                    "loop",
                ]
            ]

            # Calculate lineIDs to be unique across the regions

            flowlines["lineID"] += huc_id
            # Set updated lineIDs with the HUC4 prefix
            joins.loc[joins.upstream_id != 0, "upstream_id"] += huc_id
            joins.loc[joins.downstream_id != 0, "downstream_id"] += huc_id

            ### Read waterbodies
            read_start = time()
            waterbodies = extract_waterbodies(
                gdb,
                target_crs=CRS,
                exclude_ftypes=WATERBODY_EXCLUDE_FTYPES,
                min_area=WATERBODY_MIN_SIZE,
            )
            print(
                "Read {:,} waterbodies in  {:.0f} seconds".format(
                    len(waterbodies), time() - read_start
                )
            )

            # calculate ids to be unique across region
            waterbodies["wbID"] += huc_id

            ### Only retain waterbodies that intersect flowlines
            print("Intersecting waterbodies and flowlines")
            wb_joins = gp.sjoin(waterbodies, flowlines, how="inner", op="intersects")[
                ["wbID", "lineID"]
            ]

            waterbodies = waterbodies.loc[waterbodies.wbID.isin(wb_joins.wbID)].copy()
            print(
                "Retained {:,} waterbodies that intersect flowlines".format(
                    len(waterbodies)
                )
            )

            merged_flowlines = append(merged_flowlines, flowlines)
            merged_joins = append(merged_joins, joins)
            merged_waterbodies = append(merged_waterbodies, waterbodies)
            merged_waterbody_joins = append(merged_waterbody_joins, wb_joins)

    print("--------------------")

    flowlines = merged_flowlines.reset_index(drop=True)
    joins = merged_joins.reset_index(drop=True)
    waterbodies = merged_waterbodies.reset_index(drop=True)
    wb_joins = merged_waterbody_joins.reset_index(drop=True)

    ### Deduplicate waterbodies that are duplicated between adjacent HUC4s
    print("Removing duplicate waterbodies, starting with {:,}".format(len(waterbodies)))
    # Calculate a hash of the WKB bytes of the polygon.
    # This correctly catches polygons that are EXACTLY the same.
    # It will miss those that are NEARLY the same.
    waterbodies["hash"] = waterbodies.geometry.apply(lambda g: hash(g.wkb))

    id_map = (
        waterbodies.set_index("wbID")[["hash"]]
        .join(waterbodies.groupby("hash").wbID.first(), on="hash")
        .wbID
    )
    # extract out where they are not equal; these are the ones to drop
    waterbodies = (
        waterbodies.loc[waterbodies.wbID.isin(id_map)]
        .drop(columns=["hash"])
        .reset_index(drop=True)
    )
    print("{:,} waterbodies remain after removing duplicates".format(len(waterbodies)))

    # remove their corresponding joins
    ix = wb_joins.loc[~wb_joins.wbID.isin(id_map)].index
    # update IDs using map
    wb_joins.loc[ix, "wbID"] = wb_joins.loc[ix].wbID.map(id_map)
    wb_joins = wb_joins.drop_duplicates().reset_index(drop=True)

    ### Update the missing upstream_ids at the joins between HUCs.
    # These are the segments that are immediately DOWNSTREAM of segments that flow into this HUC4
    # We set a new UPSTREAM id for them based on the segment that is next upstream

    huc_in_idx = merged_joins.loc[joins.type == "huc_in"].index
    cross_huc_joins = joins.loc[huc_in_idx]

    new_upstreams = (
        cross_huc_joins.join(
            joins.set_index("downstream").downstream_id.rename("new_upstream"),
            on="upstream",
        )
        .new_upstream.fillna(0)
        .astype("uint32")
    )
    joins.loc[new_upstreams.index, "upstream_id"] = new_upstreams

    # update new internal joins
    joins.loc[(joins.type == "huc_in") & (joins.upstream_id != 0), "type"] = "internal"

    # remove the duplicate downstreams that used to be terminals for their respective HUCs
    joins = joins.loc[
        ~(joins.upstream.isin(cross_huc_joins.upstream) & (joins.type == "terminal"))
    ]

    # remove dead ends
    joins = joins.loc[~((joins.downstream == 0) & (joins.upstream == 0))].copy()

    print("serializing {:,} flowlines to feather".format(len(flowlines)))
    to_geofeather(flowlines, region_dir / "flowlines.feather")
    serialize_df(joins, region_dir / "flowline_joins.feather", index=False)

    print("serializing {:,} waterbodies to feather".format(len(waterbodies)))
    to_geofeather(waterbodies, region_dir / "waterbodies.feather")
    serialize_df(wb_joins, region_dir / "waterbody_flowline_joins.feather", index=False)
    print("Region done in {:.0f}s".format(time() - region_start))


print("Done in {:.2f}s\n============================".format(time() - start))


# FIXME: add a post-processing step for this
# Exclude flowlines as needed

# if HUC4 in EXCLUDE_IDs:
#     exclude_ids = EXCLUDE_IDs[HUC4]
#     flowlines = flowlines.loc[~flowlines.NHDPlusID.isin(exclude_ids)].copy()

#     # update downstream end of joins
#     downstream_idx = joins.loc[joins.downstream.isin(exclude_ids)].index
#     joins.loc[downstream_idx, "downstream_id"] = 0
#     joins.loc[downstream_idx, "downstream"] = 0
#     joins.loc[downstream_idx, "type"] = "terminal"

#     # remove upstream end of joins
#     joins = joins.loc[~joins.upstream.isin(exclude_ids)].copy()

#     # reset dtypes
#     joins.downstream = joins.downstream.astype("uint64")
#     joins.downstream_id = joins.downstream_id.astype("uint32")

#     print(
#         "Removed excluded flowlines, now have {:,}".format(len(flowlines))
#     )

# FIXME: do this in later step
# * FIXME: flowline.sidx: serialized bounding box data used to reconstruct the spatial index for flowlines
# TODO: use .to_file() method instead of to_shp()
# serialize_sindex(merged, region_dir / "flowline.sidx")

# print("serializing to shp")
# serialize_start = time()
# to_shp(merged.reset_index(drop=True), region_dir / "flowline.shp")
# print("serialize done in {:.0f}s".format(time() - serialize_start))
