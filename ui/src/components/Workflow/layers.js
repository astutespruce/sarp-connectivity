export const maskFill = {
  id: 'mask',
  source: 'region_boundaries',
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
  source: 'region_boundaries',
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

export const priorityWatersheds = [coaPriorityFill, coaPriorityOutline]

export const priorityWatershedLegends = {
  coa: {
    id: 'coa',
    entries: [
      {
        color: '#3182bd99',
        label: 'SARP conservation opportunity areas',
      },
    ],
  },
}
