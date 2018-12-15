import { List } from "immutable"

export const TILE_HOST =
    process.env.NODE_ENV === "production"
        ? `${window.location.protocol}//${window.location.host}`
        : "http://localhost:8000"

// Bounds around all selected HUC6s
export const SARP_BOUNDS = List([-107.87000919, 17.62370026, -64.5126611, 44.26093852])

// from colorbrewer
export const COUNT_COLORS = [
    "#ffffcc",
    "#ffeda0",
    "#fed976",
    "#feb24c",
    "#fd8d3c",
    "#fc4e2a",
    "#e31a1c",
    "#bd0026",
    "#800026"
]

export const COLORS = {
    count: {
        // http://colorbrewer2.org/#type=sequential&scheme=YlOrRd&n=9
        9: ["#ffffcc", "#ffeda0", "#fed976", "#feb24c", "#fd8d3c", "#fc4e2a", "#e31a1c", "#bd0026", "#800026"],
        7: ["#ffffb2", "#fed976", "#feb24c", "#fd8d3c", "#fc4e2a", "#e31a1c", "#b10026"],
        5: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"]
    }
}

// there are 20 tiers
// Viridis_20 from palettable
export const TIER_COLORS = [
    "#440154",
    "#481467",
    "#482677",
    "#453781",
    "#3F4788",
    "#39558C",
    "#32648E",
    "#2D718E",
    "#287D8E",
    "#238A8D",
    "#1F968B",
    "#20A386",
    "#29AF7F",
    "#3BBB75",
    "#56C667",
    "#73D056",
    "#95D840",
    "#B8DE29",
    "#DDE318",
    "#FDE725"
] // TODO: may need to be reversed

// from colorbrewer: http://colorbrewer2.org/#type=sequential&scheme=BuPu&n=5
export const PRIORITY_TIER_COLORS = ["#edf8fb", "#b3cde3", "#8c96c6", "#8856a7", "#810f7c"].reverse()

export const SYSTEMS = {
    ADM: "State / County",
    HUC: "Hydrologic unit",
    ECO: "Ecoregion"
}

export const SCENARIOS = {
    NC: "Network Connnectivity",
    WC: "Watershed Condition",
    NCWC: "Combined"
}

