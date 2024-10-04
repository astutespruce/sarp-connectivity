from pathlib import Path

from pyogrio import read_dataframe
import shapely

from analysis.constants import CRS


BUFFER_SIZE = 250

data_dir = Path("data")
src_dir = data_dir / "boundaries/source"
out_dir = data_dir / "boundaries"

df = (
    read_dataframe(
        src_dir / "S_USA.WildScenicRiver_LN/S_USA.WildScenicRiver_LN.shp", columns=["WSR_RIVER1"], use_arrow=True
    )
    .to_crs(CRS)
    .rename(columns={"WSR_RIVER1": "name"})
)

df["geometry"] = shapely.buffer(df.geometry.values, BUFFER_SIZE)

df.to_feather(out_dir / "wild_scenic_rivers.feather")
