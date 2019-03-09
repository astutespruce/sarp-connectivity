import React, { Component } from "react"
import PropTypes from "prop-types"
import { fromJS } from "immutable"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"

import * as actions from "../../../actions/priority"
import Legend from "./Legend"
import { FeaturePropType, SearchFeaturePropType } from "../../../CustomPropTypes"
import { recordsToGeoJSON } from "../../../utils/geojson"

import { TILE_HOST } from "../../../config"
import { SCENARIOS } from "../../../constants"
import {
    maskFill,
    maskOutline,
    unitFill,
    unitOutline,
    parentOutline,
    unitHighlightFill,
    unitHighlightOutline,
    pointHighlight,
    backgroundPoint,
    excludedPoint,
    includedPoint,
    topRank,
    lowerRank
} from "./styles"
import { LAYER_CONFIG } from "./config"
import Map from "../../map/index"

class PriorityMap extends Component {
    constructor() {
        super()

        this.state = {
            zoom: null
        }

        this.map = null
    }

    componentDidUpdate(prevProps) {
        const { map } = this
        if (map === null) return

        const {
            scenario: prevScenario,
            summaryUnits: prevSummaryUnits,
            layer: prevLayer,
            selectedFeature: prevSelectedFeature,
            mode: prevMode,
            filters: prevFilters,
            tierThreshold: prevTierThreshold,
            searchFeature: prevSearchFeature
        } = prevProps
        const {
            scenario,
            summaryUnits,
            layer,
            selectedFeature,
            mode,
            filters,
            tierThreshold,
            searchFeature
        } = this.props

        // Only changes on select / deselect of a barrier
        if (!selectedFeature.equals(prevSelectedFeature)) {
            this.updateBarrierHighlight()
        }

        // Only happens on start over or when going back from a selected layer
        if (layer !== prevLayer) {
            if (prevLayer !== null) {
                this.removeUnitLayers()
            }

            if (layer !== null) {
                this.addUnitLayers()
            }
        }

        // Only changes on select / deselect of summary units, which is limited to select mode
        if (summaryUnits !== prevSummaryUnits) {
            if (layer !== null) {
                this.updateUnitHighlight()
            }
        }

        // Only happens in results view
        if (scenario !== prevScenario || tierThreshold !== prevTierThreshold) {
            map.setFilter("rank-top", ["<=", `${scenario}_tier`, tierThreshold])
            map.setFilter("rank-low", [">", `${scenario}_tier`, tierThreshold])
        }

        if (mode !== prevMode) {
            if (mode === "select") {
                this.setUnitLayerVisibility(true)
            } else {
                this.setUnitLayerVisibility(false)
            }

            if (prevMode === "filter" && mode !== "results") {
                this.removeBarrierFilterLayers()
            }

            if ((prevMode === "filter" || prevMode === "results") && (mode !== "filter" && mode !== "results")) {
                map.setLayoutProperty("point-no-network", "visibility", "none")
            }

            if (mode === "filter") {
                if (prevMode === "results") {
                    this.setFilterLayerVisibility(true)
                } else {
                    this.addBarrierFilterLayers()
                }

                map.setLayoutProperty("point-no-network", "visibility", "visible")
            }

            if (prevMode === "results") {
                this.removeRankedBarrierLayers()
            }

            if (mode === "results") {
                this.setFilterLayerVisibility(false)
                this.addRankedBarrierLayers()
            }
        }

        if (mode === "filter" && filters !== prevFilters) {
            this.updateBarrierFilters()
        }

        if (!searchFeature.equals(prevSearchFeature) && !searchFeature.isEmpty()) {
            const { id = null, bbox } = searchFeature.toJS()

            // if feature is already visible, select it
            // otherwise, zoom and attempt to select it
            const feature = this.selectUnitByID(id)
            if (!feature) {
                map.once("moveend", () => {
                    this.selectUnitByID(id)
                })
            }
            map.fitBounds(bbox, { padding: 20, duration: 500 })
        }
    }

    selectUnitByID = id => {
        const { map } = this
        const { selectUnit, summaryUnits } = this.props

        const [feature] = map.queryRenderedFeatures({ layers: ["unit-fill"], filter: ["==", "id", id] })
        if (feature !== undefined) {
            const { properties } = feature
            if (!summaryUnits.map(u => u.get("id")).has(properties.id)) {
                // only select it if it wasn't previously selected, otherwise
                // we unexpectedly remove it
                selectUnit(feature.properties)
            }
        }
        return feature
    }

