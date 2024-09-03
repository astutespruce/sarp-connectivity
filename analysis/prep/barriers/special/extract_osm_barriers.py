from pathlib import Path
import shutil
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
from pyogrio import (
    read_dataframe,
    write_dataframe,
    set_gdal_config_options,
)
import shapely

from analysis.constants import CRS
from analysis.lib.joins import find_joins
from analysis.lib.util import append

warnings.filterwarnings("ignore", message=".*invalid value encountered.*")

TOLERANCE = 250

# date downloaded from OSM distributor
OSM_DATE = "08/29/2024"


def get_height(value):
    if not value:
        return np.nan

    # default units are in meters
    value = value.replace(" ", "").replace("m", "").replace("\\", "")

    # convert feet to meters
    if "'" in value:
        meters = float(value.split("'")[0]) * 0.3048

    elif "ft" in value:
        meters = float(value.replace("ft", "")) * 0.3048

    else:
        meters = float(value)

    return meters


bnd_dir = Path("data/boundaries")
nhd_dir = Path("data/nhd/clean")
src_dir = Path("data/barriers/source")
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True)

infilename = src_dir / "northamerica_osm.gpkg"
outfilename = out_dir / "osm_barriers.gdb"
if outfilename.exists():
    shutil.rmtree(outfilename)


str_cols = ["Name", "OSMSource", "waterway", "natural", "other_tags"]


set_gdal_config_options(
    {
        "OSM_CONFIG_FILE": Path("analysis/prep/barriers/special/osmconf.ini").absolute(),
        "OGR_INTERLEAVED_READING": True,
    }
)

huc4 = gp.read_feather(bnd_dir / "huc4.feather", columns=["HUC4", "HUC2", "geometry"])

################################################################################
### Read data
################################################################################

points = (
    read_dataframe(infilename, layer="points", use_arrow=True)
    .rename(columns={"osm_id": "SourceDBID", "name": "Name", "source": "OSMSource"})
    .to_crs(CRS)
)
points = points.loc[
    ~(
        points.OSMSource.str.lower().str.contains("nhd")
        | points.OSMSource.str.lower().str.contains("usgs")
        | points.OSMSource.str.lower().str.contains("gnis")
        | points.OSMSource.str.lower().str.contains("nrcan")
        | points.OSMSource.str.lower().str.contains("3dep")
        | points.other_tags.str.lower().str.contains("gnis:")
    )
].reset_index(drop=True)
points["Link"] = "https://www.openstreetmap.org/node/" + points.SourceDBID


lines = (
    read_dataframe(infilename, layer="lines", use_arrow=True)
    .rename(columns={"osm_id": "SourceDBID", "name": "Name", "source": "OSMSource"})
    .to_crs(CRS)
)
lines = lines.loc[
    ~(
        lines.OSMSource.str.lower().str.contains("nhd")
        | lines.OSMSource.str.lower().str.contains("usgs")
        | lines.OSMSource.str.lower().str.contains("gnis")
        | lines.OSMSource.str.lower().str.contains("nrcan")
        | lines.OSMSource.str.lower().str.contains("3dep")
        | lines.other_tags.str.lower().str.contains("gnis:")
    )
].reset_index(drop=True)
lines["Link"] = "https://www.openstreetmap.org/way/" + lines.SourceDBID
lines = lines.drop(columns=["z_order"])


poly = (
    read_dataframe(infilename, layer="multipolygons", use_arrow=True)
    .rename(columns={"osm_id": "SourceDBID", "name": "Name", "source": "OSMSource"})
    .to_crs(CRS)
)
poly = poly.loc[
    ~(
        poly.OSMSource.str.lower().str.contains("nhd")
        | poly.OSMSource.str.lower().str.contains("usgs")
        | poly.OSMSource.str.lower().str.contains("gnis")
        | poly.OSMSource.str.lower().str.contains("nrcan")
        | poly.OSMSource.str.lower().str.contains("3dep")
        | poly.other_tags.str.lower().str.contains("gnis:")
    )
].reset_index(drop=True)

