from pathlib import Path
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from pyogrio import read_dataframe, write_dataframe
import shapely


from analysis.constants import CRS
from analysis.lib.geometry import make_valid, dissolve
from analysis.lib.geometry.lines import merge_lines
from analysis.lib.io import read_arrow_tables


warnings.filterwarnings("ignore", ".*organizePolygons.*")
warnings.filterwarnings("ignore", ".*invalid value encountered in hausdorff_distance.*")


# meters
# NOTE: region 06 has some areas where there are parallel lines on either side of a riverine waterway instead of centerline
# NOTE: region 09 has a lower level of alignment between EPA lines and NHD lines and needs bigger tolerance
# Other regions adjusted as needed
SELECTION_TOLERANCE = {
    "default": 50,
    "03": 75,
    "06": 75,
    "09": 100,
    "10": 100,
    "11": 150,
    "14": 75,
    "16": 75,
    "17": 100,
    "18": 100,
}

ENDPOINT_TOLERANCE = 5  # meters; used to determine if endpoints are close enough to EPA lines
MAX_ENDPOINT_DIFF = 1000  # meters

data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"
waterbodies_dir = data_dir / "waterbodies"
epa_dir = data_dir / "epa"
src_dir = epa_dir / "source"
out_dir = epa_dir / "derived"
out_dir.mkdir(exist_ok=True)
infilename = src_dir / "ATTAINS_Assessment_20250117.gdb"

huc2s = gp.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2", "geometry"])

cols = [
    "temperature",
    "cause_unknown_impaired_biota",
    "oxygen_depletion",
    "algal_growth",
    "flow_alterations",
    "habitat_alterations",
    "hydrologic_alteration",
    "cause_unknown_fish_kills",
]
where = " OR ".join(f"{col}='Cause'" for col in cols)

epa_core_cols = ["year", "on303dlist", "url"] + cols


