from pathlib import Path

import geopandas as gp
import numpy as np
from pyogrio import read_dataframe, write_dataframe
import shapely

from analysis.constants import CRS, SALMONID_ESU_LAYER_TO_CODE
from analysis.lib.geometry import dissolve


data_dir = Path("data")
bnd_dir = data_dir / "boundaries"
src_dir = data_dir / "species/source"
salmonid_esu_gdb = src_dir / "ESU_DPS_CA_WA_OR_ID.gdb"

# the HUC12s listed in the US dataset do not match the master HUC12 dataset
# (both boundaries and codes don't always match).
# We have to do a spatial join instead and find HUC12s with >= 5% overlap

huc12 = gp.read_feather(bnd_dir / "huc12.feather", columns=["HUC12", "geometry"])
tree = shapely.STRtree(huc12.geometry.values)

for layer in SALMONID_ESU_LAYER_TO_CODE.keys():
    print(f"Processing {layer}")
    df = read_dataframe(salmonid_esu_gdb, layer=layer, columns=[]).to_crs(CRS)

    df["group"] = 0

    df = dissolve(df.explode(ignore_index=True), by="group")
    if not shapely.is_valid(df.geometry.values).all():
        raise ValueError(f"Invalid geometry found for {layer}")

    bnd = df.geometry.values[0]
    shapely.prepare(bnd)
    ix = np.sort(np.unique(tree.query(bnd, predicate="intersects")))

    tmp = huc12.take(ix)
    tmp["overlap"] = 0
    contains = shapely.contains_properly(bnd, tmp.geometry.values)
    tmp.loc[contains, "overlap"] = 1.0
    tmp.loc[~contains, "overlap"] = shapely.area(
        shapely.intersection(bnd, tmp.loc[~contains].geometry.values)
    ) / shapely.area(tmp.loc[~contains].geometry.values)

    # keep anything with > 10% overlap
    huc12s = tmp.loc[tmp.overlap >= 0.1].HUC12
    huc12[layer] = huc12.HUC12.isin(huc12s)


# only keep HUC12s that had values present
esu_cols = list(SALMONID_ESU_LAYER_TO_CODE.keys())
esu_codes = np.array(list(SALMONID_ESU_LAYER_TO_CODE.values()))

huc12 = huc12.loc[huc12[esu_cols].sum(axis=1) > 0].reset_index(drop=True)

# extract comma-delimited list of ESU codes
huc12["salmonid_esu"] = huc12[esu_cols].apply(
    lambda row: ",".join(str(x) for x in esu_codes[row.values]), axis=1
)
huc12["salmonid_esu_count"] = huc12[esu_cols].sum(axis=1)


huc12.drop(columns=["geometry"]).to_feather(src_dir / "salmonid_esu.feather")
write_dataframe(huc12, src_dir / "salmonid_esu.fgb")
