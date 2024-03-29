"""
Preprocess road / stream crossings into data needed by tippecanoe for creating vector tiles.

Input:
* USGS Road / Stream crossings, projected to match SARP standard projection (Albers CONUS).
* pre-processed and snapped small barriers


Outputs:
`data/barriers/intermediate/road_crossings.feather`: road / stream crossing data for merging in with small barriers that do not have networks
"""

from pathlib import Path
from time import time

import geopandas as gp
import pandas as pd
import shapely
from pyogrio import read_dataframe, write_dataframe
import numpy as np

from analysis.constants import (
    CROSSINGS_ID_OFFSET,
    CRS,
    FCODE_TO_STREAMTYPE,
    CROSSING_TYPE_TO_DOMAIN,
)
from analysis.lib.graph.speedups import DirectedGraph
from analysis.lib.io import read_feathers
from analysis.prep.barriers.lib.snap import snap_to_flowlines
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins


SNAP_TOLERANCE = 10
DUPLICATE_TOLERANCE = 5

start = time()

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
nhd_dir = data_dir / "nhd"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
qa_dir = barriers_dir / "qa"


def dedup_crossings(df):
    # we only want to dedup those that are really close, and some may be in chains of
    # crossings, so only dedup by distance not neighborhoods
    tree = shapely.STRtree(df.geometry.values)
    pairs = pd.DataFrame(
        tree.query(df.geometry.values, predicate="dwithin", distance=DUPLICATE_TOLERANCE).T,
        columns=["left", "right"],
    )
    g = DirectedGraph(
        df.id.take(pairs.left.values).values.astype("int64"),
        df.id.take(pairs.right.values).values.astype("int64"),
    )

    # note: components accounts for self-intersections and symmetric pairs
    groups, values = g.flat_components()
    groups = pd.DataFrame({"group": groups, "id": values}).astype(df.id.dtype)

    keep_ids = groups.groupby("group").first().id.values.astype("uint64")

    print(f"Dropping {len(df)-len(keep_ids):,} very close road crossings")
    return df.loc[df.id.isin(keep_ids)].copy()


print("Reading road crossings")

# rename columns to match small barriers
# NOTE: tiger2020_feature_names is a combination of multiple road names
df = read_dataframe(
    src_dir / "stream_crossings_united_states_feb_2022.gpkg",
    layer="stream_crossing_sites",
    columns=[
        "stream_crossing_id",
        "tiger2020_feature_names",
        "nhdhr_gnis_stream_name",
        "nhdhr_permanent_identifier",
        "crossing_type",
    ],
    use_arrow=True,
).rename(
    columns={
        "tiger2020_feature_names": "Road",
        "nhdhr_gnis_stream_name": "River",
        "stream_crossing_id": "SARPID",
        "crossing_type": "CrossingType",
    }
)
print(f"Read {len(df):,} road crossings")


df["Source"] = "USGS Database of Stream Crossings in the United States (2022)"


# project HUC4 to match crossings
huc4 = gp.read_feather(boundaries_dir / "huc4.feather", columns=["geometry", "HUC4"]).to_crs(df.crs)
tree = shapely.STRtree(df.geometry.values)
left, right = tree.query(huc4.geometry.values, predicate="intersects")
huc4_join = (
    pd.DataFrame({"HUC4": huc4.HUC4.values.take(left)}, index=df.index.values.take(right)).groupby(level=0).HUC4.first()
)

df = df.join(huc4_join, how="inner").reset_index(drop=True)
df["HUC2"] = df.HUC4.str[:2]
print(f"Selected {len(df):,} road crossings in region")

# use original latitude / longitude (NAD83) values
lon, lat = shapely.get_coordinates(df.geometry.values).astype("float32").T
df["lon"] = lon
df["lat"] = lat

# project to match SARP CRS
df = df.to_crs(CRS)

df["id"] = (df.index.values + CROSSINGS_ID_OFFSET).astype("uint64")
df = df.set_index("id", drop=False)

# There are a bunch of crossings with identical coordinates, remove them
# NOTE: they have different labels, but that seems like it is a result of
# them methods used to identify the crossings (e.g., named highways, roads, etc)
print("Removing duplicate crossings at same location...")

# round to int
x, y = shapely.get_coordinates(df.geometry.values).astype("int").T
df["x"] = x
df["y"] = y

keep_ids = df[["x", "y", "id"]].groupby(["x", "y"]).first().reset_index().id
print(f"Dropping {len(df) - len(keep_ids):,} duplicate road crossings")

