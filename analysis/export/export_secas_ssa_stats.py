"""
Calculate statistics for the SECAS Species Status Landscape Assessment tool.

This is a one-off script; it is not part of a larger processing chain.
"""

from pathlib import Path

import geopandas as gp
import pandas as pd
from pyogrio import write_dataframe
import numpy as np
import shapely
from shapely import STRtree

from analysis.constants import SARP_STATES

METERS_TO_MILES = 0.000621371

data_dir = Path("data")
bnd_dir = data_dir / "boundaries"
api_dir = data_dir / "api"

out_dir = Path("../secas-ssa/source_data/sarp")

if not out_dir.exists():
    out_dir.mkdir(exist_ok=True, parents=False)


### Read states and HUC12s to determine which HUC12s are in scope
states = gp.read_feather(bnd_dir / "states.feather", columns=["geometry", "id"])
states = states.loc[states.id.isin(SARP_STATES)]
huc12 = gp.read_feather(bnd_dir / "huc12.feather", columns=["geometry", "HUC12"])

# derive SECAS boundary from union of selected states
secas_bnd = shapely.get_parts(shapely.coverage_union_all(states.geometry.values))
tree = STRtree(huc12.geometry.values)
ix = tree.query(secas_bnd, predicate="intersects")[1]
huc12 = huc12.take(np.unique(ix))

### Read dams
dams = pd.read_feather(
    data_dir / "barriers/master/dams.feather",
    columns=["id", "HUC12", "removed"],
)
# drop removed dams
dams = dams.loc[(~dams.removed) & (dams.HUC12.isin(huc12.HUC12))].drop(columns=["removed"])

### Read road crossings
# NOTE: we use the raw crossings data because we don't want them deduplicated
# by dams / inventoried barriers
crossings = pd.read_feather(data_dir / "barriers/source/road_crossings.feather", columns=["id", "HUC12"])
crossings = crossings.loc[crossings.HUC12.isin(huc12.HUC12)].reset_index(drop=True)

### Calculate counts by HUC12
df = (
    huc12.set_index("HUC12")
    .join(dams.groupby("HUC12").size().rename("dams"))
    .join(crossings.groupby("HUC12").size().rename("crossings"))
)
df[["dams", "crossings"]] = df[["dams", "crossings"]].fillna(0).astype("uint")


### Calculate percent altered by HUC12
huc2s = sorted(huc12.HUC12.str[:2].unique())
huc4s = sorted(huc12.HUC12.str[:4].unique())

merged = None
for huc2 in huc2s:
    print(f"Processing altered stats for {huc2}")

    flowlines = gp.read_feather(
        data_dir / f"nhd/clean/{huc2}/flowlines.feather",
        columns=["geometry", "lineID", "altered", "HUC4"],
    )
    flowlines = flowlines.loc[flowlines.HUC4.isin(huc4s)].reset_index(drop=True)
    huc12s_in_huc2 = huc12.loc[huc12.HUC12.str[:2] == huc2]

    tree = STRtree(flowlines.geometry.values)
    left, right = tree.query(huc12s_in_huc2.geometry.values, predicate="intersects")
    pairs = pd.DataFrame(
        {
            "HUC12": huc12s_in_huc2.HUC12.values.take(left),
            "HUC12_geom": huc12s_in_huc2.geometry.values.take(left),
            "lineID": flowlines.lineID.values.take(right),
            "flowline": flowlines.geometry.values.take(right),
            "altered": flowlines.altered.values.take(right),
        }
    )

    shapely.prepare(pairs.HUC12_geom.values)
    pairs["contained"] = shapely.contains_properly(pairs.HUC12_geom.values, pairs.flowline.values)

    # clip any that are not totally contained in HUC12
    tmp = pairs.loc[~pairs.contained]
    pairs.loc[~pairs.contained, "flowline"] = shapely.intersection(tmp.flowline.values, tmp.HUC12_geom.values)

    # calculate length in miles
    pairs["miles"] = shapely.length(pairs.flowline) * METERS_TO_MILES

    # drop any that don't have any length
    pairs = pairs.loc[pairs.miles > 0].drop(columns=["HUC12_geom", "contained", "lineID"])

    # calculate statistics by HUC12
    flowline_stats = (
        pd.DataFrame(pairs.groupby("HUC12").miles.sum().rename("total_miles"))
        .join(pairs.loc[pairs.altered].groupby("HUC12").miles.sum().rename("altered_miles"))
        .fillna(0)
        .reset_index()
    )

    flowline_stats["pct_altered"] = 100 * flowline_stats.altered_miles / flowline_stats.total_miles

    if merged is None:
        merged = flowline_stats
    else:
        merged = pd.concat([merged, flowline_stats], ignore_index=True)


flowline_stats = merged.reset_index(drop=True).set_index("HUC12")


df = df.join(flowline_stats)
df[["altered_miles", "total_miles", "pct_altered"]] = df[["altered_miles", "total_miles", "pct_altered"]].fillna(0)

df = df.reset_index()
df.to_feather(out_dir / "huc12_stats.feather")

# DEBUG:
write_dataframe(df, "/tmp/huc12_stats.fgb")
