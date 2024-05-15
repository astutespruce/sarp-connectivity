from copy import deepcopy
import json
import os
from pathlib import Path

from dotenv import load_dotenv
import geopandas as gp
from pymgl import Map
import shapely

from analysis.constants import GEO_CRS, STATES
from analysis.lib.geometry.polygons import unwrap_antimeridian


load_dotenv()
TOKEN = os.getenv("MAPBOX_TOKEN", None)
if not TOKEN:
    raise ValueError("MAPBOX_TOKEN must be defined in your .env file")


map_units_tiles = Path("data/tiles/map_units.mbtiles").absolute()
dam_tiles = Path("tiles/dams.mbtiles").absolute()
small_barrier_tiles = Path("tiles/small_barriers.mbtiles").absolute()


WIDTH = 600
HEIGHT = 456

STYLE = {
    "version": 8,
    "sources": {
        "basemap": {
            "type": "raster",
            "tiles": [
                "https://api.mapbox.com/styles/v1/mapbox/light-v10/tiles/{z}/{x}/{y}?access_token=" + TOKEN,
            ],
            "tileSize": 512,
        },
        "map_units": {
            "type": "vector",
            "url": f"mbtiles://{map_units_tiles}",
            "minzoom": 0,
            "maxzoom": 8,
        },
        "dams": {
            "type": "vector",
            "url": f"mbtiles://{dam_tiles}",
            "minzoom": 2,
            "maxzoom": 16,
        },
        "small_barriers": {
            "type": "vector",
            "url": f"mbtiles://{small_barrier_tiles}",
            "minzoom": 2,
            "maxzoom": 16,
        },
    },
    "layers": [
        {"id": "basemap", "type": "raster", "source": "basemap"},
        {
            "id": "dams",
            "source": "dams",
            "source-layer": "ranked_dams",
            "type": "circle",
            "paint": {
                "circle-radius": {
                    "base": 0.5,
                    "stops": [[2, 0.5], [4, 1.5], [6, 2], [8, 3]],
                },
                "circle-opacity": 1,
                "circle-color": "#1891ac",
            },
        },
        {
            "id": "small_barriers",
            "source": "small_barriers",
            "source-layer": "ranked_small_barriers",
            "type": "circle",
            "paint": {
                "circle-radius": {
                    "base": 0.25,
                    "stops": [[2, 0.25], [4, 1.1], [6, 1.5], [8, 2]],
                },
                "circle-opacity": 1,
                "circle-color": "#1891ac",
            },
        },
        {
            "id": "states-outline-mask",
            "source": "map_units",
            "source-layer": "State",
            "type": "line",
            "minzoom": 0,
            "maxzoom": 22,
            "paint": {"line-color": "#FFFFFF", "line-width": 1.5, "line-opacity": 1},
        },
        {
            "id": "states-outline",
            "source": "map_units",
            "source-layer": "State",
            "type": "line",
            "minzoom": 0,
            "maxzoom": 22,
            "paint": {"line-color": "#333333", "line-width": 0.5, "line-opacity": 1},
        },
        {
            "id": "unit-mask",
            "source": "map_units",
            "source-layer": "mask",
            "type": "fill",
            "minzoom": 0,
            "maxzoom": 22,
            # filter: set dynamically when loaded
            "paint": {
                "fill-color": "#FFFFFF",
                "fill-opacity": 0.6,
            },
        },
        {
            "id": "unit-boundary",
            "source": "map_units",
            # "source-layer": set dynamically when loaded
            "type": "line",
            "minzoom": 0,
            "maxzoom": 22,
            # "filter": set dynamically when loaded
            "paint": {
                "line-color": "#000000",
                "line-width": 2,
            },
        },
    ],
}


out_dir = Path("ui/src/images/maps")
out_dir.mkdir(exist_ok=True)
region_dir = out_dir / "regions"
region_dir.mkdir(exist_ok=True)
state_dir = out_dir / "states"
state_dir.mkdir(exist_ok=True)
fhp_dir = out_dir / "fhp"
fhp_dir.mkdir(exist_ok=True)

