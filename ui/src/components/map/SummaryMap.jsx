import React, { Component } from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"
import { fromJS } from "immutable"
import * as actions from "../../actions/summary"
import Legend from "./Legend"
import { equalIntervals } from "../../utils/stats"
import { FeaturePropType } from "../../CustomPropTypes"
// import { LabelPointPropType } from "../../CustomPropTypes"
// import { labelsToGeoJSON } from "../../utils/geojson"

import summaryStats from "../../data/summary_stats.json"

import { TILE_HOST, COUNT_COLORS, LAYER_CONFIG } from "./config"
import Map from "./index"

// Precalculate colors
// TODO: make this vary by metric
const LEVEL_LEGEND = {}
LAYER_CONFIG.forEach(({ id }) => {
    LEVEL_LEGEND[id] = {
        // bins: equalIntervals(summaryStats[id].dams.range, COUNT_COLORS.length),
        bins: summaryStats[id].percentiles,
        colors: COUNT_COLORS
    }
})

class SummaryMap extends Component {
    constructor() {
        super()

        this.state = {
            zoom: null
        }

        this.map = null
        this.layers = []
    }

    componentDidUpdate(prevProps) {
        const { map } = this
        if (map === null) return

        const { system: prevSystem, selectedFeature: prevFeature } = prevProps
        const { system, selectedFeature } = this.props

        const visibleLayers = this.layers.filter(({ group }) => group === system)

        if (system !== prevSystem) {
            if (prevSystem !== null) {
                const hideLayers = this.layers.filter(({ group }) => group === prevSystem)
                hideLayers.forEach(({ id }) => this.setLayerVisibility(id, false))
            }

            if (system !== null) {
                visibleLayers.forEach(({ id }) => this.setLayerVisibility(id, true))
            }
        }

        if (selectedFeature !== prevFeature) {
            visibleLayers.forEach(({ id }) =>
                this.setHighlight(id, selectedFeature === null ? null : selectedFeature.get("id")))
        }

        // TODO: compare before updating
        // map.getSource("unit-labels").setData(labelsToGeoJSON(labels.toJS()))
    }

    setLayerVisibility = (id, visible) => {
        // set fill and outline layer visibility
        const { map } = this
        const visibility = visible ? "visible" : "none"
        map.setLayoutProperty(`${id}-fill`, "visibility", visibility)
        map.setLayoutProperty(`${id}-outline`, "visibility", visibility)
        map.setLayoutProperty(`${id}-highlight`, "visibility", visibility)
    }

    setHighlight = (id, featureId) => {
        this.map.setFilter(`${id}-highlight`, ["==", "id", featureId === null ? Infinity : featureId])
    }

    addLayers = (layers, visible = true) => {
        const { map } = this

        layers.forEach(lyr => {
            const { id, minzoom, maxzoom } = lyr
            const { bins, colors } = LEVEL_LEGEND[id]
            const renderColors = []
            // bins.forEach(([min, max], i) => {
            //     renderColors.push((max - min) / 2 + min) // interpolate from the midpoint
            //     renderColors.push(colors[i])
            // })
            bins.forEach((bin, i) => {
                renderColors.push(bin)
                renderColors.push(colors[i])
            })

            let outlineColor = "#AAA"
            if (id.startsWith("HUC")) {
                outlineColor = "#3F6DD7"
            } else if (id.startsWith("ECO")) {
                outlineColor = "#008040"
            }

            // TODO: merge objects using immutable instead
            const config = fromJS({
                source: "sarp",
                "source-layer": id,
                type: "fill",
                minzoom: minzoom || 0,
                maxzoom: maxzoom || 21,
                filter: [">=", "dams", 0],
                layout: {
                    visibility: visible ? "visible" : "none"
                }
            })
            const fillConfig = config.merge(
                fromJS({
                    id: `${id}-fill`,
                    type: "fill",
                    paint: {
                        "fill-opacity": 0.3,
                        "fill-color": ["interpolate", ["linear"], ["get", "dams"], ...renderColors]
                    }
                })
            )
            const outlineConfig = config.merge(
                fromJS({
                    id: `${id}-outline`,
                    type: "line",
                    paint: {
                        "line-opacity": 1,
                        "line-width": 0.5,
                        "line-color": outlineColor
                    }
                })
            )

            map.addLayer(fillConfig.toJS())
            map.addLayer(outlineConfig.toJS())

            this.layers.push(lyr)
        })
    }

    addHighlightLayer = (layer, visible = true) => {
        const { id } = layer

        this.map.addLayer({
            id: `${id}-highlight`,
            source: "sarp",
            "source-layer": id,
            type: "line",
            minzoom: 0,
            maxzoom: 21,
            layout: {
                "line-cap": "round",
                "line-join": "round",
                visibility: visible ? "visible" : "none"
            },
            paint: {
                "line-opacity": 1,
                "line-width": 4,
                "line-color": "#333"
            },
            filter: ["==", "id", Infinity]
        })
    }

