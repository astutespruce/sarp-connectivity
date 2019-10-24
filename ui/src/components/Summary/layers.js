export const layers = [
  {
    id: 'HUC6',
    system: 'HUC',
    title: 'Basin',
    bins: {
      dams: [100, 500, 750, 1000, 1500, 2000, 2500, 5000, 25000],
      barriers: [10, 100, 200, 300, 500, 1000, 2500],
    },
    fill: {
      minzoom: 0,
      maxzoom: 6,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [[2, 0.4], [4, 0.25], [5, 0.25], [6, 0.1]],
        },
      },
    },
    outline: {
      minzoom: 0,
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
      dams: [10, 50, 100, 200, 250, 300, 400, 500, 5000],
      barriers: [25, 50, 100, 150, 1500],
    },
    fill: {
      minzoom: 6,
      maxzoom: 8,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [[6, 0.1], [7, 0.25], [8, 0.1]],
        },
      },
    },
    outline: {
      minzoom: 6,
      maxzoom: 24,
      paint: {
        'line-width': {
          base: 0.1,
          stops: [[6, 0.1], [8, 0.5], [8, 1.5], [9, 2.5]],
        },
      },
    },
  },
  {
    id: 'HUC12',
    system: 'HUC',
    title: 'Subwatershed',
    bins: {
      dams: [1, 10, 25, 100, 200],
      barriers: [1, 10, 25, 100, 200],
    },
    fill: {
      minzoom: 8,
      maxzoom: 24,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [[8, 0.1], [9, 0.25], [11, 0.25], [12, 0.15], [14, 0]],
        },
      },
    },
    outline: {
      minzoom: 8,
      maxzoom: 24,
      paint: {
        'line-width': {
          base: 0.1,
          stops: [[8, 0.1], [9.5, 0.5]],
        },
      },
    },
  },
  {
    id: 'ECO3',
    system: 'ECO',
    title: 'Level 3 Ecoregion',
    bins: {
      dams: [100, 250, 500, 1000, 2500, 5000, 7500, 10000, 25000],
      barriers: [10, 100, 250, 500, 1000, 2500, 10000],
    },
    fill: {
      minzoom: 0,
      maxzoom: 7,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [[2, 0.4], [4, 0.25], [6, 0.25], [7, 0.1]],
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
    id: 'ECO4',
    system: 'ECO',
    title: 'Level 4 Ecoregion',
    bins: {
      dams: [10, 100, 250, 500, 750, 1000, 1500, 2000, 10000],
      barriers: [10, 50, 100, 250, 500, 1000, 2000],
    },
    fill: {
      minzoom: 7,
      maxzoom: 24,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [[7, 0.1], [8, 0.25], [11, 0.25], [12, 0.15], [14, 0]],
        },
      },
    },
    outline: {
      minzoom: 6,
      maxzoom: 24,
      paint: {
        'line-width': {
          base: 0.1,
          stops: [[6, 0.1], [8, 0.5], [10, 1], [12, 1.5]],
        },
      },
    },
  },
  {
    id: 'State',
    system: 'ADM',
    title: 'State',
    bins: {
      dams: [500, 1000, 5000, 10000, 15000, 20000, 25000],
      barriers: [100, 250, 500, 1000, 2500, 5000, 10000],
    },
    fill: {
      minzoom: 0,
      maxzoom: 5,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [[2, 0.4], [4, 0.25], [6, 0.25], [7, 0.1]],
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
      dams: [10, 50, 100, 250, 1000],
      barriers: [10, 25, 50, 100, 500],
    },
    fill: {
      minzoom: 5,
      maxzoom: 24,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [[5, 0.1], [6, 0.25], [9, 0.25], [10, 0.15], [14, 0]],
        },
      },
    },
    outline: {
      minzoom: 5,
      maxzoom: 24,
      paint: {
        'line-width': {
          base: 0.1,
          stops: [[6, 0.1], [8, 0.5], [10, 1], [12, 1.5]],
        },
      },
    },
  },
]

// points filtered IN with networks
export const pointLayer = {
  // id: '' // provided by specific layer
  // source: "" // provided by specific layer
  // 'source-layer': '', // provided by specific layer
  type: 'circle',
  minzoom: 10,
  maxzoom: 24,
  paint: {
    'circle-color': '#c51b8a',
    'circle-radius': { stops: [[10, 1], [12, 2], [14, 4], [16, 8]] },
    'circle-opacity': { stops: [[10, 0.25], [12, 0.5], [14, 1]] },
    'circle-stroke-color': '#FFFFFF',
    'circle-stroke-width': { stops: [[10, 0], [12, 1], [14, 3]] },
  },
}

export const backgroundPointLayer = {
  // id: '', // provided by specific layer
  // source: "" // provided by specific layer
  'source-layer': 'background',
  type: 'circle',
  minzoom: 12,
  maxzoom: 24,
  paint: {
    'circle-color': '#999',
    'circle-radius': { stops: [[12, 1], [14, 3], [16, 6]] },
    'circle-opacity': { stops: [[12, 0.5], [14, 1]] },
    'circle-stroke-color': '#666',
    'circle-stroke-width': { stops: [[12, 0], [14, 1]] },
  },
}

export const pointLegends = {
  primary: {
    radius: 8,
    color: pointLayer.paint['circle-color'],
  },
  background: {
    radius: 6,
    color: backgroundPointLayer.paint['circle-color'],
    borderColor: backgroundPointLayer.paint['circle-stroke-color'],
    borderWidth: 1,
  },
}

export const pointHighlightLayer = {
  id: 'point-highlight',
  source: {
    type: 'geojson',
    data: null,
  },
  type: 'circle',
  minzoom: 12,
  maxzoom: 24,
  paint: {
    'circle-color': '#fd8d3c',
    'circle-radius': 14,
    'circle-stroke-width': 3,
    'circle-stroke-color': '#f03b20',
  },
}