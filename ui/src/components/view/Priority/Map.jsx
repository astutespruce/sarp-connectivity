import React, { Component } from "react"
import PropTypes from "prop-types"
import { fromJS } from "immutable"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"

import * as actions from "../../../actions/priority"
// import Legend from "./Legend"
import { FeaturePropType } from "../../../CustomPropTypes"

import { TILE_HOST, PRIORITY_TIER_COLORS, SYSTEMS } from "../../map/config"
import {
    FILL_STYLE,
    OUTLINE_STYLE,
    HIGHLIGHT_STYLE,
    PARENT_STYLE,
    HIGHLIGHT_OUTLINE_STYLE,
    POINT_HIGHLIGHT_STYLE
} from "./styles"
import { LAYER_CONFIG } from "./config"
import Map from "../../map/index"

// Construct colors for mapbox GL layers in advance
const priorityColors = PRIORITY_TIER_COLORS.reduce((out, color, i) => out.concat([i, color]), [])

class PriorityMap extends Component {
    constructor() {
        super()

        this.state = {
            zoom: null
        }

        this.map = null
        // this.hoverId = null
    }

    componentDidUpdate(prevProps) {
        const { map, layers } = this
        if (map === null) return

        const {
            scenario: prevScenario,
            summaryUnits: prevSummaryUnits,
            layer: prevLayer,
            selectedFeature: prevSelectedFeature,
            mode: prevMode
        } = prevProps
        const { scenario, summaryUnits, layer, selectedFeature, mode } = this.props

        if (layer !== prevLayer) {
            if (prevLayer !== null) {
                // remove layers
                this.removeUnitLayers(prevLayer)

                // this.setLayerVisibility(prevLayer, false)
                // clear out previous highlight
                // this.map.setFilter(`${prevLayer}-highlight`, ["==", "id", Infinity])
                // map.setFilter(`${prevLayer}-highlight-outline`, ["==", "id", Infinity])
                // map.off("mousemove", `${layer}-fill`, this.handleFeatureHover)
                // map.off("mouseleave", `${layer}-fill`, this.handleFeatureUnhover)
            }

            if (layer !== null) {
                this.addUnitLayers(layer, true)

                // clear out previous highlight
                // this.map.setFilter(`${layer}-highlight`, ["==", "id", Infinity])
                // map.setFilter(`${layer}-highlight-outline`, ["==", "id", Infinity])
                // this.setLayerVisibility(layer, true)
                // map.on("mousemove", `${layer}-fill`, this.handleFeatureHover)
                // map.on("mouseleave", `${layer}-fill`, this.handleFeatureUnhover)
            }
        }

        if (summaryUnits !== prevSummaryUnits) {
            if (layer !== null) {
                this.setHighlight(summaryUnits.toJS().map(({ id }) => id))
            }
        }

        if (mode !== prevMode) {
            if (mode === "select") {
                if (layer !== null) {
                    this.setLayerVisibility(true)
                }
            } else {
                this.setLayerVisibility(false)
                map.setLayoutProperty(`${layer}-highlight-outline`, "visibility", "visible")
            }

            if (mode === "prioritize") {
                // Convert to outline instead and turn on dams
                console.log(layer, summaryUnits.toJS())
                map.setFilter("dams-low", [">", `${layer}_${scenario}_tier`, 3])
                map.setFilter("dams-top", [
                    "all",
                    ["<=", `${layer}_${scenario}_tier`, 3],
                    ["in", layer, ...summaryUnits.toJS().map(({ id }) => id)]
                ])
            }
            const damsVisible = mode === "prioritize" ? "visible" : "none"

            map.setLayoutProperty("dams-no", "visibility", damsVisible)
            map.setLayoutProperty("dams-low", "visibility", damsVisible)
            map.setLayoutProperty("dams-top", "visibility", damsVisible)
        }

        if (selectedFeature !== prevSelectedFeature) {
            if (prevSelectedFeature !== null) {
                this.map.setFilter(`${prevSelectedFeature.get("layerId")}-selected`, ["==", "id", Infinity])
            }
            if (selectedFeature !== null) {
                this.map.setFilter(`${selectedFeature.get("layerId")}-selected`, [
                    "==",
                    "id",
                    selectedFeature.get("id")
                ])
            }
        }
    }

