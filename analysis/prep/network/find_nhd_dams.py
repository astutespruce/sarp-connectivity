from pathlib import Path
from time import time
import warnings

import pandas as pd
import pygeos as pg
import geopandas as gp
from pyogrio import write_dataframe

from analysis.constants import CRS
from analysis.lib.joins import find_joins
from analysis.lib.geometry import sjoin_geometry, nearest
from analysis.lib.util import append
from analysis.lib.geometry import aggregate_contiguous

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
src_dir = Path("data/nhd/clean")
out_dir = Path("data/nhd/merged")


huc2s = sorted(
    pd.read_feather(
        data_dir / "boundaries/huc4.feather", columns=["HUC2"]
    ).HUC2.unique()
)


start = time()

### Merge NHD lines and areas that represent dams and dam-related features
print("Reading NHD lines and areas, and merging...")
nhd_lines = gp.read_feather(out_dir / "nhd_lines.feather")
nhd_lines = nhd_lines.loc[
    (nhd_lines.FType.isin([343, 369, 398])) & nhd_lines.geometry.notnull()
].reset_index(drop=True)
# create buffers (5m) to merge with NHD areas
# from visual inspection, this helps coalesce those that are in pairs
nhd_lines["geometry"] = pg.buffer(nhd_lines.geometry.values.data, 5, quadsegs=1)

# All NHD areas indicate a dam-related feature
nhd_areas = gp.read_feather(out_dir / "nhd_poly.feather")
nhd_areas = nhd_areas.loc[nhd_areas.geometry.notnull()].reset_index(drop=True)
# buffer polygons slightly so we can dissolve touching ones together.
nhd_areas["geometry"] = pg.buffer(nhd_areas.geometry.values.data, 0.001)

# Dissolve adjacent nhd lines and polygons together
nhd_dams = nhd_lines.append(nhd_areas, ignore_index=True, sort=False)
nhd_dams = aggregate_contiguous(
    nhd_dams,
    agg={
        "GNIS_Name": lambda n: ", ".join({s for s in n if s}),
        # set missing NHD fields as 0
        "FType": lambda x: 0,
        "FCode": lambda x: 0,
        "NHDPlusID": lambda x: 0,
        "HUC4": "first",
    },
).reset_index(drop=True)

# fill in missing values
nhd_dams.GNIS_Name = nhd_dams.GNIS_Name.fillna("")

nhd_dams.geometry = pg.make_valid(nhd_dams.geometry.values.data)

nhd_dams["damID"] = nhd_dams.index.copy()
nhd_dams.damID = nhd_dams.damID.astype("uint32")
nhd_dams = nhd_dams.set_index("damID")

### Intersect with flowlines by huc2