    updateUnitHighlight = () => {
        const { map } = this
        const { summaryUnits } = this.props

        const ids = summaryUnits.toJS().map(({ id }) => id)
        const filterExpr = ids.length > 0 ? ["in", "id", ...ids] : ["==", "id", Infinity]

        map.setFilter("unit-highlight-fill", filterExpr)
        map.setFilter("unit-highlight-outline", filterExpr)
    }

    updateBarrierHighlight = () => {
        const { map } = this
        const { selectedFeature } = this.props

        if (!selectedFeature.isEmpty()) {
            map.getSource("point-highlight").setData({
                type: "Point",
                coordinates: [selectedFeature.get("lon"), selectedFeature.get("lat")]
            })

            // make sure it is on top
            /* eslint-disable no-underscore-dangle */
            map.moveLayer("point-highlight", map.style._layers.length)
            map.setLayoutProperty("point-highlight", "visibility", "visible")
        } else {
            map.setLayoutProperty("point-highlight", "visibility", "none")
        }
    }

    setUnitLayerVisibility = visible => {
        // set fill and outline layer visibility
        const { map } = this

        if (!map.getLayer("unit-fill")) return

        const visibility = visible ? "visible" : "none"
        map.setLayoutProperty("unit-fill", "visibility", visibility)
        map.setLayoutProperty("unit-outline", "visibility", visibility)
        map.setLayoutProperty("unit-highlight-fill", "visibility", visibility)
        // unit-highlight-outline deliberately left as-is

        if (map.getLayer("unit-parent-outline")) {
            map.setLayoutProperty("unit-parent-outline", "visibility", visibility)
        }
    }

    setFilterLayerVisibility = visible => {
        const { map } = this

        const layer = map.getLayer("point-included")

        if (!layer) return

        // have to flip layout state to force refresh
        layer.setLayoutProperty("visibility", visible ? "visible" : "none")
    }

    addUnitLayers = () => {
        const { map } = this
        const { layer } = this.props
        const { minzoom = 0, maxzoom = 24, parent } = LAYER_CONFIG[layer]

        const config = fromJS({
            "source-layer": layer,
            minzoom,
            maxzoom
        })

        if (parent) {
            map.addLayer(
                config
                    .merge({ "source-layer": parent })
                    .mergeDeep(fromJS(parentOutline))
                    .toJS()
            )
        }
        map.addLayer(config.mergeDeep(fromJS(unitFill)).toJS())
        map.addLayer(config.mergeDeep(fromJS(unitOutline)).toJS())
        map.addLayer(config.mergeDeep(fromJS(unitHighlightFill)).toJS())
        map.addLayer(config.mergeDeep(fromJS(unitHighlightOutline)).toJS())
    }

    removeUnitLayers = () => {
        const { map } = this

        if (!map.getLayer("unit-fill")) return

        map.removeLayer("unit-fill")
        map.removeLayer("unit-outline")
        map.removeLayer("unit-highlight-fill")
        map.removeLayer("unit-highlight-outline")
        if (map.getLayer("unit-parent-outline")) {
            map.removeLayer("unit-parent-outline")
        }
    }

    getBarrierFilter = inclusive => {
        const { layer, summaryUnits, filters } = this.props
        const unitIds = summaryUnits.toJS().map(({ id }) => id)

        const inExpr = inclusive ? "in" : "!in"

        const filterValues = Object.entries(filters.toJS())
            .filter(([, v]) => v.length > 0)
            .map(([k, v]) => [inExpr, k, ...v])

        let filterExpr = null
        if (inclusive) {
            filterExpr = ["all", [inExpr, layer, ...unitIds], ...filterValues]
        } else {
            filterExpr = ["all", ["any", [inExpr, layer, ...unitIds], ...filterValues]]
        }

        return filterExpr
    }

    addBarrierFilterLayers = () => {
        const { map } = this
        const { type } = this.props

        const config = fromJS({
            source: type,
            "source-layer": type
        })

        map.addLayer(
            fromJS(excludedPoint)
                .merge(config)
                .merge({
                    filter: this.getBarrierFilter(false)
                })
                .toJS()
        )
        map.addLayer(
            fromJS(includedPoint)
                .merge(config)
                .merge({
                    filter: this.getBarrierFilter(true)
                })
                .toJS()
        )
    }

