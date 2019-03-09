import React, { Component } from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"
import { fromJS } from "immutable"
import * as actions from "../../../actions/summary"
import Legend from "../../map/Legend"
import { hexToRGB } from "../../../utils/colors"
import { FeaturePropType, SearchFeaturePropType } from "../../../CustomPropTypes"

import { TILE_HOST } from "../../../config"
import { SYSTEMS } from "../../../constants"
import { COLORS, LAYER_CONFIG } from "./config"

import Map from "../../map/index"

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
        const { map, layers } = this
        if (map === null) return

        const {
            system: prevSystem,
            type: prevType,
            searchFeature: prevSearchFeature,
            selectedFeature: prevFeature
        } = prevProps
        const { system, type, searchFeature, selectedFeature } = this.props

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

        if (!selectedFeature.equals(prevFeature)) {
            const featureId = selectedFeature.get("id", null)
            visibleLayers.forEach(({ id }) => {
                this.setHighlight(id, featureId)
            })
        }

        if (type !== prevType) {
            layers.forEach(lyr => {
                const { id } = lyr

                const renderColors = []
                const bins = lyr.bins[type]
                const colors = COLORS.count[bins.length]

                bins.forEach((bin, i) => {
                    renderColors.push(bin)
                    renderColors.push(colors[i])
                })

                map.setPaintProperty(`${id}-fill`, "fill-color", [
                    "interpolate",
                    ["linear"],
                    ["get", type],
                    ...renderColors
                ])
                map.setFilter(`${id}-fill`, [">", type, 0])
                map.setFilter(`${id}-outline`, [">", type, 0])
            })
        }

        if (!searchFeature.equals(prevSearchFeature) && !searchFeature.isEmpty()) {
            const { id = null, layer, bbox, maxZoom } = searchFeature.toJS()

            // if feature is already visible, select it
            // otherwise, zoom and attempt to select it
            const feature = this.selectFeatureByID(id, layer)
            if (!feature) {
                map.once("moveend", () => {
                    this.selectFeatureByID(id, layer)
                })
            }

            map.fitBounds(bbox, { padding: 20, maxZoom, duration: 500 })
        }
    }

    selectFeatureByID = (id, layer) => {
        const { map } = this
        const { selectFeature } = this.props

        const [feature] = map.querySourceFeatures("sarp", { sourceLayer: layer, filter: ["==", "id", id] })

        if (feature !== undefined) {
            selectFeature(fromJS(feature.properties).merge({ layerId: layer }))
        }
        return feature
        
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
        const { type } = this.props

        layers.forEach(lyr => {
            this.layers.push(lyr)

            const { id, minzoom, maxzoom, fill = {}, outline = {} } = lyr
            const renderColors = []
            const bins = lyr.bins[type]
            const colors = COLORS.count[bins.length]
            bins.forEach((bin, i) => {
                renderColors.push(bin)
                renderColors.push(colors[i])
            })

            const config = fromJS({
                source: "sarp",
                "source-layer": id,
                minzoom: minzoom || 0,
                maxzoom: maxzoom || 24,
                filter: [">", type, 0],
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
                            "fill-color": ["interpolate", ["linear"], ["get", type], ...renderColors]
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
                            "line-color": "#CC99A8" // last color of COUNT_COLORS, then lightened several shades
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
            const layers = this.layers.map(({ id }) => `${id}-fill`)
            const features = map.queryRenderedFeatures(e.point, { layers })
            if (features.length === 0) return

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
        const { system, type } = this.props

        if (system === null) return null

        const visibleLayers = this.getVisibleLayers()
        if (visibleLayers.length === 0) return null

        const lyr = visibleLayers[0]
        const { title } = lyr
        const bins = lyr.bins[type]

        const opacity = 0.3
        const colors = COLORS.count[bins.length].slice().map(c => {
            const [r, g, b] = hexToRGB(c)
            return `rgba(${r},${g},${b},${opacity})`
        })

        const labels = bins.map((bin, i) => {
            if (i === 0) {
                return `≤ ${Math.round(bin).toLocaleString()} ${type}`
            }
            if (i === bins.length - 1) {
                return `≥ ${Math.round(bin).toLocaleString()} ${type}`
            }
            // Use midpoint value
            return Math.round(bin).toLocaleString()
        })

        // flip the order since we are displaying from top to bottom
        colors.reverse()
        labels.reverse()

        return <Legend title={title} labels={labels} colors={colors} footnote={`areas with no ${type} are not shown`} />
    }

    render() {
        const { system, type, setSystem, setType, bounds } = this.props

        return (
            <React.Fragment>
                <Map bounds={bounds} onCreateMap={this.handleCreateMap} />

                <div id="SystemChooser" className="mapboxgl-ctrl-top-left flex-container flex-align-center">
                    <h5 style={{ marginRight: "1rem" }}>Show:</h5>
                    <div className="button-group">
                        <button
                            type="button"
                            className={`button ${type === "dams" ? "active" : ""}`}
                            onClick={() => setType("dams")}
                        >
                            dams
                        </button>
                        <button
                            type="button"
                            className={`button ${type === "barriers" ? "active" : ""}`}
                            onClick={() => setType("barriers")}
                        >
                            road-related barriers
                        </button>
                    </div>
                    <h5 style={{ margin: "0 1rem" }}>by</h5>
                    <div className="button-group">
                        {Object.entries(SYSTEMS).map(([key, name]) => (
                            <button
                                key={key}
                                className={`button ${system === key ? "active" : ""}`}
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
    bounds: ImmutablePropTypes.listOf(PropTypes.number).isRequired, // example: [-180, -86, 180, 86]
    system: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    searchFeature: SearchFeaturePropType.isRequired,
    selectedFeature: FeaturePropType.isRequired,

    setSystem: PropTypes.func.isRequired,
    setType: PropTypes.func.isRequired,
    selectFeature: PropTypes.func.isRequired
}

const mapStateToProps = globalState => {
    const state = globalState.get("summary")

    return {
        bounds: globalState.get("map").get("bounds"),
        system: state.get("system"),
        type: state.get("type"),
        searchFeature: state.get("searchFeature"),
        selectedFeature: state.get("selectedFeature")
    }
}

export default connect(
    mapStateToProps,
    actions
)(SummaryMap)
