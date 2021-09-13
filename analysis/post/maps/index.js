import fs from 'fs'
import path from 'path'
import render from 'mbgl-renderer'
import dotenv from 'dotenv'

dotenv.config()
const token = process.env.MAPBOX_TOKEN
if (!token) {
  throw new Error(
    'Mapbox token is not defined, you must have this in MAPBOX_TOKEN in the .env file in this directory.'
  )
}

const outDir = '../../../ui/src/images/maps'
const tilePath = path.join(__dirname, '../../../tiles')

const width = 600
const height = 456

const regions = JSON.parse(
  fs.readFileSync('../../../ui/data/region_bounds.json')
)

const style = {
  version: 8,
  sources: {
    basemap: {
      type: 'raster',
      tiles: [
        `https://api.mapbox.com/styles/v1/mapbox/light-v10/tiles/{z}/{x}/{y}?access_token=${token}`,
      ],
      tileSize: 512,
    },
    regions: {
      type: 'vector',
      url: 'mbtiles://summary',
      minzoom: 0,
      maxzoom: 8,
    },
    dams: {
      type: 'vector',
      url: 'mbtiles://dams',
      minzoom: 2,
      maxzoom: 16,
    },
  },
  layers: [
    { id: 'basemap', type: 'raster', source: 'basemap' },
    {
      id: 'dams',
      source: 'dams',
      'source-layer': 'dams',
      type: 'circle',
      paint: {
        'circle-radius': {
          base: 0.5,
          stops: [
            [2, 0.5],
            [6, 1.5],
          ],
        },
        'circle-opacity': 1,
        'circle-color': '#1891ac',
      },
    },
    {
      id: 'states',
      source: 'regions',
      'source-layer': 'State',
      type: 'line',
      minzoom: 0,
      maxzoom: 22,
      paint: {
        'line-color': '#666666',
        'line-width': 0.2,
      },
    },
    {
      id: 'region-mask',
      source: 'regions',
      'source-layer': 'mask',
      type: 'fill',
      minzoom: 0,
      maxzoom: 22,
      // filter: set dynamically when loaded
      paint: {
        'fill-color': '#FFFFFF',
        'fill-opacity': 0.6,
      },
    },
    {
      id: 'region-boundary',
      source: 'regions',
      'source-layer': 'boundary',
      type: 'line',
      minzoom: 0,
      maxzoom: 22,
      // filter: set dynamically when loaded
      paint: {
        'line-color': '#000000',
        'line-width': 2,
      },
    },
  ],
}

Object.entries(regions).forEach(([id, bounds]) => {
  console.log(`Creating region map for ${id}`)
  style.layers[3].filter = ['==', 'id', id]
  style.layers[4].filter = ['==', 'id', id]
  render(style, width, height, {
    token,
    // zoom: 5,
    // center: [
    //   (bounds[2] - bounds[0]) / 2 + bounds[0],
    //   (bounds[3] - bounds[1]) / 2 + bounds[1],
    // ],
    bounds,
    padding: id === 'se' ? 10 : 20,
    tilePath,
  }).then((data) => {
    fs.writeFileSync(`${outDir}/${id}.png`, data)
  })
})
