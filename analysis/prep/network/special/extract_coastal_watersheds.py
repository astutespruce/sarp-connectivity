from pathlib import Path

import geopandas as gp
import pandas as pd
import shapely

from analysis.lib.io import read_feathers
from analysis.lib.geometry import dissolve

MARINE_BUFFER = 20000  # meters (used 20km per guidance from Kat)


data_dir = Path("data")
out_dir = Path()

print("Reading marine areas")
huc2s = sorted(
    pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"]).HUC2
)
paths = [Path(data_dir / f"nhd/raw/{huc2}/nhd_marine.feather") for huc2 in huc2s]
paths = [p for p in paths if p.exists()]

marine = read_feathers(paths, geo=True).explode(ignore_index=True)

print(f"Creating {MARINE_BUFFER}m buffer around marine areas")
marine["geometry"] = shapely.buffer(marine.geometry.values, MARINE_BUFFER)

print("Dissolving marine areas")
marine["group"] = 1
marine = dissolve(marine, by="group").explode(ignore_index=True)


### Add coastal status to existing HUC8 dataset
huc8s = gp.read_feather(data_dir / "boundaries/huc8.feather").drop(
    columns=["coastal"], errors="ignore"
)

tree = shapely.STRtree(huc8s.geometry.values)
ix = huc8s.index.take(
    tree.query(marine.geometry.values, predicate="intersects")[1]
).unique()
huc8s["coastal"] = huc8s.index.isin(ix)

huc8s.to_feather(data_dir / "boundaries/huc8.feather")