merged = None
for huc2 in huc2s:
    region_start = time()

    print(f"----- {huc2} ------")

    dams = nhd_dams.loc[nhd_dams.HUC4.str[:2] == huc2].copy()

    print("Reading flowlines...")
    flowlines = gp.read_feather(
        src_dir / huc2 / "flowlines.feather", columns=["lineID", "geometry"]
    ).set_index("lineID")
    joins = pd.read_feather(
        src_dir / huc2 / "flowline_joins.feather",
        columns=["downstream_id", "upstream_id"],
    )

    waterbodies = gp.read_feather(
        src_dir / huc2 / "waterbodies.feather", columns=["wbID", "geometry"]
    ).set_index("wbID")

    drains = gp.read_feather(
        src_dir / huc2 / "waterbody_drain_points.feather", columns=["wbID", "geometry"],
    )

    ### Associate with waterbodies, so that we know which waterbodies are claimed
    # Note: because dams are buffered slightly, they should always intersect with
    # their neighboring waterbody (if there is one)
    print("Joining to waterbodies...")

    join_start = time()

    # find the nearest waterbodies up to 50m away
    # more than that and we pick up downstream waterbodies
    nearest_wb = nearest(
        pd.Series(dams.geometry.values.data, index=dams.index),
        pd.Series(waterbodies.geometry.values.data, index=waterbodies.index),
        50,
        keep_all=True,
    )

    # keep those that only have one waterbody
    s = nearest_wb.groupby(level=0).size()
    keep = nearest_wb.loc[nearest_wb.index.isin(s[s == 1].index)].copy()

    # distill the others down based on drain point contained by the dam
    tmp = (
        nearest_wb.loc[nearest_wb.index.isin(s[s > 1].index)]
        .join(dams.geometry)
        .join(drains.set_index("wbID").geometry.rename("drain"), on="wbID")
    )
    contains = pg.contains(tmp.geometry.values.data, tmp.drain.values.data)
    tmp = (
        tmp.loc[contains]
        .reset_index()
        .groupby(["damID", "wbID"])
        .first()
        .reset_index()
        .set_index("damID")
    )

    s = tmp.groupby(level=0).size()
    errors = (s > 1).sum()
    if errors:
        print(
            f"WARNING: {errors} dams contain drain points from multiple waterbodies; keeping only the first"
        )

        tmp = tmp.groupby(level=0).first()

    dam_wb = (
        keep[["wbID"]]
        .reset_index()
        .append(tmp[["wbID"]].reset_index(), ignore_index=True)
        .set_index("damID")
    )

    print(
        f"Found {len(dam_wb):,} dams associated with waterbodies and {len(dams) - len(dam_wb):,} not associated with waterbodies in {time() - join_start:,.2f}s"
    )

    print("Joining {:,} NHD dams to {:,} flowlines".format(len(dams), len(flowlines)))
    join_start = time()
    dams = (
        pd.DataFrame(
            sjoin_geometry(
                pd.Series(dams.geometry.values.data, index=dams.index),
                pd.Series(flowlines.geometry.values.data, flowlines.index),
            ).rename("lineID")
        )
        .reset_index()
        .join(dams[["GNIS_Name", "geometry"]], on="damID")
        .join(flowlines.geometry.rename("flowline"), on="lineID")
    ).reset_index(drop=True)
    print("Join elapsed {:.2f}s".format(time() - join_start))

    print("Extracting intersecting flowlines...")
    # Only keep the joins for lines that significantly cross (have a line / multiline and not a point)
    dams["clipped"] = pg.intersection(
        dams.geometry.values.data, dams.flowline.values.data
    )
    t = pg.get_type_id(dams.clipped)
    dams = dams.loc[(t == 1) | (t == 5)].copy()

    print("Deduplicating joins and taking furthest upstream point...")

    # aggregate to their upstream-most segments
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
        dams[["damID", "GNIS_Name", "geometry"]]
        .join(downstreams, on="damID", how="inner")
        .drop_duplicates(subset=["damID", "lineID"])
        .join(flowlines.geometry.rename("flowline"), on="lineID")
        .reset_index(drop=True)
    )
    print(f"Found {len(dams):,} joins between NHD dams and flowlines")

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
    # WARNING: this might fail for odd intersection geoms
    pt = pd.Series(
        pg.get_point(
            pg.intersection(
                dams.loc[ix].geometry.values.data, dams.loc[ix].flowline.values.data
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
        dams[["damID", "lineID", "pt"]]
        .dropna(subset=["pt"])
        .rename(columns={"pt": "geometry"})
        .set_index("damID")
    )

    dams = dams.join(dam_wb)
    dams.wbID = dams.wbID.fillna(-1)

    print("Region done in {:.2f}s".format(time() - region_start))

    # Concat to merged dams
    merged = append(merged, dams.reset_index())

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
dams.wbID = dams.wbID.astype("int32")

print("Serializing...")
dams.to_feather(out_dir / "nhd_dams_pt.feather")
write_dataframe(dams, out_dir / "nhd_dams_pt.gpkg")


nhd_dams.to_feather(out_dir / "nhd_dams_poly.feather")
write_dataframe(nhd_dams, out_dir / "nhd_dams_poly.gpkg")


print("==============\nAll done in {:.2f}s".format(time() - start))