poly["Link"] = "https://www.openstreetmap.org/relation/" + poly.SourceDBID
ix = poly.SourceDBID.isnull()
poly.loc[ix, "SourceDBID"] = poly.loc[ix].osm_way_id
poly.loc[ix, "Link"] = "https://www.openstreetmap.org/way/" + poly.loc[ix].SourceDBID
poly = poly.drop(columns=["osm_way_id"])


for df in [points, lines, poly]:
    for col in str_cols:
        df[col] = df[col].fillna("")

    df["Source"] = "OpenStreetMap (https://opendatacommons.org/licenses/odbl/)"
    df["OSMDate"] = OSM_DATE
    df["tags"] = df.other_tags.apply(
        lambda x: dict([tag.split("=>") for tag in x.replace('"', "").split(",") if "=>" in tag]) if x else {}
    )


################################################################################
### Extract waterfalls
################################################################################
waterfalls = points.loc[(points.waterway == "waterfall")]

# drop any that we likely already have
wf = gp.read_feather("data/barriers/source/waterfalls.feather", columns=["geometry"]).to_crs(CRS)

tree = shapely.STRtree(waterfalls.geometry.values)
ix = np.unique(tree.query(wf.geometry.values, predicate="dwithin", distance=TOLERANCE)[1])
print(f"Found {len(ix):,} OSM waterfalls within {TOLERANCE}m of existing waterfalls")

waterfalls = waterfalls.loc[~waterfalls.index.isin(waterfalls.index.values.take(ix))]
print(f"Found {len(waterfalls):,} OSM waterfalls we don't likely already have")

# extract height
waterfalls["height_meters"] = waterfalls.tags.apply(lambda x: get_height(x.get("height", "")))

write_dataframe(
    waterfalls.drop(columns=["tags", "other_tags", "natural", "waterway"]),
    outfilename,
    layer="waterfalls",
    driver="OpenFileGDB",
)


################################################################################
### Extract fish_pass points and lines
### (used manually by SARP to set fish passage presence for dam)
################################################################################
write_dataframe(
    points.loc[points.waterway == "fish_pass"].drop(columns=["other_tags", "natural", "waterway"]),
    outfilename,
    layer="fish_pass_pts",
    driver="OpenFileGDB",
)

write_dataframe(
    lines.loc[lines.waterway == "fish_pass"].drop(columns=["other_tags", "natural", "waterway"]),
    out_dir / "osm_barriers.gdb",
    layer="fish_pass_line",
    driver="OpenFileGDB",
)


################################################################################
### Extract dams / weirs
################################################################################
dams_master = gp.read_feather("data/barriers/master/dams.feather", columns=["geometry"])

dam_pts = points.loc[points.waterway.isin(["dam", "weir"])].reset_index(drop=True)
dam_lines = lines.loc[lines.waterway.isin(["dam", "weir"])].reset_index(drop=True)
dam_poly = poly.loc[poly.waterway.isin(["dam", "weir"])].reset_index(drop=True)

for df in [dam_pts, dam_lines, dam_poly]:
    df["height_meters"] = df.tags.apply(lambda x: get_height(x.get("height", "")))
    df["material"] = df.tags.apply(lambda x: x.get("material", ""))
    df["operator"] = df.tags.apply(lambda x: x.get("operator"))

## Extract dam points
# drop any we likely already have
tree = shapely.STRtree(dam_pts.geometry.values)
ix = np.unique(tree.query(dams_master.geometry.values, predicate="dwithin", distance=TOLERANCE)[1])
dam_pts = dam_pts.loc[~dam_pts.index.isin(dam_pts.index.values.take(ix))]
print(f"Found {len(ix):,} OSM dam points within {TOLERANCE}m of existing dams")
print(f"Found {len(dam_pts):,} OSM dam points we don't likely already have")


write_dataframe(
    dam_pts.drop(columns=["tags", "other_tags", "natural", "waterway"]),
    outfilename,
    layer="dam_pts",
    driver="OpenFileGDB",
)


### Extract dam lines
# drop any that are close to existing dams or OSM points above
tree = shapely.STRtree(dam_lines.geometry.values)
ix = np.unique(
    np.concatenate(
        [
            tree.query(dams_master.geometry.values, predicate="dwithin", distance=TOLERANCE)[1],
            tree.query(dam_pts.geometry.values, predicate="dwithin", distance=TOLERANCE)[1],
        ]
    )
)
dam_lines = dam_lines.loc[~dam_lines.index.isin(dam_lines.index.values.take(ix))]
print(f"Found {len(ix):,} OSM dam lines within {TOLERANCE}m of OSM dam points or existing dams")

