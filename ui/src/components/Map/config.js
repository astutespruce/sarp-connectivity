// @refresh reset

import { siteMetadata } from 'config'

const { tileHost } = siteMetadata

export const mapConfig = {
  // Bounds around all selected HUC6s
  bounds: [-124.9022044, 17.83087146, -65.16797072, 52.88065373],
  styleID: 'light-v10',
  minZoom: 2,
  maxZoom: 22,
  projection: 'mercator',
}

export const sources = {
  region_boundaries: {
    type: 'vector',
    maxzoom: 8,
    tiles: [`${tileHost}/services/region_boundaries/tiles/{z}/{x}/{y}.pbf`],
  },
  summary: {
    type: 'vector',
    maxzoom: 8,
    tiles: [`${tileHost}/services/map_units_summary/tiles/{z}/{x}/{y}.pbf`],
  },
  dams: {
    type: 'vector',
    tiles: [`${tileHost}/services/dams/tiles/{z}/{x}/{y}.pbf`],
    minzoom: 2,
    maxzoom: 16,
    promoteId: 'id',
  },
  small_barriers: {
    type: 'vector',
    tiles: [`${tileHost}/services/small_barriers/tiles/{z}/{x}/{y}.pbf`],
    minzoom: 2,
    maxzoom: 16,
    promoteId: 'id',
  },
  combined_barriers: {
    type: 'vector',
    tiles: [`${tileHost}/services/combined_barriers/tiles/{z}/{x}/{y}.pbf`],
    minzoom: 2,
    maxzoom: 16,
    promoteId: 'id',
  },
  largefish_barriers: {
    type: 'vector',
    tiles: [`${tileHost}/services/largefish_barriers/tiles/{z}/{x}/{y}.pbf`],
    minzoom: 2,
    maxzoom: 16,
    promoteId: 'id',
  },
  smallfish_barriers: {
    type: 'vector',
    tiles: [`${tileHost}/services/smallfish_barriers/tiles/{z}/{x}/{y}.pbf`],
    minzoom: 2,
    maxzoom: 16,
    promoteId: 'id',
  },
  road_crossings: {
    type: 'vector',
    tiles: [`${tileHost}/services/road_crossings/tiles/{z}/{x}/{y}.pbf`],
    minzoom: 3,
    maxzoom: 16,
  },
  waterfalls: {
    type: 'vector',
    tiles: [`${tileHost}/services/waterfalls/tiles/{z}/{x}/{y}.pbf`],
    minzoom: 9,
    maxzoom: 16,
    promoteId: 'id',
  },
  networks: {
    type: 'vector',
    tiles: [`${tileHost}/services/networks/tiles/{z}/{x}/{y}.pbf`],
    minzoom: 3,
    maxzoom: 16,
  },
}

export const basemapLayers = {
  imagery: [
    {
      id: 'imagery',
      source: {
        type: 'raster',
        tiles: [
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        ],
        attribution: 'Esri, DigitalGlobe. ...',
        tileSize: 256,
      },
      type: 'raster',
      layout: {
        visibility: 'none',
      },
    },
    {
      id: 'imagery-ref',
      source: {
        type: 'raster',
        tiles: [
          'https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        ],
        tileSize: 256,
      },
      type: 'raster',
      layout: {
        visibility: 'none',
      },
    },
    {
      id: 'imagery-streets',
      source: {
        type: 'raster',
        tiles: [
          'https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}',
        ],
        tileSize: 256,
      },
      type: 'raster',
      minzoom: 10,
      layout: {
        visibility: 'none',
      },
      paint: {
        'raster-opacity': {
          stops: [
            [10, 0.1],
            [12, 0.5],
            [14, 1],
          ],
        },
      },
    },
  ],
  topo: [
    {
      id: 'topo',
      source: {
        type: 'raster',
        tiles: [
          'https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        ],
        attribution: 'Esri, HERE, Garmin, ...',
        tileSize: 256,
      },
      type: 'raster',
      layout: {
        visibility: 'none',
      },
    },
  ],
  streets: [
    {
      id: 'streets',
      source: {
        type: 'raster',
        tiles: [
          'https://services.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
        ],
        attribution: 'Esri, HERE, Garmin, ...',
        tileSize: 256,
      },
      type: 'raster',
      layout: {
        visibility: 'none',
      },
    },
  ],
}

// used for downloadable reports
export const basemapAttribution = {
  imagery: '© Mapbox, © OpenStreetMap',
  'light-v10': '© Mapbox, © OpenStreetMap',
  topo: 'Esri, HERE, Garmin, Intermap, increment P Corp., GEBCO, USGS, FAO, NPS, NRCAN, GeoBase, IGN, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), © OpenStreetMap contributors, and the GIS User Community',
  streets:
    'Esri, HERE, Garmin, USGS, Intermap, INCREMENT P, NRCan, Esri Japan, METI, Esri China (Hong Kong), Esri Korea, Esri (Thailand), NGCC, © OpenStreetMap contributors, and the GIS User Community',
}
