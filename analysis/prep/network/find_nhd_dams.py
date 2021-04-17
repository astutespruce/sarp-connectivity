from pathlib import Path
import os
from time import time
import warnings

import numpy as np
import pandas as pd
import pygeos as pg
import geopandas as gp
from pyogrio import write_dataframe

from analysis.lib.joins import find_joins
from analysis.lib.util import append
from analysis.lib.geometry import (
    dissolve,
    explode,
    sjoin_geometry,
    nearest,
    find_contiguous_groups,
)
from analysis.lib.io import read_feathers

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


# consider dam associated with waterbody drain if within 50m
NEAREST_DRAIN_TOLERANCE = 50


data_dir = Path("data")
raw_dir = Path("data/nhd/raw")
clean_dir = Path("data/nhd/clean")
out_dir = Path("data/nhd/merged")

if not out_dir.exists():
    os.makedirs(out_dir)

start = time()

huc2s = sorted(
    pd.read_feather(
        data_dir / "boundaries/huc4.feather", columns=["HUC2"]
    ).HUC2.unique()
)

### Merge NHD lines and areas that represent dams and dam-related features
print("Reading NHD points, lines, and areas, and merging...")
nhd_pts = read_feathers(
    [raw_dir / huc2 / "nhd_points.feather" for huc2 in huc2s],
    geo=True,
    new_fields={"HUC2": huc2s},
)
nhd_pts = nhd_pts.loc[nhd_pts.FType.isin([343])].copy()

# write original points for SARP
write_dataframe(nhd_pts, out_dir / "nhd_dam_pts_nhdpoint.gpkg")

nhd_pts["source"] = "NHDPoint"


# create circular buffers to merge with others
nhd_pts["geometry"] = pg.buffer(nhd_pts.geometry.values.data, 5)

nhd_lines = read_feathers(
    [raw_dir / huc2 / "nhd_lines.feather" for huc2 in huc2s],
    geo=True,
    new_fields={"HUC2": huc2s},
)
nhd_lines = nhd_lines.loc[
    (nhd_lines.FType.isin([343, 369, 398])) & nhd_lines.geometry.notnull()
].reset_index(drop=True)
# create buffers (5m) to merge with NHD areas
# from visual inspection, this helps coalesce those that are in pairs
nhd_lines["geometry"] = pg.buffer(nhd_lines.geometry.values.data, 5, quadsegs=1)
nhd_lines["source"] = "NHDLine"

# All NHD areas indicate a dam-related feature
nhd_areas = read_feathers(
    [raw_dir / huc2 / "nhd_poly.feather" for huc2 in huc2s],
    geo=True,
    new_fields={"HUC2": huc2s},
)
nhd_areas = nhd_areas.loc[nhd_areas.geometry.notnull()].reset_index(drop=True)
# buffer polygons slightly so we can dissolve touching ones together.
nhd_areas["geometry"] = pg.buffer(nhd_areas.geometry.values.data, 0.001)
nhd_areas["source"] = "NHDArea"

# Dissolve adjacent nhd lines and polygons together
nhd_dams = (
    nhd_pts.append(nhd_lines, ignore_index=True, sort=False)
    .append(nhd_areas, ignore_index=True, sort=False)
    .reset_index(drop=True)
)

# find contiguous groups for dissolve
nhd_dams = nhd_dams.join(find_contiguous_groups(nhd_dams.geometry.values.data))
# fill in the isolated dams
ix = nhd_dams.group.isnull()
next_group = nhd_dams.group.max() + 1
nhd_dams.loc[ix, "group"] = next_group + np.arange(ix.sum())
nhd_dams.group = nhd_dams.group.astype("uint")

print("Dissolving overlapping dams")
nhd_dams = dissolve(
    explode(nhd_dams),
    by=["HUC2", "source", "group"],
    agg={
        "GNIS_Name": lambda n: ", ".join({s for s in n if s}),
        # set missing NHD fields as 0
        "FType": lambda n: ", ".join({str(s) for s in n}),
        "FCode": lambda n: ", ".join({str(s) for s in n}),
        "NHDPlusID": lambda n: ", ".join({str(s) for s in n}),
    },
).reset_index(drop=True)

