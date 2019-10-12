export const COLORS = {
  count: {
    // http://colorbrewer2.org/#type=sequential&scheme=YlOrRd&n=9
    9: [
      '#ffffcc',
      '#ffeda0',
      '#fed976',
      '#feb24c',
      '#fd8d3c',
      '#fc4e2a',
      '#e31a1c',
      '#bd0026',
      '#800026',
    ],
    7: [
      '#ffffb2',
      '#fed976',
      '#feb24c',
      '#fd8d3c',
      '#fc4e2a',
      '#e31a1c',
      '#b10026',
    ],
    5: ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026'],
  },
}

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
      maxzoom: 10,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [[6, 0.1], [7, 0.25], [9, 0.25], [10, 0.1]],
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
      minzoom: 10,
      maxzoom: 24,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [[10, 0.1], [11, 0.25], [12, 0.15]],
        },
      },
    },
    outline: {
      minzoom: 10,
      maxzoom: 24,
      paint: {
        'line-width': {
          base: 0.1,
          stops: [[9, 0.1], [9.5, 0.5]],
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
          stops: [[7, 0.1], [8, 0.25], [11, 0.25], [12, 0.15]],
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
    id: 'County',
    system: 'ADM',
    title: 'County',
    bins: {
      dams: [10, 50, 100, 250, 1000],
      barriers: [10, 25, 50, 100, 500],
    },
    fill: {
      minzoom: 7,
      maxzoom: 24,
      paint: {
        'fill-opacity': {
          base: 0.25,
          stops: [[7, 0.1], [11, 0.25], [12, 0.15]],
        },
      },
    },
    outline: {
      minzoom: 7,
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
