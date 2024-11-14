from pathlib import Path

import geopandas as gp
import pandas as pd
from pyogrio import read_dataframe
import shapely


from analysis.constants import CRS

data_dir = Path("data")
working_dir = data_dir / "lagos"

huc2 = gp.read_feather(data_dir / "boundaries/huc2.feather", columns=["geometry", "HUC2"])

df = read_dataframe(
    working_dir / "LAGOS_US_RESERVOIR.gpkg",
    columns=["lake_reservoir_lake_rsvr_model_class"],
    where=""" "lake_reservoir_lake_rsvr_model_class" = 'RSVR' """,
    use_arrow=True,
).to_crs(CRS)


shapely.prepare(df.geometry.values)
df["rep_pt"] = shapely.centroid(df.geometry.values)
ix = ~shapely.contains_properly(df.geometry.values, df.rep_pt.values)
df.loc[ix, "rep_pt"] = shapely.point_on_surface(df.loc[ix].geometry.values)

df = gp.GeoDataFrame(geometry=df.rep_pt.values, crs=CRS)

tree = shapely.STRtree(df.geometry.values)
left, right = tree.query(huc2.geometry.values, predicate="intersects")
huc2_join = pd.Series(huc2.HUC2.values.take(left), index=df.index.values.take(right), name="HUC2")

df = df.join(huc2_join)

df.to_feather(working_dir / "lagos_reservoir_pt.feather")
