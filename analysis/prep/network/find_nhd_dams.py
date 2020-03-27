from pathlib import Path
from time import time

import numpy as np
import pandas as pd
import pygeos as pg
import networkx as nx
from geofeather.pygeos import to_geofeather, from_geofeather
from pgpkg import to_gpkg
import geopandas as gp

from nhdnet.io import deserialize_df
from nhdnet.nhd.joins import find_joins

from analysis.pygeos_compat import sjoin_geometry as sjoin, dissolve, to_gdf

from analysis.constants import REGION_GROUPS, CRS
from analysis.util import append
from analysis.prep.barriers.lib.points import nearest, neighborhoods

nhd_dir = Path("data/nhd")
src_dir = nhd_dir / "clean"
out_dir = nhd_dir / "merged"
extra_dir = nhd_dir / "extra"


start = time()

### Merge NHD lines and areas that represent dams and dam-related features
print("Reading NHD lines and areas, and merging...")
nhd_lines = from_geofeather(extra_dir / "nhd_lines.feather")
nhd_lines = nhd_lines.loc[
    (nhd_lines.FType.isin([343, 369, 398])) & nhd_lines.geometry.notnull()
].copy()
# create buffers (10m) to merge with NHD areas
# from visual inspection, this helps coalesce those that are in pairs
nhd_lines["geometry"] = pg.buffer(nhd_lines.geometry, 10, quadsegs=1)

# All NHD areas indicate a dam-related feature
nhd_areas = from_geofeather(extra_dir / "nhd_areas.feather")
nhd_areas = nhd_areas.loc[nhd_areas.geometry.notnull()].copy()
# buffer polygons slightly so we can dissolve touching ones together.
nhd_areas["geometry"] = pg.buffer(nhd_areas.geometry, 5)

# Dissolve adjacent nhd lines and waterbodies together
nhd_dams = nhd_lines.append(nhd_areas, ignore_index=True, sort=False)
nearby = sjoin(nhd_dams.geometry, nhd_dams.geometry, how="inner")
network = nx.from_pandas_edgelist(nearby.reset_index(), "index", "index_right")
components = pd.Series(nx.connected_components(network)).apply(list)
groups = (
    pd.DataFrame(components.explode().rename("index_right"))
    .reset_index()
    .rename(columns={"index": "group", "index_right": "index"})
    .set_index("index")
)

nhd_dams = nhd_dams.join(groups)
# Extract composite names for the group
name = (
    nhd_dams.groupby("group")
    .GNIS_Name.unique()
    .apply(lambda n: ", ".join([s for s in n if s]))
)

nhd_dams = (
    dissolve(nhd_dams[["HUC2", "group", "geometry"]], by="group")
    .join(name)
    .reset_index(drop=True)
    .rename(columns={"group": "id"})
    .set_index("id")
)
nhd_dams.GNIS_Name = nhd_dams.GNIS_Name.fillna("")

# cleanup invalid geometries
ix = ~pg.is_valid(nhd_dams.geometry)
nhd_dams.loc[ix, "geometry"] = pg.buffer(nhd_dams.loc[ix].geometry, 0.1, quadsegs=1)


