import React, { Component } from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"

import * as actions from "../../actions/priority"
// import Legend from "./Legend"
import { FeaturePropType } from "../../CustomPropTypes"

import { TILE_HOST, LAYER_CONFIG, TIER_COLORS } from "./config"
import Map from "./index"

class PriorityMap extends Component {
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

        const { system: prevSystem } = prevProps
        const { system } = this.props

        if (system !== prevSystem) {
            if (prevSystem !== null) {
                const hideUnits = this.layers.filter(({ group }) => group === prevSystem)
                hideUnits.forEach(({ id }) => this.setLayerVisibility(id, false))
            }

            if (system !== null) {
                const showUnits = this.layers.filter(({ group }) => group === system)
                showUnits.forEach(({ id }) => this.setLayerVisibility(id, true))
            }
        }
    }

    setLayerVisibility = (id, visible) => {
        // set fill and outline layer visibility
        const { map } = this
        const visibility = visible ? "visible" : "none"
        map.setLayoutProperty(`${id}-fill`, "visibility", visibility)
        map.setLayoutProperty(`${id}-outline`, "visibility", visibility)
    }

    addLayers = (layers, visible = true) => {
        const { map } = this

        layers.forEach(lyr => {
            const { id, minzoom, maxzoom } = lyr

            let outlineColor = "#AAA"
            if (id.startsWith("HUC")) {
                outlineColor = "#3F6DD7"
            } else if (id.startsWith("ECO")) {
                outlineColor = "#008040"
            }

            const config = {
                source: "sarp",
                "source-layer": id,
                type: "fill",
                minzoom: minzoom || 0,
                maxzoom: maxzoom || 21,
                filter: [">", "dams", 0],
                layout: {
                    visibility: visible ? "visible" : "none"
                }
            }
            const fillConfig = Object.assign({}, config, {
                id: `${id}-fill`,
                type: "fill",
                paint: {
                    "fill-opacity": 0.3,
                    "fill-color": "#FFF"
                    // "fill-color": ["interpolate", ["linear"], ["get", "dams"], ...renderColors]
                }
            })
            const outlineConfig = Object.assign({}, config, {
                id: `${id}-outline`,
                type: "line",
                paint: {
                    "line-opacity": 1,
                    "line-width": 0.5,
                    "line-color": outlineColor
                }
            })

            map.addLayer(fillConfig)
            map.addLayer(outlineConfig)

            this.layers.push(lyr)

            // Show this and set the filter to highlight selected features
            // map.addLayer({
            //     id: `${id}-outline-highlight`,
            //     source: "sarp",
            //     "source-layer": id,
            //     type: "line",
            //     layout: {
            //         visibility: "none",
            //         "line-cap": "round",
            //         "line-join": "round"
            //     },
            //     paint: {
            //         "line-opacity": 1,
            //         "line-width": 4,
            //         "line-color": "#333"
            //     }
            // })
        })
    }

    handleCreateMap = map => {
        this.map = map
        const { system } = this.props

        this.setState({ zoom: this.map.getZoom() })

        map.on("load", () => {
            const { scenario } = this.props

            map.addSource("sarp", {
                type: "vector",
                maxzoom: 8,
                tiles: [`${TILE_HOST}/services/sarp_summary/tiles/{z}/{x}/{y}.pbf`]
            })

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
                    // "line-color": "#AAA"
                    "line-color": "#4A0025"
                }
            })

            // const systems = ["State", "HUC", "ECO"]
            // systems.forEach(s => {
            //     this.addLayers(LAYER_CONFIG.filter(({ group }) => group === s), s === system)
            // })

            const colors = TIER_COLORS.reduce((out, color, i) => out.concat([i, color]), [])
            const maxRadius = 20
            const minRadius = 6
            const numSizes = TIER_COLORS.length
            const increment = (maxRadius - minRadius) / (numSizes - 1)
            const sizes = Array.from(Array(numSizes), (_, i) => numSizes - increment * i).reduce(
                (out, size, i) => out.concat([i, size]),
                []
            )

            map.addSource("dams", {
                type: "vector",
                tiles: [`${TILE_HOST}/services/dams_full/tiles/{z}/{x}/{y}.pbf`],
                maxzoom: 14
            })
            map.addLayer({
                id: "dams-heatmap",
                source: "dams",
                "source-layer": "dams",
                type: "heatmap",
                paint: {
                    "heatmap-intensity": 1,
                    "heatmap-color": [
                        "interpolate",
                        ["linear"],
                        ["heatmap-density"],
                        0,
                        "rgba(255,0, 0,0)",
                        0.1,
                        "rgba(255,0,0, 0.5)",
                        1,
                        "rgb(178,24,43)"
                    ],
                    // "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 6, 2, 9, 20],
                    "heatmap-radius": 2,
                    "heatmap-opacity": ["interpolate", ["linear"], ["zoom"], 7, 1, 8, 0]
                }
            })
            map.addLayer({
                id: "dams",
                source: "dams",
                "source-layer": "dams",
                type: "circle",
                minzoom: 5,
                filter: [
                    "any",
                    ["all", ["<=", ["number", ["get", scenario]], 4], ["!=", ["number", ["get", scenario]], -1]],
                    [">=", ["zoom"], 10]
                ],
                paint: {
                    // "circle-color": "rgb(178,24,43)",
                    // TODO: color on tier
                    "circle-color": ["match", ["get", scenario], ...colors, "#AAA"],
                    // "circle-radius": ["interpolate", ["linear"], ["zoom"], 7, 4, 14, 8],
                    "circle-radius": ["match", ["get", scenario], ...sizes, 3],
                    // "circle-opacity": ["case", [">=", ["get", scenario], 0], 0.85, 0.1],
                    "circle-opacity": 0.85,
                    "circle-stroke-width": 1,
                    "circle-stroke-color": "#AAA"
                    // "circle-stroke-opacity": ["case", [">=", ["get", scenario], 0], 0.85, 0.1]
                    // "circle-blur": ["interpolate", ["linear"], ["zoom"], 7, 0.5, 9, 0]
                }
            })

            map.addLayer({
                id: "dams-heatmap-background",
                source: "dams",
                "source-layer": "dams",
                type: "heatmap",
                layout: {
                    visibility: "none"
                },
                paint: {
                    "heatmap-intensity": 1,
                    "heatmap-color": [
                        "interpolate",
                        ["linear"],
                        ["heatmap-density"],
                        0,
                        "rgba(255,255, 255,0)",
                        0.1,
                        "rgba(240, 240, 240, 0.1)",
                        1,
                        "rgb(122,1,119)"
                    ],
                    "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 6, 2, 9, 10],
                    "heatmap-opacity": ["interpolate", ["linear"], ["zoom"], 7, 0.5, 8, 0]
                }
            })
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
        })

        map.on("zoom", () => this.setState({ zoom: this.map.getZoom() }))
        map.on("click", e => {
            const { scenario, selectFeature } = this.props

            const features = map.queryRenderedFeatures(e.point, { layers: ["dams"] })
            if (features.length === 0) return
            console.log("click features", features, features[0].properties[scenario])
            selectFeature(features[0].properties)
        })
        map.foo = () => {
            map.setFilter("dams-heatmap", ["==", "State", "Alabama"])
            map.setFilter("dams-heatmap-background", ["!=", "State", "Alabama"])
            map.setFilter("dams", ["==", "State", "Alabama"])
            map.setFilter("dams-background", ["!=", "State", "Alabama"])
            map.setLayoutProperty("dams-background", "visibility", "visible")
            map.setLayoutProperty("dams-heatmap-background", "visibility", "visible")
        }
    }

    getVisibleLayers = () => {
        const { zoom } = this.state
        const { system } = this.props

        return this.layers.filter(
            ({ group, minzoom, maxzoom }) => group === system && zoom >= minzoom && zoom < maxzoom
        )
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
            </React.Fragment>
        )
    }
}

PriorityMap.propTypes = {
    scenario: PropTypes.string,
    bounds: ImmutablePropTypes.listOf(PropTypes.number), // example: [-180, -86, 180, 86]
    system: PropTypes.string,
    selectedFeature: FeaturePropType,

    setSystem: PropTypes.func.isRequired,
    selectFeature: PropTypes.func.isRequired
}

PriorityMap.defaultProps = {
    scenario: null,
    bounds: null,
    system: null,
    selectedFeature: null
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        bounds: state.get("bounds"),
        system: state.get("system"),
        selectedFeature: state.get("selectedFeature"),
        scenario: state.get("scenario")
    }
}

export default connect(
    mapStateToProps,
    actions
)(PriorityMap)
