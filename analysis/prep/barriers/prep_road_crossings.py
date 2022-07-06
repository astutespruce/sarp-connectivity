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
from pyogrio import write_dataframe

from analysis.prep.barriers.lib.duplicates import mark_duplicates

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

DUPLICATE_TOLERANCE = 10  # meters

start = time()

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
out_dir = barriers_dir / "master"
qa_dir = barriers_dir / "qa"


print("Reading road crossings")
df = gp.read_feather(src_dir / "road_crossings.feather")

# update crossingtype
df.loc[df.crossingtype == "tiger2020 road", "crossingtype"] = "assumed culvert"


### Remove those that otherwise duplicate existing small barriers
print("Removing crossings that duplicate existing barriers")
barriers = gp.read_feather(barriers_dir / "master/small_barriers.feather")
barriers = barriers.loc[~barriers.duplicate]
barriers["kind"] = "barrier"

df["joinID"] = (df.index * 1e6).astype("uint32")
df["kind"] = "crossing"

merged = pd.concat(
    [barriers[["kind", "geometry"]], df[["joinID", "kind", "geometry"]]],
    sort=False,
    ignore_index=True,
)
merged = mark_duplicates(merged, tolerance=DUPLICATE_TOLERANCE)

dup_groups = merged.loc[
    (merged.dup_count > 1) & (merged.kind == "barrier")
].dup_group.unique()
remove_ids = merged.loc[
    merged.dup_group.isin(dup_groups) & (merged.kind == "crossing")
].joinID
print(f"{len(remove_ids):,} crossings appear to be duplicates of existing barriers")

df = df.loc[~df.joinID.isin(remove_ids)].drop(columns=["joinID", "kind"])

# make sure that id is unique of small barriers
df["id"] = (barriers.id.max() + 100000 + df.index.astype("uint")).astype("uint")

print(f"Serializing {len(df):,} road crossings")

df = df.reset_index(drop=True)
df.to_feather(out_dir / "road_crossings.feather")
write_dataframe(df, qa_dir / "road_crossings.fgb")


# save snapped road crossings for later analysis
print(f"Serializing {df.snapped.sum():,} snapped road crossings")
df.loc[
    df.snapped,
    ["geometry", "id", "HUC2", "lineID", "NHDPlusID", "loop", "intermittent"],
].reset_index(drop=True).to_feather(barriers_dir / "snapped/road_crossings.feather")


print("Done in {:.2f}".format(time() - start))
