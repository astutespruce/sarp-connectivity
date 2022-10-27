import { pointColors } from 'constants'
import { getHighlightExpr } from '../Map/util'

export const maskFill = {
  id: 'mask',
  source: 'summary',
  'source-layer': 'mask',
  type: 'fill',
  filter: ['==', ['get', 'id'], 'total'],
  paint: {
    'fill-opacity': 0.6,
    'fill-color': '#AAA',
  },
}

export const maskOutline = {
  id: 'mask-outline',
  source: 'summary',
  'source-layer': 'boundary',
  type: 'line',
  filter: ['==', ['get', 'id'], 'total'],
  paint: {
    'line-opacity': 0.8,
    'line-width': 2,
    'line-color': '#4A0025',
  },
}

// Used to capture click events from the unit layer
export const unitFill = {
  id: 'unit-fill',
  source: 'summary',
  // 'source-layer': '', // provided by specific layer
  // minzoom: 0, // provided by specific layer
  // maxzoom: 24, // provided by specific layer
  type: 'fill',
  layout: {
    visibility: 'none',
  },
  paint: {
    'fill-color': '#BBB',
  },
}

export const unitOutline = {
  id: 'unit-outline',
  source: 'summary',
  // 'source-layer': '', // provided by specific layer
  // minzoom: 0, // provided by specific layer
  // maxzoom: 24, // provided by specific layer
  type: 'line',
  layout: {
    visibility: 'none',
    'line-cap': 'round',
    'line-join': 'round',
  },
  paint: {
    'line-opacity': 1,
    'line-width': {
      base: 0.1,
      stops: [
        [4, 0.1],
        [8, 0.5],
      ],
    },
    'line-color': '#0B1CF4',
  },
}

export const parentOutline = {
  id: 'unit-parent-outline',
  source: 'summary',
  // 'source-layer': '', // provided by specific layer
  // minzoom: 0, // provided by specific layer
  // maxzoom: 24, // provided by specific layer
  type: 'line',
  layout: {
    visibility: 'none',
    'line-cap': 'round',
    'line-join': 'round',
  },
  paint: {
    'line-opacity': 1,
    'line-width': {
      base: 1,
      stops: [
        [4, 0.1],
        [8, 2],
      ],
    },
    'line-color': '#0B1CF4',
  },
}

// highlight is visible at all scales
export const unitHighlightFill = {
  id: 'unit-highlight-fill',
  source: 'summary',
  // 'source-layer': '', // provided by specific layer
  type: 'fill',
  minzoom: 0,
  maxzoom: 24,
  layout: {
    visibility: 'none',
  },
  filter: ['==', 'id', Infinity],
  paint: {
    'fill-opacity': 0.2,
    'fill-color': '#0B1CF4',
  },
}

export const unitHighlightOutline = {
  id: 'unit-highlight-outline',
  type: 'line',
  source: 'summary',
  // 'source-layer': '', // provided by specific layer
  minzoom: 0,
  maxzoom: 24,
  layout: {
    visibility: 'none',
    'line-cap': 'round',
    'line-join': 'round',
  },
  filter: ['==', 'id', Infinity],
  paint: {
    'line-opacity': 1,
    'line-width': 2,
    'line-color': '#000',
  },
}

export const unitLayers = [unitFill, unitOutline]

export const unitHighlightLayers = [unitHighlightFill, unitHighlightOutline]

export const offnetworkPoint = {
  id: 'point-no-network',
  // id: '', // provided by specific layer
  // source: "", // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 10,
  maxzoom: 24,
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

export const unrankedPoint = {
  id: 'point-no-network',
  // id: '', // provided by specific layer
  // source: "", // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 10,
  maxzoom: 24,
  paint: {
    'circle-color': '#999',
    'circle-radius': {
      stops: [
        [10, 0.5],
        [14, 4],
      ],
    },
    'circle-opacity': {
      stops: [
        [10, 0.5],
        [14, 1],
      ],
    },
    'circle-stroke-color': '#666',
    'circle-stroke-width': {
      stops: [
        [10, 0],
        [14, 1],
      ],
    },
  },
}

// ranked points with networks filtered IN
export const excludedPoint = {
  id: 'point-excluded',
  // source: "" // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 4,
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
      4,
      getHighlightExpr(0.5, 2),
      5,
      getHighlightExpr(1, 5),
      9,
      getHighlightExpr(2, 10),
      14,
      getHighlightExpr(6, 14),
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
        [11, 0.25],
        [14, 1],
      ],
    },
  },
}

