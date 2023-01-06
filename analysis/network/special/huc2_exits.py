from pathlib import Path

import pandas as pd
import shapely
import geopandas as gp
from pyogrio import write_dataframe

from analysis.lib.geometry import explode

network_dir = Path("data/networks/raw")
out_dir = Path("/tmp")

huc2_bnd = gp.read_feather("data/boundaries/huc2.feather")
huc2_bnd = explode(huc2_bnd)

huc2 = "18"
joins = pd.read_feather(network_dir / huc2 / "flowline_joins.feather")
terminal_ids = joins.loc[joins.type == "terminal"].upstream_id.unique()
marine_ids = joins.loc[joins.marine].upstream_id.unique()

flowlines = gp.read_feather(
    network_dir / huc2 / "flowlines.feather",
    columns=["lineID", "StreamOrder", "geometry", "TerminalID"],
)

# export marine terminals
if len(marine_ids):
    write_dataframe(
        flowlines.loc[flowlines.lineID.isin(marine_ids)],
        out_dir / f"region{huc2}_marine_flowlines.fgb",
    )

# only keep the major rivers
flowlines = flowlines.loc[flowlines.StreamOrder > 5].copy()
write_dataframe(flowlines, out_dir / f"region{huc2}_major_flowlines.fgb")


# select the terminals
flowlines = flowlines.loc[flowlines.lineID.isin(terminal_ids)].copy()

write_dataframe(flowlines, out_dir / f"region{huc2}_flowline_terminals.fgb")

tree = shapely.STRtree(flowlines.geometry.values.data)

# extract linear rings
# huc2_bnd.geometry = shapely.get_exterior_ring(huc2_bnd.geometry.values.data)
left, right = tree.query(huc2_bnd.geometry.values.data, predicate="intersects")

df = pd.DataFrame(
    {
        "HUC2": huc2_bnd.HUC2.values.take(left),
        "lineID": flowlines.lineID.values.take(right),
    }
)

df = df.loc[df.HUC2 != huc2]

print(df)
