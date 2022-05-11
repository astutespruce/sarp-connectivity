from pathlib import Path

import pyarrow.dataset as pa
from pyarrow.feather import read_table
import pandas as pd

from api.logger import log


data_dir = Path("data/api")


### Read source data into memory
# we can do this because data do not consume much memory

try:
    dams = read_table(data_dir / "dams.feather")
    ranked_dams = dams.filter(dams["Ranked"])

    barriers = read_table(data_dir / "small_barriers.feather")
    ranked_barriers = barriers.filter(barriers["Ranked"])

    print(
        f"Loaded {len(dams):,} dams ({len(ranked_dams):,} ranked), {len(barriers):,} barriers ({len(ranked_barriers):,} ranked) "
    )

    units = pa.dataset(data_dir / "unit_bounds.feather", format="feather")

except Exception as e:
    print("ERROR: not able to load data")
    log.error(e)


# on demand instead of in-memory
def get_removed_dams():
    return read_table(data_dir / "removed_dams.feather")
