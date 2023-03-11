from pathlib import Path
from time import time
import warnings

import geopandas as gp
import numpy as np
import shapely
from pyogrio import write_dataframe

from api.constants import ROAD_CROSSING_API_FIELDS

# considered to duplicate an assessed road barriers if within this value
DUPLICATE_TOLERANCE = 10  # meters

start = time()

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
out_dir = barriers_dir / "master"
api_dir = data_dir / "api"
qa_dir = barriers_dir / "qa"


print("Reading road crossings")
df = gp.read_feather(src_dir / "road_crossings.feather")

df["Source"] = "USGS Database of Stream Crossings in the United States (2022)"


tree = shapely.STRtree(df.geometry.values.data)

### Remove those that co-occur with dams
dams = gp.read_feather(barriers_dir / "master/dams.feather", columns=["geometry"])
right = tree.query(
    dams.geometry.values.data, predicate="dwithin", distance=DUPLICATE_TOLERANCE
)[1]
dam_ix = df.index.values.take(np.unique(right))

print(f"Found {len(dam_ix)} road crossings within {DUPLICATE_TOLERANCE}m of dams")

### Remove those that co-occur with waterfalls
waterfalls = gp.read_feather(
    barriers_dir / "master/waterfalls.feather", columns=["geometry"]
)
right = tree.query(
    waterfalls.geometry.values.data, predicate="dwithin", distance=DUPLICATE_TOLERANCE
)[1]
wf_ix = df.index.values.take(np.unique(right))

print(f"Found {len(wf_ix)} road crossings within {DUPLICATE_TOLERANCE}m of waterfalls")

### Remove those that otherwise duplicate existing small barriers
print("Removing crossings that duplicate existing barriers")
barriers = gp.read_feather(barriers_dir / "master/small_barriers.feather")

right = tree.query(
    barriers.geometry.values.data, predicate="dwithin", distance=DUPLICATE_TOLERANCE
)[1]
sb_ix = df.index.values.take(np.unique(right))

print(
    f"Dropping {len(sb_ix):,} road crossings that are within {DUPLICATE_TOLERANCE} of inventoried barriers"
)

drop_ix = np.unique(np.concatenate([dam_ix, wf_ix, sb_ix]))
df = df.loc[~df.index.isin(drop_ix)].copy()


### Export all barriers for use in counts / tiles
print(f"Serializing {len(df):,} road crossings")

df = df.reset_index(drop=True)
df.to_feather(out_dir / "road_crossings.feather")
write_dataframe(df, qa_dir / "road_crossings.fgb")


### Extract out only the snapped ones on loops for use in network analysis
# NOTE: any that were not snapped were dropped in earlier processing
print(f"Serializing {df.snapped.sum():,} snapped road crossings")
snapped = df.loc[
    df.snapped & (~df.loop),
    ["geometry", "id", "HUC2", "lineID", "NHDPlusID", "loop", "intermittent"],
].reset_index(drop=True)

snapped.lineID = snapped.lineID.astype("uint32")
snapped.NHDPlusID = snapped.NHDPlusID.astype("uint64")

snapped.to_feather(barriers_dir / "snapped/road_crossings.feather")


### Export for use in API

df = df.rename(
    columns={
        "intermittent": "Intermittent",
        "loop": "OnLoop",
        "sizeclass": "StreamSizeClass",
        "crossingtype": "CrossingType",
    }
)[["id"] + ROAD_CROSSING_API_FIELDS]


df.to_feather(api_dir / "road_crossings.feather")


print("Done in {:.2f}".format(time() - start))
