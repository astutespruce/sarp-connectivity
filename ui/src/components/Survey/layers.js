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
      [
        'match',
        ['get', 'symbol'],
        1, // unsnapped
        pointColors.offNetwork.color,
        2, // non-barrier
        pointColors.nonBarrier.color,
        3, // minor barrier
        pointColors.minorBarrier.color,
        4, // invasive barrier (should mostly be handled in unranked layer)
        pointColors.invasive.color,
        5, // removed barrier
        pointColors.removed.color,
        // last entry is default (0/1)
        pointColors.included.color,
      ],
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
        getHighlightExpr(0.05, 2),
        6,
        getHighlightExpr(0.25, 5),
        8,
        getHighlightExpr(0.5, 5),
        12,
        getHighlightExpr(2.5, 14),
        14,
        getHighlightExpr(4, 14),
        16,
        getHighlightExpr(6, 14),
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
    'circle-stroke-width': [
      'interpolate',
      ['linear'],
      ['zoom'],
      3,
      getHighlightExpr(0.5, 0.5),
      6,
      getHighlightExpr(0.75, 0.75),
      8,
      getHighlightExpr(1.5, 1),
      12,
      getHighlightExpr(2, 1),
      14,
      getHighlightExpr(3, 1),
      16,
      getHighlightExpr(4, 1),
    ],
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
