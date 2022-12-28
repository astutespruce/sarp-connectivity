from pathlib import Path

from pyarrow.dataset import dataset

from api.logger import log


data_dir = Path("data/api")


try:
    dams = dataset(data_dir / "dams.feather", format="feather")
    small_barriers = dataset(data_dir / "small_barriers.feather", format="feather")
    removed_dams = dataset(data_dir / "removed_dams.feather", format="feather")
    road_crossings = dataset(data_dir / "road_crossings.feather", format="feather")

    units = dataset(data_dir / "unit_bounds.feather", format="feather")

except Exception as e:
    print("ERROR: not able to load data")
    log.error(e)
