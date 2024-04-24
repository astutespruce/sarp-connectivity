import { pointColors } from 'config'
import { getHighlightExpr } from '../Map/util'

// ranked points with networks filtered IN
export const includedPointLayer = {
  id: 'point-included',
  source: 'road_crossings',
  'source-layer': 'road_crossings',
  type: 'circle',
  minzoom: 3,
  maxzoom: 24,
  filter: ['==', 'id', 'Infinity'], // will be filtered using "in" or "!in"
  paint: {
    'circle-color': getHighlightExpr(
      pointColors.included.color,
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      pointColors.included.color,
      pointColors.highlight.strokeColor
    ),
    'circle-radius':
      // interpolate has to be top-level
      [
        'interpolate',
        ['linear'],
        ['zoom'],
        3,
        getHighlightExpr(0.25, 2),
        6,
        getHighlightExpr(1.5, 5),
        8,
        getHighlightExpr(2, 5),
        12,
        getHighlightExpr(3, 14),
        14,
        getHighlightExpr(6, 14),
        16,
        getHighlightExpr(8, 14),
        18,
        getHighlightExpr(10, 14),
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
  source: 'road_crossings',
  'source-layer': 'road_crossings',
  type: 'circle',
  minzoom: 3,
  maxzoom: 24,
  // filter:  [], // will be filtered using "in" or "!in"
  paint: {
    'circle-color': getHighlightExpr(
      pointColors.excluded.color,
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      pointColors.excluded.strokeColor,
      pointColors.highlight.strokeColor
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      3,
      getHighlightExpr(0.25, 2),
      5,
      getHighlightExpr(0.75, 5),
      6,
      getHighlightExpr(1, 5),
      10,
      getHighlightExpr(2, 10),
      12,
      getHighlightExpr(2.5, 10),
      14,
      getHighlightExpr(4, 14),
      16,
      getHighlightExpr(8, 14),
      18,
      getHighlightExpr(10, 14),
    ],
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      3,
      getHighlightExpr(0.5, 1),
      5,
      getHighlightExpr(0.75, 1),
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

// all other barrier point layers are small_barriers
export const rankedPointLayer = {
  id: 'point-ranked',
  source: 'small_barriers',
  'source-layer': 'ranked_small_barriers',
  type: 'circle',
  minzoom: 10,
  maxzoom: 24,
  paint: {
    'circle-color': getHighlightExpr(
      pointColors.offNetwork.color, // FIXME:
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      pointColors.offNetwork.strokeColor, // FIXME:
      pointColors.highlight.strokeColor
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      10,
      getHighlightExpr(0.5, 2),
      12,
      getHighlightExpr(2, 14),
      14,
      getHighlightExpr(3, 14),
      16,
      getHighlightExpr(4, 14),
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

// unranked points include everything that was included in network analysis
// but not prioritized; right now this is only invasive barriers (symbol=4)
export const unrankedPointLayer = {
  id: 'point-unranked',
  source: 'small_barriers',
  'source-layer': 'unranked_small_barriers',
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
      getHighlightExpr(0.5, 2),
      12,
      getHighlightExpr(2, 14),
      14,
      getHighlightExpr(3, 14),
      16,
      getHighlightExpr(4, 14),
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
  source: 'small_barriers',
  'source-layer': 'removed_small_barriers',
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
      12,
      getHighlightExpr(2, 14),
      14,
      getHighlightExpr(3, 14),
      16,
      getHighlightExpr(4, 14),
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

// Other barriers are those that are not ranked and not marked as unranked;
// they include: off-network barriers, non-barriers, minor barriers
export const otherBarrierPointLayer = {
  id: 'point-other',
  source: 'small_barriers',
  'source-layer': 'other_small_barriers',
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
      12,
      getHighlightExpr(2, 14),
      14,
      getHighlightExpr(3, 14),
      16,
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