# lines identified by manual review that are not otherwise included in rules below
keep_line_ids = np.array(
    [
        5000701352747,
        5000701357113,
        5000701359625,
        5000701366067,
        5000701370257,
        5000701374082,
        5000701374127,
        5000701376553,
        5000701379247,
        5000701382941,
        5000801712069,
        5000801773431,
        5000801748004,
        5000801747049,
        5000801732218,
        5000801732856,
        10000200519660,
        10000700018688,
        10000700002397,
        10000700018669,
        10000700045694,
        5000801733925,
        10000200498730,
        10000200618783,
        10000200618794,
        23001000005069,
        23001000018056,
        23001000028535,
        23001000028963,
        23001000031663,
        23001000041640,
        23001000048815,
        23001000052283,
        23001000069688,
        23001000080393,
        23001700009948,
        23001700010245,
        23001700030519,
        23001700031209,
        23001700031250,
        23001700041631,
        23001700041644,
        23001700052265,
        23001700061685,
        23001700062193,
        23001700072612,
        23001700082983,
        24001300001369,
        24001300010541,
        24001300101691,
        24001300104341,
        24001300195925,
        24001300297558,
        24001300383673,
        24001300387269,
        24001300389483,
        24001300479246,
        24001300488534,
        24001300575522,
        24001300675925,
        24001300772114,
        24001300776893,
        24001300872439,
        24001301060049,
        24001301064036,
        24001301247924,
        25000400343246,
        65000100011560,
        65000200002672,
        65000200075761,
        15001500012334,
        15001500127708,
        15001500127518,
        15000500055047,
        60000800221690,
        60000800316609,
        60000800206012,
        60000800299943,
        60000800268387,
        60000800288174,
        60000800209211,
        60000800196860,
        60001300081504,
        60001300011410,
        60000800299940,
        60000800292665,
        60001800024222,
        24000500005240,
        24000500004873,
        24000500009446,
        24001200020792,
        24001300577544,
        24001300888171,
        24001301080598,
        24001300884125,
        24001301267895,
        24001301458044,
        24001300774344,
        24001300103913,
        24001300387885,
        25000400309715,
        25000400393542,
        25000400418866,
        25000400309960,
        25000300007923,
        22001400002665,
        22000600030502,
        22000600016884,
        20000500000012,
        20000700010564,
        20000700020781,
        20000700011021,
        20000700073479,
        20000700010445,
        20000700072851,
        20000700020784,
        20000700031281,
        20000700041778,
        20000700022212,
        20000700000006,
        20000700000009,
        20000700001509,
        20000700001510,
        20000700022407,
        20000700020794,
        20000700075707,
        65000200040327,
        21000800033888,
        21000800056410,
        21000800018660,
        21000800048954,
        21000800022506,
        21000800007418,
        21000800022411,
        21000800040898,
        21000800052079,
        21000800033342,
        21000800014390,
        21000800002972,
        21000800059643,
        21000800052080,
        21000800010629,
        21000800010628,
        21000800052080,
        21000800010629,
        21000700017868,
        21000700022134,
        21000700032110,
        21000700002904,
        21001200023285,
        21001200050289,
        21000300152574,
        21000300057022,
        35000300108768,
        35000300108766,
        35000300144914,
        35000300108742,
        35000300181264,
        35000300036355,
        35000700020312,
        41000300087386,
        41000300087439,
        41000600119462,
        41000600131788,
        41000300044101,
        41000700082873,
        41000700055384,
        41000300009790,
        41000300008195,
        41000300005874,
        41000300016606,
        41000300016667,
        41000300090102,
        41000300016555,
        41000300005858,
        41000300015331,
        41000300011041,
        41000200019941,
        70000600012658,
        70000600002356,
        70000600002300,
        70000600012673,
        70000600008309,
        70000600008366,
        70000600008337,
        70000600009394,
        70000600009440,
        70000600008326,
        70000600013916,
        70000500047475,
        70000500102604,
        70000500038058,
        70000500047463,
        70000300035456,
        70000300035405,
        70000300035408,
        70000300035441,
        70000300035393,
        70000300052651,
        55001200049629,
        55001200065533,
        55001200001443,
        55001200033557,
        55001200049632,
        55001200049876,
        55000700234578,
        55000700245698,
        55000700234252,
        55000700256469,
        55000700267350,
        55000700223347,
        55000700345644,
        55000700234424,
        55000700301279,
        55000700234423,
        55000700323584,
        55000700334793,
        55000700255413,
        55001100314991,
        55001100273009,
        55001100230653,
        55001100187248,
        55001100270919,
        55001100016485,
        55001100143739,
        55001100271703,
        55001100055818,
        50000400299788,
        50000400259824,
        50000400258674,
        50000400000097,
        50000400170756,
        50000400000131,
        50000400256466,
        50000400299416,
        50000400042986,
        50000400085817,
        50000400086239,
        50000400171264,
        50000400043470,
        50000400171259,
        50000400128917,
        50000400095986,
        50000300026406,
        50000200036093,
        50000100072690,
        50000100072691,
        50000100185486,
        50000100072695,
        50000100072697,
        50000100129010,
        50000100049867,
        50000100162651,
        50000900250178,
        50000900454782,
        50000900277130,
        50000900249828,
        50000900101280,
        50000900220301,
        50000900309258,
        50000900279522,
        50000900042496,
        50000400212794,
        50000900156555,
        50000900335135,
        50000900275920,
        50000900365006,
        50000900038890,
        50000900186886,
        50000900186886,
        50000900157620,
        50000900306019,
        50000900127799,
        50000900394899,
        50000900246678,
        50000900306347,
        50000900246830,
        50000900246832,
        50000900395091,
        50000900365500,
        50000900069009,
        50000900306177,
        50000900335870,
        50000900217334,
        50000900009895,
    ],
    dtype="uint64",
)


################################################################################
### Prepare lines and areas
### NOTE: some of these areas are HUC12s or older versions of HUC12s / NHD Med
### Resolution catchments and can't be joined directly to waterbodies
################################################################################
# print("Reading EPA lines and areas")
# lines = (
#     read_dataframe(
#         infilename,
#         layer="attains_au_lines",
#         use_arrow=True,
#         where=where,
#         columns=["geometry", "state", "waterbodyreportlink", "reportingcycle", "on303dlist"] + cols,
#     )
#     .rename(columns={"waterbodyreportlink": "url", "reportingcycle": "year"})
#     .to_crs(CRS)
#     .explode(ignore_index=True)
#     .drop_duplicates()
#     .reset_index(drop=True)
# )

