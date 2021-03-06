from pathlib import Path

import pandas as pd

from api.logger import log


data_dir = Path("data/api")


### Read source data into memory
# we can do this because data do not consume much memory

try:
    dams = pd.read_feather(data_dir / "dams.feather").set_index(["id"])
    dams_with_networks = dams.loc[dams.HasNetwork]

    barriers = pd.read_feather(data_dir / "small_barriers.feather").set_index(["id"])
    barriers_with_networks = barriers.loc[barriers.HasNetwork]

    print("Data loaded")

except Exception as e:
    print("ERROR: not able to load data")
    log.error(e)


# on demand instead of in-memory
def get_removed_dams():
    return pd.read_feather(data_dir / "removed_dams.feather")