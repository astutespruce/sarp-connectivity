export const unitLayerConfig = {
  HUC6: {
    title: 'Basin',
    minzoom: 0,
    maxzoom: 24,
  },
  HUC8: {
    minzoom: 0,
    maxzoom: 24,
    parent: 'HUC6',
  },
  HUC12: {
    minzoom: 0,
    maxzoom: 24,
    parent: 'HUC8',
  },
  State: {
    minzoom: 0,
    maxzoom: 24,
  },
  County: {
    minzoom: 0,
    maxzoom: 24,
  },
  ECO3: {
    minzoom: 0,
    maxzoom: 24,
  },
  ECO4: {
    minzoom: 0,
    maxzoom: 24,
  },
}
