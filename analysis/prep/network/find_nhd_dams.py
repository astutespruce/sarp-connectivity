from pathlib import Path
import os
from time import time
import warnings

import numpy as np
import pandas as pd
import shapely
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
from analysis.lib.graph.speedups.graph import DirectedGraph

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


# consider dam associated with waterbody drain if within 15m
MAX_DRAIN_DISTANCE = 15


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
write_dataframe(nhd_pts, out_dir / "nhd_dam_pts_nhdpoint.fgb")

nhd_pts["source"] = "NHDPoint"

# create tiny circular buffers around points to merge with others
# WARNING: using a larger buffer causes displacement of the dam point upstream,
# which is not desirable
nhd_pts["geometry"] = shapely.buffer(nhd_pts.geometry.values.data, 1e-6)

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
nhd_lines["geometry"] = shapely.buffer(nhd_lines.geometry.values.data, 5, quadsegs=1)
nhd_lines["source"] = "NHDLine"

# All NHD areas indicate a dam-related feature
nhd_areas = read_feathers(
    [raw_dir / huc2 / "nhd_poly.feather" for huc2 in huc2s],
    geo=True,
    new_fields={"HUC2": huc2s},
)
nhd_areas = nhd_areas.loc[nhd_areas.geometry.notnull()].reset_index(drop=True)
# buffer polygons slightly so we can dissolve touching ones together.
nhd_areas["geometry"] = shapely.buffer(nhd_areas.geometry.values.data, 0.001)
nhd_areas["source"] = "NHDArea"

# Dissolve adjacent nhd lines and polygons together
nhd_dams = pd.concat(
    [nhd_pts, nhd_lines, nhd_areas], ignore_index=True, sort=False
).reset_index(drop=True)

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

