const flowlinesLayer = {
  id: 'flowlines',
  source: 'networks',
  'source-layer': 'networks',
  filter: ['any', ['==', 'mapcode', 0], ['==', 'mapcode', 2]],
  layout: {
    'line-cap': 'round',
  },
  minzoom: 5,
  type: 'line',
  paint: {
    'line-opacity': {
      base: 0,
      stops: [
        [5, 0.5],
        [7, 0.75],
        [9, 1],
      ],
    },
    // NOTE: size classes start at 0, so we add to them before scaling
    'line-width': [
      'interpolate',
      ['linear'],
      ['zoom'],
      6,
      ['*', ['-', ['get', 'sizeclass'], 10], 0.1],
      9,
      ['*', ['-', ['get', 'sizeclass'], 3], 0.25],
      11,
      ['*', ['+', ['get', 'sizeclass'], 0.25], 0.15],
      12,
      ['*', ['+', ['get', 'sizeclass'], 0.5], 0.25],
      14,
      ['*', ['+', ['get', 'sizeclass'], 0.75], 1],
    ],
    'line-color': ['case', ['<', ['get', 'mapcode'], 2], '#1891ac', 'red'],
  },
}

const intermittentFlowlinesLayer = {
  ...flowlinesLayer,
  id: 'flowlines-intermittent',
  filter: ['any', ['==', 'mapcode', 1], ['==', 'mapcode', 3]],
  paint: {
    ...flowlinesLayer.paint,
    'line-dasharray': [3, 2],
  },
}

const networkHighlightLayer = {
  ...flowlinesLayer,
  id: 'network-highlight',
  filter: ['==', 'dams', Infinity],
  paint: {
    ...flowlinesLayer.paint,
    'line-opacity': 1,
    'line-color': '#fd8d3c',
  },
}

const intermittentNetworkHighlightLayer = {
  ...networkHighlightLayer,
  id: 'network-intermittent-highlight',
  paint: {
    ...networkHighlightLayer.paint,
    'line-dasharray': [3, 2],
  },
}

export const networkLayers = [
  flowlinesLayer,
  intermittentFlowlinesLayer,
  networkHighlightLayer,
  intermittentNetworkHighlightLayer,
]
