export const unitLayerConfig = {
  HUC6: {
    title: 'Basin',
    minzoom: 0,
    maxzoom: 24,
  },
  HUC8: {
    minzoom: 0,
    maxzoom: 24,
    parent: {
      id: 'HUC6',
      minzoom: 4,
    },
  },
  HUC10: {
    minzoom: 6,
    maxzoom: 24,
    parent: {
      id: 'HUC8',
      minzoom: 7,
    },
  },
  HUC12: {
    minzoom: 8,
    maxzoom: 24,
    parent: {
      id: 'HUC10',
      minzoom: 9,
    },
  },
  State: {
    minzoom: 0,
    maxzoom: 24,
  },
  County: {
    minzoom: 3,
    maxzoom: 24,
    parent: {
      id: 'State',
      minzoom: 0,
    },
  },
}