# attribute to HUC2
tree = shapely.STRtree(dam_lines.geometry.values)
left, right = tree.query(huc4.geometry.values, predicate="intersects")
pairs = (
    pd.Series(
        huc4.HUC2.values.take(left),
        name="HUC2",
        index=dam_lines.index.values.take(right),
    )
    .groupby(level=0)
    .first()
)
dam_lines = dam_lines.join(pairs, how="inner")
print(f"Kept {len(dam_lines):,} OSM dam lines we don't likely already have within HUC4 analysis regions")


### Extract dam lines
# drop any that are close to existing dams or OSM points or lines above
tree = shapely.STRtree(dam_poly.geometry.values)
ix = np.unique(
    np.concatenate(
        [
            tree.query(dams_master.geometry.values, predicate="dwithin", distance=TOLERANCE)[1],
            tree.query(dam_pts.geometry.values, predicate="dwithin", distance=TOLERANCE)[1],
            tree.query(dam_lines.geometry.values, predicate="dwithin", distance=TOLERANCE)[1],
        ]
    )
)
dam_poly = dam_poly.loc[~dam_poly.index.isin(dam_poly.index.values.take(ix))]
print(f"Found {len(ix):,} OSM dam polygons within {TOLERANCE}m of OSM dam points / lines or existing dams")

# attribute to HUC2
tree = shapely.STRtree(dam_poly.geometry.values)
left, right = tree.query(huc4.geometry.values, predicate="intersects")
pairs = (
    pd.Series(
        huc4.HUC2.values.take(left),
        name="HUC2",
        index=dam_poly.index.values.take(right),
    )
    .groupby(level=0)
    .first()
)
dam_poly = dam_poly.join(pairs, how="inner")
print(f"Kept {len(dam_poly):,} OSM dam polygons we don't likely already have within HUC4 analysis regions")

