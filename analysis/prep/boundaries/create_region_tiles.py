from pathlib import Path
import subprocess

import geopandas as gp
from pyogrio import write_dataframe

from analysis.constants import GEO_CRS

SUMMARY_UNITS = ["State", "COUNTYFIPS", "HUC6", "HUC8", "HUC12", "ECO3", "ECO4"]

tippecanoe_args = [
    "tippecanoe",
    "-f",
    "-P",
    "-pg",
    "--detect-shared-borders"
]


src_dir = Path("data/boundaries")
tile_dir = Path("data/tiles")
tmp_dir = Path("/tmp")


### Full analysis area and regions
print("Creating region tiles")
df = gp.read_feather(src_dir / "region_boundary.feather").to_crs(GEO_CRS)
json_filename = tmp_dir / "region_boundary.json"
write_dataframe(df, json_filename, driver="GeoJSONSeq")
mbtiles_filename = tile_dir / "boundary.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", "8"]
    + ["-l", "boundary"]
    + ["-o", f"{str(mbtiles_filename)}", str(json_filename)]
)
ret.check_returncode()
json_filename.unlink()


### Mask of full analysis area and regions
print("Creating mask tiles")
df = gp.read_feather(src_dir / "region_mask.feather").to_crs(GEO_CRS)
json_filename = tmp_dir / "region_mask.json"
write_dataframe(df, json_filename, driver="GeoJSONSeq")
mbtiles_filename = tile_dir / "mask.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", "8"]
    + ["-l", "mask"]
    + ["-o", f"{str(mbtiles_filename)}", str(json_filename)]
)
ret.check_returncode()
json_filename.unlink()


### States
print("Creating state tiles")
df = gp.read_feather(src_dir / "region_states.feather", columns=['geometry', 'id']).to_crs(GEO_CRS)
json_filename = tmp_dir / "region_states.json"
write_dataframe(df, json_filename, driver="GeoJSONSeq")
mbtiles_filename = tile_dir / "State.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", "8"]
    + ["-l", "State"]
    + ["-o", f"{str(mbtiles_filename)}", str(json_filename)]
)
ret.check_returncode()
json_filename.unlink()


### Counties
print("Creating county tiles")
df = gp.read_feather(src_dir / "region_counties.feather", columns=['geometry', 'id', 'name']).to_crs(GEO_CRS)
json_filename = tmp_dir / "region_counties.json"
write_dataframe(df, json_filename, driver="GeoJSONSeq")
mbtiles_filename = tile_dir / "County.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "3", "-z", "12"]
    + ["-l", "County"]
    + ["-o", f"{str(mbtiles_filename)}", str(json_filename)]
)
ret.check_returncode()
json_filename.unlink()


## HUC2
print("Creating HUC2 tiles")
df = gp.read_feather(src_dir / "HUC2.feather").rename(columns={'HUC2': 'id'}).to_crs(GEO_CRS)
json_filename = tmp_dir / "HUC2.json"
write_dataframe(df, json_filename, driver="GeoJSONSeq")
mbtiles_filename = tile_dir / "HUC2.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", "8"]
    + ["-l", "HUC2"]
    + ["-T", "id:string"]
    + ["-o", f"{str(mbtiles_filename)}", str(json_filename)]
)
ret.check_returncode()
json_filename.unlink()

### HUC6 - HUC12
# have to render all to zoom 14 or boundaries mismatch
huc_zoom_levels = {
    'HUC6': [0,14],
    'HUC8': [0,14],
    'HUC10': [6,14],
    'HUC12': [8,14]
}

for huc, (minzoom, maxzoom) in huc_zoom_levels.items():
    print(f"Creating tiles for {huc}")
    df = gp.read_feather(src_dir / f"{huc}.feather").rename(columns={huc: 'id'}).to_crs(GEO_CRS)
    json_filename = tmp_dir / f"{huc}.json"
    write_dataframe(df, json_filename, driver="GeoJSONSeq")
    mbtiles_filename = tile_dir / f"{huc}.mbtiles"
    ret = subprocess.run(
        tippecanoe_args
        + ["-Z", str(minzoom), "-z", str(maxzoom)]
        + ["-l", huc]
        + ["-T", "id:string"]
        + ["-o", f"{str(mbtiles_filename)}", str(json_filename)]
    )
    ret.check_returncode()
    json_filename.unlink()


### ECO3
print("Creating ECO3 tiles")
df = gp.read_feather(src_dir / "region_eco3.feather").to_crs(GEO_CRS)
json_filename = tmp_dir / "region_eco3.json"
write_dataframe(df, json_filename, driver="GeoJSONSeq")
mbtiles_filename = tile_dir / "ECO3.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", "10"]
    + ["-l", "ECO3"]
    + ["-T", "id:string"]
    + ["-o", f"{str(mbtiles_filename)}", str(json_filename)]
)
ret.check_returncode()
json_filename.unlink()


### ECO4
print("Creating ECO4 tiles")
df = gp.read_feather(src_dir / "region_eco4.feather").to_crs(GEO_CRS)
json_filename = tmp_dir / "region_eco4.json"
write_dataframe(df, json_filename, driver="GeoJSONSeq")
mbtiles_filename = tile_dir / "ECO4.mbtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "3", "-z", "12"]
    + ["-l", "ECO4"]
    + ["-T", "id:string"]
    + ["-o", f"{str(mbtiles_filename)}", str(json_filename)]
)
ret.check_returncode()
json_filename.unlink()

print("All done!")