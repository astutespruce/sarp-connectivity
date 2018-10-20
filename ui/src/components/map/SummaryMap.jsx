import React, { Component } from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"

import * as actions from "../../actions"
import Legend from "./Legend"
import { mapColorsToRange } from "../../utils/colors"
import { equalIntervals } from "../../utils/stats"
import { getParentId } from "../../utils/features"
// import { LabelPointPropType } from "../../CustomPropTypes"
import { labelsToGeoJSON } from "../../utils/geojson"

import summaryStats from "../../data/summary_stats.json"

import { TILE_HOST, COUNT_COLORS } from "./config"
import MapBase from "./MapBase"

const FEATURE_ID_FIELD = {
    HUC2: "HUC2",
    HUC4: "HUC4",
    HUC8: "HUC8",
    ecoregion3: "NA_L3CODE",
    ecoregion4: "US_L4CODE"
}

const ZOOM_LEVELS = {
    HUC2: [0, 4.5],
    HUC4: [4.5, 6],
    HUC8: [6, 21],
    ecoregion3: [0, 6],
    ecoregion4: [6, 21]
}

const SYSTEM_LEVELS = {
    HUC: ["HUC2", "HUC4", "HUC8"],
    ecoregion: ["ecoregion3", "ecoregion4"]
}

const LEVEL_LABELS = {
    HUC2: "Hydrologic region",
    HUC4: "Hydrologic subregion",
    HUC8: "Hydrologic subbasin",
    ecoregion3: "Level 3 Ecoregion",
    ecoregion4: "Level 4 Ecoregion"
}
// Precalculate colors
const LEVEL_LEGEND = {}
Object.keys(SYSTEM_LEVELS).forEach(s => {
    SYSTEM_LEVELS[s].forEach(l => {
        LEVEL_LEGEND[l] = {
            bins: equalIntervals(summaryStats[l].dams, COUNT_COLORS.length),
            colors: COUNT_COLORS
        }
    })
})

class SummaryMap extends Component {
    constructor() {
        super()

        this.state = {
            activeLayer: null // root ID of the active layer(s)
        }

        this.map = null
    }

    componentDidUpdate(prevProps) {
        const { map } = this
        if (map === null) return

        const { system: prevSystem } = prevProps
        const { system } = this.props

        if (system !== prevSystem) {
            if (prevSystem !== null) {
                this.setUnitLayerVisibility(prevSystem, false)
            }

            if (system !== null) {
                this.setUnitLayerVisibility(system, true)
            }
        }

        // TODO: compare before updating
        // map.getSource("unit-labels").setData(labelsToGeoJSON(labels.toJS()))
    }

    setUnitLayerVisibility = (system, visible) => {
        SYSTEM_LEVELS[system].forEach(lyr => this.setLayerVisibility(lyr, visible))
    }

    setLayerVisibility = (layerId, visible) => {
        // set fill and outline layer visibility
        const { map } = this
        const visibility = visible ? "visible" : "none"

        map.setLayoutProperty(`${layerId}-fill`, "visibility", visibility)
        map.setLayoutProperty(`${layerId}-outline`, "visibility", visibility)
    }

    addUnitLayers = (units, visible = false) => {
        units.reverse() // make sure that higher level units are stacked on lower level ones

        const { map } = this
        units.forEach(unit => {
            const { bins, colors } = LEVEL_LEGEND[unit]
            const [minzoom, maxzoom] = ZOOM_LEVELS[unit]

            const renderColors = []
            bins.forEach(([min, max], i) => {
                renderColors.push((max - min) / 2 + min) // interpolate from the midpoint
                renderColors.push(colors[i])
            })

            let outlineColor = "#AAA"
            if (unit.startsWith("HUC")) {
                outlineColor = "#3F6DD7"
            } else if (unit.startsWith("ecoregion")) {
                outlineColor = "#008040"
            }

            map.addLayer({
                id: `${unit}-fill`,
                source: "sarp",
                "source-layer": unit,
                type: "fill",
                minzoom,
                maxzoom,
                filter: [">", "dams", 0],
                layout: {
                    visibility: visible ? "visible" : "none"
                },
                paint: {
                    "fill-opacity": 0.6,
                    "fill-color": ["interpolate", ["linear"], ["get", "dams"], ...renderColors]
                }
            })
            map.addLayer({
                id: `${unit}-outline`,
                source: "sarp",
                "source-layer": unit,
                type: "line",
                minzoom,
                maxzoom,
                filter: [">", "dams", 0],
                layout: {
                    visibility: visible ? "visible" : "none"
                },
                paint: {
                    "line-opacity": 1,
                    "line-width": 0.5,
                    "line-color": outlineColor
                }
            })

            // Show this and set the filter to highlight selected features
            map.addLayer({
                id: `${unit}-outline-highlight`,
                source: "sarp",
                "source-layer": unit,
                type: "line",
                layout: {
                    visibility: "none",
                    "line-cap": "round",
                    "line-join": "round"
                },
                paint: {
                    "line-opacity": 1,
                    "line-width": 4,
                    "line-color": "#333"
                }
            })
        })
    }

