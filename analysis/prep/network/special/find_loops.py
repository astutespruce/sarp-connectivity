from pathlib import Path
import pandas as pd

from analysis.lib.graph.speedups import DirectedGraph

data_dir = Path("data")

nhd_dir = data_dir / "nhd/raw"

huc2_df = pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"])
huc2s = huc2_df.HUC2.sort_values().values

# manually subset keys from above for processing
# huc2s = [
# "01",
# "02",
# "03",
# "04",
# "05",
# "06",
# "07",
# "08",
# "09",
# "10",
# "11",
# "12",
# "13",
# "14",
# "15",
# "16",
# "17",
# "18",
# "19",
# "21",
# ]


for huc2 in huc2s:
    print(f"Finding loops for {huc2}...")
    joins = pd.read_feather(
        nhd_dir / huc2 / "flowline_joins.feather",
        columns=["upstream", "downstream", "upstream_id", "downstream_id", "loop"],
    )

    # drop known loops
    joins = joins.loc[~joins.loop].drop(columns=["loop"])

    # drop terminals
    joins = joins.loc[(joins.upstream_id != 0) & (joins.downstream_id != 0)].copy()

    # make a directed graph of the raw network, facing upstream
    # NOTE: this uses NHDPlusIDs, not lineIDs
    g = DirectedGraph(
        joins.downstream.values.astype("int64"), joins.upstream.values.astype("int64")
    )

    origins = joins.loc[
        ~joins.downstream.isin(joins.upstream.unique())
    ].downstream.unique()

    # NOTE: these may not find the correct loop, but will find the problem so that
    # the correct loop can be identified manually.
    loops = g.find_loops(origins.astype("int64"))

    if loops:
        print(f"Potential loops: {(', ').join([str(l) for l in loops])}")
