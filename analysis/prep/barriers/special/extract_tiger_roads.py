from pathlib import Path

from pyogrio import read_dataframe


data_dir = Path("data")
src_dir = data_dir / "source"

tiger = read_dataframe(
    src_dir / "tlgdb_2020_a_us_roads.gdb",
    columns=["LINEARID", "RTTYP", "MTFCC", "SUFTYP"],
    where=""" "RTTYP" IS NOT NULL """,
    use_arrow=True,
)

tiger.to_feather(src_dir / "tiger_roads_2020.feather")
