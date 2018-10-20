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

import { TILE_HOST, COUNT_COLORS, LAYER_CONFIG } from "./config"
import MapBase from "./MapBase"

// Precalculate colors
// TODO: make this vary by metric
const LEVEL_LEGEND = {}
Object.keys(LAYER_CONFIG).forEach(lyr => {
    LEVEL_LEGEND[lyr] = {
        bins: equalIntervals(summaryStats[lyr].dams, COUNT_COLORS.length),
        colors: COUNT_COLORS
    }
})

class SummaryMap extends Component {
    constructor() {
        super()

        this.state = {
            // activeLayer: null // root ID of the active layer(s)
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


        // TODO: set activeLayer 
        if (system !== prevSystem) {
            if (prevSystem !== null) {
                const hideUnits = this.layers.filter(({group}) => group === prevSystem)
                hideUnits.forEach(({id}) => this.setLayerVisibility(id, false))
            }

            if (system !== null) {
                const showUnits = this.layers.filter(({group}) => group === system)
                showUnits.forEach(({id}) => this.setLayerVisibility(id, true))
            }
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
    }

    addLayers = (layers, visible=true) => {
        const { map } = this

        layers.forEach(lyr => {
            const { bins, colors } = LEVEL_LEGEND[lyr]
            const { id, minzoom, maxzoom } = lyr

            const renderColors = []
            bins.forEach(([min, max], i) => {
                renderColors.push((max - min) / 2 + min) // interpolate from the midpoint
                renderColors.push(colors[i])
            })

            let outlineColor = "#AAA"
            if (id.startsWith("HUC")) {
                outlineColor = "#3F6DD7"
            } else if (id.startsWith("ecoregion")) {
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
                    "fill-opacity": 0.6,
                    "fill-color": ["interpolate", ["linear"], ["get", "dams"], ...renderColors]
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

            // this.layers[id] = [`${id}-fill`, `${id}-outline`]

            // map.addLayer({
            //     id: `${id}-fill`,
            //     source: "sarp",
            //     "source-layer": id,
            //     type: "fill",
            //     minzoom: minzoom || 0,
            //     maxzoom: maxzoom || 21,
            //     filter: [">", "dams", 0],
            //     layout: {
            //         visibility: visible ? "visible" : "none"
            //     },
            //     paint: {
            //         "fill-opacity": 0.6,
            //         "fill-color": ["interpolate", ["linear"], ["get", "dams"], ...renderColors]
            //     }
            // })
            // map.addLayer({
            //     id: `${id}-outline`,
            //     source: "sarp",
            //     "source-layer": id,
            //     type: "line",
            //     minzoom: minzoom || 0,
            //     maxzoom: maxzoom || 21,
            //     filter: [">", "dams", 0],
            //     layout: {
            //         visibility: visible ? "visible" : "none"
            //     },
            //     paint: {
            //         "line-opacity": 1,
            //         "line-width": 0.5,
            //         "line-color": outlineColor
            //     }
            // })

            

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

        // this.updateActiveLevel()

        map.on("load", () => {
            map.addSource("sarp", {
                type: "vector",
                maxzoom: 8,
                tiles: [`${TILE_HOST}/services/sarp_summary/tiles/{z}/{x}/{y}.pbf`]
            })

            const hucs = LAYER_CONFIG.filter(({group})=> group === 'HUC')
            const ecoregions = LAYER_CONFIG.filter(({group})=> group === 'ecoregion')

            this.addLayers(hucs, system === 'HUC')
            this.addLayers(ecoregions, system === 'ecoregion')

            // this.addLabelLayer(labels.toJS())
        })

        map.on("zoom", this.setState({ zoom: map.getZoom() }))
        map.on("click", e => {
            // const { activeLayer } = this.state
            const { system, level, setUnit } = this.props

            if (system === null) return

            // TODO: capture and emit all intersected IDs, let consumer figure out which to process?
            // TODO: can add all layers, only those that are visible will be returned.  Just need to extract out the appropriate IDs
            const features = map.queryRenderedFeatures(e.point, { layers: [`${level}-fill`] })
            if (features.length === 0) return
            console.log("click features", features)
            setUnit(features[0].properties[FEATURE_ID_FIELD[level]])
        })
    }

    getVisibleLayers = () => {
        const { zoom } = this.state
        return this.layers.filter(({ minzoom, maxzoom }) => zoom >= minzoom && zoom < maxzoom)
    }

    renderLegend() {
        // const { activeLayer } = this.state
        
        const { system, level } = this.props

        const visibleLayers = this.getVisibleLayers()

        if (system === null || level === null) return null

        const title = LEVEL_LABELS[level]
        const legendInfo = LEVEL_LEGEND[level]
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

        return <Legend title={title} labels={labels} colors={colors} />
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
    bounds: ImmutablePropTypes.listOf(PropTypes.number), // example: [-180, -86, 180, 86]
    system: PropTypes.string,
    // level: PropTypes.string,
    unit: PropTypes.string,
    labels: ImmutablePropTypes.listOf(ImmutablePropTypes.map),
    
    setSystem: PropTypes.func.isRequired,
    setLevel: PropTypes.func.isRequired,
    setUnit: PropTypes.func.isRequired
}

SummaryMap.defaultProps = {
    bounds: null,
    system: null,
    // level: null,
    unit: null,
    labels: []
}

const mapStateToProps = state => ({
    bounds: state.get("bounds"),
    system: state.get("system"),
    // level: state.get("level"),
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
