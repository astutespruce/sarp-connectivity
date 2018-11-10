export const FILL_STYLE = {
    // id: '',  // provided by specific layer
    // source: 'sarp',  // provided by specific layer
    // 'source-layer': '', // provided by specific layer
    // minzoom: 0, // provided by specific layer
    // maxzoom: 24, // provided by specific layer
    type: "fill",
    // filter: [">=", "dams", 0],
    paint: {
        "fill-opacity": 0,
        "fill-color": "#FFF"
    }
}

export const OUTLINE_STYLE = {
    // id: '',  // provided by specific layer
    // source: 'sarp',  // provided by specific layer
    // 'source-layer': '', // provided by specific layer
    // minzoom: 0, // provided by specific layer
    // maxzoom: 24, // provided by specific layer
    type: "line",
    layout: {
        "line-cap": "round",
        "line-join": "round"
    },
    // filter: [">=", "dams", 0],
    paint: {
        "line-opacity": 1,
        "line-width": 0.5,
        "line-color": "#CC99A8" // last color of COUNT_COLORS, then lightened several shades
    }
}

export const PARENT_STYLE = {
    // id: '',  // provided by specific layer
    // source: 'sarp',  // provided by specific layer
    // 'source-layer': '', // provided by specific layer
    // minzoom: 0, // provided by specific layer
    // maxzoom: 24, // provided by specific layer
    type: "line",
    layout: {
        "line-cap": "round",
        "line-join": "round"
    },
    filter: [">=", "dams", 0],
    paint: {
        "line-opacity": 1,
        "line-width": 2,
        "line-color": "#CC99A8" // last color of COUNT_COLORS, then lightened several shades
    }
}

// highlight is visible at all scales
export const HIGHLIGHT_STYLE = {
    // id: '',  // provided by specific layer
    // source: 'sarp',  // provided by specific layer
    // 'source-layer': '', // provided by specific layer
    type: "fill",
    minzoom: 0,
    maxzoom: 24,
    filter: ["==", "id", Infinity],
    paint: {
        "fill-opacity": 0.5,
        "fill-color": "#CC99A8" // last color of COUNT_COLORS, then lightened several shades
    }
}