// ranked points with networks filtered IN
export const includedPoint = {
  id: 'point-included',
  // source: "" // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 2,
  maxzoom: 24,
  filter: ['==', 'id', 'Infinity'], // will be filtered using "in" or "!in"
  paint: {
    'circle-color': getHighlightExpr(
      pointColors.included.color,
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      pointColors.included.strokeColor,
      pointColors.highlight.strokeColor
    ),
    'circle-radius':
      // interpolate has to be top-level
      [
        'interpolate',
        ['linear'],
        ['zoom'],
        3,
        getHighlightExpr(0.5, 2),
        4,
        getHighlightExpr(1, 4),
        5,
        getHighlightExpr(1.25, 5),
        14,
        getHighlightExpr(8, 14),
      ],
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      2,
      getHighlightExpr(0.1, 1),
      3,
      getHighlightExpr(0.5, 1),
      4,
      getHighlightExpr(0.75, 1),
      7,
      1,
    ],

    'circle-stroke-width': {
      stops: [
        [7, 0],
        [8, 0.25],
        [10, 1],
        [14, 3],
      ],
    },
  },
}

export const topRank = {
  id: 'rank-top',
  source: 'ranked',
  type: 'circle',
  minzoom: 3,
  maxzoom: 24,
  // filter:  // provided by specific layer
  paint: {
    'circle-color': getHighlightExpr(
      pointColors.topRank.color,
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      pointColors.topRank.strokeColor,
      pointColors.highlight.strokeColor
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      3,
      getHighlightExpr(1, 3),
      4,
      getHighlightExpr(1.5, 4),
      5,
      getHighlightExpr(3, 5),
      14,
      getHighlightExpr(10, 14),
    ],
    'circle-opacity': 1,
    'circle-stroke-width': {
      stops: [
        [4, 0],
        [6, 0.25],
        [8, 0.5],
        [14, 3],
      ],
    },
  },
}

export const lowerRank = {
  id: 'rank-low',
  source: 'ranked',
  type: 'circle',
  minzoom: 3,
  maxzoom: 24,
  // filter:  // provided by specific layer
  paint: {
    'circle-color': getHighlightExpr(
      pointColors.lowerRank.color,
      pointColors.highlight.color
    ),
    'circle-stroke-color': getHighlightExpr(
      pointColors.lowerRank.strokeColor,
      pointColors.highlight.strokeColor
    ),
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      3,
      getHighlightExpr(0.5, 3),
      4,
      getHighlightExpr(1, 4),
      5,
      getHighlightExpr(1.25, 5),
      14,
      getHighlightExpr(8, 14),
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
        [10, 0],
        [11, 0.25],
        [14, 1],
      ],
    },
  },
}

// NOTE: this is ONLY for displaying dams when small barriers are selected
export const damsSecondaryLayer = {
  id: 'dams-secondary',
  source: 'dams',
  'source-layer': 'ranked_dams',
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
      getHighlightExpr(6, 14),
    ],
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      10,
      getHighlightExpr(0.25, 1),
      12,
      getHighlightExpr(0.5, 1),
      14,
      1,
    ],
    'circle-stroke-width': {
      stops: [
        [10, 0],
        [12, 1],
        [14, 2],
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
      getHighlightExpr(2, 14),
      14,
      getHighlightExpr(4, 14),
      16,
      getHighlightExpr(6, 14),
    ],
    'circle-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      10,
      getHighlightExpr(0.25, 1),
      12,
      getHighlightExpr(0.5, 1),
      14,
      1,
    ],
    'circle-stroke-width': {
      stops: [
        [10, 0],
        [12, 1],
        [14, 2],
      ],
    },
  },
}