    setHighlight = ids => {
        const { map } = this

        const filterExpr = ids.length > 0 ? ["in", "id", ...ids] : ["==", "id", Infinity]

        map.setFilter(`highlight`, filterExpr)
        map.setFilter(`highlight-outline`, filterExpr)
    }

    setLayerVisibility = visible => {
        // set fill and outline layer visibility
        const { map } = this
        const { layer } = this.props
        const visibility = visible ? "visible" : "none"
        map.setLayoutProperty("fill", "visibility", visibility)
        map.setLayoutProperty("outline", "visibility", visibility)
        map.setLayoutProperty("highlight", "visibility", visibility)

        if (LAYER_CONFIG[layer].parent) {
            map.setLayoutProperty("parent-outline", "visibility", visibility)
        }
    }

    addBoundaryLayers = () => {
        const { map } = this

        // Initially the mask and boundary are visible
        map.addLayer({
            id: "sarp-mask",
            source: "sarp",
            "source-layer": "mask",
            type: "fill",
            layout: {},
            paint: {
                "fill-opacity": 0.6,
                "fill-color": "#AAA"
            }
        })
        map.addLayer({
            id: "sarp-outline",
            source: "sarp",
            "source-layer": "boundary",
            type: "line",
            layout: {},
            paint: {
                "line-opacity": 0.8,
                "line-width": 2,
                "line-color": "#4A0025"
            }
        })
    }

    addUnitLayers = layer => {
        const { map } = this
        const { minzoom = 0, maxzoom = 24, parent } = LAYER_CONFIG[layer]

        const config = fromJS({
            source: "sarp",
            "source-layer": layer,
            minzoom,
            maxzoom
        })

        map.addLayer(
            config
                .merge({ id: "fill" })
                .mergeDeep(fromJS(FILL_STYLE))
                .toJS()
        )
        map.addLayer(
            config
                .merge({ id: "outline" })
                .mergeDeep(fromJS(OUTLINE_STYLE))
                .toJS()
        )
        map.addLayer(
            config
                .merge({ id: "highlight" })
                .mergeDeep(fromJS(HIGHLIGHT_STYLE))
                .toJS()
        )

        map.addLayer(
            config
                .merge({ id: "highlight-outline" })
                .mergeDeep(fromJS(HIGHLIGHT_OUTLINE_STYLE))
                .toJS()
        )

        if (parent) {
            map.addLayer(
                config
                    .merge({ id: "parent-outline", "source-layer": parent })
                    .mergeDeep(fromJS(PARENT_STYLE))
                    .toJS()
            )
        }
    }

    removeUnitLayers = layer => {
        const { map } = this

        map.removeLayer("fill")
        map.removeLayer("outline")
        map.removeLayer("highlight")
        map.removeLayer("highlight-outline")
        if (LAYER_CONFIG[layer]) {
            map.removeLayer("parent-outline")
        }
    }

    addDams = () => {
        // TODO: add these LATER!!
        const { map } = this

        // Add dams that have no network
        map.addLayer({
            id: "dams-no",
            source: "dams",
            "source-layer": "dams",
            type: "circle",
            minzoom: 10,
            maxzoom: 24,
            layout: {
                visibility: "none"
            },
            filter: ["=="],
            paint: {
                "circle-color": { stops: [[10, "#AAA"], [14, "#999"]] },
                "circle-radius": { stops: [[10, 0.5], [14, 4]] },
                "circle-opacity": { stops: [[10, 0.5], [14, 1]] },
                "circle-stroke-color": "#666",
                "circle-stroke-width": { stops: [[10, 0], [14, 1]] }
            }
        })

        map.addLayer({
            id: "dams-low",
            source: "dams",
            "source-layer": "dams",
            type: "circle",
            minzoom: 5,
            maxzoom: 24,
            layout: {
                visibility: "none"
            },
            // TODO: threshold from user or zoom
            // filter: [">", `${layer}_${scenario}_tier`, 3],
            filter: [">", "State_NCWC_tier", 1],
            paint: {
                "circle-color": "#fbb4b9",
                "circle-radius": { stops: [[10, 0.5], [14, 6]] },
                "circle-opacity": { stops: [[10, 0.5], [14, 1]] },
                "circle-stroke-color": "#c51b8a",
                "circle-stroke-width": { stops: [[10, 0], [14, 1]] }
            }
        })

        map.addLayer({
            id: "dams-top",
            source: "dams",
            "source-layer": "dams",
            type: "circle",
            minzoom: 5,
            maxzoom: 24,
            layout: {
                visibility: "none"
            },
            // TODO: threshold from user or zoom
            // TODO: selected unit
            // filter: ["<=", `${layer}_${scenario}_tier`, 3],
            filter: ["<=", "State_NCWC_tier", 1],
            paint: {
                "circle-color": "#c51b8a",
                "circle-radius": { stops: [[6, 4], [14, 8]] },
                "circle-opacity": { stops: [[5, 0.1], [6, 0.25], [7, 1]] },
                "circle-stroke-color": "#FFFFFF",
                "circle-stroke-width": { stops: [[6, 0.25], [10, 1], [14, 3]] }
            }
        })

        map.addLayer({
            id: "dams-selected",
            source: "dams",
            "source-layer": "dams",
            type: "circle",
            minzoom: 5,
            maxzoom: 24,
            layout: {},
            // TODO
            filter: ["==", "id", Infinity],
            paint: {
                "circle-color": "#fd8d3c",
                "circle-radius": 14,
                "circle-stroke-width": 3,
                "circle-stroke-color": "#f03b20"
            }
        })
    }

