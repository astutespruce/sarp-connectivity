export const maskFill = {
  id: 'sarp-mask',
  source: 'sarp',
  'source-layer': 'mask',
  type: 'fill',
  paint: {
    'fill-opacity': 0.6,
    'fill-color': '#AAA',
  },
}

export const maskOutline = {
  id: 'sarp-outline',
  source: 'sarp',
  'source-layer': 'boundary',
  type: 'line',
  paint: {
    'line-opacity': 0.8,
    'line-width': 2,
    'line-color': '#4A0025',
  },
}

// Used to capture click events from the unit layer
export const unitFill = {
  id: 'unit-fill',
  source: 'sarp',
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
  source: 'sarp',
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
      stops: [[4, 0.1], [8, 0.5]],
    },
    'line-color': '#0B1CF4',
  },
}

export const parentOutline = {
  id: 'unit-parent-outline',
  source: 'sarp',
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
      stops: [[4, 0.1], [8, 2]],
    },
    'line-color': '#0B1CF4',
  },
}

// highlight is visible at all scales
export const unitHighlightFill = {
  id: 'unit-highlight-fill',
  source: 'sarp',
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
  source: 'sarp',
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
    'line-color': '#fd8d3c',
  },
}

export const unitLayers = [unitFill, unitOutline]

export const unitHighlightLayers = [unitHighlightFill, unitHighlightOutline]

export const flowlinesLayer = {
  id: 'flowlines',
  source: 'dams_network',
  'source-layer': 'networks',
  minzoom: 9,
  type: 'line',
  paint: {
    'line-opacity': {
      base: 0,
      stops: [[10, 0.1], [12, 0.5], [14, 1]],
    },
    'line-width': {
      base: 0.1,
      stops: [[10, 0.1], [11, 0.5], [15, 1], [17, 1.5]],
    },
    'line-color': '#1891ac',
  },
}

export const networkHighlightLayer = {
  id: 'networks',
  // source: '', // set dynamically when map loads based on barrierType
  'source-layer': 'networks',
  minzoom: 9,
  type: 'line',
  filter: ['==', 'networkID', Infinity],
  paint: {
    'line-opacity': {
      base: 0,
      stops: [[10, 0.1], [11, 0.5], [14, 1], [16, 1]],
    },
    'line-width': {
      base: 0.1,
      stops: [[10, 0.1], [11, 1], [14, 2.5], [15, 3], [16, 4]],
    },
    'line-color': '#fd8d3c',
  },
}

export const backgroundPoint = {
  id: 'point-no-network',
  // source: "" // provided by specific layer
  'source-layer': 'background',
  type: 'circle',
  minzoom: 10,
  maxzoom: 24,
  paint: {
    'circle-color': '#999',
    'circle-radius': { stops: [[10, 0.5], [14, 4]] },
    'circle-opacity': { stops: [[10, 0.5], [14, 1]] },
    'circle-stroke-color': '#666',
    'circle-stroke-width': { stops: [[10, 0], [14, 1]] },
  },
}

// points filtered OUT with networks
export const excludedPoint = {
  id: 'point-excluded',
  // source: "" // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 7,
  maxzoom: 24,
  // filter:  [], // will be filtered using "in" or "!in"
  paint: {
    'circle-color': '#fbb4b9',
    'circle-stroke-color': '#c51b8a',
    'circle-radius': { stops: [[7, 0.5], [10, 4], [14, 6]] },
    'circle-opacity': { stops: [[10, 0.5], [14, 1]] },
    'circle-stroke-width': { stops: [[10, 0], [11, 0.25], [14, 1]] },
  },
}

// points filtered IN with networks
export const includedPoint = {
  id: 'point-included',
  // source: "" // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 5,
  maxzoom: 24,
  filter: ['==', 'id', 'Infinity'], // will be filtered using "in" or "!in"
  paint: {
    'circle-color': '#c51b8a',
    'circle-radius': { stops: [[5, 1], [6, 2], [14, 8]] },
    'circle-opacity': { stops: [[5, 0.2], [6, 0.5], [7, 1]] },
    'circle-stroke-color': '#FFFFFF',
    'circle-stroke-width': { stops: [[7, 0], [8, 0.25], [10, 1], [14, 3]] },
  },
}

export const topRank = {
  id: 'rank-top',
  source: 'ranked',
  type: 'circle',
  minzoom: 5,
  maxzoom: 24,
  // filter:  // provided by specific layer
  paint: {
    'circle-color': '#c51b8a',
    'circle-radius': { stops: [[5, 4], [6, 6], [14, 8]] },
    'circle-opacity': { stops: [[5, 0.5], [6, 1]] },
    'circle-stroke-color': '#FFFFFF',
    'circle-stroke-width': { stops: [[5, 2], [14, 3]] },
  },
}