merged = None
for huc2 in sorted(huc4.HUC2.unique()):
    print(f"----------------\nProcessing {huc2}\n-------------------")
    huc2_lines = dam_lines.loc[dam_lines.HUC2 == huc2]
    huc2_poly = dam_poly.loc[dam_poly.HUC2 == huc2]

    if not (len(huc2_lines) + len(huc2_poly)):
        continue

    flowlines = gp.read_feather(
        nhd_dir / huc2 / "flowlines.feather",
        columns=["geometry", "NHDPlusID", "lineID", "loop", "offnetwork"],
    ).set_index("lineID")
    tree = shapely.STRtree(flowlines.geometry.values)

    joins = pd.read_feather(
        nhd_dir / huc2 / "flowline_joins.feather",
        columns=["downstream_id", "upstream_id"],
    )

    if len(huc2_lines):
        left, right = tree.query(huc2_lines.geometry.values, predicate="intersects")
        df = gp.GeoDataFrame(
            {
                "NHDPlusID": flowlines.NHDPlusID.values.take(right),
                "geometry": shapely.intersection(
                    flowlines.geometry.values.take(right),
                    huc2_lines.geometry.values.take(left),
                ),
            },
            geometry="geometry",
            index=huc2_lines.index.values.take(left),
            crs=CRS,
        )

        # keep only the first point if there are multiple
        df["geometry"] = shapely.get_geometry(df.geometry.values, 0)

        df = df.join(
            huc2_lines.drop(
                columns=[
                    "geometry",
                    "HUC2",
                    "waterway",
                    "natural",
                    "tags",
                    "other_tags",
                ]
            )
        )
        df["notes"] = "derived from intersection of OSM dam / weir line and NHD HR flowline"

        merged = append(merged, df)

    if len(huc2_poly):
        left, right = tree.query(huc2_poly.geometry.values, predicate="intersects")
        df = gp.GeoDataFrame(
            {
                "lineID": flowlines.index.values.take(right),
                "flowline": flowlines.geometry.values.take(right),
                "geometry": huc2_poly.geometry.values.take(left),
                "SourceDBID": huc2_poly.SourceDBID.take(left),
            },
            geometry="geometry",
            index=huc2_poly.index.values.take(left),
            crs=CRS,
        )

        # Only keep the joins for lines that significantly cross (have a line / multiline and not a point)
        clipped = shapely.intersection(df.flowline.values, df.geometry.values)
        t = shapely.get_type_id(clipped)
        df = df.loc[(t == 1) | (t == 5)].copy()

        # find all joins for lines that start or end at these dams
        j = find_joins(
            joins,
            df.lineID.unique(),
            downstream_col="downstream_id",
            upstream_col="upstream_id",
        )

        def find_upstreams(ids):
            if len(ids) == 1:
                return ids

            # multiple segments, find the dowstream ones
            dam_joins = find_joins(j, ids, downstream_col="downstream_id", upstream_col="upstream_id")
            return dam_joins.loc[
                dam_joins.downstream_id.isin(ids) & ~dam_joins.upstream_id.isin(ids)
            ].downstream_id.unique()

        grouped = df.groupby("SourceDBID")
        lines_by_dam = grouped.lineID.unique()

        # NOTE: downstreams is indexed on id, not dams.index
        downstreams = (
            lines_by_dam.apply(find_upstreams)
            .reset_index()
            .explode("lineID")
            .drop_duplicates()
            .set_index("SourceDBID")
            .lineID.astype("uint32")
        )

        # Now can just reduce dams back to these lineIDs
        df = (
            df[["SourceDBID", "geometry"]]
            .join(downstreams, on="SourceDBID", how="inner")
            .drop_duplicates(subset=["SourceDBID", "lineID"])
            .join(
                flowlines.geometry.rename("flowline"),
                on="lineID",
            )
            .reset_index(drop=True)
        )
        print(f"Found {len(df):,} joins between OSM dam polygons and flowlines")

        ### Extract representative point
        # Look at either end of overlapping line and use that as representative point.
        # Otherwise intersect and extract first coordinate of overlapping line
        last_pt = shapely.get_point(df.flowline.values, -1)
        ix = shapely.intersects(df.geometry.values, last_pt)
        df.loc[ix, "pt"] = last_pt[ix]

        # override with upstream most point when both intersect
        first_pt = shapely.get_point(df.flowline.values, 0)
        ix = shapely.intersects(df.geometry.values, first_pt)
        df.loc[ix, "pt"] = first_pt[ix]

        ix = df.pt.isnull()
        tmp = shapely.get_geometry(
            shapely.intersection(df.loc[ix].geometry.values, df.loc[ix].flowline.values),
            0,
        )
        tmp_ix = shapely.get_type_id(tmp) == 1
        tmp[tmp_ix] = shapely.get_point(tmp[tmp_ix], 0)

        # WARNING: this might fail for odd intersection geoms; we always take the first line
        # below
        pt = pd.Series(
            tmp,
            index=df.loc[ix].index,
        ).dropna()
        df.loc[pt.index, "pt"] = pt

        # Few should be dropped at this point, since all should have overlapped at least by a point
        errors = df.pt.isnull()
        if errors.max():
            print(f"{errors.sum():,} dam / flowline joins could not be represented as points and were dropped")

        df = (
            df.loc[df.pt.notnull(), ["SourceDBID", "lineID", "pt"]]
            .rename(columns={"pt": "geometry"})
            .join(
                huc2_poly.set_index("SourceDBID").drop(
                    columns=[
                        "geometry",
                        "HUC2",
                        "waterway",
                        "water",
                        "natural",
                        "tags",
                        "other_tags",
                    ]
                ),
                on="SourceDBID",
            )
            .join(flowlines[["NHDPlusID", "loop", "offnetwork"]], on="lineID")
            .drop(columns=["lineID"])
        )

        df["notes"] = "derived from intersection of OSM dam / weir polygon and NHD HR flowline"

        df = gp.GeoDataFrame(df, geometry="geometry", crs=CRS)

        merged = append(merged, df)

df = merged.reset_index(drop=True)

write_dataframe(df, outfilename, layer="dam_derived_pt", driver="OpenFileGDB")
