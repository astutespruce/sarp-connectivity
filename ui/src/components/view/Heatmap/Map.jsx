import React, { Component } from "react"
import PropTypes from "prop-types"
// import { fromJS } from "immutable"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"

// import * as actions from "../../../actions/priority"
// import Legend from "./Legend"
import { FeaturePropType } from "../../../CustomPropTypes"

import { TILE_HOST } from '../../../config'
import { LAYER_CONFIG, TIER_COLORS, PRIORITY_TIER_COLORS, SCENARIOS, SYSTEMS } from "../../map/config"
import { default as MapBase } from "../../map/index"

// Construct colors for mapbox GL layers in advance
const priorityColors = PRIORITY_TIER_COLORS.reduce((out, color, i) => out.concat([i, color]), [])

class Map extends Component {
    constructor() {
        super()

        // this.state = {}

        this.map = null
        this.layers = []
    }

    addHeatmapLayer = () => {
        // Show a heatmap of all points (no attributes)
        // TODO: make this gray or push to background with zoom?
        this.map.addLayer({
            id: "dams_heatmap",
            source: "dams",
            "source-layer": "dams_heatmap",
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
                    "rgba(178,24,43, 0.8)"
                ],
                // "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 6, 2, 9, 20],
                "heatmap-radius": 2,
                "heatmap-opacity": ["interpolate", ["linear"], ["zoom"], 7, 1, 8, 0]
            }
        })
    }

    addDamsLayer = () => {
        const { map } = this

        map.addLayer({
            id: "dams",
            source: "dams",
            "source-layer": "dams",
            type: "circle",
            minzoom: 7,
            paint: {
                "circle-color": "rgb(178,24,43)",
                "circle-radius": ["interpolate", ["linear"], ["zoom"], 9, 2, 14, 8],
                // "circle-opacity": 0.25,
                "circle-stroke-width": 0.1,
                "circle-stroke-color": "#FFF",
                "circle-blur": ["interpolate", ["linear"], ["zoom"], 7, 0.5, 9, 0]
            }
        })
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
                // "line-color": "#AAA"
                "line-color": "#4A0025"
            }
        })
    }

    handleCreateMap = map => {
        this.map = map
        // const { system } = this.props

        // this.setState({ zoom: this.map.getZoom() })

        map.on("load", () => {
            // const { scenario } = this.props

            map.addSource("sarp", {
                type: "vector",
                maxzoom: 8,
                tiles: [`${TILE_HOST}/services/sarp_summary/tiles/{z}/{x}/{y}.pbf`]
            })
            map.addSource("dams", {
                type: "vector",
                tiles: [`${TILE_HOST}/services/dams/tiles/{z}/{x}/{y}.pbf`],
                maxzoom: 14
            })

            this.addBoundaryLayers()
            this.addHeatmapLayer()
            this.addDamsLayer()
        })

        // map.on("click", e => {
        //     const { scenario, layer, selectFeature, selectUnit } = this.props

        //     if (layer !== null) {
        //         const features = map.queryRenderedFeatures(e.point, { layers: [`${layer}-fill`] })
        //         if (features.length > 0) {
        //             selectUnit(features[0].properties.id)
        //         }
        //         return
        //     }

        //     const features = map.queryRenderedFeatures(e.point, { layers: ["dams_priority"] })
        //     if (features.length === 0) return
        //     console.log("click features", features, features[0].properties[scenario])
        //     selectFeature(features[0].properties)
        // })
        // map.foo = () => {
        //     map.setFilter("dams-heatmap", ["==", "State", "Alabama"])
        //     map.setFilter("dams-heatmap-background", ["!=", "State", "Alabama"])
        //     map.setFilter("dams", ["==", "State", "Alabama"])
        //     map.setFilter("dams-background", ["!=", "State", "Alabama"])
        //     map.setLayoutProperty("dams-background", "visibility", "visible")
        //     map.setLayoutProperty("dams-heatmap-background", "visibility", "visible")
        // }
    }

    render() {
        const { bounds } = this.props

        return <MapBase bounds={bounds} onCreateMap={this.handleCreateMap} />
    }
}

Map.propTypes = {
    // scenario: PropTypes.string,
    bounds: ImmutablePropTypes.listOf(PropTypes.number) // example: [-180, -86, 180, 86]
    // system: PropTypes.string,
    // selectedFeature: FeaturePropType,
    // layer: PropTypes.string,
    // summaryUnits: ImmutablePropTypes.set.isRequired,

    // setSystem: PropTypes.func.isRequired,
    // setScenario: PropTypes.func.isRequired
    // selectFeature: PropTypes.func.isRequired,
    // selectUnit: PropTypes.func.isRequired
}

Map.defaultProps = {
    // scenario: null,
    bounds: null
    // system: null,
    // selectedFeature: null,
    // layer: null
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        bounds: state.get("bounds")
        // system: state.get("system"),
        // selectedFeature: state.get("selectedFeature"),
        // scenario: state.get("scenario")
        // summaryUnits: state.get("summaryUnits"),
        // layer: state.get("layer")
    }
}

export default connect(
    mapStateToProps
    // actions
)(Map)

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