# areas = (
#     read_dataframe(
#         infilename,
#         layer="attains_au_areas",
#         use_arrow=True,
#         where=where,
#         columns=["geometry", "state", "waterbodyreportlink", "reportingcycle", "on303dlist"] + cols,
#     )
#     .rename(columns={"waterbodyreportlink": "url", "reportingcycle": "year"})
#     .to_crs(CRS)
#     .explode(ignore_index=True)
#     .drop_duplicates()
#     .reset_index(drop=True)
# )

# for df in [lines, areas]:
#     for col in cols:
#         df[col] = df[col] == "Cause"

#     df["year"] = df.year.astype("str")
#     df["on303dlist"] = df.on303dlist == "Y"
#     df["geometry"] = make_valid(df.geometry.values)

# ### Remove any lines within areas, including those that are at the boundary of the line
# # Note: some polygons are represented as both polygons and lines along their outer edge;
# # we have to buffer the polygons slightly because they don't exactly match
# left, right = shapely.STRtree(lines.geometry.values).query(areas.geometry.values, predicate="intersects")
# pairs = pd.DataFrame(
#     {
#         "left": areas.index.values.take(left),
#         "right": lines.index.values.take(right),
#         "line": lines.geometry.values.take(right),
#     }
# )
# ix = pairs.left.unique()
# buffers = pd.Series(shapely.buffer(areas.geometry.values.take(ix), 1, quad_segs=1), name="wb", index=ix)
# pairs = pairs.join(buffers, on="left")
# shapely.prepare(pairs.wb.values)
# contains = shapely.contains_properly(pairs.wb.values, pairs.line.values)
# lines = lines.loc[~lines.index.isin(pairs.loc[contains].right.unique())].reset_index(drop=True)


# ### Some waterbodies are represented as lines of their outline; fix
# # find all those that are polygons where the first and last points are the same
# # NOTE: there are some waterbodies in CA that are part of a chain of multilinestrings, some true lines,
# # some outlines in multiple parts; these could not be fixed by methods below
# tmp = lines.loc[lines.state.isin(["OK", "CA"])].copy()
# first_pt = shapely.get_point(tmp.geometry.values, 0)
# last_pt = shapely.get_point(tmp.geometry.values, -1)
# tmp = tmp.loc[shapely.equals(first_pt, last_pt)]
# tmp["num_pts"] = shapely.get_num_points(tmp.geometry.values)
# # by visual inspection, ones with low numbers of points are loops in lines not waterbodies
# tmp = tmp.loc[tmp.num_pts >= 10].copy()
# ix = tmp.index.values

# wb_lines = lines.loc[lines.index.isin(ix)].reset_index(drop=True)
# lines = lines.loc[~lines.index.isin(ix)].reset_index(drop=True)

# wb_lines["geometry"] = wb_lines.geometry.apply(shapely.Polygon)

# # remove interior polygons / islands
# left, right = shapely.STRtree(wb_lines.geometry.values).query(wb_lines.geometry.values, predicate="contains_properly")
# wb_lines = wb_lines.take(np.unique(np.setdiff1d(wb_lines.index.values, right)))
# areas = pd.concat([areas, wb_lines], ignore_index=True).reset_index(drop=True)

# # dissolve to waterbodyreport link
# areas = dissolve(
#     areas.explode(ignore_index=True),
#     by="url",
#     agg={"year": "max", "on303dlist": "max", **{c: "max" for c in cols}},
# )

# # remove duplicates
# areas = gp.GeoDataFrame(areas.groupby("geometry").first().reset_index(), crs=areas.crs)

# # assign our own unique ID
# areas["epaWbID"] = areas.index.values
# lines["epaLineID"] = lines.index.values


# areas = areas.explode(ignore_index=True)

# ################################################################################
# ### Assign HUC2
# ################################################################################
# print("Intersecting with HUC2s")

