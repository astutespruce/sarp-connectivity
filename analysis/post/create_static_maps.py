from copy import deepcopy
import json
import os
from pathlib import Path

from dotenv import load_dotenv
import geopandas as gp
import pyarrow as pa
import pyarrow.compute as pc
from pymgl import Map
import shapely

from analysis.constants import GEO_CRS, STATES
from analysis.lib.geometry.polygons import unwrap_antimeridian
from api.constants import FISH_HABITAT_PARTNERSHIPS


load_dotenv()
TOKEN = os.getenv("MAPBOX_TOKEN", None)
if not TOKEN:
    raise ValueError("MAPBOX_TOKEN must be defined in your .env file")


region_tiles = Path("tiles/region_boundaries.mbtiles").absolute()
state_tiles = Path("data/tiles/State.mbtiles").absolute()
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
        "regions": {
            "type": "vector",
            "url": f"mbtiles://{region_tiles}",
            "minzoom": 0,
            "maxzoom": 8,
        },
        "states": {
            "type": "vector",
            "url": f"mbtiles://{state_tiles}",
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
            "source": "states",
            "source-layer": "State",
            "type": "line",
            "minzoom": 0,
            "maxzoom": 22,
            "paint": {"line-color": "#FFFFFF", "line-width": 1.5, "line-opacity": 1},
        },
        {
            "id": "states-outline",
            "source": "states",
            "source-layer": "State",
            "type": "line",
            "minzoom": 0,
            "maxzoom": 22,
            "paint": {"line-color": "#333333", "line-width": 0.5, "line-opacity": 1},
        },
    ],
}


REGION_STYLE = deepcopy(STYLE)
REGION_STYLE["layers"].extend(
    [
        {
            "id": "region-mask",
            "source": "regions",
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
            "id": "region-boundary",
            "source": "regions",
            "source-layer": "boundary",
            "type": "line",
            "minzoom": 0,
            "maxzoom": 22,
            # filter: set dynamically when loaded
            "paint": {
                "line-color": "#000000",
                "line-width": 2,
            },
        },
    ]
)

STATE_STYLE = deepcopy(STYLE)
STATE_STYLE["sources"]["mask"] = {
    "type": "geojson",
    "data": "",
}
STATE_STYLE["layers"].extend(
    [
        {
            "id": "state-mask",
            "source": "mask",
            "source-layer": "mask",
            "type": "fill",
            "minzoom": 0,
            "maxzoom": 22,
            "paint": {
                "fill-color": "#FFFFFF",
                "fill-opacity": 0.6,
            },
        },
        {
            "id": "selected-state-outline",
            "source": "states",
            "source-layer": "State",
            "type": "line",
            "minzoom": 0,
            "maxzoom": 22,
            "paint": {"line-color": "#333333", "line-width": 2, "line-opacity": 1},
        },
    ]
)


FHP_STYLE = deepcopy(STYLE)
FHP_STYLE["layers"].extend(
    [
        {
            "id": "fhp-mask",
            "source": "regions",
            "source-layer": "fhp_mask",
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
            "id": "fhp-boundary",
            "source": "regions",
            "source-layer": "fhp_boundary",
            "type": "line",
            "minzoom": 0,
            "maxzoom": 22,
            # filter: set dynamically when loaded
            "paint": {
                "line-color": "#000000",
                "line-width": 2,
            },
        },
    ]
)


out_dir = Path("ui/src/images/maps")
out_dir.mkdir(exist_ok=True)
state_dir = out_dir / "states"
state_dir.mkdir(exist_ok=True)
fhp_dir = out_dir / "fhp"
fhp_dir.mkdir(exist_ok=True)

### Render region maps
df = gp.read_feather("data/boundaries/region_boundary.feather").to_crs(GEO_CRS).set_index("id")

for id, row in df.bounds.iterrows():
    print(f"Rendering map for {id}")
    style = deepcopy(REGION_STYLE)
    style["layers"][-2]["filter"] = ["==", "id", id]
    style["layers"][-1]["filter"] = ["==", "id", id]

    if id == "ak":
        style["layers"][1]["paint"]["circle-radius"] = 3
        style["layers"][2]["paint"]["circle-radius"] = 2

    with Map(json.dumps(style), WIDTH, HEIGHT, ratio=1, token=TOKEN, provider="mapbox") as map:
        map.setBounds(*row.values, padding=10 if id == "se" else 20)
        png = map.renderPNG()
        with open(out_dir / f"{id}.png", "wb") as out:
            _ = out.write(png)


### Render state maps
df = (
    gp.read_feather("data/boundaries/states.feather", columns=["id", "geometry"])
    .to_crs(GEO_CRS)
    .sort_values(by="id")
    .set_index("id")
)
df = df.loc[df.index.isin(STATES.keys())].copy()

# clip data to avoid wrapping antimeridian
df.loc["AK", "geometry"] = shapely.intersection(df.loc["AK"].geometry, shapely.box(-180, -90, 0, 90))

for id, row in df.iterrows():
    print(f"Rendering map for {id}")
    style = deepcopy(STATE_STYLE)

    bounds = shapely.bounds(row.geometry)

    if id == "AK":
        style["layers"][1]["paint"]["circle-radius"] = 3
        style["layers"][2]["paint"]["circle-radius"] = 2

    mask = shapely.to_geojson(shapely.difference(shapely.box(-180, -90, 180, 90), row.geometry))
    style["sources"]["mask"]["data"] = json.loads(mask)
    style["layers"][-1]["filter"] = ["==", "id", id]
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
    style = deepcopy(FHP_STYLE)
    style["layers"][-2]["filter"] = ["==", "id", id]
    style["layers"][-1]["filter"] = ["==", "id", id]

    if id == "ak":
        style["layers"][1]["paint"]["circle-radius"] = 3
        style["layers"][2]["paint"]["circle-radius"] = 2

    with Map(json.dumps(style), WIDTH, HEIGHT, ratio=1, token=TOKEN, provider="mapbox") as map:
        map.setBounds(*row.values, padding=10 if id == "se" else 20)
        png = map.renderPNG()
        with open(fhp_dir / f"{id}.png", "wb") as out:
            _ = out.write(png)