    updateBarrierFilters = () => {
        const { map } = this

        if (!map.getLayer("point-included")) return

        map.setFilter("point-excluded", this.getBarrierFilter(false))
        map.setFilter("point-included", this.getBarrierFilter(true))
    }

    removeBarrierFilterLayers = () => {
        const { map } = this

        if (!map.getLayer("point-included")) return

        map.removeLayer("point-excluded")
        map.removeLayer("point-included")
    }

    addRankedBarrierLayers = () => {
        const { map } = this
        const { rankData, scenario, tierThreshold } = this.props

        if (!rankData.size) return

        const geojson = recordsToGeoJSON(rankData.toJS())

        map.addSource("ranked", {
            type: "geojson",
            data: geojson
        })

        map.addLayer(
            fromJS(lowerRank)
                .merge({ filter: [">", `${scenario}_tier`, tierThreshold] })
                .toJS()
        )

        map.addLayer(
            fromJS(topRank)
                .merge({ filter: ["<=", `${scenario}_tier`, tierThreshold] })
                .toJS()
        )
    }

    removeRankedBarrierLayers = () => {
        const { map } = this

        if (!map.getLayer("rank-top")) return

        map.removeLayer("rank-top")
        map.removeLayer("rank-low")
        map.removeSource("ranked")
    }

    handleCreateMap = map => {
        this.map = map

        const { type, onMapLoad } = this.props

        this.setState({ zoom: map.getZoom() })

        map.on("load", () => {
            map.addSource("sarp", {
                type: "vector",
                maxzoom: 8,
                tiles: [`${TILE_HOST}/services/sarp_summary/tiles/{z}/{x}/{y}.pbf`]
            })

            // Initially the mask and boundary are visible
            map.addLayer(maskFill)
            map.addLayer(maskOutline)

            map.addSource(type, {
                type: "vector",
                tiles: [`${TILE_HOST}/services/sarp_${type}/tiles/{z}/{x}/{y}.pbf`],
                minzoom: 5,
                maxzoom: 12
            })

            map.addLayer(
                fromJS(backgroundPoint)
                    .merge({
                        source: type,
                        "source-layer": "background"
                    })
                    .toJS()
            )

            // Add highlight layer.  Note: on subsequent additions of layers, move this to the top.
            map.addLayer(pointHighlight)

            onMapLoad()
        })

        map.on("zoom", () => this.setState({ zoom: this.map.getZoom() }))
        map.on("click", e => {
            const { layer, selectFeature, selectUnit, mode } = this.props
            const { zoom } = this.state

            switch (mode) {
                case "select": {
                    if (layer !== null) {
                        const features = map.queryRenderedFeatures(e.point, { layers: ["unit-fill"] })
                        if (features.length > 0) {
                            selectUnit(features[0].properties)
                        }
                    }
                    break
                }
                case "filter": {
                    if (zoom < 9) return
                    const points = map.queryRenderedFeatures(e.point, {
                        layers: ["point-no-network", "point-excluded", "point-included"]
                    })
                    if (points.length > 0) {
                        const point = points[0]
                        selectFeature(
                            fromJS(point.properties).merge({ hasnetwork: point.layer.id !== "point-no-network" })
                        )
                    }
                    break
                }
                case "results": {
                    const points = map.queryRenderedFeatures(e.point, {
                        layers: ["rank-top", "rank-low", "point-excluded", "point-no-network"]
                    })
                    if (points.length > 0) {
                        const point = points[0]

                        const properties = fromJS(point.properties).merge({
                            hasnetwork: point.layer.id !== "point-no-network"
                        })

                        if (point.source === "ranked") {
                            const { id } = point.properties
                            const tilePoints = map.querySourceFeatures(type, {
                                sourceLayer: type,
                                filter: ["==", "id", id]
                            })
                            if (tilePoints.length) {
                                selectFeature(fromJS(tilePoints[0].properties).mergeDeep(properties))
                            }
                        } else {
                            selectFeature(properties)
                        }
                    }
                    break
                }
            }
        })
    }

