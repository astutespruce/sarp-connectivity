import duckdb
from pyarrow.dataset import dataset

from api.logger import log
from api.settings import API_DATA_PATH


try:
    db = duckdb.connect(str(API_DATA_PATH / "api.db"), read_only=True)

    dams = dataset(API_DATA_PATH / "dams.feather", format="feather")
    small_barriers = dataset(API_DATA_PATH / "small_barriers.feather", format="feather")
    combined_barriers = dataset(API_DATA_PATH / "combined_barriers.feather", format="feather")
    largefish_barriers = dataset(API_DATA_PATH / "largefish_barriers.feather", format="feather")
    smallfish_barriers = dataset(API_DATA_PATH / "smallfish_barriers.feather", format="feather")
    road_crossings = dataset(API_DATA_PATH / "road_crossings.feather", format="feather")
    waterfalls = dataset(API_DATA_PATH / "waterfalls.feather", format="feather")

    barrier_datasets = {
        "dams": dams,
        "small_barriers": small_barriers,
        "combined_barriers": combined_barriers,
        "largefish_barriers": largefish_barriers,
        "smallfish_barriers": smallfish_barriers,
        "road_crossings": road_crossings,
        "waterfalls": waterfalls,
    }

    units = dataset(API_DATA_PATH / "map_units.feather", format="feather")

    # removed dams for public API; not used internally
    removed_dams = dataset(API_DATA_PATH / "removed_dams.feather", format="feather")

except Exception as e:
    print("ERROR: not able to load data")
    log.error(e)
