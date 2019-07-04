import { siteMetadata } from '../../../gatsby-config'

const { tileHost } = siteMetadata

export const config = {
  // Bounds around all selected HUC6s
  bounds: [-107.87000919, 17.62370026, -64.5126611, 44.26093852],
  styleID: 'light-v9',
  minZoom: 2,
  maxZoom: 24,
}

export const sources = {
  sarp: {
    type: 'vector',
    maxzoom: 8,
    tiles: [`${tileHost}/services/sarp_summary/tiles/{z}/{x}/{y}.pbf`],
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
          stops: [[10, 0.1], [12, 0.5], [14, 1]],
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
}
