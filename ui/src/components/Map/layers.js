const flowlinesLayer = {
  id: 'flowlines',
  source: 'networks',
  'source-layer': 'networks',
  filter: ['any', ['==', 'mapcode', 0], ['==', 'mapcode', 2]],
  minzoom: 5,
  type: 'line',
  paint: {
    'line-opacity': {
      base: 0,
      stops: [
        [6, 0.05],
        [8, 0.1],
        [10, 0.25],
        [14, 0.5],
        [16, 1],
      ],
    },
    'line-width': [
      'interpolate',
      ['linear'],
      ['zoom'],
      5,
      ['*', ['get', 'sizeclass'], 0.01],
      6,
      ['*', ['get', 'sizeclass'], 0.05],
      9,
      ['*', ['get', 'sizeclass'], 0.25],
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
    'line-width': [
      'interpolate',
      ['linear'],
      ['zoom'],
      5,
      1,
      9,
      ['*', ['get', 'sizeclass'], 0.3],
      11,
      ['*', ['get', 'sizeclass'], 0.6],
      12,
      ['+', ['get', 'sizeclass'], 0.75],
      14,
      ['+', ['get', 'sizeclass'], 1.5],
    ],
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
