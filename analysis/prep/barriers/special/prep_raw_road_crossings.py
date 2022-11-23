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
import warnings

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

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


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
    tree = shapely.STRtree(df.geometry.values.data)
    pairs = pd.DataFrame(
        tree.query(
            df.geometry.values.data, predicate="dwithin", distance=DUPLICATE_TOLERANCE
        ).T,
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
).rename(
    columns={
        "tiger2020_feature_names": "Road",
        "nhdhr_gnis_stream_name": "Stream",
        "stream_crossing_id": "SARPID",
        "crossing_type": "crossingtype",
    }
)
print(f"Read {len(df):,} road crossings")

# project HUC4 to match crossings
huc4 = gp.read_feather(boundaries_dir / "huc4.feather", columns=["geometry"]).to_crs(
    df.crs
)
tree = shapely.STRtree(df.geometry.values.data)
ix = tree.query(huc4.geometry.values.data, predicate="intersects")[1]

df = df.take(ix).reset_index(drop=True)
print(f"Selected {len(df):,} road crossings in region")

# use original latitude / longitude (NAD83) values
lon, lat = shapely.get_coordinates(df.geometry.values.data).astype("float32").T
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
x, y = shapely.get_coordinates(df.geometry.values.data).astype("int").T
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

df.Stream = df.Stream.str.strip().fillna("")
df.Road = df.Road.str.strip().fillna("")

df.loc[
    (df.Stream.str.strip().str.len() > 0) & (df.Road.str.strip().str.len() > 0), "Name"
] = (df.Stream + " / " + df.Road)

df.Name = df.Name.fillna("")

# update crossingtype and set as domain
df.loc[df.crossingtype == "tiger2020 road", "crossingtype"] = "assumed culvert"

errors = [v for v in df.crossingtype.unique() if not v in CROSSING_TYPE_TO_DOMAIN]
if len(errors):
    raise ValueError(
        f"Values present in crossingtype not present in CROSSING_TYPE_TO_DOMAIN: {errors}"
    )

df["crossingtype"] = df.crossingtype.map(CROSSING_TYPE_TO_DOMAIN)


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


df["CoastalHUC8"] = df.CoastalHUC8.fillna(False)

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

### Remove crossings that are very close after snapping
print("Removing nearby road crossings after snapping...")
df = dedup_crossings(df)
print(f"now have {len(df):,} road crossings")


### Join to line atts
flowlines = read_feathers(
    [
        nhd_dir / "clean" / huc2 / "flowlines.feather"
        for huc2 in df.HUC2.unique()
        if huc2
    ],
    columns=[
        "lineID",
        "NHDPlusID",
        "GNIS_Name",
        "sizeclass",
        "StreamOrder",
        "FCode",
        "loop",
        "AnnualFlow",
        "AnnualVelocity",
        "TotDASqKm",
    ],
).set_index("lineID")

df = df.join(flowlines, on="lineID")

df.StreamOrder = df.StreamOrder.fillna(-1).astype("int8")

# Add name from snapped flowline if not already present
df["GNIS_Name"] = df.GNIS_Name.fillna("").str.strip()
ix = (df.Stream == "") & (df.GNIS_Name != "")
df.loc[ix, "Stream"] = df.loc[ix].GNIS_Name
df = df.drop(columns=["GNIS_Name"])


# calculate stream type
df["stream_type"] = df.FCode.map(FCODE_TO_STREAMTYPE).fillna(0).astype("uint8")

# calculate intermittent + ephemeral
df["intermittent"] = df.FCode.isin([46003, 46007])

# Fix missing field values
df["loop"] = df.loop.fillna(False)
df["sizeclass"] = df.sizeclass.fillna("")
df["FCode"] = df.FCode.fillna(-1).astype("int32")
# -9998.0 values likely indicate AnnualVelocity data is not available, equivalent to null
df.loc[df.AnnualVelocity < 0, "AnnualVelocity"] = np.nan

for field in ["lineID", "NHDPlusID", "AnnualVelocity", "AnnualFlow", "TotDASqKm"]:
    df[field] = df[field].astype("float32")

df.reset_index(drop=True).to_feather(src_dir / "road_crossings.feather")
write_dataframe(df, qa_dir / "raw_road_crossings.fgb")


print(f"Done in {time() - start:.2f}")