    handleCreateMap = map => {
        this.map = map

        this.setState({ zoom: this.map.getZoom() })

        map.on("load", () => {
            map.addSource("sarp", {
                type: "vector",
                maxzoom: 8,
                tiles: [`${TILE_HOST}/services/sarp_summary/tiles/{z}/{x}/{y}.pbf`]
            })
            map.addSource("dams", {
                type: "vector",
                tiles: [`${TILE_HOST}/services/sarp_dams/tiles/{z}/{x}/{y}.pbf`],
                minzoom: 5,
                maxzoom: 12
            })

            this.addBoundaryLayers()

            // this.addDams()
        })

        map.on("zoom", () => this.setState({ zoom: this.map.getZoom() }))
        map.on("click", e => {
            const { layer, selectFeature, selectUnit, mode } = this.props

            switch (mode) {
                case "select": {
                    if (layer !== null) {
                        const features = map.queryRenderedFeatures(e.point, { layers: ["fill"] })
                        if (features.length > 0) {
                            selectUnit(features[0].properties)
                        }
                    }
                    break
                }
                case "prioritize": {
                    const points = map.queryRenderedFeatures(e.point, { layers: ["dams-top", "dams-low", "dams-no"] })
                    if (points.length > 0) {
                        const point = points[0]
                        console.log(point)
                        selectFeature(fromJS(point.properties).merge({ layerId: point.sourceLayer, type: "dam" }))
                    }
                    break
                }
            }
        })
    }

    render() {
        const { scenario, setScenario, bounds } = this.props

        return (
            <React.Fragment>
                <Map baseStyle="streets-v9" bounds={bounds} onCreateMap={this.handleCreateMap} />
            </React.Fragment>
        )
    }
}

PriorityMap.propTypes = {
    scenario: PropTypes.string,
    bounds: ImmutablePropTypes.listOf(PropTypes.number), // example: [-180, -86, 180, 86]
    selectedFeature: FeaturePropType,
    layer: PropTypes.string,
    summaryUnits: ImmutablePropTypes.set.isRequired,
    mode: PropTypes.string.isRequired,

    setScenario: PropTypes.func.isRequired,
    selectFeature: PropTypes.func.isRequired,
    selectUnit: PropTypes.func.isRequired
}

PriorityMap.defaultProps = {
    scenario: null,
    bounds: null,
    selectedFeature: null,
    layer: null
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        bounds: state.get("bounds"),
        selectedFeature: state.get("selectedFeature"),
        scenario: state.get("scenario"),
        summaryUnits: state.get("summaryUnits"),
        layer: state.get("layer"),
        mode: state.get("mode")
    }
}

export default connect(
    mapStateToProps,
    actions
)(PriorityMap)

// TODO: make this work based on featureIDs set via tippecanoe.  Requires new version of tippecanoe and int IDs
// handleFeatureHover = e => {
//     const { map } = this