    renderLegend() {
        const { zoom } = this.state
        const { mode, type, tierThreshold } = this.props

        const excludedLegend = {
            label: `Not selected ${type}`,
            color: excludedPoint.paint["circle-color"],
            borderColor: excludedPoint.paint["circle-stroke-color"],
            size: 12
        }

        const backgroundLegend = {
            label: "Not included in analysis",
            color: backgroundPoint.paint["circle-color"],
            borderColor: backgroundPoint.paint["circle-stroke-color"],
            size: 10
        }

        if (mode === "filter") {
            if (zoom <= includedPoint.minzoom) {
                return <Legend title={`Zoom in further to see selected ${type}`} />
            }

            const entries = [
                {
                    label: `Selected ${type}`,
                    color: includedPoint.paint["circle-color"],
                    size: 16
                }
            ]
            if (zoom >= excludedPoint.minzoom) {
                entries.push(excludedLegend)
            }
            if (zoom >= backgroundPoint.minzoom) {
                entries.push(backgroundLegend)
            }

            return <Legend entries={entries} />
        }

        if (mode === "results") {
            if (zoom <= topRank.minzoom) {
                return <Legend title={`Zoom in further to see top-ranked ${type}`} />
            }

            const tierLabel = tierThreshold === 1 ? "tier 1" : `tiers 1 - ${tierThreshold}`
            const entries = [
                {
                    label: `Top-ranked ${type} (${tierLabel})`,
                    color: topRank.paint["circle-color"],
                    size: 16
                }
            ]
            if (zoom >= lowerRank.minzoom) {
                // TODO: lower ranks
                entries.push({
                    label: `Lower-ranked ${type}`,
                    color: lowerRank.paint["circle-color"],
                    size: 16
                })
            }
            if (zoom >= excludedPoint.minzoom) {
                entries.push(excludedLegend)
            }
            if (zoom >= backgroundPoint.minzoom) {
                entries.push(backgroundLegend)
            }

            return <Legend entries={entries} />
        }

        return null
    }

    render() {
        const { mode, scenario, setScenario } = this.props

        return (
            <React.Fragment>
                <Map baseStyle="streets-v9" onCreateMap={this.handleCreateMap} />

                {mode === "results" ? (
                    <div id="SystemChooser" className="mapboxgl-ctrl-top-left flex-container flex-align-center">
                        <h5 style={{ marginRight: "1rem" }}>Show ranks for:</h5>
                        <div className="button-group">
                            {Object.entries(SCENARIOS).map(([key, name]) => (
                                <button
                                    key={key}
                                    className={`button ${scenario === key ? "active" : ""}`}
                                    type="button"
                                    onClick={() => setScenario(key)}
                                >
                                    {name}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : null}

                {this.renderLegend()}
            </React.Fragment>
        )
    }
}

PriorityMap.propTypes = {
    type: PropTypes.string.isRequired,
    scenario: PropTypes.string,
    bounds: ImmutablePropTypes.listOf(PropTypes.number), // example: [-180, -86, 180, 86]
    selectedFeature: FeaturePropType.isRequired,
    searchFeature: SearchFeaturePropType.isRequired,
    filters: ImmutablePropTypes.mapOf(
        ImmutablePropTypes.setOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number]))
    ).isRequired,
    layer: PropTypes.string,
    summaryUnits: ImmutablePropTypes.set.isRequired,
    mode: PropTypes.string.isRequired,
    rankData: ImmutablePropTypes.listOf(ImmutablePropTypes.map).isRequired,
    tierThreshold: PropTypes.number.isRequired,

    setScenario: PropTypes.func.isRequired,
    selectFeature: PropTypes.func.isRequired,
    selectUnit: PropTypes.func.isRequired,
    onMapLoad: PropTypes.func.isRequired
}

PriorityMap.defaultProps = {
    scenario: null,
    bounds: null,
    layer: null
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")
    const crossfilter = globalState.get("crossfilter")

    return {
        type: state.get("type"),
        selectedFeature: state.get("selectedFeature"),
        searchFeature: state.get("searchFeature"),
        scenario: state.get("scenario"),
        summaryUnits: state.get("summaryUnits"),
        layer: state.get("layer"),
        mode: state.get("mode"),
        rankData: state.get("rankData"),
        tierThreshold: state.get("tierThreshold"),

        filters: crossfilter.get("filters")
    }
}

export default connect(
    mapStateToProps,
    actions
)(PriorityMap)

// TODO: make this work based on featureIDs set via tippecanoe.  Requires new version of tippecanoe and int IDs

// map.off("mousemove", `${layer}-fill`, this.handleFeatureHover)
// map.off("mouseleave", `${layer}-fill`, this.handleFeatureUnhover)

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