    handleCreateMap = map => {
        this.map = map

        this.updateActiveLayer()

        map.on("load", () => {
            map.addSource("sarp", {
                type: "vector",
                maxzoom: 8,
                tiles: [`${TILE_HOST}/services/sarp_summary/tiles/{z}/{x}/{y}.pbf`]
            })

            this.addUnitLayers(SYSTEM_LEVELS.HUC, true)
            this.addUnitLayers(SYSTEM_LEVELS.ecoregion, false)
            // this.addLabelLayer(labels.toJS())
        })

        map.on("zoom", this.updateActiveLayer)
        map.on("click", e => {
            const { activeLayer } = this.state
            const { system, setUnit } = this.props

            if (system === null) return

            // TODO: capture and emit all intersected IDs, let consumer figure out which to process?
            const features = map.queryRenderedFeatures(e.point, { layers: [`${activeLayer}-fill`] })
            if (features.length === 0) return
            console.log("click features", features)
            setUnit(activeLayer, features[0].properties[FEATURE_ID_FIELD[activeLayer]])
        })
    }

    updateActiveLayer = () => {
        // TODO: optimize this since it is called on every render
        const { map } = this
        const { activeLayer: prevActiveLayer } = this.state
        const { system } = this.props

        if (map === null) return

        const zoom = this.map.getZoom()

        if (system !== null) {
            const available = SYSTEM_LEVELS[system].filter(u => {
                const [minzoom, maxzoom] = ZOOM_LEVELS[u]
                return zoom >= minzoom && zoom < maxzoom
            })
            const activeLayer = available.length > 0 ? available[0] : null

            if (activeLayer !== prevActiveLayer) {
                this.setState({ activeLayer })
            }
        }
    }

    renderLegend() {
        const { activeLayer } = this.state
        const { system } = this.props

        if (system === null || activeLayer === null) return null

        const legendInfo = LEVEL_LEGEND[activeLayer]
        const { bins } = legendInfo
        const colors = legendInfo.colors.slice()
        const labels = bins.map(([min, max], i) => {
            if (i === 0) {
                return `< ${Math.round(max).toLocaleString()} dams`
            }
            if (i === bins.length - 1) {
                return `≥ ${Math.round(min).toLocaleString()} dams`
            }
            // Use midpoint value
            return Math.round((max - min) / 2 + min).toLocaleString()
        })
        // flip the order since we are displaying from top to bottom
        colors.reverse()
        labels.reverse()

        return <Legend title={LEVEL_LABELS[activeLayer]} labels={labels} colors={colors} />
    }

    render() {
        const { system, setSystem, bounds } = this.props

        return (
            <React.Fragment>
                <MapBase bounds={bounds} onCreateMap={this.handleCreateMap} />

                <div id="SystemChooser" className="mapboxgl-ctrl-top-left flex-container flex-align-center">
                    <h5 className="is-size-7">Summarize on: </h5>
                    <div className="buttons has-addons">
                        <button
                            className={`button is-small ${system === "HUC" ? "active" : ""}`}
                            type="button"
                            onClick={() => setSystem("HUC")}
                        >
                            Watersheds
                        </button>
                        <button
                            className={`button is-small ${system === "ecoregion" ? "active" : ""}`}
                            type="button"
                            onClick={() => setSystem("ecoregion")}
                        >
                            Ecoregions
                        </button>
                    </div>
                </div>

                {this.renderLegend()}
            </React.Fragment>
        )
    }
}

SummaryMap.propTypes = {
    index: ImmutablePropTypes.map.isRequired,
    system: PropTypes.string,
    level: PropTypes.string,
    childLevel: PropTypes.string,
    levelIndex: PropTypes.number,
    unit: PropTypes.string,
    labels: ImmutablePropTypes.listOf(ImmutablePropTypes.map),
    setUnit: PropTypes.func.isRequired,
    setSystem: PropTypes.func.isRequired,

    bounds: ImmutablePropTypes.listOf(PropTypes.number), // example: [-180, -86, 180, 86]
    // layers: PropTypes.arrayOf(DatasetPropType),
    location: PropTypes.shape({
        latitude: PropTypes.number.isRequired,
        longitude: PropTypes.number.isRequired
    }) // location to highlight on the map, such as a placename search result
}

SummaryMap.defaultProps = {
    bounds: null,
    system: null,
    level: null,
    childLevel: null,
    levelIndex: null,
    unit: null,
    labels: [],
    // layers: [],
    location: null
}

const mapStateToProps = state => ({
    index: state.get("index"),
    bounds: state.get("bounds"),
    system: state.get("system"),
    level: state.get("level"),
    childLevel: state.get("childLevel"),
    unit: state.get("unit"),
    labels: state.get("labels")
})

export default connect(
    mapStateToProps,
    actions
)(SummaryMap)

// Initially the mask and boundary are visible
// map.addLayer({
//     id: "sarp-mask",
//     source: "sarp",
//     "source-layer": "mask",
//     type: "fill",
//     layout: {},
//     paint: {
//         "fill-opacity": 0.6,
//         "fill-color": "#AAA"
//     }
// })
// create fill layer only for consistency w/ other units below
// map.addLayer({
//     id: "sarp-fill",
//     source: "sarp",
//     "source-layer": "boundary",
//     type: "fill",
//     layout: {},
//     paint: {
//         "fill-opacity": 0
//     }
// })
// map.addLayer({
//     id: "sarp-outline",
//     source: "sarp",
//     "source-layer": "boundary",
//     type: "line",
//     layout: {},
//     paint: {
//         "line-opacity": 0.8,
//         "line-width": 2,
//         // "line-color": "#AAA"
//         "line-color": "#4A0025"
//     }
// })
