from copy import deepcopy
import json
import os
from pathlib import Path

from dotenv import load_dotenv
import geopandas as gp
from pymgl import Map

from analysis.constants import GEO_CRS


load_dotenv()
TOKEN = os.getenv("MAPBOX_TOKEN", None)
if not TOKEN:
    raise ValueError("MAPBOX_TOKEN must be defined in your .env file")


region_tiles = Path("data/tiles/boundary.mbtiles").absolute()
dam_tiles = Path("tiles/dams.mbtiles").absolute()


WIDTH = 600
HEIGHT = 456

STYLE = {
  "version": 8,
  "sources": {
    "basemap": {
      "type": 'raster',
      "tiles": [
        "https://api.mapbox.com/styles/v1/mapbox/light-v10/tiles/{z}/{x}/{y}?access_token=" + TOKEN,
      ],
      "tileSize": 512,
    },
    "regions": {
      "type": 'vector',
      "url": f'mbtiles://{region_tiles}',
      "minzoom": 0,
      "maxzoom": 8,
    },
    "dams": {
      "type": 'vector',
      "url": f'mbtiles://{dam_tiles}',
      "minzoom": 2,
      "maxzoom": 16,
    },
  },
  "layers": [
    { "id": 'basemap', "type": 'raster', "source": 'basemap' },
    {
      "id": 'dams',
      "source": 'dams',
      'source-layer': 'dams',
      "type": 'circle',
      "paint": {
        'circle-radius': {
          "base": 0.5,
          "stops": [
            [2, 0.5],
            [6, 1.5],
          ],
        },
        'circle-opacity': 1,
        'circle-color': '#1891ac',
      },
    },
    {
      "id": 'states',
      "source": 'regions',
      'source-layer': 'State',
      "type": 'line',
      "minzoom": 0,
      "maxzoom": 22,
      "paint": {
        'line-color': '#666666',
        'line-width': 0.2,
      },
    },
    {
      "id": 'region-mask',
      "source": 'regions',
      'source-layer': 'mask',
      "type": 'fill',
      "minzoom": 0,
      "maxzoom": 22,
      # filter: set dynamically when loaded
      "paint": {
        'fill-color': '#FFFFFF',
        'fill-opacity': 0.6,
      },
    },
    {
      "id": 'region-boundary',
      "source": 'regions',
      'source-layer': 'boundary',
      "type": 'line',
      "minzoom": 0,
      "maxzoom": 22,
      # filter: set dynamically when loaded
      "paint": {
        'line-color': '#000000',
        'line-width': 2,
      },
    },
  ],
}


out_dir = Path("ui/src/images/maps")
if not out_dir.exists():
    os.makedirs(out_dir)


df = gp.read_feather("data/boundaries/region_boundary.feather").to_crs(GEO_CRS).set_index('id')

for id, row in df.bounds.iterrows():
    print(f"Rendering map for {id}")
    style = deepcopy(STYLE)
    style['layers'][3]['filter'] = ['==', 'id', id]
    style['layers'][4]['filter'] = ['==', 'id', id]
    with Map(json.dumps(style), WIDTH, HEIGHT, ratio=1, token=TOKEN, provider="mapbox") as map:
        map.setBounds(*row.values, padding = 10 if id=="se" else 20)
        png = map.renderPNG()
        with open(out_dir / f"{id}.png", 'wb') as out:
            out.write(png)

