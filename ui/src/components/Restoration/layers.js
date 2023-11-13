import { pointColors } from 'config'
import { getHighlightExpr } from '../Map/util'

export const layers = [
  {
    id: 'HUC2',
    system: 'HUC',
    title: 'Region',
    bins: {
      dams: [1, 2, 5, 10, 100, 500],
      small_barriers: [1, 5, 10, 25, 50, 1_000, 2_500],
      combined_barriers: [1, 5, 10, 25, 50, 1_000, 2_500],
    },
    fill: {
      minzoom: 0,
      maxzoom: 4,
      paint: {
        'fill-opacity': {
          base: 0.1,
          stops: [
            [1, 0.25],
            [2, 0.4],
            [4, 0.25],
          ],
        },
      },
    },
    outline: {
      minzoom: 0,
      maxzoom: 6,
      paint: {
        'line-width': {
          base: 0.1,
          stops: [
            [3, 0.75],
            [5, 1.5],
            [6, 2],
          ],
        },
      },
    },
  },
  {
    id: 'HUC6',
    system: 'HUC',
    title: 'Basin',
    bins: {
      dams: [1, 2, 5, 10, 50, 100],
      small_barriers: [1, 2, 5, 10, 50, 100, 500],
      combined_barriers: [1, 2, 5, 10, 50, 100, 500],
    },
    fill: {
      minzoom: 4,
      maxzoom: 6,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [
            [4, 0.25],
            [5, 0.25],
            [6, 0.1],
          ],
        },
      },
    },
    outline: {
      minzoom: 4,
      maxzoom: 9.5,
      paint: {
        'line-width': {
          base: 0.1,
          stops: [
            [4, 0.1],
            [5, 0.25],
            [6, 0.5],
            [6.5, 1.5],
            [8, 2],
            [9, 4],
            [12, 6],
          ],
        },
      },
    },
  },
  {
    id: 'HUC8',
    system: 'HUC',
    title: 'Subbasin',
    bins: {
      dams: [1, 2, 5, 10, 50],
      small_barriers: [1, 2, 5, 10, 50, 100],
      combined_barriers: [1, 2, 5, 10, 50, 100],
    },
    fill: {
      minzoom: 6,
      maxzoom: 8,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [
            [6, 0.1],
            [7, 0.25],
            [8, 0.1],
          ],
        },
      },
    },
    outline: {
      minzoom: 6,
      maxzoom: 10,
      paint: {
        'line-width': {
          base: 0.1,
          stops: [
            [6, 0.1],
            [8, 0.5],
            [8, 1.5],
            [9, 2.5],
          ],
        },
      },
    },
  },
  {
    id: 'HUC10',
    system: 'HUC',
    title: 'Watershed',
    bins: {
      dams: [1, 2, 5, 10, 25],
      small_barriers: [1, 2, 5, 10, 25],
      combined_barriers: [1, 2, 5, 10, 25],
    },
    fill: {
      minzoom: 7,
      maxzoom: 9,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [
            [7, 0.1],
            [8, 0.25],
            [9, 0.1],
          ],
        },
      },
    },
    outline: {
      minzoom: 7,
      maxzoom: 24,
      paint: {
        'line-width': {
          base: 0.1,
          stops: [
            [7, 0.1],
            [8, 0.5],
            [9, 1],
            [10, 2.5],
          ],
        },
      },
    },
  },
  {
    id: 'HUC12',
    system: 'HUC',
    title: 'Subwatershed',
    bins: {
      dams: [1, 2, 5, 10, 25],
      small_barriers: [1, 2, 5, 10, 25],
      combined_barriers: [1, 2, 5, 10, 25],
    },
    fill: {
      minzoom: 9,
      maxzoom: 24,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [
            [8, 0.1],
            [9, 0.25],
            [11, 0.25],
            [12, 0.15],
            [14, 0],
          ],
        },
      },
    },
    outline: {
      minzoom: 9,
      maxzoom: 24,
      paint: {
        'line-width': {
          base: 0.1,
          stops: [
            [8, 0.1],
            [9.5, 0.5],
          ],
        },
      },
    },
  },
  {
    id: 'State',
    system: 'ADM',
    title: 'State',
    bins: {
      dams: [1, 5, 10, 50, 100, 250, 500],
      small_barriers: [1, 5, 10, 50, 100, 500, 1_000],
      combined_barriers: [1, 5, 10, 50, 100, 500, 1_000],
    },
    fill: {
      minzoom: 0,
      maxzoom: 5,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [
            [2, 0.4],
            [4, 0.25],
            [6, 0.25],
            [7, 0.1],
          ],
        },
      },
    },
    outline: {
      minzoom: 0,
      maxzoom: 12,
      paint: {
        'line-width': {
          base: 0.1,
          stops: [
            [4, 0.1],
            [5, 0.25],
            [6, 0.5],
            [6.5, 1.5],
            [8, 2],
            [9, 4],
            [12, 6],
          ],
        },
      },
    },
  },
  {
    id: 'County',
    system: 'ADM',
    title: 'County',
    bins: {
      dams: [1, 2, 5, 10, 25],
      small_barriers: [1, 2, 5, 10, 50, 100],
      combined_barriers: [1, 2, 5, 10, 50, 100],
    },
    fill: {
      minzoom: 5,
      maxzoom: 24,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [
            [5, 0.1],
            [6, 0.25],
            [9, 0.25],
            [10, 0.15],
            [14, 0],
          ],
        },
      },
    },
    outline: {
      minzoom: 5,
      maxzoom: 24,
      paint: {
        'line-width': {
          base: 0.1,
          stops: [
            [6, 0.1],
            [8, 0.5],
            [10, 1],
            [12, 1.5],
          ],
        },
      },
    },
  },
]

export const flowlineLegend = {}

export const removedPointLayer = {
  // id: '' // provided by specific layer
  // source: "" // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 6,
  maxzoom: 24,
  // filter: ['==', 'symbol', 5],
  paint: {
    'circle-color': getHighlightExpr(
      [
        'match',
        ['get', 'barriertype'],
        'small_barriers',
        pointColors.removed.damsColor,
        pointColors.removed.color,
      ],
      pointColors.highlight.color
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      6,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 0.5, 1],
        6
      ),
      8,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 1, 2],
        10
      ),
      12,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 2, 3],
        12
      ),
      14,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 3, 4],
        14
      ),
      16,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 6, 8],
        14
      ),
    ],
    'circle-opacity': 1,
    'circle-stroke-color': getHighlightExpr(
      pointColors.removed.strokeColor,
      pointColors.highlight.strokeColor
    ),
    'circle-stroke-width': {
      stops: [
        [6, 0.25],
        [10, 1],
        [14, 2],
      ],
    },
  },
}

export const regionLayers = [
  {
    id: 'region-mask',
    source: 'summary',
    'source-layer': 'mask',
    type: 'fill',
    maxzoom: 24,
    filter: ['==', ['get', 'id'], 'total'],
    paint: {
      'fill-opacity': 0.6,
      'fill-color': '#AAA',
    },
  },
  {
    id: 'region-bounds',
    source: 'summary',
    'source-layer': 'boundary',
    type: 'line',
    maxzoom: 24,
    filter: ['==', ['get', 'id'], 'total'],
    paint: {
      'line-opacity': 0.8,
      'line-width': 2,
      'line-color': '#4A0025',
    },
  },
]