//     if (e.features.length) {
//         const { source, sourceLayer, properties } = e.features[0]
//         const { id } = properties
//         if (this.hoverId !== null) {
//             map.setFeatureState({source, sourceLayer, id: this.hoverId}, {hover: false})
//         }
//         this.hoverId = e.features[0].id
//         map.setFeatureState({source, sourceLayer, id}, {hover: false})
//     }
// }

// handleFeatureUnhover = () => {
//     if (this.hoverId !== null) {
//         map.setFeatureState({source, sourceLayer, id: this.hoverId}, {hover: false})
//     }
// }

// const colors = TIER_COLORS.reduce((out, color, i) => out.concat([i, color]), [])
// const maxRadius = 20
// const minRadius = 6
// const numSizes = TIER_COLORS.length
// const increment = (maxRadius - minRadius) / (numSizes - 1)
// const sizes = Array.from(Array(numSizes), (_, i) => numSizes - increment * i).reduce(
//     (out, size, i) => out.concat([i, size]),
//     []
// )

// Show priority dams
// map.addLayer({
//     id: "dams_priority",
//     source: "dams",
//     "source-layer": "dams_priority",
//     type: "circle",
//     minzoom: 3,
//     filter: ["<=", ["get", scenario], 1], // only show the top priorities for the current scenario.  TODO: update on change of scenario
//     paint: {
//         "circle-color": ["match", ["get", scenario], ...priorityColors, "#AAA"],
//         // "circle-radius": ["interpolate", ["linear"], ["get", scenario], 1, 10, 4, 4],
//         "circle-radius": ["interpolate", ["linear"], ["get", scenario], 1, 3, 4, 3]
//         // "circle-opacity": 1
//         // "circle-stroke-width": 1,
//         // "circle-stroke-color": "#AAA"
//     }
// })

// map.addLayer({
//     id: "dams-priority",
//     source: "dams",
//     "source-layer": "dams_priority",
//     type: "circle",
//     minzoom: 3,
//     // filter: [
//     //     "any",
//     //     ["all", ["<=", ["number", ["get", scenario]], 4], ["!=", ["number", ["get", scenario]], -1]],
//     //     [">=", ["zoom"], 10]
//     // ],
//     paint: {
//         "circle-color": ["match", ["get", scenario], ...priorityColors, "#AAA"],
//         // "circle-radius": ["interpolate", ["linear"], ["zoom"], 7, 4, 14, 8],
//         "circle-radius": ["interpolate", ["linear"], ["get", scenario], 1, 20, 4, 6],
//         // "circle-opacity": ["case", [">=", ["get", scenario], 0], 0.85, 0.1],
//         "circle-opacity": 0.85,
//         "circle-stroke-width": 1,
//         "circle-stroke-color": "#AAA"
//         // "circle-stroke-opacity": ["case", [">=", ["get", scenario], 0], 0.85, 0.1]
//         // "circle-blur": ["interpolate", ["linear"], ["zoom"], 7, 0.5, 9, 0]
//     }
// })

// map.addLayer({
//     id: "dams-heatmap-background",
//     source: "dams",
//     "source-layer": "dams",
//     type: "heatmap",
//     layout: {
//         visibility: "none"
//     },
//     paint: {
//         "heatmap-intensity": 1,
//         "heatmap-color": [
//             "interpolate",
//             ["linear"],
//             ["heatmap-density"],
//             0,
//             "rgba(255,255, 255,0)",
//             0.1,
//             "rgba(240, 240, 240, 0.1)",
//             1,
//             "rgb(122,1,119)"
//         ],
//         "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 6, 2, 9, 10],
//         "heatmap-opacity": ["interpolate", ["linear"], ["zoom"], 7, 0.5, 8, 0]
//     }
// })
// map.addLayer({
//     id: "dams-background",
//     source: "dams",
//     "source-layer": "dams",
//     type: "circle",
//     minzoom: 7,
//     layout: {
//         visibility: "none"
//     },
//     paint: {
//         "circle-color": "rgb(122,1,119)",
//         "circle-radius": ["interpolate", ["linear"], ["zoom"], 9, 2, 14, 4],
//         "circle-opacity": 0.25,
//         "circle-stroke-width": 0,
//         "circle-blur": ["interpolate", ["linear"], ["zoom"], 7, 0.5, 9, 0]
//     }
// })
