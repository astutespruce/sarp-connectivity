import { pointColors } from 'config'
import { getHighlightExpr, getTierExpr } from '../Map/util'

export const getTierPointColor = (scenario, tierThreshold) =>
  getHighlightExpr(
    getTierExpr(
      scenario,
      tierThreshold,
      [
        'match',
        ['get', 'barriertype'],
        'small_barriers',
        pointColors.topRank.smallBarriersColor,
        pointColors.topRank.color,
      ],
      [
        'match',
        ['get', 'barriertype'],
        'small_barriers',
        pointColors.lowerRank.smallBarriersColor,
        pointColors.lowerRank.color,
      ]
    ),
    pointColors.highlight.color
  )

// sizes fall back to match includedPoint when not top rank
export const getTierPointSize = (scenario, tierThreshold) => [
  'interpolate',
  ['linear'],
  ['zoom'],
  3,
  getHighlightExpr(getTierExpr(scenario, tierThreshold, 1, 0.75), 3),
  4,
  getHighlightExpr(getTierExpr(scenario, tierThreshold, 1.5, 1.25), 4),
  5,
  getHighlightExpr(
    getTierExpr(
      scenario,
      tierThreshold,
      ['match', ['get', 'barriertype'], 'small_barriers', 2, 3],
      1.25
    ),
    5
  ),
  14,
  getHighlightExpr(
    getTierExpr(
      scenario,
      tierThreshold,
      ['match', ['get', 'barriertype'], 'small_barriers', 8, 10],
      4
    ),
    14
  ),
]

// ranked points with networks filtered IN
export const includedPointLayer = {
  id: 'point-included',
  // source: "" // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 3,
  maxzoom: 24,
  filter: ['==', 'id', 'Infinity'], // will be filtered using "in" or "!in"
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
    'circle-radius':
      // interpolate has to be top-level
      [
        'interpolate',
        ['linear'],
        ['zoom'],
        3,
        getHighlightExpr(
          ['match', ['get', 'barriertype'], 'small_barriers', 0.25, 0.5],
          2
        ),
        5,
        getHighlightExpr(
          ['match', ['get', 'barriertype'], 'small_barriers', 1.5, 2],
          5
        ),
        14,
        getHighlightExpr(
          ['match', ['get', 'barriertype'], 'small_barriers', 6, 8],
          14
        ),
      ],
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      3,
      getHighlightExpr(0.5, 1),
      4,
      getHighlightExpr(0.75, 1),
      7,
      1,
    ],

    'circle-stroke-width': {
      stops: [
        [7, 0.1],
        [8, 0.25],
        [10, 1],
        [14, 2],
      ],
    },
  },
}

// ranked points with networks filtered OUT
export const excludedPointLayer = {
  id: 'point-excluded',
  // source: "" // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 4,
  maxzoom: 24,
  // filter:  [], // will be filtered using "in" or "!in"
  paint: {
    'circle-color': getHighlightExpr(
      [
        'match',
        ['get', 'barriertype'],
        'small_barriers',
        pointColors.excluded.smallBarriersColor,
        pointColors.excluded.color,
      ],
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      [
        'match',
        ['get', 'barriertype'],
        'small_barriers',
        pointColors.excluded.smallBarriersStrokeColor,
        pointColors.excluded.strokeColor,
      ],
      pointColors.highlight.strokeColor
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      4,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 0.25, 0.5],
        2
      ),
      5,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 0.5, 1],
        5
      ),
      9,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 1, 2],
        10
      ),
      14,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 4, 6],
        14
      ),
    ],
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      10,
      getHighlightExpr(0.5, 1),
      12,
      1,
    ],
    'circle-stroke-width': {
      stops: [
        [10, 0],
        [11, 0.25],
        [14, 1],
      ],
    },
  },
}

// unranked points include everything that was included in network analysis
// but not prioritized; right now this is only invasive barriers (symbol=4)
export const unrankedPointLayer = {
  id: 'point-unranked',
  // source: "", // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 10,
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
      10,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 0.25, 0.5],
        2
      ),
      14,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 2.5, 4],
        14
      ),
    ],
    'circle-opacity': 1,
    'circle-stroke-width': {
      stops: [
        [10, 0],
        [14, 1],
      ],
    },
  },
}

// Other barriers are those that are not ranked and not marked as unranked;
// they include: off-network barriers, non-barriers, minor barriers, removed barriers
export const removedBarrierPointLayer = {
  id: 'point-removed',
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
      10,
      getHighlightExpr(0.5, 2),
      14,
      getHighlightExpr(4, 14),
    ],
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      10,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 0.25, 0.5],
        1
      ),
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

// Other barriers are those that are not ranked and not marked as unranked;
// they include: off-network barriers, non-barriers, minor barriers
export const otherBarrierPointLayer = {
  id: 'point-other',
  // source: "", // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 10,
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
      10,
      getHighlightExpr(0.5, 2),
      14,
      getHighlightExpr(4, 14),
    ],
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      10,
      getHighlightExpr(
        ['match', ['get', 'barriertype'], 'small_barriers', 0.25, 0.5],
        1
      ),
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

export const prioritizedPointLayer = {
  id: 'point-prioritized',
  // source: "" // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 3,
  maxzoom: 24,
  layout: {
    visibility: 'none',
  },
  // filter:  // set to match includedPoint above
  paint: {
    'circle-color': '#000000', // provided dynamically when added to map
    'circle-stroke-color': getHighlightExpr(
      pointColors.topRank.color,
      pointColors.highlight.strokeColor
    ),
    'circle-radius': 6, // provided dynamically when added to map
    'circle-opacity': 1,
    'circle-stroke-width': {
      stops: [
        // [4, 0],
        [6, 0],
        [8, 0.1],
        [14, 2],
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
      pointColors.roadCrossings.color,
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      pointColors.roadCrossings.strokeColor,
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

// NOTE: this is ONLY for displaying dams when small barriers type is selected
// (not combined barriers type)
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
        [12, 0.5],
      ],
    },
  },
}

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
      getHighlightExpr(3, 14),
      14,
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