### Intersect with flowlines by region
merged = None
for region, HUC2s in list(REGION_GROUPS.items()):
    region_start = time()

    print("\n----- {} ------\n".format(region))

    print("Reading flowlines...")
    flowlines = from_geofeather(src_dir / region / "flowlines.feather").set_index(
        "lineID"
    )
    joins = deserialize_df(
        src_dir / region / "flowline_joins.feather",
        columns=["downstream_id", "upstream_id"],
    )

    dams = nhd_dams.loc[nhd_dams.HUC2.isin(HUC2s)].copy()

    print("Joining {:,} NHD dams to {:,} flowlines".format(len(dams), len(flowlines)))
    join_start = time()
    dams = (
        pd.DataFrame(sjoin(dams.geometry, flowlines.geometry).rename("lineID"))
        .join(dams[["GNIS_Name", "geometry"]])
        .join(flowlines.geometry.rename("line"), on="lineID")
    ).reset_index()
    print("Join elapsed {:.2f}s".format(time() - join_start))

    print("Extracting intersecting flowlines...")
    # Only keep the joins for lines that signficantly cross
    intersection = pg.intersection(dams.geometry, dams.line)
    ix = pg.get_type_id(intersection).isin([1, 5])
    dams = dams.loc[ix].copy()

    print("Deduplicating joins...")
    # Some joins will have multiple flowlines
    # aggregate these to their lowest common flowline
    j = find_joins(
        joins,
        dams.lineID.unique(),
        downstream_col="downstream_id",
        upstream_col="upstream_id",
    )

    def find_downstreams(ids):
        if len(ids) == 1:
            return ids

        # multiple segments, find the dowstream ones
        dam_joins = find_joins(
            j, ids, downstream_col="downstream_id", upstream_col="upstream_id"
        )
        return dam_joins.loc[
            dam_joins.upstream_id.isin(ids) & ~dam_joins.downstream_id.isin(ids)
        ].upstream_id.unique()

    grouped = dams.groupby("id")
    lines_by_dam = grouped.lineID.unique()

    # NOTE: downstreams is indexed on id, not dams.index
    downstreams = (
        lines_by_dam.apply(find_downstreams)
        .reset_index()
        .explode("lineID")
        .drop_duplicates()
        .set_index("id")
        .lineID
    )

    # Now can just reduce dams back to these lineIDs
    dams = (
        dams[["id", "GNIS_Name", "geometry"]]
        .join(downstreams, on="id", how="inner")
        .drop_duplicates(subset=["id", "lineID"])
        .join(flowlines.geometry.rename("line"), on="lineID")
        .reset_index(drop=True)
    )
    print("Found {:,} joins between NHD dams and flowlines".format(len(dams)))

    ### Extract representative point
    # Look at either end of overlapping line and use that as representative point.
    # Otherwise intersect and extract first coordinate of overlapping line
    first = pg.get_point(dams.line, 0)
    intersects_first = pg.intersects(dams.geometry, first)
    ix = intersects_first
    dams.loc[ix, "pt"] = first.loc[ix]

    ix = ~intersects_first
    last = pg.get_point(dams.loc[ix].line, -1)
    intersects_last = pg.intersects(dams.loc[ix].geometry, last)
    last = last.loc[intersects_last]
    dams.loc[last.index, "pt"] = last

    ix = dams.pt.isnull()
    # WARNING: this might fail for odd intersection geoms
    pt = pg.get_point(
        pg.intersection(dams.loc[ix].geometry, dams.loc[ix].line), 0
    ).dropna()
    dams.loc[pt.index, "pt"] = pt

    # Few should be dropped at this point, since all should have overlapped at least by a point
    errors = dams.pt.isnull()
    if errors.max():
        print(
            "{:,} dam / flowline joins could not be represented as points and were dropped".format(
                errors.sum()
            )
        )

    dams = dams.dropna(subset=["pt"])

    dams = dams[["id", "lineID", "pt"]].rename(columns={"pt": "geometry"})
    dams.id = dams.id.astype("uint32")
    dams.lineID = dams.lineID.astype("uint32")

    # Concat to merged dams
    merged = append(merged, dams)

    print("Region done in {:.2f}s".format(time() - region_start))


print("----------------------------------------------")

dams = merged.reset_index(drop=True)
print("Found {:,} NHD dam / flowline crossings".format(len(dams)))

### Associate with waterbodies, so that we know which waterbodies are claimed
print("Joining to waterbodies...")
wb = from_geofeather(nhd_dir / "merged" / "waterbodies.feather").set_index("wbID")
drains = from_geofeather(
    nhd_dir / "merged" / "waterbody_drain_points.feather"
).set_index("id")

join_start = time()
# join from waterbodies to dams, due to the large difference in footprints
# then invert
joined = (
    sjoin(wb.geometry, dams.geometry, how="left")
    .rename("id")
    .reset_index()
    .drop_duplicates()
    .dropna(subset=["id"])
    .astype("uint32")
    .set_index("id")
)

