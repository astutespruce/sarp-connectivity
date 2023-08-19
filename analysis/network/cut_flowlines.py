from pathlib import Path
import os
from time import time
import warnings

import geopandas as gp
import numpy as np
import pandas as pd

from analysis.lib.io import read_feathers
from analysis.lib.flowlines import cut_flowlines_at_barriers
from analysis.constants import CRS

warnings.simplefilter("always")  # show geometry related warnings every time


data_dir = Path("data")
barriers_dir = data_dir / "barriers/snapped"
nhd_dir = data_dir / "nhd/clean"
out_dir = data_dir / "networks/raw"

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


start = time()

### Aggregate barriers
# NOTE: any barriers on loops or off-network flowlines have already been removed
# from the snapped barrier data.  All barriers in this dataset cut the raw
# networks, but subsets of them are used to create different network scenarios
print("Aggregating barriers")
kinds = ["waterfall", "dam", "small_barrier", "road_crossing"]
barriers = read_feathers(
    [barriers_dir / f"{kind}s.feather" for kind in kinds],
    geo=True,
    new_fields={"kind": kinds},
).set_index("id", drop=False)


# removed is not applicable for road crossings or waterfalls, backfill with False
barriers["removed"] = barriers.removed.fillna(False)
barriers["YearRemoved"] = barriers.YearRemoved.fillna(0).astype("uint16")

print(f"Serializing {len(barriers):,} barriers")
barriers.to_feather(out_dir / "all_barriers.feather")


### Cut flowlines in each HUC2
for huc2 in huc2s:
    region_start = time()
    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2

    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    huc2_barriers = barriers.loc[(barriers.HUC2 == huc2)]

    ##################### Cut flowlines at barriers #################
    ### Read NHD flowlines and joins
    print("Reading flowlines...")
    flowline_start = time()

    flowlines = (
        gp.read_feather(nhd_dir / huc2 / "flowlines.feather").set_index(
            "lineID", drop=False
        )
        # TEMP: explicitly set the CRS for latest version of PROJ
        .set_crs(CRS)
    )
    print(f"Read {len(flowlines):,} flowlines in {time() - flowline_start:.2f}s")

    # increment lineIDs before dropping loops
    next_segment_id = flowlines.lineID.max() + np.uint32(1)

    joins = pd.read_feather(
        nhd_dir / huc2 / "flowline_joins.feather",
        columns=[
            "upstream",
            "downstream",
            "upstream_id",
            "downstream_id",
            "type",
            "marine",
            "great_lakes",
            "loop",
        ],
    )

    # drop all loops from the analysis
    print(f"Dropping {flowlines.loop .sum():,} loops")
    flowlines = flowlines.loc[~(flowlines.loop | flowlines.offnetwork)].drop(
        columns=["loop"]
    )
    # NOTE: off-network flowlines don't have joins, so they don't need to be removed here
    joins = joins.loc[~joins.loop].drop(columns=["loop"])

    flowlines, joins, barrier_joins = cut_flowlines_at_barriers(
        flowlines, joins, huc2_barriers, next_segment_id=next_segment_id
    )

    barrier_joins = barrier_joins.join(huc2_barriers.kind)

    print(f"Serializing {len(flowlines):,} cut flowlines...")

    flowlines = flowlines.reset_index(drop=True)
    flowlines.to_feather(huc2_dir / "flowlines.feather")

    joins.reset_index(drop=True).to_feather(huc2_dir / "flowline_joins.feather")
    barrier_joins.reset_index(drop=True).to_feather(
        huc2_dir / "barrier_joins.feather",
    )

    print(f"Region done in {time() - region_start:.2f}s\n\n")

print("All done in {:.2f}s".format(time() - start))
