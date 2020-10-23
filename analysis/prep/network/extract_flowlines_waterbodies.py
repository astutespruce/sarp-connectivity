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

import pandas as pd
import geopandas as gp
import pygeos as pg
from pyogrio import write_dataframe

from nhdnet.nhd.extract import extract_flowlines, extract_waterbodies
from nhdnet.io import serialize_df, serialize_sindex, to_shp

from analysis.constants import (
    REGIONS,
    REGION_GROUPS,
    CRS,
    WATERBODY_EXCLUDE_FTYPES,
    WATERBODY_MIN_SIZE,
)
from analysis.pygeos_compat import sjoin_geometry
from analysis.util import append


src_dir = Path("data/nhd/source/huc4")
out_dir = Path("data/nhd/raw")

if not out_dir.exists():
    os.makedirs(out_dir)

start = time()

# useful slices are [:2], [2:4], [4:]
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
            # use waterbodies to query flowlines since there are many more flowlines
            wb_joins = sjoin_geometry(
                pd.Series(waterbodies.geometry.values.data, index=waterbodies.index),
                pd.Series(flowlines.geometry.values.data, index=flowlines.index),
                how="inner",
            )
            wb_joins = (
                waterbodies[["wbID"]]
                .join(wb_joins, how="inner")
                .join(flowlines[["lineID"]], on="index_right", how="inner")[
                    ["wbID", "lineID"]
                ]
            )

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

    # TODO: rework this to use pygeos
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

    print("serializing {:,} flowlines".format(len(flowlines)))
    flowlines.to_feather(region_dir / "flowlines.feather")

    write_dataframe(flowlines, region_dir / "flowlines.gpkg", driver="GPKG")
    serialize_df(joins, region_dir / "flowline_joins.feather", index=False)

    print("serializing {:,} waterbodies".format(len(waterbodies)))
    waterbodies.to_feather(region_dir / "waterbodies.feather")
    write_dataframe(waterbodies, region_dir / "waterbodies.gpkg", driver="GPKG")
    serialize_df(wb_joins, region_dir / "waterbody_flowline_joins.feather", index=False)

    print("Region done in {:.0f}s".format(time() - region_start))


print("Done in {:.2f}s\n============================".format(time() - start))

