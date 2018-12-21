export const maskFill = {
    id: "sarp-mask",
    source: "sarp",
    "source-layer": "mask",
    type: "fill",
    paint: {
        "fill-opacity": 0.6,
        "fill-color": "#AAA"
    }
}

export const maskOutline = {
    id: "sarp-outline",
    source: "sarp",
    "source-layer": "boundary",
    type: "line",
    paint: {
        "line-opacity": 0.8,
        "line-width": 2,
        "line-color": "#4A0025"
    }
}

// Used to capture click events from the unit layer
export const unitFill = {
    id: "unit-fill",
    source: "sarp",
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

export const unitOutline = {
    id: "unit-outline",
    source: "sarp",
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
        "line-color": "#0B1CF4"
    }
}

export const parentOutline = {
    id: "unit-parent-outline",
    source: "sarp",
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
        "line-color": "#0B1CF4"
    }
}

// highlight is visible at all scales
export const unitHighlightFill = {
    id: "unit-highlight-fill",
    source: "sarp",
    // 'source-layer': '', // provided by specific layer
    type: "fill",
    minzoom: 0,
    maxzoom: 24,
    filter: ["==", "id", Infinity],
    paint: {
        "fill-opacity": 0.2,
        "fill-color": "#0B1CF4"
    }
}

export const unitHighlightOutline = {
    id: "unit-highlight-outline",
    type: "line",
    source: "sarp",
    // 'source-layer': '', // provided by specific layer
    minzoom: 0,
    maxzoom: 24,
    layout: {
        "line-cap": "round",
        "line-join": "round"
    },
    filter: ["==", "id", Infinity],
    paint: {
        "line-opacity": 1,
        "line-width": 2,
        "line-color": "#fd8d3c"
    }
}

export const backgroundPoint = {
    id: "point-no-network",
    // soruce: "" // provided by specific layer
    // 'source-layer': '', // provided by specific layer
    type: "circle",
    minzoom: 10,
    maxzoom: 24,
    filter: ["==", "hasnetwork", false],
    layout: {
        visibility: "none"
    },
    paint: {
        "circle-color": { stops: [[10, "#AAA"], [14, "#999"]] },
        "circle-radius": { stops: [[10, 0.5], [14, 4]] },
        "circle-opacity": { stops: [[10, 0.5], [14, 1]] },
        "circle-stroke-color": "#666",
        "circle-stroke-width": { stops: [[10, 0], [14, 1]] }
    }
}

// points filtered OUT with networks
export const excludedPoint = {
    id: "point-excluded",
    // soruce: "" // provided by specific layer
    // 'source-layer': '', // provided by specific layer
    type: "circle",
    minzoom: 5,
    maxzoom: 24,
    // filter: compound filter, must include ["==", "hasnetwork", true]
    // layout: {
    //     visibility: "none"
    // },
    paint: {
        "circle-color": "#fbb4b9",
        "circle-radius": { stops: [[10, 0.5], [14, 6]] },
        "circle-opacity": { stops: [[10, 0.5], [14, 1]] },
        "circle-stroke-color": "#c51b8a",
        "circle-stroke-width": { stops: [[10, 0], [14, 1]] }
    }
}

// points filtered IN with networks
export const includedPoint = {
    id: "point-included",
    // soruce: "" // provided by specific layer
    // 'source-layer': '', // provided by specific layer
    type: "circle",
    minzoom: 5,
    maxzoom: 24,
    // filter: compound filter, must include ["==", "hasnetwork", true]
    // layout: {
    //     visibility: "none"
    // },
    paint: {
        "circle-color": "#c51b8a",
        "circle-radius": { stops: [[6, 4], [14, 8]] },
        "circle-opacity": { stops: [[5, 0.1], [6, 0.25], [7, 1]] },
        "circle-stroke-color": "#FFFFFF",
        "circle-stroke-width": { stops: [[6, 0.25], [10, 1], [14, 3]] }
    }
}

export const pointHighlight = {
    id: "point-highlight",
    // soruce: "" // provided by specific layer
    // 'source-layer': '', // provided by specific layer
    type: "circle",
    minzoom: 5,
    maxzoom: 24,
    filter: ["==", "id", Infinity],
    paint: {
        "circle-color": "#fd8d3c",
        "circle-radius": 14,
        "circle-stroke-width": 3,
        "circle-stroke-color": "#f03b20"
    }
}
