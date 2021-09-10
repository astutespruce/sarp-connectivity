import json

from pyogrio import read_dataframe

from analysis.constants import GEO_CRS

df = (
    read_dataframe("data/boundaries/region_boundary.gpkg")
    .to_crs(GEO_CRS)
    .set_index("id")
)