### Render region maps
df = gp.read_feather("data/boundaries/region_boundary.feather").to_crs(GEO_CRS).set_index("id")
df = df.loc[df.id != "total"]

for id, row in df.bounds.iterrows():
    print(f"Rendering map for {id}")
    style = deepcopy(STYLE)
    style["layers"][-2]["filter"] = ["==", "id", id]
    style["layers"][-1]["source-layer"] = "boundary"
    style["layers"][-1]["filter"] = ["==", "id", id]

    # There are very few points in AK, make them bigger so they are more visible
    if id == "alaska":
        style["layers"][1]["paint"]["circle-radius"] = 3
        style["layers"][2]["paint"]["circle-radius"] = 2

    with Map(json.dumps(style), WIDTH, HEIGHT, ratio=1, token=TOKEN, provider="mapbox") as map:
        map.setBounds(*row.values, padding=10 if id == "southeast" else 20)
        png = map.renderPNG()
        with open(region_dir / f"{id}.png", "wb") as out:
            _ = out.write(png)


### Render state maps
df = gp.read_feather("data/boundaries/states.feather", columns=["id", "geometry"]).to_crs(GEO_CRS).sort_values(by="id")
df = df.loc[df.id.isin(STATES.keys())].explode(ignore_index=True)
# unwrap Alaska around antimeridian
df["geometry"] = unwrap_antimeridian(df.geometry.values)
df = gp.GeoDataFrame(
    df.groupby("id")
    .agg({"geometry": shapely.multipolygons, **{c: "first" for c in df.columns if c not in {"geometry", "id"}}})
    .reset_index(),
    geometry="geometry",
    crs=df.crs,
).set_index("id")


for id, row in df.iterrows():
    print(f"Rendering map for {id}")
    style = deepcopy(STYLE)
    style["layers"][-2]["filter"] = ["==", "id", id]
    style["layers"][-1]["source-layer"] = "State"
    style["layers"][-1]["filter"] = ["==", "id", id]

    bounds = shapely.bounds(row.geometry)

    if id == "AK":
        style["layers"][1]["paint"]["circle-radius"] = 3
        style["layers"][2]["paint"]["circle-radius"] = 2

    with Map(json.dumps(style), WIDTH, HEIGHT, ratio=1, token=TOKEN, provider="mapbox") as map:
        map.setBounds(*bounds, padding=20)
        png = map.renderPNG()
        with open(state_dir / f"{id}.png", "wb") as out:
            _ = out.write(png)


### Render FHP maps
df = (
    gp.read_feather("data/boundaries/fhp_boundary.feather", columns=["id", "geometry"])
    .to_crs(GEO_CRS)
    .explode(ignore_index=True)
    .set_index("id")
)

# have to unwrap antimeridian
df["geometry"] = unwrap_antimeridian(df.geometry.values)

df = gp.GeoDataFrame(df.groupby(level=0).agg({"geometry": shapely.multipolygons}), geometry="geometry", crs=df.crs)

for id, row in df.bounds.iterrows():
    print(f"Rendering map for {id}")
    style = deepcopy(STYLE)
    style["layers"][-2]["filter"] = ["==", "id", id]
    style["layers"][-1]["source-layer"] = "fhp_boundary"
    style["layers"][-1]["filter"] = ["==", "id", id]

    if id == "ak":
        style["layers"][1]["paint"]["circle-radius"] = 3
        style["layers"][2]["paint"]["circle-radius"] = 2

    with Map(json.dumps(style), WIDTH, HEIGHT, ratio=1, token=TOKEN, provider="mapbox") as map:
        map.setBounds(*row.values, padding=20)
        png = map.renderPNG()
        with open(fhp_dir / f"{id}.png", "wb") as out:
            _ = out.write(png)
