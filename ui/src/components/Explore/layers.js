// color bins last updated 11/10/2023

import { pointColors } from 'config'
import { getHighlightExpr } from '../Map/util'

export const layers = [
  {
    id: 'HUC2',
    system: 'HUC',
    title: 'Region',
    bins: {
      dams: [1_500, 5_000, 10_000, 25_000, 75_000, 150_000],
      small_barriers: [500, 1_000, 5_000, 10_000, 25_000, 50_000],
      combined_barriers: [2_500, 10_000, 25_000, 50_000, 100_000, 150_000],
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
      dams: [50, 250, 500, 1_000, 5_000, 10_000],
      small_barriers: [10, 50, 250, 1_000, 2_500, 10_000],
      combined_barriers: [50, 500, 1_000, 2_500, 5_000, 10_000],
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
      dams: [10, 50, 100, 250, 1_000, 5_000],
      small_barriers: [5, 25, 50, 250, 500, 5_000],
      combined_barriers: [10, 50, 150, 500, 1_000, 5_000],
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
      dams: [1, 5, 10, 50, 100, 500, 1_000],
      small_barriers: [1, 5, 10, 50, 100, 500, 1_000],
      combined_barriers: [1, 5, 10, 50, 100, 500, 1_000],
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
      dams: [1, 2, 5, 10, 25, 50, 100, 500],
      small_barriers: [1, 2, 5, 10, 25, 50, 100, 500],
      combined_barriers: [1, 2, 5, 10, 25, 50, 100, 500],
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
      dams: [500, 1_000, 5_000, 10_000, 25_000, 50_000],
      small_barriers: [100, 500, 1_000, 5_000, 10_000, 25_000],
      combined_barriers: [500, 1_000, 5_000, 10_000, 25_000, 50_000],
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
      dams: [10, 25, 100, 250, 500, 1_000, 5_000],
      small_barriers: [5, 10, 50, 250, 500, 1_000, 5_000],
      combined_barriers: [10, 50, 250, 500, 1_000, 5_000],
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

export const waterfallsLayer = {
  id: 'waterfalls',
  source: 'waterfalls',
  'source-layer': 'waterfalls',
  type: 'circle',
  minzoom: 10,
  maxzoom: 24,
  paint: {
    'circle-color': getHighlightExpr(
      pointColors.waterfalls.color,
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      pointColors.waterfalls.strokeColor,
      pointColors.highlight.strokeColor
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      10,
      getHighlightExpr(1, 10),
      12,
      getHighlightExpr(2, 14),
      14,
      getHighlightExpr(4, 14),
      16,
      getHighlightExpr(6, 14),
    ],
    'circle-opacity': 1,
    'circle-stroke-width': {
      stops: [
        [10, 0],
        [12, 1],
      ],
    },
  },
}

// Note: this is ONLY for display when small barriers are selected
export const roadCrossingsLayer = {
  id: 'road-crossings',
  source: 'road_crossings',
  'source-layer': 'road_crossings',
  type: 'circle',
  minzoom: 11,
  maxzoom: 24,
  layout: {
    visibility: 'none',
  },
  filter: ['==', ['get', 'surveyed'], 0],
  paint: {
    'circle-color': getHighlightExpr(
      pointColors.offNetwork.color,
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      pointColors.offNetwork.strokeColor,
      pointColors.highlight.strokeColor
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      11,
      getHighlightExpr(0.5, 2),
      12,
      getHighlightExpr(1, 2),
      14,
      getHighlightExpr(3, 14),
    ],
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      10,
      getHighlightExpr(0.5, 1),
      14,
      1,
    ],
    'circle-stroke-width': {
      stops: [
        [10, 0],
        [14, 1],
      ],
    },
  },
}

// NOTE: this is ONLY for displaying dams when small barriers are selected
export const damsSecondaryLayer = {
  id: 'dams-secondary',
  source: 'combined_barriers',
  'source-layer': 'ranked_combined_barriers',
  filter: ['==', 'barriertype', 'dams'],
  layout: {
    visibility: 'none',
  },
  type: 'circle',
  minzoom: 10,
  maxzoom: 24,
  paint: {
    'circle-color': getHighlightExpr(
      pointColors.damsSecondary.color,
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      pointColors.damsSecondary.strokeColor,
      pointColors.highlight.strokeColor
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      10,
      getHighlightExpr(1, 10),
      12,
      getHighlightExpr(2, 14),
      14,
      getHighlightExpr(4, 14),
      16,
      getHighlightExpr(8, 14),
    ],
    'circle-opacity': 1,
    'circle-stroke-width': {
      stops: [
        [10, 0],
        [12, 1],
        [14, 2],
      ],
    },
  },
}

// ranked points with networks
export const rankedPointLayer = {
  // id: '' // provided by specific layer
  // source: "" // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 10,
  maxzoom: 24,
  paint: {
    'circle-color': getHighlightExpr(
      [
        'match',
        ['get', 'barriertype'],
        'small_barriers',
        pointColors.included.smallBarriersColor,
        pointColors.included.color,
      ],
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      [
        'match',
        ['get', 'barriertype'],
        'dams',
        pointColors.included.damsStrokeColor,
        pointColors.included.color,
      ],
      pointColors.highlight.strokeColor
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      9,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 0.5, 1],
        9
      ),
      10,
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
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      9,
      getHighlightExpr(0.25, 1),
      12,
      getHighlightExpr(0.5, 1),
      14,
      1,
    ],
    'circle-stroke-width': {
      stops: [
        [9, 0],
        [12, 1],
        [14, 2],
      ],
    },
  },
}

