from pathlib import Path
import pandas as pd

from analysis.lib.graph.speedups import DirectedGraph

data_dir = Path("data")

nhd_dir = data_dir / "nhd/raw"

huc2_df = pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"])
huc2s = huc2_df.HUC2.sort_values().values

# manually subset keys from above for processing
# huc2s = [
#     "01",
#     "02",
#     "03",
#     "04",
#     "05",
#     "06",
#     "07",
#     "08",
#     "09",
#     "10",
#     "11",
#     "12",
#     "13",
#     "14",
#     "15",
#     "16",
#     "17",
#     "18",
#     "19",
#     "20",
#     "21",
# ]


for huc2 in huc2s:
    print(f"Finding bad joins for {huc2}...")
    joins = pd.read_feather(
        nhd_dir / huc2 / "flowline_joins.feather",
        columns=["upstream", "downstream", "upstream_id", "downstream_id", "type"],
    )

    # find any joins  where there was not a flowline in the region
    missing_downstream = joins.loc[(joins.downstream != 0) & (joins.downstream_id == 0) & (joins["type"] == "internal")]

    if len(missing_downstream):
        print("The following joins have missing downstream flowlines; they may be bogus joins:")
        print(missing_downstream)

    missing_upstream = joins.loc[(joins.upstream != 0) & (joins.upstream_id == 0) & (joins["type"] == "internal")]

    if len(missing_upstream):
        print("The following joins have missing missing_upstream flowlines; they may be bogus joins:")
        print(missing_upstream)
