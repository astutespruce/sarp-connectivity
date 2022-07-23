from pathlib import Path
import os
from time import time
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
from pyogrio import write_dataframe

from analysis.lib.io import read_feathers
from analysis.lib.flowlines import cut_flowlines_at_barriers

warnings.simplefilter("always")  # show geometry related warnings every time
warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


DEBUG = False

# ID ranges for each type
WATERFALLS_ID = 1e6
DAMS_ID = 2 * 1e6
SB_ID = 3 * 1e6
CROSSINGS_ID = 4 * 1e6

data_dir = Path("data")
barriers_dir = data_dir / "barriers/snapped"
nhd_dir = data_dir / "nhd/clean"
out_dir = data_dir / "networks/raw"

huc2_df = pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"])
huc2s = huc2_df.HUC2.sort_values().values

# manually subset keys from above for processing
# huc2s = [
# "02",
# "03",
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
# "18"
# "21",
# ]


start = time()

### Aggregate barriers
kinds = ["waterfall", "dam", "small_barrier", "road_crossing"]
kind_ids = [WATERFALLS_ID, DAMS_ID, SB_ID, CROSSINGS_ID]

barriers = read_feathers(
    [barriers_dir / f"{kind}s.feather" for kind in kinds],
    geo=True,
    new_fields={"kind": kinds},
)

barriers["barrierID"] = np.uint64(0)

for kind, init_id in zip(kinds, kind_ids):
    ix = barriers.kind == kind
    barriers.loc[ix, "barrierID"] = barriers.loc[ix].id + init_id

print(f"Serializing {len(barriers):,} barriers")
barriers.to_feather(out_dir / "all_barriers.feather")


### Cut flowlines in each HUC2
for huc2 in huc2s:
    region_start = time()
    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2

    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    # drop any barriers on loops in this region
    huc2_barriers = barriers.loc[(barriers.HUC2 == huc2) & (~barriers.loop)].set_index(
        "barrierID", drop=False
    )

    ##################### Cut flowlines at barriers #################
    ### Read NHD flowlines and joins
    print("Reading flowlines...")
    flowline_start = time()
    flowlines = gp.read_feather(nhd_dir / huc2 / "flowlines.feather").set_index(
        "lineID", drop=False
    )
    print(f"Read {len(flowlines):,} flowlines in {time() - flowline_start:.2f}s")

    # increment lineIDs before dropping loops
    next_segment_id = flowlines.lineID.max() + np.uint32(1)

    joins = pd.read_feather(nhd_dir / huc2 / "flowline_joins.feather")

    # drop all loops from the analysis
    print(f"Dropping {flowlines.loop .sum():,} loops")
    flowlines = flowlines.loc[~flowlines.loop].drop(columns=["loop"])
    joins = joins.loc[~joins.loop].drop(columns=["loop"])

    flowlines, joins, barrier_joins = cut_flowlines_at_barriers(
        flowlines, joins, huc2_barriers, next_segment_id=next_segment_id
    )

    barrier_joins = barrier_joins.join(huc2_barriers.kind)

    print(f"Serializing {len(flowlines):,} cut flowlines...")

    flowlines = flowlines.reset_index(drop=True)
    flowlines.to_feather(huc2_dir / "flowlines.feather")
    if DEBUG:
        write_dataframe(flowlines, huc2_dir / "flowlines.gpkg")

    joins.reset_index(drop=True).to_feather(huc2_dir / "flowline_joins.feather")
    barrier_joins.reset_index(drop=True).to_feather(
        huc2_dir / "barrier_joins.feather",
    )

    print(f"Region done in {time() - region_start:.2f}s\n\n")

print("All done in {:.2f}s".format(time() - start))
