export const LAYER_CONFIG = [
    {
        id: "HUC6",
        group: "HUC",
        title: "Basin",
        minzoom: 0,
        maxzoom: 24
    },
    {
        id: "HUC8",
        group: "HUC",
        title: "Hydrologic subbasin",
        minzoom: 5,
        maxzoom: 24,
        parent: "HUC6"
    },
    {
        id: "HUC12",
        group: "HUC",
        title: "Subwatershed",
        minzoom: 7,
        maxzoom: 24,
        parent: "HUC8"
    },
    { id: "ECO3", group: "ECO", minzoom: 0, maxzoom: 6, title: "Level 3 Ecoregion" },
    { id: "ECO4", group: "ECO", minzoom: 6, maxzoom: 24, title: "Level 4 Ecoregion" },
    { id: "State", group: "ADM", minzoom: 0, maxzoom: 24, title: "State" }
]

export default LAYER_CONFIG
