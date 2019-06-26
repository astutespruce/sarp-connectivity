import { siteMetadata } from '../../../gatsby-config'

const { tileHost } = siteMetadata

export const config = {
  // Bounds around all selected HUC6s
  bounds: [-107.87000919, 17.62370026, -64.5126611, 44.26093852],
  baseStyle: 'light-v9',
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
