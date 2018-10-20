export const TILE_HOST = process.env.NODE_ENV === "production" ? "http://34.237.24.48:8000" : "http://localhost:8000"

export const COUNT_COLORS = [
    "#fff7ec",
    "#fee8c8",
    "#fdd49e",
    "#fdbb84",
    "#fc8d59",
    "#ef6548",
    "#d7301f",
    "#b30000",
    "#7f0000"
]

// export const FEATURE_ID_FIELD = {
//     HUC2: "HUC2",
//     HUC4: "HUC4",
//     HUC8: "HUC8",
//     ecoregion3: "NA_L3CODE",
//     ecoregion4: "US_L4CODE"
// }

// export const ZOOM_LEVELS = {
//     HUC2: [0, 4.5],
//     HUC4: [4.5, 6],
//     HUC8: [6, 21],
//     ecoregion3: [0, 6],
//     ecoregion4: [6, 21]
// }

// export const SYSTEM_LEVELS = {
//     HUC: ["HUC2", "HUC4", "HUC8"],
//     ecoregion: ["ecoregion3", "ecoregion4"]
// }

// export const LEVEL_LABELS = {
//     HUC2: "Hydrologic region",
//     HUC4: "Hydrologic subregion",
//     HUC8: "Hydrologic subbasin",
//     ecoregion3: "Level 3 Ecoregion",
//     ecoregion4: "Level 4 Ecoregion"
// }

export const LAYER_CONFIG = [
    { id: "HUC2", group: "HUC", minzoom: 0, maxzoom: 4.5, title: "Hydrologic region" },
    { id: "HUC4", group: "HUC", minzoom: 4.5, maxzoom: 6, title: "Hydrologic subregion" },
    { id: "HUC8", group: "HUC", minzoom: 6, maxzoom: 21, title: "Hydrologic subbasin" },
    { id: "ECO3", group: "ECO", minzoom: 0, maxzoom: 6, title: "Level 3 Ecoregion" },
    { id: "ECO4", group: "ECO", minzoom: 6, maxzoom: 21, title: "Level 4 Ecoregion" },
    { id: "states", group: "states", minzoom: 0, maxzoom: 21, title: "State" }
]
