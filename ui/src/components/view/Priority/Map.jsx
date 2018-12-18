import React, { Component } from "react"
import PropTypes from "prop-types"
import { fromJS } from "immutable"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"

import * as actions from "../../../actions/priority"
// import Legend from "./Legend"
import { FeaturePropType } from "../../../CustomPropTypes"

import { TILE_HOST, PRIORITY_TIER_COLORS, SYSTEMS } from "../../map/config"
import { FILL_STYLE, OUTLINE_STYLE, HIGHLIGHT_STYLE, PARENT_STYLE } from "./styles"
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
        this.layers = []
        this.layerIndex = {}
        this.hoverId = null
    }

    componentDidUpdate(prevProps) {
        const { map } = this
        if (map === null) return

        const {
            system: prevSystem,
            scenario: prevScenario,
            summaryUnits: prevSummaryUnits,
            layer: prevLayer,
            selectedFeature: prevSelectedFeature,
            mode: prevMode
        } = prevProps
        const { system, scenario, summaryUnits, layer, selectedFeature, mode } = this.props

        // if (system !== prevSystem) {
        //     if (prevSystem !== null) {
        //         const hideUnits = this.layers.filter(({ group }) => group === prevSystem)
        //         hideUnits.forEach(({ id }) => this.setLayerVisibility(id, false))
        //     }

        //     if (system !== null) {
        //         const showUnits = this.layers.filter(({ group }) => group === system)
        //         showUnits.forEach(({ id }) => this.setLayerVisibility(id, true))
        //     }
        // }
        // if (scenario !== prevScenario) {
        //     // Note: scenarios cannot be null
        //     map.setFilter("dams_priority", ["<=", ["get", scenario], 4])
        //     map.setPaintProperty("dams_priority", "circle-color", [
        //         "match",
        //         ["get", scenario],
        //         ...priorityColors,
        //         "#AAA"
        //     ])
        //     map.setPaintProperty("dams_priority", "circle-radius", [
        //         "interpolate",
        //         ["linear"],
        //         ["get", scenario],
        //         1,
        //         20,
        //         4,
        //         6
        //     ])
        // }

        if (layer !== prevLayer) {
            if (prevLayer !== null) {
                this.setLayerVisibility(prevLayer, false)
                // clear out previous highlight
                this.map.setFilter(`${prevLayer}-highlight`, ["==", "id", Infinity])
                // map.off("mousemove", `${layer}-fill`, this.handleFeatureHover)
                // map.off("mouseleave", `${layer}-fill`, this.handleFeatureUnhover)
            }

            if (layer !== null) {
                // clear out previous highlight
                this.map.setFilter(`${layer}-highlight`, ["==", "id", Infinity])
                this.setLayerVisibility(layer, true)
                // map.on("mousemove", `${layer}-fill`, this.handleFeatureHover)
                // map.on("mouseleave", `${layer}-fill`, this.handleFeatureUnhover)
            }
        }

        if (summaryUnits !== prevSummaryUnits) {
            // TODO: set filter based on the current units

            if (layer !== null) {
                if (!summaryUnits.size) {
                    this.map.setFilter(`${layer}-highlight`, ["==", "id", Infinity])
                } else {
                    this.map.setFilter(`${layer}-highlight`, ["in", "id", ...summaryUnits.toJS().map(({ id }) => id)])
                }
            }
        }

        if (mode !== prevMode) {
            if (mode === "prioritize") {
                // Convert to outline instead and turn on dams
                console.log(system, summaryUnits.toJS())
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

    setLayerVisibility = (id, visible) => {
        // set fill and outline layer visibility
        const { map } = this
        const visibility = visible ? "visible" : "none"
        map.setLayoutProperty(`${id}-fill`, "visibility", visibility)
        map.setLayoutProperty(`${id}-outline`, "visibility", visibility)
        map.setLayoutProperty(`${id}-highlight`, "visibility", visibility)

        if (this.layerIndex[id].parent) {
            map.setLayoutProperty(`${id}-parent-outline`, "visibility", visibility)
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

    addLayers = (layers, visible = true) => {
        const { map } = this

        layers.forEach(lyr => {
            const { id, minzoom = 0, maxzoom = 24, parent } = lyr

            const config = fromJS({
                source: "sarp",
                "source-layer": id,
                minzoom,
                maxzoom,
                layout: {
                    visibility: visible ? "visible" : "none"
                }
            })

            map.addLayer(
                config
                    .merge({ id: `${id}-fill` })
                    .mergeDeep(fromJS(FILL_STYLE))
                    .toJS()
            )
            map.addLayer(
                config
                    .merge({ id: `${id}-outline` })
                    .mergeDeep(fromJS(OUTLINE_STYLE))
                    .toJS()
            )
            map.addLayer(
                config
                    .merge({ id: `${id}-highlight` })
                    .mergeDeep(fromJS(HIGHLIGHT_STYLE))
                    .toJS()
            )

            if (parent) {
                map.addLayer(
                    config
                        .merge({ id: `${id}-parent-outline`, "source-layer": parent })
                        .mergeDeep(fromJS(PARENT_STYLE))
                        .toJS()
                )
            }

            this.layers.push(lyr)
            this.layerIndex[id] = lyr
        })
    }

    addDams = () => {
        const { map } = this

        // Add dams that have no network
        map.addLayer({
            id: "dams-no",
            source: "dams",
            "source-layer": "no_network",
            type: "circle",
            minzoom: 10,
            maxzoom: 24,
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
            paint: {
                "circle-color": "#c51b8a",
                "circle-radius": { stops: [[6, 4], [14, 8]] },
                "circle-opacity": { stops: [[5, 0.1], [6, 0.25], [7, 1]] },
                "circle-stroke-color": "#FFFFFF",
                "circle-stroke-width": { stops: [[6, 0.25], [10, 1], [14, 3]] }
            }
        })

        map.addLayer({
            id: "no_network-selected",
            source: "dams",
            "source-layer": "no_network",
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

    handleCreateMap = map => {
        this.map = map
        const { system, mode } = this.props

        this.setState({ zoom: this.map.getZoom() })

        map.on("load", () => {
            const { scenario } = this.props

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

            this.addDams()

            // Add summary unit layers
            Object.keys(SYSTEMS).forEach(s => {
                this.addLayers(
                    LAYER_CONFIG.filter(({ group }) => group === s)
                        .slice()
                        .reverse(),
                    s === system
                )
            })
        })

        map.on("zoom", () => this.setState({ zoom: this.map.getZoom() }))
        map.on("click", e => {
            const { layer, selectFeature, selectUnit, mode: curMode } = this.props

            switch (curMode) {
                case "select": {
                    if (layer !== null) {
                        const features = map.queryRenderedFeatures(e.point, { layers: [`${layer}-fill`] })
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

        // map.foo = () => {
        //     map.setFilter("dams-heatmap", ["==", "State", "Alabama"])
        //     map.setFilter("dams-heatmap-background", ["!=", "State", "Alabama"])
        //     map.setFilter("dams", ["==", "State", "Alabama"])
        //     map.setFilter("dams-background", ["!=", "State", "Alabama"])
        //     map.setLayoutProperty("dams-background", "visibility", "visible")
        //     map.setLayoutProperty("dams-heatmap-background", "visibility", "visible")
        // }
    }

    getVisibleLayers = () => {
        const { zoom } = this.state
        const { system } = this.props

        return this.layers.filter(
            ({ group, minzoom, maxzoom }) => group === system && zoom >= minzoom && zoom < maxzoom
        )
    }

    render() {
        const { scenario, system, setSystem, setScenario, bounds } = this.props

        return (
            <React.Fragment>
                <Map baseStyle="streets-v9" bounds={bounds} onCreateMap={this.handleCreateMap} />

                {/* <div id="SystemChooser" className="mapboxgl-ctrl-top-left flex-container flex-align-center">
                    <h5 className="is-size-7">Show Tiers for: </h5>
                    <div className="buttons has-addons">
                        {Object.entries(SCENARIOS).map(([key, name]) => (
                            <button
                                key={key}
                                className={`button is-small ${scenario === key ? "active" : ""}`}
                                type="button"
                                onClick={() => setScenario(key)}
                            >
                                {name}
                            </button>
                        ))}
                    </div>
                </div> */}
            </React.Fragment>
        )
    }
}

PriorityMap.propTypes = {
    scenario: PropTypes.string,
    bounds: ImmutablePropTypes.listOf(PropTypes.number), // example: [-180, -86, 180, 86]
    system: PropTypes.string,
    selectedFeature: FeaturePropType,
    layer: PropTypes.string,
    summaryUnits: ImmutablePropTypes.set.isRequired,
    mode: PropTypes.string.isRequired,

    setSystem: PropTypes.func.isRequired,
    setScenario: PropTypes.func.isRequired,
    selectFeature: PropTypes.func.isRequired,
    selectUnit: PropTypes.func.isRequired
}

PriorityMap.defaultProps = {
    scenario: null,
    bounds: null,
    system: null,
    selectedFeature: null,
    layer: null
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        bounds: state.get("bounds"),
        system: state.get("system"),
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
