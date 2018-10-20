import React, { Component } from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"

import * as actions from "../../actions/priority"
import Legend from "./Legend"
import { FeaturePropType } from "../../CustomPropTypes"

import { TILE_HOST, LAYER_CONFIG } from "./config"
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
            map.addSource("sarp", {
                type: "vector",
                maxzoom: 8,
                tiles: [`${TILE_HOST}/services/sarp_summary/tiles/{z}/{x}/{y}.pbf`]
            })

            const systems = ["states", "HUC", "ECO"]
            systems.forEach(s => {
                this.addLayers(LAYER_CONFIG.filter(({ group }) => group === s), s === system)
            })

            // this.addLabelLayer(labels.toJS())
        })

        map.on("zoom", () => this.setState({ zoom: this.map.getZoom() }))
        map.on("click", e => {
            const { system: curSystem, selectFeature } = this.props

            const layers = this.layers.filter(({ group }) => group === curSystem).map(({ id }) => `${id}-fill`)
            const features = map.queryRenderedFeatures(e.point, { layers })
            if (features.length === 0) return
            console.log("click features", features)
            selectFeature(features[0].properties)
        })
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
    bounds: ImmutablePropTypes.listOf(PropTypes.number), // example: [-180, -86, 180, 86]
    system: PropTypes.string,
    selectedFeature: FeaturePropType,
    labels: ImmutablePropTypes.listOf(ImmutablePropTypes.map),

    setSystem: PropTypes.func.isRequired,
    selectFeature: PropTypes.func.isRequired
}

PriorityMap.defaultProps = {
    bounds: null,
    system: null,
    selectedFeature: null,
    labels: []
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")

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
)(PriorityMap)

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