dams = dams.join(joined, how="left")
print(
    "Found {:,} dams in waterbodies in {:.2f}s".format(len(joined), time() - join_start)
)

print("Finding nearest waterbody drain for those that didn't join to waterbodies")

# some might be immediately downstream, find the closest drain within 250m
nearest_start = time()
ix = dams.wbID.isnull()
nearest_drains = nearest(dams.loc[ix].geometry, drains.set_index("wbID").geometry, 250)

dams.loc[nearest_drains.index, "wbID"] = nearest_drains
print(
    "Found {:,} nearest neighbors in {:.2f}s".format(
        len(nearest_drains), time() - nearest_start
    )
)

print("{:,} dams not associated with waterbodies".format(dams.wbID.isnull().sum()))

dams.wbID = dams.wbID.fillna(-1)

print("Serializing...")
# dams = to_gdf(dams, crs=CRS).reset_index(drop=True)
dams = dams.reset_index()
to_geofeather(dams, out_dir / "nhd_dams_pt.feather", crs=CRS)
to_gpkg(dams, out_dir / "nhd_dams_pt")

nhd_dams = nhd_dams.loc[nhd_dams.index.isin(dams.id.unique())].reset_index()
to_geofeather(nhd_dams, out_dir / "nhd_dams_poly.feather", crs=CRS)
to_gpkg(nhd_dams, out_dir / "nhd_dams_poly")

# TODO: exporting to shapefile segfaults, not sure why.  Issue likely with conversion to shapely geoms

print("==============\nAll done in {:.2f}s".format(time() - start))


#### Old code - tries to use network topology to reduce set of lines per dam:
# counts = downstreams.apply(len)
# ix = dams.loc[dams.id.isin(counts.loc[counts == 1].index)].index
# dams.loc[ix, "newLineID"] = dams.loc[ix].id.apply(lambda id: downstreams.loc[id][0])
# dams.loc[dams.id.isin(ids)].id.apply(lambda id: downstreams.loc[id][0])
# ix = lines_by_dam.loc[counts == 1]
# where len of downstreams is null, can set that as the lineID of the dam
# if > 1, need to build subnetworks

# # Following logic doesn't work for lineIDs shared between dams
# lineIDs = dams.loc[dams.id.isin(counts.loc[counts > 1].index)].lineID

# # extract overlapping nodes and build subnetworks
# # NOTE: this must be for edges that are in lineIDs
# j = joins.loc[joins.upstream_id.isin(lineIDs) & joins.downstream_id.isin(lineIDs)]

# # downstream-most segments are those that terminate in a segment not in our set here
# downstreams = find_downstream_terminals(
#     j, downstream_col="downstream_id", upstream_col="upstream_id"
# )
# nodes = j.loc[
#     (j.upstream_id != 0) & (j.downstream_id != 0), ["downstream_id", "upstream_id"]
# ]
# use undirected graph for finding neighbors
# network = nx.from_pandas_edgelist(nodes, "upstream_id", "downstream_id")
# components = pd.Series(nx.connected_components(network)).apply(list)

# # WARNING: this might blow up if there are true terminals (downstream == 0)
# downstream_for_group = components.apply(lambda c: np.intersect1d(c, downstreams)[0])
# nets = (
#     pd.DataFrame(components.explode().rename("lineID"))
#     .reset_index()
#     .rename(columns={"index": "netID"})
#     .set_index("lineID")
# )

# # netID == nan are single segment joins, not a problem
# dams = dams.join(nets, on="lineID", how="left").join(
#     downstream_for_group.rename("newLineID"), on="netID", how="left"
# )
# ix = dams.netID.notnull()
# dams.loc[ix, "lineID"] = dams.loc[ix].newLineID.astype("uint32")
# dams = (
#     dams.drop(columns=["netID", "newLineID"])
#     .drop_duplicates(subset=["id", "lineID"])
#     .drop(columns=["line"])
# )

# # join back to flowlines to get updated line
# dams = dams.join(flowlines.geometry.rename("line"), on="lineID")
