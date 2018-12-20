export const LAYER_CONFIG = {
    HUC6: {
        title: "Basin",
        minzoom: 0,
        maxzoom: 24
    },
    HUC8: {
        minzoom: 7,
        maxzoom: 24,
        parent: "HUC6"
    },
    HUC12: {
        minzoom: 8.5,
        maxzoom: 24,
        parent: "HUC8"
    },
    State: {
        minzoom: 0,
        maxzoom: 24
    },
    County: {
        minzoom: 3,
        maxzoom: 24
    },
    ECO3: {
        minzoom: 0,
        maxzoom: 24
    },
    ECO4: {
        minzoom: 6,
        maxzoom: 24
    }
}

export default LAYER_CONFIG