export const LAYER_CONFIG = [
    {
        id: "HUC6",
        group: "HUC",
        title: "Basin",
        minzoom: 0,
        maxzoom: 6.5,
        bins: {
            dams: [100, 500, 750, 1000, 1500, 2000, 2500, 5000, 25000],
            barriers: [10, 100, 200, 300, 500, 1000, 2500]
        },
        fill: {
            minzoom: 0,
            maxzoom: 7,
            paint: {
                "fill-opacity": {
                    base: 0.25,
                    stops: [[2, 0.4], [4, 0.25], [6, 0.25], [7, 0]]
                }
            }
        },
        outline: {
            minzoom: 0,
            maxzoom: 9.5,
            paint: {
                "line-width": {
                    base: 0.1,
                    stops: [[4, 0.1], [5, 0.25], [6, 0.5], [6.5, 1.5], [8, 2], [9, 4], [12, 6]]
                }
            }
        }
    },
    {
        id: "HUC8",
        group: "HUC",
        minzoom: 6.5,
        maxzoom: 9,
        title: "Hydrologic subbasin",
        bins: {
            dams: [10, 50, 100, 200, 250, 300, 400, 500, 5000],
            barriers: [25, 50, 100, 150, 1500]
        },
        fill: {
            minzoom: 6,
            maxzoom: 9.5,
            paint: {
                "fill-opacity": {
                    base: 0.25,
                    stops: [[6, 0], [7, 0.25], [8.5, 0.25], [9.5, 0]]
                }
            }
        },
        outline: {
            minzoom: 6,
            maxzoom: 24,
            paint: {
                "line-width": {
                    base: 0.1,
                    stops: [[6, 0.1], [8, 0.5], [8, 1.5], [9, 2.5]]
                }
            }
        }
    },
    {
        id: "HUC12",
        group: "HUC",
        minzoom: 8.5,
        maxzoom: 24,
        title: "Subwatershed",
        bins: {
            dams: [1, 10, 25, 100, 200],
            barriers: [1, 10, 25, 100, 200]
        },
        fill: {
            minzoom: 8.5,
            maxzoom: 24,
            paint: {
                "fill-opacity": {
                    base: 0.25,
                    stops: [[8.5, 0], [9.5, 0.25], [11, 0.25], [12, 0.15]]
                }
            }
        },
        outline: {
            minzoom: 8.5,
            maxzoom: 24,
            paint: {
                "line-width": {
                    base: 0.1,
                    stops: [[9, 0.1], [9.5, 0.5]]
                }
            }
        }
    },
    {
        id: "ECO3",
        group: "ECO",
        minzoom: 0,
        maxzoom: 6,
        title: "Level 3 Ecoregion",
        bins: {
            dams: [100, 250, 500, 1000, 2500, 5000, 7500, 10000, 25000],
            barriers: [10, 100, 250, 500, 1000, 2500, 10000]
        },
        fill: {
            minzoom: 0,
            maxzoom: 7,
            paint: {
                "fill-opacity": {
                    base: 0.25,
                    stops: [[2, 0.4], [4, 0.25], [6, 0.25], [7, 0]]
                }
            }
        },
        outline: {
            minzoom: 0,
            maxzoom: 12,
            paint: {
                "line-width": {
                    base: 0.1,
                    stops: [[4, 0.1], [5, 0.25], [6, 0.5], [6.5, 1.5], [8, 2], [9, 4], [12, 6]]
                }
            }
        }
    },
    {
        id: "ECO4",
        group: "ECO",
        minzoom: 6,
        maxzoom: 24,
        title: "Level 4 Ecoregion",
        bins: {
            dams: [10, 100, 250, 500, 750, 1000, 1500, 2000, 10000],
            barriers: [10, 50, 100, 250, 500, 1000, 2000]
        },
        fill: {
            minzoom: 6,
            maxzoom: 24,
            paint: {
                "fill-opacity": {
                    base: 0.25,
                    stops: [[6, 0], [7, 0.25], [11, 0.25], [12, 0.15]]
                }
            }
        },
        outline: {
            minzoom: 6,
            maxzoom: 24,
            paint: {
                "line-width": {
                    base: 0.1,
                    stops: [[6, 0.1], [8, 0.5], [10, 1], [12, 1.5]]
                }
            }
        }
    },
    {
        id: "State",
        group: "ADM",
        minzoom: 0,
        maxzoom: 6.5,
        title: "State",
        bins: {
            dams: [500, 1000, 5000, 10000, 15000, 20000, 25000],
            barriers: [100, 250, 500, 1000, 2500, 5000, 10000]
        },
        fill: {
            minzoom: 0,
            maxzoom: 7,
            paint: {
                "fill-opacity": {
                    base: 0.25,
                    stops: [[2, 0.4], [4, 0.25], [6, 0.25], [7, 0]]
                }
            }
        },
        outline: {
            minzoom: 0,
            maxzoom: 12,
            paint: {
                "line-width": {
                    base: 0.1,
                    stops: [[4, 0.1], [5, 0.25], [6, 0.5], [6.5, 1.5], [8, 2], [9, 4], [12, 6]]
                }
            }
        }
    },
    {
        id: "County",
        group: "ADM",
        minzoom: 6.5,
        maxzoom: 24,
        title: "County",
        bins: {
            dams: [10, 50, 100, 250, 1000],
            barriers: [10, 25, 50, 100, 500]
        },
        fill: {
            minzoom: 6,
            maxzoom: 24,
            paint: {
                "fill-opacity": {
                    base: 0.25,
                    stops: [[6, 0], [7, 0.25], [11, 0.25], [12, 0.15]]
                }
            }
        },
        outline: {
            minzoom: 6,
            maxzoom: 24,
            paint: {
                "line-width": {
                    base: 0.1,
                    stops: [[6, 0.1], [8, 0.5], [10, 1], [12, 1.5]]
                }
            }
        }
    }
]