// unranked points include everything that was included in network analysis
// but not prioritized; right now this is only invasive barriers
export const unrankedPointLayer = {
  // id: '', // provided by specific layer
  // source: "", // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 12,
  maxzoom: 24,
  paint: {
    'circle-color': getHighlightExpr(
      [
        'match',
        ['get', 'symbol'],
        4, // invasive barrier
        [
          'match',
          ['get', 'barriertype'],
          'dams',
          pointColors.invasive.damsColor,
          pointColors.invasive.color,
        ],
        // default
        pointColors.offNetwork.color,
      ],
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      [
        'match',
        ['get', 'symbol'],
        4, // invasive barrier
        pointColors.invasive.strokeColor,
        // default
        pointColors.offNetwork.strokeColor,
      ],
      pointColors.highlight.strokeColor
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      12,
      getHighlightExpr(1, 12),
      14,
      getHighlightExpr(3, 14),
      16,
      getHighlightExpr(6, 14),
    ],
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      12,
      getHighlightExpr(0.5, 1),
      14,
      1,
    ],

    'circle-stroke-width': {
      stops: [
        [12, 0],
        [14, 1],
      ],
    },
  },
}

export const removedBarrierPointLayer = {
  // id: '', // provided by specific layer
  // source: "", // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 10,
  maxzoom: 24,
  paint: {
    'circle-color': getHighlightExpr(
      [
        'match',
        ['get', 'barriertype'],
        'dams',
        pointColors.removed.damsColor,
        pointColors.removed.color,
      ],
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      pointColors.removed.strokeColor,
      pointColors.highlight.strokeColor
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      12,
      getHighlightExpr(1, 12),
      14,
      getHighlightExpr(4, 14),
    ],
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      12,
      getHighlightExpr(0.5, 1),
      14,
      1,
    ],
    'circle-stroke-width': {
      stops: [
        [12, 0],
        [14, 1],
      ],
    },
  },
}

// Other barriers are those that are not ranked and not marked as unranked;
// they include: off-network barriers, non-barriers, minor barriers
export const otherBarrierPointLayer = {
  // id: '', // provided by specific layer
  // source: "", // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 12,
  maxzoom: 24,
  paint: {
    'circle-color': getHighlightExpr(
      [
        'match',
        ['get', 'symbol'],
        1, // unsnapped (actually off-network)
        pointColors.offNetwork.color,
        2, // non-barrier
        [
          'match',
          ['get', 'barrier_type'],
          'dams',
          pointColors.nonBarrier.damsColor,
          pointColors.nonBarrier.color,
        ],
        // NOTE: this only gets used when minor barriers are NOT included in
        // ranked / unranked barrier tile layers
        3, // minor barrier
        pointColors.minorBarrier.color,
        // pointColors.nonBarrier.color,
        4, // invasive barrier (should mostly be handled in unranked layer)
        [
          'match',
          ['get', 'barriertype'],
          'dams',
          pointColors.invasive.damsColor,
          pointColors.invasive.color,
        ],
        // last entry is default
        pointColors.offNetwork.color,
      ],
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      [
        'match',
        ['get', 'symbol'],
        1, // unsnapped
        pointColors.offNetwork.strokeColor,
        2, // non-barrier
        pointColors.nonBarrier.strokeColor,
        3, // minor barrier
        pointColors.minorBarrier.strokeColor,
        4, // invasive barrier
        pointColors.invasive.strokeColor,
        pointColors.offNetwork.strokeColor,
      ],
      pointColors.highlight.strokeColor
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      12,
      getHighlightExpr(1, 12),
      14,
      getHighlightExpr(4, 14),
    ],
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      12,
      getHighlightExpr(0.5, 1),
      14,
      1,
    ],
    'circle-stroke-width': {
      stops: [
        [12, 0],
        [14, 1],
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