nhd_dams.geometry = shapely.make_valid(nhd_dams.geometry.values.data)

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
        clean_dir / huc2 / "flowlines.feather",
        columns=["lineID", "loop", "geometry", "sizeclass"],
    ).set_index("lineID")
    joins = pd.read_feather(
        clean_dir / huc2 / "flowline_joins.feather",
        columns=["downstream_id", "upstream_id"],
    )

    ### Find all intersection points with flowlines
    # we do this before looking for adjacent drain points, since there may be
    # multiple flowlines of different networks associated with a given dam

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
    print(f"Found {len(dams):,} joins in {time() - join_start:.2f}s")

    print("Extracting intersecting flowlines...")
    # Only keep the joins for lines that significantly cross (have a line / multiline and not a point)
    clipped = shapely.intersection(dams.geometry.values.data, dams.flowline.values.data)
    t = shapely.get_type_id(clipped)
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
        .lineID.astype("uint32")
    )

    # Now can just reduce dams back to these lineIDs
    dams = (
        dams[["damID", "geometry"]]
        .join(downstreams, on="damID", how="inner")
        .drop_duplicates(subset=["damID", "lineID"])
        .join(
            flowlines.geometry.rename("flowline"),
            on="lineID",
        )
        .reset_index(drop=True)
    )
    print(f"Found {len(dams):,} joins between NHD dams and flowlines")

    ### Extract representative point
    # Look at either end of overlapping line and use that as representative point.
    # Otherwise intersect and extract first coordinate of overlapping line
    last_pt = shapely.get_point(dams.flowline.values.data, -1)
    ix = shapely.intersects(dams.geometry.values.data, last_pt)
    dams.loc[ix, "pt"] = last_pt[ix]

    # override with upstream most point when both intersect
    first_pt = shapely.get_point(dams.flowline.values.data, 0)
    ix = shapely.intersects(dams.geometry.values.data, first_pt)
    dams.loc[ix, "pt"] = first_pt[ix]

    ix = dams.pt.isnull()
    # WARNING: this might fail for odd intersection geoms; we always take the first line
    # below
    pt = pd.Series(
        shapely.get_point(
            shapely.get_geometry(
                shapely.intersection(
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
        dams[
            [
                "damID",
                "lineID",
                "geometry",
                "pt",
            ]
        ].dropna(subset=["pt"])
        # .rename(columns={"pt": "geometry"})
    )
    dams.index.name = "damPtID"

    ### Associate with waterbody drain points
    print("Joining to waterbody drain points...")
    join_start = time()

    drains = gp.read_feather(
        clean_dir / huc2 / "waterbody_drain_points.feather",
        columns=["wbID", "drainID", "lineID", "km2", "geometry"],
    ).set_index("drainID")

    # find any waterbody drain points within MAX_DRAIN_DISTANCE of dam polygons

    # Find the nearest dam polygon for each drain, within MAX_DRAIN_DISTANCE
    # We do it this way because the dam may intersect or affect multiple drain points
    # so we can't always take the first or nearest from the dam's perspective
    tmp_dams = dams.groupby("damID").geometry.first()
    tree = shapely.STRtree(tmp_dams.values.data)
    drain_ix, dam_ix = tree.query_nearest(
        drains.geometry.values.data, max_distance=MAX_DRAIN_DISTANCE
    )
    near_drains = pd.DataFrame(
        {
            "drainID": drains.index.values.take(drain_ix),
        },
        index=pd.Series(tmp_dams.index.values.take(dam_ix), name="damID"),
    ).join(drains, on="drainID")

    # If the drain is immediately upstream or downstream on the same subnetwork
    # up to 4 nodes away, use the drain point instead
    tmp_joins = joins.loc[joins.upstream_id != 0]
    g = DirectedGraph(
        tmp_joins.downstream_id.values.astype("int64"),
        tmp_joins.upstream_id.values.astype("int64"),
    )

    # find all combinations of dam crossing points and drain points
    tmp = (
        dams[["damID", "lineID", "pt"]]
        .reset_index()
        .join(
            near_drains[["drainID", "wbID", "lineID", "km2", "geometry"]].rename(
                columns={"lineID": "drainLineID"}
            ),
            on="damID",
            how="inner",
        )
    )
    tmp["lineID"] = tmp.lineID.astype("int64")
    tmp["drainLineID"] = tmp.drainLineID.astype("int64")
    # some drains are at exact same point as extracted flowline crossing point
    tmp["same_subnet"] = tmp.lineID == tmp.drainLineID
    ix = ~tmp.same_subnet
    tmp.loc[ix, "same_subnet"] = g.is_reachable(
        tmp.loc[ix].lineID.values, tmp.loc[ix].drainLineID.values, 4
    )
    # try from other direction
    ix = ~tmp.same_subnet
    tmp.loc[ix, "same_subnet"] = g.is_reachable(
        tmp.loc[ix].drainLineID.values, tmp.loc[ix].lineID.values, 4
    )

    tmp = tmp.loc[tmp.same_subnet].copy()
    # take the closest drain to the crossing point if there are multiple on the
    # same flowline
    tmp["dist"] = shapely.distance(tmp.geometry.values.data, tmp.pt.values.data)
    use_drains = (
        tmp.sort_values(by=["damPtID", "dist"], ascending=True)
        .drop(columns=["same_subnet", "dist", "pt", "lineID"])
        .groupby("damPtID")
        .first()
    )

    dams = dams.join(
        use_drains[["drainID", "wbID", "drainLineID", "km2", "geometry"]].rename(
            columns={"geometry": "drain"}
        )
    )
    ix = dams.drainID.notnull()
    print(
        f"Found {ix.sum():,} dams associated with waterbodies in {time() - join_start:,.2f}s"
    )
    dams["geometry"] = dams.pt.values
    dams.loc[ix, "geometry"] = dams.loc[ix].drain.values.data
    dams.loc[ix, "lineID"] = dams.loc[ix].drainLineID.astype("uint32")

    dams = dams.drop(columns=["drain", "drainLineID", "pt"]).join(
        flowlines[["loop", "sizeclass"]], on="lineID"
    )

    # drop duplicates
    dams = dams.reset_index().drop_duplicates(
        subset=["damPtID", "damID", "lineID", "geometry"]
    )

    merged = append(merged, dams)

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
dams.loop = dams.loop.astype("bool")

print("Serializing...")
dams.to_feather(out_dir / "nhd_dams_pt.feather")
write_dataframe(dams, out_dir / "nhd_dams_pt.fgb")


nhd_dams = nhd_dams.reset_index()
nhd_dams.to_feather(out_dir / "nhd_dams_poly.feather")
write_dataframe(nhd_dams, out_dir / "nhd_dams_poly.fgb")


print("==============\nAll done in {:.2f}s".format(time() - start))
