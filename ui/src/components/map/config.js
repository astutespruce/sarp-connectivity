import { List } from "immutable"

export const TILE_HOST =
    process.env.NODE_ENV === "production"
        ? `${window.location.protocol}//${window.location.host}`
        : "http://localhost:8000"

export const SARP_BOUNDS = List([-106.645646, 17.623468, -64.512674, 40.61364])

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

export const LAYER_CONFIG = [
    { id: "HUC2", group: "HUC", minzoom: 0, maxzoom: 4.5, title: "Hydrologic region" },
    // { id: "HUC4", group: "HUC", minzoom: 4.5, maxzoom: 5, title: "Hydrologic subregion" },
    { id: "HUC6", group: "HUC", minzoom: 4.5, maxzoom: 6, title: "Hydrologic basin" },
    // { id: "HUC8", group: "HUC", minzoom: 6, maxzoom: 7, title: "Hydrologic subbasin" },
    { id: "HUC10", group: "HUC", minzoom: 6, maxzoom: 21, title: "Hydrologic watershed" },
    { id: "ECO3", group: "ECO", minzoom: 0, maxzoom: 6, title: "Level 3 Ecoregion" },
    { id: "ECO4", group: "ECO", minzoom: 6, maxzoom: 21, title: "Level 4 Ecoregion" },
    { id: "State", group: "ADM", minzoom: 0, maxzoom: 21, title: "State" }
]
