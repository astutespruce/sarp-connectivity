import React, { Component } from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"
import { fromJS } from "immutable"
import * as actions from "../../../actions/summary"
import Legend from "../../map/Legend"
// import { equalIntervals } from "../../../utils/stats"
import { hexToRGB } from "../../../utils/colors"
import { FeaturePropType } from "../../../CustomPropTypes"
// import { LabelPointPropType } from "../../CustomPropTypes"
// import { labelsToGeoJSON } from "../../utils/geojson"

import summaryStats from "../../../data/summary_stats.json"

import { TILE_HOST, COUNT_COLORS, LAYER_CONFIG, SYSTEMS } from "../../map/config"
import Map from "../../map/index"

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
            const featureId = selectedFeature === null ? null : selectedFeature.get("id")
            visibleLayers.forEach(({ id }) => {
                const featureIdForLyr = featureId
                console.log("foo", featureId, id)

                // if incoming featureId is for a HUC12, also highlight its containing HUC8
                // if (featureId && id === "HUC8" && featureId.length === 12) {
                //     featureIdForLyr = featureId.slice(0, 8)
                // }

                this.setHighlight(id, featureIdForLyr)
            })
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
        map.setLayoutProperty(`${id}-highlight-fill`, "visibility", visibility)
    }

    setHighlight = (id, featureId) => {
        this.map.setFilter(`${id}-highlight`, ["==", "id", featureId === null ? Infinity : featureId])
        // this.map.setFilter(`${id}-highlight-fill`, ["==", "id", featureId === null ? Infinity : featureId])
    }

    addLayers = (layers, visible = true) => {
        const { map } = this

        layers.forEach(lyr => {
            this.layers.push(lyr)

            const { id, minzoom, maxzoom, fill = {}, outline = {} } = lyr
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

            const config = fromJS({
                source: "sarp",
                "source-layer": id,
                minzoom: minzoom || 0,
                maxzoom: maxzoom || 24,
                filter: [">=", "dams", 0],
                layout: {
                    visibility: visible ? "visible" : "none"
                }
            })
            const fillConfig = config
                .mergeDeep(
                    fromJS({
                        id: `${id}-fill`,
                        type: "fill",
                        paint: {
                            "fill-opacity": 0.25,
                            "fill-color": ["interpolate", ["linear"], ["get", "dams"], ...renderColors]
                        }
                    })
                )
                .mergeDeep(fromJS(fill))

            // outline should always be visible for higher level units (e.g., HUC8, )
            // merge in specific style overrides for the layer
            const outlineConfig = config
                .mergeDeep(
                    fromJS({
                        id: `${id}-outline`,
                        type: "line",
                        maxzoom: 24,
                        layout: {
                            "line-cap": "round",
                            "line-join": "round"
                        },
                        paint: {
                            "line-opacity": 1,
                            "line-width": 0.5,
                            "line-color": "#CC99A8" // last color of COUNT_COLORS, then lighted several shades
                        }
                    })
                )
                .mergeDeep(fromJS(outline))

            map.addLayer(fillConfig.toJS())
            map.addLayer(outlineConfig.toJS())
        })
    }

    addHighlightLayer = ({ id }, visible = true) => {
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

        // this.map.addLayer({
        //     id: `${id}-highlight-fill`,
        //     source: "sarp",
        //     "source-layer": id,
        //     type: "fill",
        //     minzoom: 0,
        //     maxzoom: 21,
        //     paint: {
        //         "fill-opacity": 0.25,
        //         // "line-width": 4,
        //         "fill-color": "#333"
        //     },
        //     filter: ["==", "id", Infinity]
        // })
    }

    handleCreateMap = map => {
        this.map = map
        const { system } = this.props

        map.on("load", () => {
            map.setMaxZoom(12)
            map.addSource("sarp", {
                type: "vector",
                maxzoom: 8,
                tiles: [`${TILE_HOST}/services/sarp_summary/tiles/{z}/{x}/{y}.pbf`]
            })

            Object.keys(SYSTEMS).forEach(s => {
                this.addLayers(
                    LAYER_CONFIG.filter(({ group }) => group === s).slice(),
                    // .reverse(),
                    s === system
                )
            })

            this.layers.forEach(lyr => this.addHighlightLayer(lyr, lyr.group === system))

            this.setState({ zoom: this.map.getZoom() })
        })

        map.on("zoom", () => this.setState({ zoom: this.map.getZoom() }))
        map.on("click", e => {
            const { selectFeature } = this.props

            // const layers = this.getVisibleLayers().map(({ id }) => `${id}-fill`)
            const layers = this.layers.map(({ id }) => `${id}-fill`)
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
        const opacity = 0.3
        const colors = legendInfo.colors.slice().map(c => {
            const [r, g, b] = hexToRGB(c)
            return `rgba(${r},${g},${b},${opacity})`
        })

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
                    <h5 className="is-size-7">Show Tiers for: </h5>
                    <div className="buttons has-addons">
                        {Object.entries(SYSTEMS).map(([key, name]) => (
                            <button
                                key={key}
                                className={`button is-small ${system === key ? "active" : ""}`}
                                type="button"
                                onClick={() => setSystem(key)}
                            >
                                {name}
                            </button>
                        ))}
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
