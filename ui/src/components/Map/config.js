import { siteMetadata } from '../../../gatsby-config'

const { tileHost } = siteMetadata

export const config = {
  // Bounds around all selected HUC6s
  bounds: [-116.049153, 17.831509, -65.168503, 49.0011],
  styleID: 'light-v9',
  minZoom: 2,
  maxZoom: 24,
}

export const sources = {
  summary: {
    type: 'vector',
    maxzoom: 8,
    tiles: [`${tileHost}/services/summary/tiles/{z}/{x}/{y}.pbf`],
  },
  dams: {
    type: 'vector',
    tiles: [`${tileHost}/services/dams/tiles/{z}/{x}/{y}.pbf`],
    minzoom: 5,
    maxzoom: 12,
  },
  small_barriers: {
    type: 'vector',
    tiles: [`${tileHost}/services/small_barriers/tiles/{z}/{x}/{y}.pbf`],
    minzoom: 5,
    maxzoom: 12,
  },
  networks: {
    type: 'vector',
    tiles: [`${tileHost}/services/networks/tiles/{z}/{x}/{y}.pbf`],
    minzoom: 6,
    maxzoom: 16,
  },
  waterfalls: {
    type: 'vector',
    tiles: [`${tileHost}/services/waterfalls/tiles/{z}/{x}/{y}.pbf`],
    minzoom: 5,
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
          '//server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
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
          '//services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
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
          '//services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}',
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
          '//services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
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
          '//services.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
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
  'light-v9': '© Mapbox, © OpenStreetMap',
  topo: 'Esri, HERE, Garmin, Intermap, increment P Corp., GEBCO, USGS, FAO, NPS, NRCAN, GeoBase, IGN, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), © OpenStreetMap contributors, and the GIS User Community',
  streets:
    'Esri, HERE, Garmin, USGS, Intermap, INCREMENT P, NRCan, Esri Japan, METI, Esri China (Hong Kong), Esri Korea, Esri (Thailand), NGCC, © OpenStreetMap contributors, and the GIS User Community',
}