export const lowerRank = {
  id: 'rank-low',
  source: 'ranked',
  type: 'circle',
  minzoom: 5,
  maxzoom: 24,
  // filter:  // provided by specific layer
  paint: {
    'circle-color': '#2c7fb8',
    'circle-stroke-color': '#FFFFFF',
    'circle-radius': { stops: [[5, 1], [7, 4], [10, 6], [14, 8]] },
    'circle-opacity': { stops: [[5, 0.5], [7, 0.5], [8, 1]] },
    'circle-stroke-width': { stops: [[5, 0], [8, 1], [14, 3]] },
  },
}

// NOTE: this is ONLY for displaying dams when small barriers are selected
export const damsSecondaryLayer = {
  id: 'dams-secondary',
  source: 'dams',
  'source-layer': 'dams',
  layout: {
    visibility: 'none',
  },
  type: 'circle',
  minzoom: 10,
  maxzoom: 24,
  paint: {
    'circle-color': '#fec44f',
    'circle-radius': { stops: [[10, 1], [12, 2], [14, 4], [16, 6]] },
    'circle-opacity': { stops: [[10, 0.25], [12, 0.5], [14, 1]] },
    'circle-stroke-color': '#FFFFFF',
    'circle-stroke-width': { stops: [[10, 0], [12, 1], [14, 2]] },
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
    'circle-color': '#2ca25f',
    'circle-radius': { stops: [[10, 1], [12, 2], [14, 4], [16, 6]] },
    'circle-opacity': { stops: [[10, 0.25], [12, 0.5], [14, 1]] },
    'circle-stroke-color': '#FFFFFF',
    'circle-stroke-width': { stops: [[10, 0], [12, 1], [14, 2]] },
  },
}

export const pointLegends = {
  included: {
    radius: 8,
    color: includedPoint.paint['circle-color'],
  },
  excluded: {
    radius: 6,
    color: `${excludedPoint.paint['circle-color']}99`,
    borderColor: `${excludedPoint.paint['circle-stroke-color']}99`,
    borderWidth: 1,
  },
  background: {
    radius: 5,
    color: backgroundPoint.paint['circle-color'],
    borderColor: backgroundPoint.paint['circle-stroke-color'],
    borderWidth: 1,
  },
  topRank: {
    radius: 8,
    color: topRank.paint['circle-color'],
  },
  lowerRank: {
    radius: 8,
    color: lowerRank.paint['circle-color'],
  },
  waterfalls: {
    radius: 6,
    color: waterfallsLayer.paint['circle-color'],
  },
  damsSecondary: {
    radius: 6,
    color: damsSecondaryLayer.paint['circle-color'],
  },
}

export const pointHighlight = {
  id: 'point-highlight',
  source: {
    type: 'geojson',
    data: null,
  },
  type: 'circle',
  minzoom: 5,
  maxzoom: 24,
  paint: {
    'circle-color': '#fd8d3c',
    'circle-radius': 14,
    'circle-stroke-width': 3,
    'circle-stroke-color': '#f03b20',
  },
}

const priorityFillStyle = {
  // id: // provided by specific layer
  source: 'sarp',
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
  source: 'sarp',
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
      stops: [[4, 0.1], [8, 0.5]],
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

const sebioPriorityFill = {
  ...priorityFillStyle,
  id: 'sebio-priority-fill',
  filter: ['>', 'sebio', 0],
  paint: {
    'fill-opacity': 0.4,
    'fill-color': [
      'match',
      ['get', 'sebio'],
      1,
      '#d95f0e',
      2,
      '#fec44f',
      '#FFF',
    ],
  },
}

const sebioPriorityOutline = {
  ...priorityOutlineStyle,
  id: 'sebio-priority-outline',
  filter: ['>', 'sebio', 0],
}

export const priorityWatersheds = [
  usfsPriorityFill,
  usfsPriorityOutline,
  coaPriorityFill,
  coaPriorityOutline,
  // sebioPriorityFill,
  // sebioPriorityOutline,
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
  sebio: {
    id: 'sebio',
    label: 'Southeast aquatic biodiversity hotspots',
    entries: [
      { color: '#d95f0e99', label: 'highest biodiversity' },
      { color: '#fec44f99', label: 'high biodiversity' },
    ],
  },
}