# fill in missing values
nhd_dams.GNIS_Name = nhd_dams.GNIS_Name.fillna("")

nhd_dams.geometry = pg.make_valid(nhd_dams.geometry.values.data)

nhd_dams["damID"] = nhd_dams.index.copy()
nhd_dams.damID = nhd_dams.damID.astype("uint32")

nhd_dams = nhd_dams.set_index("damID")

merged = None
for huc2 in huc2s:
    region_start = time()

    print(f"----- {huc2} ------")

    dams = nhd_dams.loc[nhd_dams.HUC2 == huc2, ["geometry"]].copy()

    print("Reading flowlines...")
    flowlines = gp.read_feather(
        clean_dir / huc2 / "flowlines.feather", columns=["lineID", "loop", "geometry"]
    ).set_index("lineID")
    joins = pd.read_feather(
        clean_dir / huc2 / "flowline_joins.feather",
        columns=["downstream_id", "upstream_id"],
    )

    drains = gp.read_feather(
        clean_dir / huc2 / "waterbody_drain_points.feather",
        columns=["wbID", "drainID", "lineID", "loop", "geometry"],
    ).set_index("drainID")

    ### Associate with waterbody drain points
    print("Joining to waterbody drain points...")
    join_start = time()

    # find the nearest waterbodies up to 50m away
    # more than that and we pick up downstream waterbodies
    near_drains = (
        nearest(
            pd.Series(dams.geometry.values.data, index=dams.index),
            pd.Series(drains.geometry.values.data, index=drains.index),
            NEAREST_DRAIN_TOLERANCE,
            keep_all=True,
        )
        .join(dams.drop(columns=["geometry"]))
        .join(drains, on="drainID")
        .drop(columns=["distance"])
    )

    ### Save these based on drain points
    # Note: we now have multiple records per dam because there may be multiple
    # nearest intersecting drains for these.
    # A large dam may also be associated with multiple waterbodies; these also
    # appear valid.

    merged = append(merged, near_drains.reset_index())

    print(
        f"Found {len(near_drains):,} dams associated with waterbodies in {time() - join_start:,.2f}s"
    )

    ### Intersect the remainder with flowlines to find the intersection points
    dams = dams.loc[~dams.index.isin(near_drains.index)].copy()

    print(f"Joining {len(dams):,} NHD dams to {len(flowlines):,} flowlines")
    join_start = time()
    dams = (
        pd.DataFrame(
            sjoin_geometry(
                pd.Series(dams.geometry.values.data, index=dams.index),
                pd.Series(flowlines.geometry.values.data, flowlines.index),
            ).rename("lineID")
        )
        .reset_index()
        .join(dams.geometry, on="damID")
        .join(flowlines.geometry.rename("flowline"), on="lineID")
    ).reset_index(drop=True)
    print(f"Found {len(dams)} joins in {time() - join_start:.2f}s")

    print("Extracting intersecting flowlines...")
    # Only keep the joins for lines that significantly cross (have a line / multiline and not a point)
    clipped = pg.intersection(dams.geometry.values.data, dams.flowline.values.data)
    t = pg.get_type_id(clipped)
    dams = dams.loc[(t == 1) | (t == 5)].copy()

    # find all joins for lines that start or end at these dams
    j = find_joins(
        joins,
        dams.lineID.unique(),
        downstream_col="downstream_id",
        upstream_col="upstream_id",
    )

    def find_upstreams(ids):
        if len(ids) == 1:
            return ids

        # multiple segments, find the dowstream ones
        dam_joins = find_joins(
            j, ids, downstream_col="downstream_id", upstream_col="upstream_id"
        )
        return dam_joins.loc[
            dam_joins.downstream_id.isin(ids) & ~dam_joins.upstream_id.isin(ids)
        ].downstream_id.unique()

    grouped = dams.groupby("damID")
    lines_by_dam = grouped.lineID.unique()

    # NOTE: downstreams is indexed on id, not dams.index
    downstreams = (
        lines_by_dam.apply(find_upstreams)
        .reset_index()
        .explode("lineID")
        .drop_duplicates()
        .set_index("damID")
        .lineID
    )

    # Now can just reduce dams back to these lineIDs
    dams = (
        dams[["damID", "geometry"]]
        .join(downstreams, on="damID", how="inner")
        .drop_duplicates(subset=["damID", "lineID"])
        .join(
            flowlines[["geometry", "loop"]].rename(columns={"geometry": "flowline"}),
            on="lineID",
        )
        .reset_index(drop=True)
    )
    print(f"Found {len(dams):,} joins between NHD dams and flowlines")

    # the first point is the furthest upstream; use this to represent the dam
    # if input is a multiline, take the first geometry
    # dams["geometry"] = pg.get_point(pg.get_geometry(dams.flowline.values.data, 0), 0)

    ### Extract representative point
    # Look at either end of overlapping line and use that as representative point.
    # Otherwise intersect and extract first coordinate of overlapping line
    last_pt = pg.get_point(dams.flowline.values.data, -1)
    ix = pg.intersects(dams.geometry.values.data, last_pt)
    dams.loc[ix, "pt"] = last_pt[ix]

    # override with upstream most point when both intersect
    first_pt = pg.get_point(dams.flowline.values.data, 0)
    ix = pg.intersects(dams.geometry.values.data, first_pt)
    dams.loc[ix, "pt"] = first_pt[ix]

    ix = dams.pt.isnull()
    # WARNING: this might fail for odd intersection geoms; we always take the first line
    # below
    pt = pd.Series(
        pg.get_point(
            pg.get_geometry(
                pg.intersection(
                    dams.loc[ix].geometry.values.data, dams.loc[ix].flowline.values.data
                ),
                0,
            ),
            0,
        ),
        index=dams.loc[ix].index,
    ).dropna()
    dams.loc[pt.index, "pt"] = pt

    # Few should be dropped at this point, since all should have overlapped at least by a point
    errors = dams.pt.isnull()
    if errors.max():
        print(
            f"{errors.sum():,} dam / flowline joins could not be represented as points and were dropped"
        )

    # WARNING: there may be multiple points per dam at this point, due to intersections with
    # multiple disjunct flowlines
    dams = (
        dams[["damID", "lineID", "pt", "loop",]]
        .dropna(subset=["pt"])
        .rename(columns={"pt": "geometry"})
        .set_index("damID")
    )

    # Concat to merged dams
    merged = append(merged, dams.reset_index())

    print("Region done in {:.2f}s".format(time() - region_start))


print("----------------------------------------------")

dams = merged.reset_index(drop=True).join(
    nhd_dams.drop(columns=["geometry"]), on="damID"
)

nhd_dams = nhd_dams.loc[nhd_dams.index.isin(dams.damID.unique())].reset_index()

print(
    f"Found {len(nhd_dams):,} NHD dams and {len(dams):,} NHD dam / flowline crossings"
)


dams = gp.GeoDataFrame(dams, geometry="geometry", crs=nhd_dams.crs)
dams.damID = dams.damID.astype("uint32")
dams.lineID = dams.lineID.astype("uint32")
dams.wbID = dams.wbID.fillna(-1).astype("int32")
dams.drainID = dams.drainID.fillna(-1).astype("int32")


print("Serializing...")
dams.to_feather(out_dir / "nhd_dams_pt.feather")
write_dataframe(dams, out_dir / "nhd_dams_pt.gpkg")


nhd_dams = nhd_dams.reset_index()
nhd_dams.to_feather(out_dir / "nhd_dams_poly.feather")
write_dataframe(nhd_dams, out_dir / "nhd_dams_poly.gpkg")


print("==============\nAll done in {:.2f}s".format(time() - start))
