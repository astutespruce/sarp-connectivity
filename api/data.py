from pathlib import Path

from pyarrow.dataset import dataset

from api.logger import log


data_dir = Path("data/api")


try:
    dams = dataset(data_dir / "dams.feather", format="feather")
    small_barriers = dataset(data_dir / "small_barriers.feather", format="feather")
    combined_barriers = dataset(data_dir / "combined_barriers.feather", format="feather")
    largefish_barriers = dataset(data_dir / "largefish_barriers.feather", format="feather")
    smallfish_barriers = dataset(data_dir / "smallfish_barriers.feather", format="feather")

    road_crossings = dataset(data_dir / "road_crossings.feather", format="feather")
    waterfalls = dataset(data_dir / "waterfalls.feather", format="feather")

    search_barriers = dataset(data_dir / "search_barriers.feather", format="feather")

    units = dataset(data_dir / "map_units.feather", format="feather")

    # removed dams for public API; not used internally
    removed_dams = dataset(data_dir / "removed_dams.feather", format="feather")

except Exception as e:
    print("ERROR: not able to load data")
    log.error(e)
