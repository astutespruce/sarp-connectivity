from pathlib import Path
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
from pyogrio import read_dataframe, write_dataframe
import shapely

from analysis.constants import CRS
from analysis.lib.geometry import dissolve, make_valid
from analysis.lib.util import append

warnings.filterwarnings("ignore", message=".*organizePolygons.*")


data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"
working_dir = data_dir / "tnc_resilience"
out_dir = working_dir / "derived"
out_dir.mkdir(exist_ok=True)

huc2_df = gp.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2", "geometry"])
huc2s = huc2_df.HUC2.sort_values().values

################################################################################
### Extract TNC resilient watersheds and dissolve within HUC2s
################################################################################
res_df = read_dataframe(
    working_dir / "TNC_Freshwater_Resilience_Nov2023.gdb",
    layer="Scored_Units_HUC12FCN_Ver20230928_resultfields",
    columns=["HUC12", "Resil_Cl"],
    use_arrow=True,
    # extract above average watersheds based on guidance from Kat on 2/13/2024
    where=""" "Resil_Cl" in ('Slightly Above Average', 'Above Average', 'Far Above Average') """,
).to_crs(CRS)

res_df["geometry"] = make_valid(res_df.geometry.values)

# aggregate to HUC2
res_df["HUC2"] = res_df.HUC12.str[:2]
res_df = dissolve(
    res_df.explode(ignore_index=True),
    by="HUC2",
    grid_size=1e-3,
).explode(ignore_index=True)


res_df.to_feather(working_dir / "tnc_resilient_watersheds.feather")
write_dataframe(res_df, working_dir / "tnc_resilient_watersheds.fgb")

################################################################################
### Extract TNC cold water watersheds and dissolve within HUC2s
################################################################################
temp_df = read_dataframe(
    working_dir / "FCN_wTemperatureScore.gdb",
    layer="River_FCN_Watersheds_Ver20230928_wTempScore",
    columns=["cTempZCl"],
    use_arrow=True,
    # extract above average watersheds based on guidance from Kat on 2/4/2025
    # limit these to above above average based on guidance from Kat on 2/26/2025
    where=""" "cTempZCl" in ('Above Average', 'Far Above Average') """,
).to_crs(CRS)

temp_df["geometry"] = make_valid(temp_df.geometry.values)
temp_df = temp_df.explode(ignore_index=True)

# join to HUC2 boundaries based on the representative points because the TNC
# boundaries are rasterized and do not exactly match the HUC2 boundaries
left, right = shapely.STRtree(shapely.point_on_surface(temp_df.geometry.values)).query(
    huc2_df.geometry.values, predicate="intersects"
)
temp_df = temp_df.join(pd.Series(huc2_df.HUC2.values.take(left), name="HUC2", index=temp_df.index.values.take(right)))

temp_df = dissolve(temp_df[["HUC2", "geometry"]].explode(ignore_index=True), by="HUC2").explode(ignore_index=True)

temp_df.to_feather(working_dir / "tnc_coldwater_refugia_watersheds.feather")
write_dataframe(temp_df, working_dir / "tnc_coldwater_refugia_watersheds.fgb")


################################################################################
### Extract raw flowlines that mostly overlap these watersheds
################################################################################

merged_res = None
merged_temp = None

for huc2 in huc2s:
    print(f"Processing {huc2}...")

    flowlines = gp.read_feather(nhd_dir / huc2 / "flowlines.feather", columns=["NHDPlusID", "geometry"]).set_index(
        "NHDPlusID"
    )
    tree = shapely.STRtree(flowlines.geometry.values)

    huc2_res = res_df.loc[res_df.HUC2 == huc2].reset_index(drop=True)
    left, right = tree.query(huc2_res.geometry.values, predicate="intersects")

    if len(left):
        pairs = pd.DataFrame(
            {
                "huc_geom": huc2_res.geometry.values.take(left),
                "NHDPlusID": flowlines.index.values.take(right),
                "flowline": flowlines.geometry.values.take(right),
            }
        )

        shapely.prepare(pairs.huc_geom.values)
        contains = shapely.contains_properly(pairs.huc_geom.values, pairs.flowline.values)
        pairs["pct_overlap"] = np.float64(0)
        pairs.loc[contains, "pct_overlap"] = 100

        ix = ~contains
        intersection = shapely.intersection(pairs.loc[ix].flowline.values, pairs.loc[ix].huc_geom.values)
        pairs.loc[ix, "pct_overlap"] = (
            100 * shapely.length(intersection) / shapely.length(pairs.loc[ix].flowline.values)
        )

        # aggregate up to flowline level
        overlap = pairs.groupby("NHDPlusID").pct_overlap.sum()

        # keep any that are >= 75% overlap
        keep_ids = overlap[overlap >= 75].index.values
        merged_res = append(
            merged_res,
            pd.DataFrame({"NHDPlusID": keep_ids, "HUC2": [huc2] * len(keep_ids)}),
        )

    huc2_temp = temp_df.loc[temp_df.HUC2 == huc2].reset_index(drop=True)
    left, right = tree.query(huc2_temp.geometry.values, predicate="intersects")
    if len(left):
        pairs = pd.DataFrame(
            {
                "huc_geom": huc2_temp.geometry.values.take(left),
                "NHDPlusID": flowlines.index.values.take(right),
                "flowline": flowlines.geometry.values.take(right),
            }
        )

        shapely.prepare(pairs.huc_geom.values)
        contains = shapely.contains_properly(pairs.huc_geom.values, pairs.flowline.values)
        pairs["pct_overlap"] = np.float64(0)
        pairs.loc[contains, "pct_overlap"] = 100

        ix = ~contains
        intersection = shapely.intersection(pairs.loc[ix].flowline.values, pairs.loc[ix].huc_geom.values)
        pairs.loc[ix, "pct_overlap"] = (
            100 * shapely.length(intersection) / shapely.length(pairs.loc[ix].flowline.values)
        )

        # aggregate up to flowline level
        overlap = pairs.groupby("NHDPlusID").pct_overlap.sum()

        # keep any that are >= 75% overlap
        keep_ids = overlap[overlap >= 75].index.values
        merged_temp = append(
            merged_temp,
            pd.DataFrame({"NHDPlusID": keep_ids, "HUC2": [huc2] * len(keep_ids)}),
        )


df = pd.concat([merged_res[["NHDPlusID", "HUC2"]], merged_temp[["NHDPlusID", "HUC2"]]]).drop_duplicates()
df["resilient"] = df.NHDPlusID.isin(merged_res.NHDPlusID.values)
df["cold"] = df.NHDPlusID.isin(merged_temp.NHDPlusID.values)
df.to_feather(out_dir / "tnc_resilient_flowlines.feather")
