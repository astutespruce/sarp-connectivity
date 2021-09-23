from enum import unique
from pathlib import Path
import os

import geopandas as gp
import pandas as pd
import pygeos as pg
import numpy as np

from pyogrio import write_dataframe

from analysis.constants import STATES
from analysis.lib.io import read_feathers

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
out_dir = Path("/tmp/sarp")

if not out_dir.exists():
    os.makedirs(out_dir)


dams = gp.read_feather(data_dir / "barriers/master/dams.feather")

huc2s = [x for x in sorted(dams.HUC2.unique()) if x]


drains = (
    read_feathers(
        [
            data_dir / "nhd/clean/" / huc2 / "waterbody_drain_points.feather"
            for huc2 in huc2s
        ],
        new_fields={"HUC2": huc2s},
        geo=True,
    )
    .drop(columns=["snap_to_junction", "snap_dist"])
    .rename(
        columns={
            "MaxElevSmo": "maxelev",
            "MinElevSmo": "minelev",
            "Slope": "slope",
            "StreamOrde": "fsorder",
            "km2": "wb_km2",
            "flowlineLength": "flength",
        }
    )
)

# Drop any drains with a wbID that is already associated with a dam
wbIDs = dams.loc[dams.wbID.notnull()].wbID.unique().astype("uint")

ix = drains.wbID.isin(wbIDs)
print(
    f"Excluding {ix.sum():,} drain points of waterbodies already associated with dams"
)

drains = drains.loc[~ix].copy()

# Find any that are within 50m of dams and ignore those
# This picks up any that are likely related to dams but not used for snapping
tree = pg.STRtree(drains.geometry.values.data)
(left, right), dist = tree.nearest_all(
    dams.geometry.values.data, max_distance=50, return_distance=True
)

right = np.unique(right)
ix = np.setdiff1d(np.arange(len(drains)), right)

print(f"Excluding {len(right):,} drains that are within 50m of dams")

drains = drains.iloc[ix].copy()

### Join to states
states = gp.read_feather(
    boundaries_dir / "states.feather", columns=["id", "geometry"]
).rename(columns={"id": "state"})

states = states.loc[states.state.isin(STATES.keys())].copy()

print("Joining to states...")
tree = pg.STRtree(drains.geometry.values.data)
left, right = tree.query_bulk(states.geometry.values.data, predicate="intersects")

tmp = (
    pd.DataFrame(
        {"state": states.state.values.take(left)}, index=drains.index.values.take(right)
    )
    .groupby(level=0)
    .first()
)

# drop any without states (e.g., outside region states)
drains = drains.join(tmp, how="inner")

# cleanup datatypes
for col in ["wb_km2", "TotDASqKm"]:
    drains[col] = drains[col].astype("float32")

print("Saving to shapefile")
write_dataframe(drains, out_dir / "unclaimed_drain_points.shp")

