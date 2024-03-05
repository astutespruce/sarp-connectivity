from pathlib import Path
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
from pyogrio import read_dataframe, write_dataframe
import shapely

from analysis.constants import CRS
from analysis.lib.geometry import dissolve
from analysis.lib.util import append

warnings.filterwarnings("ignore", message=".*organizePolygons.*")


data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"
working_dir = data_dir / "tnc_resilience"
out_dir = working_dir / "derived"
out_dir.mkdir(exist_ok=True)

huc2_df = pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"])
huc2s = huc2_df.HUC2.sort_values().values

################################################################################
### Extract TNC resilient watersheds and dissolve within HUC2s
################################################################################
df = read_dataframe(
    working_dir / "TNC_Freshwater_Resilience_Nov2023.gdb",
    layer="Scored_Units_HUC12FCN_Ver20230928_resultfields",
    columns=["HUC12", "Resil_Cl"],
    use_arrow=True,
    # extract above average watersheds based on guidance from Kat on 2/13/2024
    where=""" "Resil_Cl" in ('Slightly Above Average', 'Above Average', 'Far Above Average') """,
).to_crs(CRS)


# make valid
ix = ~shapely.is_valid(df.geometry.values)
df.loc[ix, "geometry"] = shapely.make_valid(df.loc[ix].geometry.values)

# aggregate to HUC2
df["HUC2"] = df.HUC12.str[:2]


df = dissolve(
    df.explode(ignore_index=True),
    by="HUC2",
    grid_size=1e-3,
).explode(ignore_index=True)


df.to_feather(working_dir / "tnc_resilient_watersheds.feather")
write_dataframe(df, working_dir / "tnc_resilient_watersheds.fgb")


################################################################################
### Extract raw flowlines that mostly overlap these watersheds
################################################################################

merged = None

for huc2 in huc2s:
    print(f"Processing {huc2}...")

    flowlines = gp.read_feather(nhd_dir / huc2 / "flowlines.feather", columns=["NHDPlusID", "geometry"]).set_index(
        "NHDPlusID"
    )
    tree = shapely.STRtree(flowlines.geometry.values)

    tmp = df.loc[df.HUC2 == huc2].reset_index(drop=True)
    left, right = tree.query(tmp.geometry.values, predicate="intersects")
    pairs = pd.DataFrame(
        {
            "huc_geom": tmp.geometry.values.take(left),
            "NHDPlusID": flowlines.index.values.take(right),
        }
    )

    if len(pairs) == 0:
        print(f"Skipping {huc2}, no overlap with TNC resilience")
        continue

    pairs = pairs.join(flowlines.geometry.rename("flowline"), on="NHDPlusID")

    shapely.prepare(pairs.huc_geom.values)
    contains = shapely.contains_properly(pairs.huc_geom.values, pairs.flowline.values)
    pairs["pct_overlap"] = np.float64(0)
    pairs.loc[contains, "pct_overlap"] = 100

    ix = ~contains
    intersection = shapely.intersection(pairs.loc[ix].flowline.values, pairs.loc[ix].huc_geom.values)
    pairs.loc[ix, "pct_overlap"] = 100 * shapely.length(intersection) / shapely.length(pairs.loc[ix].flowline.values)

    # aggregate up to flowline level
    overlap = pairs.groupby("NHDPlusID").pct_overlap.sum()

    # keep any that are >= 75% overlap
    keep_ids = overlap[overlap >= 75].index.values

    merged = append(
        merged,
        pd.DataFrame({"NHDPlusID": keep_ids, "resilient": [True] * len(keep_ids), "HUC2": [huc2] * len(keep_ids)}),
    )

merged.reset_index(drop=True).to_feather(out_dir / "tnc_resilient_flowlines.feather")