df = df.loc[keep_ids].copy()

### Remove crossings that are very close
print("Removing nearby road crossings...")
df = dedup_crossings(df)
print(f"now have {len(df):,} road crossings")

### Cleanup fields
# match dtype of SARPID elsewhere
df.SARPID = "cr" + df.SARPID.round().astype(int).astype(str)

df.River = df.River.str.strip().fillna("")
df.Road = df.Road.str.strip().fillna("")

df.loc[(df.River != "") & (df.Road != ""), "Name"] = df.River + " / " + df.Road
df.Name = df.Name.fillna("")

# update crossingtype and set as domain
df["CrossingType"] = df.CrossingType.fillna("").str.lower()
df.loc[df.CrossingType.isin(["culvert", "tiger2020 road"]), "CrossingType"] = "assumed culvert"
df["CrossingType"] = df.CrossingType.map(CROSSING_TYPE_TO_DOMAIN).astype("uint8")


# Snap to flowlines
df["snapped"] = False
df["snap_log"] = "not snapped"
df["lineID"] = np.nan  # line to which dam was snapped
df["snap_tolerance"] = SNAP_TOLERANCE

snap_start = time()
to_snap = df.copy()
df, to_snap = snap_to_flowlines(df, to_snap)
print(f"Snapped {df.snapped.sum():,} crossings in {time() - snap_start:.2f}s")

print("---------------------------------")
print("\nSnapping statistics")
print(df.groupby("snap_log").size())
print("---------------------------------\n")

print("Dropping any road crossings that didn't snap")
df = df.loc[df.snapped].copy()


### Remove crossings that are very close after snapping
print("Removing nearby road crossings after snapping...")
df = dedup_crossings(df)
print(f"now have {len(df):,} road crossings")


df = add_spatial_joins(df)

# Cleanup HUC, state, county columns that weren't assigned
for col in [
    "HUC2",
    "HUC4",
    "HUC6",
    "HUC8",
    "HUC10",
    "HUC12",
    "Basin",
    "County",
    "COUNTYFIPS",
    "State",
]:
    df[col] = df[col].fillna("")


### Drop any that didn't intersect HUCs or states (including those outside analysis region)
df = df.loc[(df.HUC12 != "") & (df.State != "")].copy()

df["CoastalHUC8"] = df.CoastalHUC8.fillna(False)


### Join to line atts
flowlines = (
    read_feathers(
        [nhd_dir / "clean" / huc2 / "flowlines.feather" for huc2 in df.HUC2.unique() if huc2],
        columns=[
            "lineID",
            "NHDPlusID",
            "GNIS_Name",
            "sizeclass",
            "StreamOrder",
            "FCode",
            "loop",
            "offnetwork",
            "AnnualFlow",
            "AnnualVelocity",
            "TotDASqKm",
        ],
    )
    .set_index("lineID")
    .rename(columns={"offnetwork": "offnetwork_flowline"})
)

df = df.join(flowlines, on="lineID")

df.lineID = df.lineID.astype("uint32")
df.NHDPlusID = df.NHDPlusID.astype("uint64")

# Add name from snapped flowline if not already present
df["GNIS_Name"] = df.GNIS_Name.fillna("").str.strip()
ix = (df.River == "") & (df.GNIS_Name != "")
df.loc[ix, "River"] = df.loc[ix].GNIS_Name
df = df.drop(columns=["GNIS_Name"])

# calculate stream type
df["stream_type"] = df.FCode.map(FCODE_TO_STREAMTYPE).fillna(0).astype("uint8")

# calculate intermittent + ephemeral
df["intermittent"] = df.FCode.isin([46003, 46007])

# Fix missing field values
df.StreamOrder = df.StreamOrder.fillna(-1).astype("int8")
df["loop"] = df.loop.fillna(False)
df["offnetwork_flowline"] = df.offnetwork_flowline.fillna(False)
df["sizeclass"] = df.sizeclass.fillna("")
df["FCode"] = df.FCode.fillna(-1).astype("int32")
# -9998.0 values likely indicate AnnualVelocity data is not available, equivalent to null
df.loc[df.AnnualVelocity < 0, "AnnualVelocity"] = np.nan

for field in ["AnnualVelocity", "AnnualFlow", "TotDASqKm"]:
    df[field] = df[field].astype("float32")

df.reset_index(drop=True).to_feather(src_dir / "road_crossings.feather")
write_dataframe(df, qa_dir / "raw_road_crossings.fgb")


print(f"Done in {time() - start:.2f}")
