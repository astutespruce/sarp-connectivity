from pathlib import Path

import geopandas as gp
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from pyogrio import write_dataframe
import shapely

from analysis.constants import CRS
from analysis.lib.io import read_arrow_tables
from analysis.lib.geometry.lines import merge_lines

src_dir = Path("data/networks")
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True, parents=True)

scenario = "dams"  # "dams", "combined_barriers", "largefish_barriers", "smallfish_barriers"
ext = "fgb"

networks = pd.read_feather(src_dir / f"clean/removed/removed_{scenario}_networks.feather").set_index("id")
# drop downstream columns
drop_cols = [c for c in networks.columns if "Downstream" in c] + ["HUC2"]
networks = networks.drop(columns=drop_cols)

# use smaller data types for smaller output files
for col in [c for c in networks.columns if c.endswith("Miles")]:
    networks[col] = networks[col].round(3).astype("float32")

for col in [c for c in networks.columns if c.startswith("Percent")]:
    networks[col] = networks[col].fillna(0).astype("int8")

for col in ["flows_to_ocean", "flows_to_great_lakes", "invasive_network"]:
    if col in networks.columns:
        networks[col] = networks[col].astype("uint8")


segments = pd.read_feather(
    src_dir / f"clean/removed/removed_{scenario}_network_segments.feather", columns=["lineID", "HUC2", "barrier_id"]
)

huc2s = sorted(segments.HUC2.unique())
lineIDs = segments.lineID.unique()

flowlines = (
    read_arrow_tables(
        [src_dir / "raw" / huc2 / "flowlines.feather" for huc2 in huc2s],
        columns=[
            "lineID",
            "geometry",
            "intermittent",
            "altered",
            "sizeclass",
            "StreamOrder",
        ],
        filter=pc.is_in(pc.field("lineID"), pa.array(lineIDs)),
    )
    .to_pandas()
    .set_index("lineID")
    .rename(columns={"StreamOrder": "streamorder"})
)
flowlines["geometry"] = shapely.from_wkb(flowlines.geometry.values)

merged = merge_lines(
    gp.GeoDataFrame(segments.join(flowlines, on="lineID"), geometry="geometry", crs=CRS), by="barrier_id"
).join(networks, on="barrier_id")
write_dataframe(merged, out_dir / f"removed_{scenario}_networks.{ext}")