# # NOTE: because some of the units are watersheds, they touch multiple HUC2s and may
# # overlap slightly; we clean these up by taking the one with the largest overlap
# left, right = shapely.STRtree(areas.geometry.values).query(huc2s.geometry.values, predicate="intersects")
# pairs = pd.DataFrame(
#     {
#         "HUC2": huc2s.HUC2.values.take(left),
#         "huc2_geom": huc2s.geometry.values.take(left),
#         "right": areas.index.values.take(right),
#         "right_geom": areas.geometry.values.take(right),
#         "overlap": np.float64(1),
#     }
# )

# s = pairs.groupby("right").HUC2.nunique()
# ix = pairs.right.isin(s[s > 1].index.values)
# pairs.loc[ix, "overlap"] = shapely.area(
#     shapely.intersection(pairs.loc[ix].huc2_geom.values, pairs.loc[ix].right_geom.values)
# ) / shapely.area(pairs.loc[ix].right_geom)

# huc2_join = pairs.sort_values(by=["right", "overlap"], ascending=[True, False]).groupby("right").HUC2.first()
# areas = areas.join(huc2_join, how="inner")
# areas.to_feather(out_dir / "epa_areas.feather")


# left, right = shapely.STRtree(lines.geometry.values).query(huc2s.geometry.values, predicate="intersects")
# pairs = pd.DataFrame(
#     {
#         "HUC2": huc2s.HUC2.values.take(left),
#         "huc2_geom": huc2s.geometry.values.take(left),
#         "right": lines.index.values.take(right),
#         "right_geom": lines.geometry.values.take(right),
#         "overlap": np.float64(0),
#     }
# )

# s = pairs.groupby("right").HUC2.nunique()
# ix = pairs.right.isin(s[s > 1].index.values)
# pairs.loc[ix, "overlap"] = shapely.length(
#     shapely.intersection(pairs.loc[ix].huc2_geom.values, pairs.loc[ix].right_geom.values)
# ) / shapely.length(pairs.loc[ix].right_geom)

# huc2_join = pairs.sort_values(by=["right", "overlap"], ascending=[True, False]).groupby("right").HUC2.first()
# lines = lines.join(huc2_join, how="inner")
# lines.to_feather(out_dir / "epa_lines.feather")


# FIXME: remove
lines = gp.read_feather(out_dir / "epa_lines.feather")
areas = gp.read_feather(out_dir / "epa_areas.feather")


