const flowlinesLayer = {
  id: 'flowlines',
  source: 'networks',
  'source-layer': 'networks',
  filter: ['any', ['==', 'mapcode', 0], ['==', 'mapcode', 2]],
  minzoom: 11,
  type: 'line',
  paint: {
    'line-opacity': {
      base: 0,
      stops: [
        [11, 0],
        [12, 0.1],
        [14, 0.5],
        [16, 1],
      ],
    },
    'line-width': [
      'interpolate',
      ['linear'],
      ['zoom'],
      11,
      ['*', ['get', 'sizeclass'], 0.5],
      12,
      ['+', ['get', 'sizeclass'], 0.5],
      14,
      ['+', ['get', 'sizeclass'], 1],
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