    handleCreateMap = map => {
        this.map = map
        const { system } = this.props

        map.on("load", () => {
            map.addSource("sarp", {
                type: "vector",
                maxzoom: 8,
                tiles: [`${TILE_HOST}/services/sarp_summary/tiles/{z}/{x}/{y}.pbf`]
            })

            const systems = ["States", "HUC", "ECO"]
            systems.forEach(s => {
                this.addLayers(
                    LAYER_CONFIG.filter(({ group }) => group === s)
                        .slice()
                        .reverse(),
                    s === system
                )
            })

            this.layers.forEach(lyr => this.addHighlightLayer(lyr, lyr.group === system))

            // TODO: add heatmap?
            // map.addSource("dams", {
            //     type: "vector",
            //     tiles: [`${TILE_HOST}/services/dams/tiles/{z}/{x}/{y}.pbf`],
            //     maxzoom: 14
            // })
            // map.addLayer({
            //     id: "dams_heatmap",
            //     source: "dams",
            //     "source-layer": "dams_heatmap",
            //     type: "heatmap",
            //     paint: {
            //         "heatmap-intensity": 1,
            //         "heatmap-color": [
            //             "interpolate",
            //             ["linear"],
            //             ["heatmap-density"],
            //             0,
            //             "rgba(255,0, 0,0)",
            //             0.1,
            //             "rgba(255,0,0, 0.5)",
            //             1,
            //             "rgb(178,24,43)"
            //         ],
            //         // "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 6, 2, 9, 20],
            //         "heatmap-radius": 2,
            //         "heatmap-opacity": ["interpolate", ["linear"], ["zoom"], 7, 1, 8, 0]
            //     }
            // })

            // this.addLabelLayer(labels.toJS())

            this.setState({ zoom: this.map.getZoom() })
        })

        map.on("zoom", () => this.setState({ zoom: this.map.getZoom() }))
        map.on("click", e => {
            const { selectFeature } = this.props

            const layers = this.getVisibleLayers().map(({ id }) => `${id}-fill`)
            const features = map.queryRenderedFeatures(e.point, { layers })
            if (features.length === 0) return
            console.log("click features", features)

            const { sourceLayer, properties } = features[0]
            selectFeature(fromJS(properties).merge({ layerId: sourceLayer }))
        })
    }

    getVisibleLayers = () => {
        const { zoom } = this.state
        const { system } = this.props

        return this.layers.filter(
            ({ group, minzoom, maxzoom }) => group === system && zoom >= minzoom && zoom < maxzoom
        )
    }

    renderLegend() {
        const { system } = this.props

        if (system === null) return null

        const visibleLayers = this.getVisibleLayers()
        if (visibleLayers.length === 0) return null

        const lyr = visibleLayers[0]
        const { id, title } = lyr

        const legendInfo = LEVEL_LEGEND[id]
        const { bins } = legendInfo
        const colors = legendInfo.colors.slice()
        // const labels = bins.map(([min, max], i) => {
        //     if (i === 0) {
        //         return `< ${Math.round(max).toLocaleString()} dams`
        //     }
        //     if (i === bins.length - 1) {
        //         return `≥ ${Math.round(min).toLocaleString()} dams`
        //     }
        //     // Use midpoint value
        //     return Math.round((max - min) / 2 + min).toLocaleString()
        // })

        const labels = bins.map((bin, i) => {
            if (i === bins.length - 1) {
                return `≥ ${Math.round(bin).toLocaleString()} dams`
            }
            // Use midpoint value
            return Math.round(bin).toLocaleString()
        })

        // flip the order since we are displaying from top to bottom
        colors.reverse()
        labels.reverse()

        return <Legend title={title} labels={labels} colors={colors} footnote="areas with no dams are not shown" />
    }

    render() {
        const { system, setSystem, bounds } = this.props

        return (
            <React.Fragment>
                <Map bounds={bounds} onCreateMap={this.handleCreateMap} />

                <div id="SystemChooser" className="mapboxgl-ctrl-top-left flex-container flex-align-center">
                    <h5 className="is-size-7">Summarize on: </h5>
                    <div className="buttons has-addons">
                        <button
                            className={`button is-small ${system === "states" ? "active" : ""}`}
                            type="button"
                            onClick={() => setSystem("states")}
                        >
                            States
                        </button>
                        <button
                            className={`button is-small ${system === "HUC" ? "active" : ""}`}
                            type="button"
                            onClick={() => setSystem("HUC")}
                        >
                            Watersheds
                        </button>
                        <button
                            className={`button is-small ${system === "ECO" ? "active" : ""}`}
                            type="button"
                            onClick={() => setSystem("ECO")}
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
    bounds: ImmutablePropTypes.listOf(PropTypes.number), // example: [-180, -86, 180, 86]
    system: PropTypes.string,
    selectedFeature: FeaturePropType,
    labels: ImmutablePropTypes.listOf(ImmutablePropTypes.map),

    setSystem: PropTypes.func.isRequired,
    selectFeature: PropTypes.func.isRequired
}

SummaryMap.defaultProps = {
    bounds: null,
    system: null,
    selectedFeature: null,
    labels: []
}

const mapStateToProps = globalState => {
    const state = globalState.get("summary")

    return {
        bounds: state.get("bounds"),
        system: state.get("system"),
        selectedFeature: state.get("selectedFeature"),
        labels: state.get("labels")
    }
}

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