################################################################################
### Join EPA areas and lines to flowlines
################################################################################
merged_areas = None
merged_lines = None
for huc2 in sorted(areas.HUC2.unique()):
    print(f"Processing {huc2}...")
    print("Joining EPA areas to flowlines")
    flowlines = gp.read_feather(nhd_dir / huc2 / "flowlines.feather", columns=["NHDPlusID", "geometry"])

    ### Join EPA areas to flowlines
    epa_subset = areas.loc[areas.HUC2 == huc2]
    left, right = shapely.STRtree(flowlines.geometry.values).query(epa_subset.geometry.values, predicate="intersects")
    pairs = pd.DataFrame(
        {
            "NHDPlusID": flowlines.NHDPlusID.values.take(right),
            "line": flowlines.geometry.values.take(right),
            "epaWbID": epa_subset.epaWbID.values.take(left),
            "epa_geom": epa_subset.geometry.values.take(left),
            "overlap": np.float64(0),
            "HUC2": huc2,
        }
    )
    shapely.prepare(pairs.epa_geom.values)
    contains = shapely.contains_properly(pairs.epa_geom.values, pairs.line.values)
    pairs.loc[contains, "overlap"] = np.float64(1)

    # keep any with >75% overlap
    overlap = shapely.length(
        shapely.intersection(pairs.loc[~contains].line.values, pairs.loc[~contains].epa_geom.values)
    ) / shapely.length(pairs.loc[~contains].line.values)
    pairs.loc[~contains, "overlap"] = overlap

    # reduce to smallest overlapping EPA waterbody when there are multiple urls
    # multiple lines with same URL get coalesced later as part of merge
    pairs = pairs.loc[pairs.overlap >= 0.75].copy()

    # have to coalesce the exploded features to one record per area
    area_atts = areas.loc[areas.HUC2 == huc2].groupby("epaWbID")[epa_core_cols].first()
    pairs = pairs.join(area_atts, on="epaWbID")
    pairs = pairs.join(pairs.groupby("NHDPlusID").url.nunique().rename("num_epa"), on="NHDPlusID")

    ix = pairs.num_epa > 1
    pairs.loc[ix, "wb_km2"] = shapely.area(pairs.loc[ix].epa_geom.values) / 1e3
    # round overlap so that those that are very nearly overlapping are same as fully overlapping
    pairs["overlap"] = pairs.overlap.round(2)
    pairs = (
        pairs.sort_values(by=["NHDPlusID", "overlap", "wb_km2"], ascending=[True, False, True])
        .groupby(["NHDPlusID"])[["HUC2", "epaWbID"] + epa_core_cols]
        .first()
        .reset_index()
    )
    line_ids = pairs.NHDPlusID.unique()

    if merged_areas is None:
        merged_areas = pairs
    else:
        merged_areas = pd.concat([merged_areas, pairs], ignore_index=True)

    print("Joining EPA lines to flowlines")
    epa_subset = lines.loc[lines.HUC2 == huc2].copy()

    # merge lines and then buffer
    epa_lines = merge_lines(epa_subset, by="epaLineID").explode(ignore_index=True)
    tolerance = SELECTION_TOLERANCE.get(huc2, SELECTION_TOLERANCE["default"])
    epa_lines["buf"] = shapely.buffer(epa_lines.geometry.values, tolerance)
    # ignore any flowlines already marked above
    subset = flowlines.loc[~flowlines.NHDPlusID.isin(line_ids)].reset_index(drop=True)

    # DEBUG
    # write_dataframe(
    #     gp.GeoDataFrame(geometry=epa_lines.buf, crs=CRS),
    #     f"/tmp/region_{huc2}_epa_buffer.fgb",
    # )

    # add upstream / downstream points
    subset["nhd_upstream_pt"] = shapely.get_point(subset.geometry.values, 0)
    subset["nhd_downstream_pt"] = shapely.get_point(subset.geometry.values, -1)

    left, right = shapely.STRtree(subset.geometry.values).query(epa_lines.buf.values, predicate="intersects")
    pairs = pd.DataFrame(
        {
            "NHDPlusID": subset.NHDPlusID.values.take(right),
            "line": subset.geometry.values.take(right),
            "nhd_upstream_pt": subset.nhd_upstream_pt.values.take(right),
            "nhd_downstream_pt": subset.nhd_downstream_pt.values.take(right),
            "epaLineID": epa_lines.epaLineID.values.take(left),
            "epa_line": epa_lines.geometry.values.take(left),
            "epa_buf": epa_lines.buf.values.take(left),
            "HUC2": huc2,
        }
    )
    pairs["upstream_dist"] = shapely.distance(pairs.nhd_upstream_pt, pairs.epa_line.values)
    pairs["downstream_dist"] = shapely.distance(pairs.nhd_downstream_pt, pairs.epa_line.values)

    tmp = pairs.groupby(by=["NHDPlusID", "epaLineID"]).agg(
        {
            "upstream_dist": "min",
            "downstream_dist": "min",
        }
    )
    pairs = pairs.drop(columns=["upstream_dist", "downstream_dist"]).join(tmp, on=["NHDPlusID", "epaLineID"])

    # calculate total overlap with buffer
    # NOTE: this may overcount due to overlapping buffer ends, but probably OK
    pairs["overlap_km"] = shapely.length(shapely.intersection(pairs.line.values, pairs.epa_buf.values)) / 1e3
    pairs["km"] = shapely.length(pairs.line.values) / 1e3
    tmp = pairs.groupby(by=["NHDPlusID", "epaLineID"]).agg({"overlap_km": "sum", "km": "first"})
    tmp["overlap"] = tmp.overlap_km / tmp.km
    pairs = pairs.join(tmp.overlap, on=["NHDPlusID", "epaLineID"])
    # pairs = pairs.join(pairs.groupby("NHDPlusID").epaLineID.nunique().rename("num_epa"), on="NHDPlusID")
    pairs = pairs.join(epa_subset.set_index("epaLineID")[epa_core_cols], on="epaLineID")
    pairs = pairs.join(pairs.groupby("NHDPlusID").url.nunique().rename("num_epa"), on="NHDPlusID")

    # must have 75% overlap, or at least 50% if both endpoints are very close to the same EPA line
    # or if the line overlaps multiple EPA buffers by at least 25%
    manual_keep_ix = pairs.NHDPlusID.isin(keep_line_ids) & (pairs.overlap >= 0.05)
    keep_ix = (
        (pairs.overlap >= 0.75)
        | (
            (pairs.upstream_dist < ENDPOINT_TOLERANCE)
            & (pairs.downstream_dist < ENDPOINT_TOLERANCE)
            & (pairs.overlap >= 0.5)
        )
        | ((pairs.num_epa >= 2) & (pairs.overlap >= 0.25))
    )
    pairs["keep"] = manual_keep_ix | keep_ix

    # warn about manual review ones that are no longer needed
    ids = np.intersect1d(pairs.loc[keep_ix].NHDPlusID.values, keep_line_ids)
    if len(ids):
        warnings.warn(f"REMOVE manual NHDPlusIDs: {ids}")

    # TODO: traverse networks within each and fill gaps (see analysis/prep/network/lib/drains.py starting around line 159)
    # this is especially needed in region 18 where there is poor alignment or waterbodies still represented as lines

    pairs = pairs.loc[pairs.keep].copy()

    # DEBUG:
    write_dataframe(
        flowlines.loc[flowlines.NHDPlusID.isin(pairs.NHDPlusID.unique())],
        f"/tmp/region_{huc2}_keep.fgb",
    )
    # write_dataframe(flowlines.loc[flowlines.NHDPlusID.isin(line_ids)], f"/tmp/region_{huc2}_in_epa_areas.fgb")
    # write_dataframe(flowlines, f"/tmp/region_{huc2}_flowlines.fgb")

    # reduce to nearest adjacent EPA line when there are multiple urls
    # multiple lines with same URL get coalesced later as part of merge

    ix = pairs.num_epa > 1
    pairs.loc[ix, "hdist"] = shapely.hausdorff_distance(pairs.loc[ix].line.values, pairs.loc[ix].epa_line.values)
    pairs = (
        pairs.sort_values(by=["NHDPlusID", "overlap", "hdist"], ascending=[True, False, True])
        .groupby(["NHDPlusID"])[["HUC2", "epaLineID"] + epa_core_cols]
        .first()
        .reset_index()
    )

    if merged_lines is None:
        merged_lines = pairs
    else:
        merged_lines = pd.concat([merged_lines, pairs], ignore_index=True)


merged_areas = merged_areas.drop_duplicates()
merged_areas.to_feather(out_dir / "epa_area_flowlines.feather")

merged_lines = merged_lines.drop_duplicates()
merged_lines.to_feather(out_dir / "epa_line_flowlines.feather")


print("writing outputs")

df = pd.concat(
    [merged_areas.drop(columns=["epaWbID"]), merged_lines.drop(columns=["epaLineID"])], ignore_index=True
).drop_duplicates()
df.to_feather(out_dir / "epa_flowlines.feather")


### export flowlines with EPA data joined
ids = pa.array(df.NHDPlusID.unique())
flowlines = read_arrow_tables(
    [nhd_dir / huc2 / "flowlines.feather" for huc2 in sorted(df.HUC2.unique())],
    columns=["NHDPlusID", "geometry"],
    filter=pc.is_in(pc.field("NHDPlusID"), ids),
).to_pandas()
flowlines["geometry"] = shapely.from_wkb(flowlines.geometry.values)
flowlines = gp.GeoDataFrame(flowlines.join(df.set_index("NHDPlusID"), on="NHDPlusID"), geometry="geometry", crs=CRS)

# DEBUG:
write_dataframe(flowlines, "/tmp/epa_flowlines.fgb")

print("All done!")
