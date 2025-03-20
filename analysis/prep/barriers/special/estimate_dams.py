import os
from pathlib import Path
from time import time

import geopandas as gp
import numpy as np
import pandas as pd
import shapely
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
        [data_dir / "nhd/clean/" / huc2 / "waterbody_drain_points.feather" for huc2 in huc2s],
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
drains.loc[drains.AnnualVelocity < 0, "AnnualVelocity"] = np.nan


merged = None
for huc2 in huc2s:
    huc2_start = time()
    print(f"----- Processing {huc2} ------")
    waterbodies = gp.read_feather(nhd_dir / huc2 / "waterbodies.feather").set_index("wbID")

    df = find_dam_faces(drains.loc[drains.HUC2 == huc2], waterbodies)
    merged = append(merged, df)

    print(f"Found {len(df):,} estimated dams in {time() - huc2_start:,.2f}s")

df = merged.reset_index(drop=True)

dams = gp.read_feather(data_dir / "barriers/master/dams.feather")
# drop any that were previously estimated
dams = dams.loc[
    dams.wbID.notnull()
    & (
        ~dams.Source.isin(
            [
                "Estimated Dams OCT 2021",
                "ESTIMATED DAMS OCT 2021",
                "Estimated Dams Summer 2022",
                "Estimated Dams JAN 2023",
            ]
        )
    )
].copy()

has_dam = df.wbID.isin(dams.wbID.unique())

states = gp.read_feather("data/boundaries/states.feather", columns=["id", "geometry"])
tree = shapely.STRtree(df.geometry.values)
left, right = tree.query(states.geometry.values, predicate="intersects")

state_join = pd.DataFrame({"state": states.id.take(left), "drain": df.index.take(right)}).groupby("drain").first()

df = df.join(state_join)

# only keep those in the region states
df = df.loc[df.state.isin(STATES)].copy()

write_dataframe(df.loc[~has_dam], out_dir / "estimated_dam_lines.fgb")
write_dataframe(df.loc[has_dam], out_dir / "estimated_dam_lines_with_dam.fgb")


outfilename = tmp_dir / "estimated_dams.gdb"

write_dataframe(df.loc[~has_dam], outfilename, layer="estimated_dam_lines", driver="OpenFileGDB")
write_dataframe(df.loc[has_dam], outfilename, layer="estimated_dam_lines_with_dam", driver="OpenFileGDB", append=True)

df = df.join(drains.geometry.rename("drain"), on="drainID").set_geometry("drain").drop(columns=["geometry"])
write_dataframe(df.loc[~has_dam], out_dir / "estimated_dams.fgb")
write_dataframe(df.loc[has_dam], out_dir / "estimated_dams_with_dam.fgb")

write_dataframe(df.loc[~has_dam], outfilename, layer="estimated_dams", driver="OpenFileGDB", append=True)
write_dataframe(df.loc[has_dam], outfilename, layer="estimated_dams_with_dam", driver="OpenFileGDB", append=True)


### Find drain points of altered waterbodies that have no associated estimated dam
altered_wb_drains = drains.loc[
    drains.altered
    & ~drains.wbID.isin(df.wbID.unique())
    & ~drains.wbID.isin(dams.wbID.dropna().unique().astype("uint32"))
]

tree = shapely.STRtree(altered_wb_drains.geometry.values)
left, right = tree.query(states.geometry.values, predicate="intersects")

altered_wb_drains = altered_wb_drains.join(
    pd.DataFrame({"state": states.id.take(left), "drain": altered_wb_drains.index.take(right)}).groupby("drain").first()
)

write_dataframe(altered_wb_drains, out_dir / "altered_waterbodies_without_dams.fgb")
write_dataframe(
    altered_wb_drains, outfilename, layer="altered_waterbodies_without_dams", driver="OpenFileGDB", append=True
)


print(f"Total elapsed {time() - start:,.2f}s")


####################
