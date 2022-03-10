import os
from pathlib import Path
from time import time

import geopandas as gp
import pandas as pd
import pygeos as pg
from pyogrio import write_dataframe

from analysis.constants import STATES
from analysis.export.lib.drains import find_dam_faces
from analysis.lib.util import append
from analysis.lib.io import read_feathers

data_dir = Path("data")
nhd_dir = data_dir / "nhd/clean"
out_dir = data_dir / "barriers/estimated"
tmp_dir = Path("/tmp/sarp")

if not out_dir.exists():
    os.makedirs(out_dir)

if not tmp_dir.exists():
    os.makedirs(tmp_dir)


start = time()

huc2_df = pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"])
huc2s = huc2_df.HUC2.sort_values().values

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
            "StreamOrder": "fsorder",
            "km2": "wb_km2",
            "flowlineLength": "flength",
        }
    )
    .set_index("drainID")
)

drains["intermittent"] = drains.lineFCode.isin([46003, 46007])


merged = None
for huc2 in huc2s:
    huc2_start = time()
    print(f"Extracting dams from waterbodies in {huc2}")
    waterbodies = gp.read_feather(nhd_dir / huc2 / "waterbodies.feather").set_index(
        "wbID"
    )

    df = find_dam_faces(drains.loc[drains.HUC2 == huc2], waterbodies)
    merged = append(merged, df)

    print(f"Found {len(df):,} estimated dams in {time() - huc2_start:,.2f}s")

df = merged.reset_index(drop=True)

dams = gp.read_feather(data_dir / "barriers/master/dams.feather")
# drop any that were previously estimated
dams = dams.loc[
    dams.wbID.notnull() & (~dams.Source.isin(["Estimated Dams OCT 2021"]))
].copy()

has_dam = df.wbID.isin(dams.wbID.unique())

states = gp.read_feather("data/boundaries/states.feather", columns=["id", "geometry"])
tree = pg.STRtree(df.geometry.values.data)
left, right = tree.query_bulk(states.geometry.values.data, predicate="intersects")

state_join = (
    pd.DataFrame({"state": states.id.take(left), "drain": df.index.take(right)})
    .groupby("drain")
    .first()
)

df = df.join(state_join)

# only keep those in the region states
df = df.loc[df.state.isin(STATES)].copy()

write_dataframe(df.loc[~has_dam], out_dir / "estimated_dam_lines.fgb")
write_dataframe(df.loc[~has_dam], tmp_dir / "estimated_dam_lines.shp")

write_dataframe(df.loc[has_dam], out_dir / "estimated_dam_lines_with_dam.fgb")
write_dataframe(df.loc[has_dam], tmp_dir / "estimated_dam_lines_with_dam.shp")


df = (
    df.join(drains.geometry.rename("drain"), on="drainID")
    .set_geometry("drain")
    .drop(columns=["geometry"])
)
write_dataframe(df.loc[~has_dam], out_dir / "estimated_dams.fgb")
write_dataframe(df.loc[~has_dam], tmp_dir / "estimated_dams.shp")

write_dataframe(df.loc[has_dam], out_dir / "estimated_dams_with_dam.fgb")
write_dataframe(df.loc[has_dam], tmp_dir / "estimated_dams_with_dam.shp")


print(f"Total elapsed {time() - start:,.2f}s")