export const pointLegends = {
  included: {
    radius: 8,
    color: pointColors.included.color,
  },
  excluded: {
    radius: 6,
    color: `${pointColors.excluded.color}99`,
    borderColor: `${pointColors.excluded.strokeColor}99`,
    borderWidth: 1,
  },
  offnetwork: {
    radius: 5,
    color: pointColors.offNetwork.color,
    borderColor: pointColors.offNetwork.strokeColor,
    borderWidth: 1,
  },
  topRank: {
    radius: 8,
    color: pointColors.topRank.color,
  },
  lowerRank: {
    radius: 8,
    color: pointColors.lowerRank.color,
  },
  waterfalls: {
    radius: 6,
    color: pointColors.waterfalls.color,
  },
  damsSecondary: {
    radius: 6,
    color: pointColors.damsSecondary.color,
  },
}

const priorityFillStyle = {
  // id: // provided by specific layer
  source: 'summary',
  'source-layer': 'HUC8',
  type: 'fill',
  minzoom: 0,
  maxzoom: 24,
  layout: {
    visibility: 'none',
  },
  // filter: // provided by specific layer
  // paint: // provided by specific layer
}

const priorityOutlineStyle = {
  // id: // provided by specific layer
  'source-layer': 'HUC8',
  source: 'summary',
  type: 'line',
  minzoom: 0,
  maxzoom: 24,
  layout: {
    visibility: 'none',
  },
  // filter: // provided by specific layer
  paint: {
    'line-opacity': 0.2,
    'line-width': {
      base: 0.1,
      stops: [
        [4, 0.1],
        [8, 0.5],
      ],
    },
    'line-color': '#AAAAAA',
  },
}

const usfsPriorityFill = {
  ...priorityFillStyle,
  id: 'usfs-priority-fill',
  filter: ['>', 'usfs', 0],
  paint: {
    'fill-opacity': 0.4,
    'fill-color': [
      'match',
      ['get', 'usfs'],
      1,
      '#31a354',
      2,
      '#addd8e',
      3,
      '#f7fcb9',
      '#FFF',
    ],
  },
}

const usfsPriorityOutline = {
  ...priorityOutlineStyle,
  id: 'usfs-priority-outline',
  filter: ['>', 'usfs', 0],
}

const coaPriorityFill = {
  ...priorityFillStyle,
  id: 'coa-priority-fill',
  filter: ['>', 'coa', 0],
  paint: {
    'fill-opacity': 0.4,
    'fill-color': '#3182bd',
  },
}

const coaPriorityOutline = {
  ...priorityOutlineStyle,
  id: 'coa-priority-outline',
  filter: ['>', 'coa', 0],
}

const sgcnPriorityFill = {
  ...priorityFillStyle,
  id: 'sgcn-priority-fill',
  filter: ['>', 'sgcn', 0],
  paint: {
    'fill-opacity': 0.4,
    'fill-color': '#d95f0e',
  },
}

const sgcnPriorityOutline = {
  ...priorityOutlineStyle,
  id: 'sgcn-priority-outline',
  filter: ['>', 'sgcn', 0],
}

export const priorityWatersheds = [
  usfsPriorityFill,
  usfsPriorityOutline,
  coaPriorityFill,
  coaPriorityOutline,
  sgcnPriorityFill,
  sgcnPriorityOutline,
]

export const priorityWatershedLegends = {
  usfs: {
    id: 'usfs',
    label: 'USFS Priority',
    entries: [
      {
        color: '#31a35499',
        label: 'highest',
      },
      {
        color: '#addd8e99',
        label: 'moderate',
      },
      {
        color: '#f7fcb999',
        label: 'lowest',
      },
    ],
  },
  coa: {
    id: 'coa',
    entries: [
      {
        color: '#3182bd99',
        label: 'SARP conservation opportunity areas',
      },
    ],
  },
  sgcn: {
    id: 'sgcn',
    entries: [
      {
        color: '#d95f0e99',
        label:
          'Watersheds with most Species of Greatest Conservation Need (SGCN) per state',
      },
    ],
  },
}
