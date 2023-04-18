from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
from pyogrio import read_dataframe
import shapely

from analysis.constants import CRS
from analysis.lib.geometry import dissolve
from analysis.lib.io import read_feathers


data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"  # intentionally use raw flowlines
src_dir = data_dir / "states/mn"
huc2s = ["04", "07", "09", "10"]


huc2_df = gp.read_feather(data_dir / "boundaries/huc2.feather")
huc2_df = huc2_df.loc[huc2_df.HUC2.isin(huc2s)].copy()

print("Reading flowlines...")
flowlines = read_feathers(
    [nhd_dir / huc2 / "flowlines.feather" for huc2 in huc2s], columns=[], geo=True
)
tree = shapely.STRtree(flowlines.geometry.values.data)


# bring in Great Lakes
print("Reading lakes")
nhd = gp.read_feather(
    nhd_dir / "04/waterbodies.feather", columns=["geometry", "GNIS_Name"]
)
nhd = nhd.loc[nhd.GNIS_Name == "Lake Superior"].reset_index(drop=True)


# Read MN waterbodies
df = read_dataframe(
    src_dir / "water_dnr_hydrography.gpkg", columns=["wb_class", "pw_basin_n"]
).to_crs(CRS)

# drop non-waterbodies and Great Lakes / Lake of the Woods
df = df.loc[
    ~(
        df.wb_class.isin(
            [
                "Drained Lakebed",
                "Drained Wetland",
                "Intermittent Water",
                "Innundation Area",
                "Island or Land",
                "Riverine island",
                "Riverine polygon",
                "Wetland",
            ]
        )
        | df.pw_basin_n.isin(
            [
                "Superior",
                "Superior (WI, MI)",
                "Lake of the Woods (Fourmile Bay)",
                "Lake of the Woods (Main)",
                "Lake of the Woods (Canada)",
                "Lake of the Woods (MN)",
            ]
        )
    )
]

print(f"Extracted {len(df):,} MN waterbodies")

left, right = tree.query(df.geometry.values.data, predicate="intersects")
df = df.iloc[np.unique(left)].reset_index(drop=True)
print(f"Kept {len(df):,} that intersect flowlines")


# drop anything that touches Lake Superior
tree = shapely.STRtree(df.geometry.values)
right = tree.query(nhd.geometry.values, predicate="intersects")[1]
df = df.loc[~df.index.isin(df.index.values.take(right))].reset_index(drop=True)


# mark altered types
df["altered"] = df.wb_class.isin(
    [
        "Artificial Basin",
        "Mine Pit Lake",
        "Mine Pit Lake (NF)",
        "Mine or Gravel Pit",
        "Natural Ore Mine",
        "P. Drained Lakebed",
        "P. Drained Wetland",
        "Reservoir",
        "Sewage/Filtration Pd",
        "Tailings Pond",
    ]
)


### Dissolve waterbodies
print("Dissolving adjacent waterbodies...")

# dissolve by altered status first
df = (
    dissolve(df.explode(ignore_index=True), by=["altered"])
    .explode(ignore_index=True)
    .reset_index(drop=True)
)

# dissolve contiguous
df["tmp"] = 1
wb = (
    dissolve(df, by="tmp")
    .drop(columns=["tmp"])
    .explode(ignore_index=True)
    .reset_index(drop=True)
)
df = df.drop(columns=["tmp"])

# mark any that are more than 50% altered as altered
altered = df.loc[df.altered]
tree = shapely.STRtree(altered.geometry.values.data)
left, right = tree.query(wb.geometry.values.data, predicate="intersects")
intersection = shapely.area(
    shapely.intersection(
        wb.geometry.values.data.take(left), altered.geometry.values.data.take(right)
    )
) / shapely.area(wb.geometry.values.data.take(left))
ix = wb.index.values.take(np.unique(left[intersection >= 0.5]))
wb["altered"] = False
wb.loc[ix, "altered"] = True


### Split out by HUC2
tree = shapely.STRtree(wb.geometry.values.data)

# confirmed by hand, there are no waterbodies that show up in multiple HUC2s
left, right = tree.query(huc2_df.geometry.values.data, predicate="intersects")

wb = wb.join(
    pd.DataFrame(
        {"HUC2": huc2_df.HUC2.values.take(left)}, index=wb.index.values.take(right)
    )
)

wb.to_feather(src_dir / "mn_waterbodies.feather")
