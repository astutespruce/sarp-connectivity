from pathlib import Path

import duckdb
from pyarrow.dataset import dataset

from api.logger import log


data_dir = Path("data/api")

try:
    db = duckdb.connect(str(data_dir / "api.db"), read_only=True)

    dams = dataset(data_dir / "dams.feather", format="feather")
    small_barriers = dataset(data_dir / "small_barriers.feather", format="feather")
    combined_barriers = dataset(data_dir / "combined_barriers.feather", format="feather")
    largefish_barriers = dataset(data_dir / "largefish_barriers.feather", format="feather")
    smallfish_barriers = dataset(data_dir / "smallfish_barriers.feather", format="feather")
    road_crossings = dataset(data_dir / "road_crossings.feather", format="feather")
    waterfalls = dataset(data_dir / "waterfalls.feather", format="feather")

    barrier_datasets = {
        "dams": dams,
        "small_barriers": small_barriers,
        "combined_barriers": combined_barriers,
        "largefish_barriers": largefish_barriers,
        "smallfish_barriers": smallfish_barriers,
        "road_crossings": road_crossings,
        "waterfalls": waterfalls,
    }

    search_barriers = dataset(data_dir / "search_barriers.feather", format="feather")

    units = dataset(data_dir / "map_units.feather", format="feather")

    # removed dams for public API; not used internally
    removed_dams = dataset(data_dir / "removed_dams.feather", format="feather")

except Exception as e:
    print("ERROR: not able to load data")
    log.error(e)
