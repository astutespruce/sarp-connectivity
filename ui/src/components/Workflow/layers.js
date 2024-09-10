import { getHighlightExpr } from '../Map/util'

export const maskFill = {
  id: 'mask',
  source: 'map_units',
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
  source: 'map_units',
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
  source: 'map_units',
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
  source: 'map_units',
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
  source: 'map_units',
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
  source: 'map_units',
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
  source: 'map_units',
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

const priorityAreasLayer = {
  // id: // provided by specific layer
  source: 'priority_areas',
  'source-layer': 'priority_areas',
  minzoom: 0,
  maxzoom: 24,
  layout: {
    visibility: 'none',
  },
  // filter: // provided based on toggle of specific subsets
}

const priorityAreasFillLayer = {
  ...priorityAreasLayer,
  id: 'priority_areas-fill',
  type: 'fill',
  paint: {
    'fill-opacity': 0.4,
    'fill-color': '#3182bd',
  },
}

const priorityAreasOutlineLayer = {
  ...priorityAreasLayer,
  id: 'priority_areas-outline',
  type: 'line',
  paint: {
    'line-opacity': getHighlightExpr(0.2, 1),
    'line-width': [
      'interpolate',
      ['linear'],
      ['zoom'],
      4,
      getHighlightExpr(0.1, 2),
      8,
      getHighlightExpr(0.5, 3),
    ],
    'line-color': getHighlightExpr('#AAAAAA', '#000000'),
  },
}

export const priorityAreaLayers = [
  priorityAreasFillLayer,
  priorityAreasOutlineLayer,
]
