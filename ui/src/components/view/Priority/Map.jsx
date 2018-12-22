import React, { Component } from "react"
import PropTypes from "prop-types"
import { fromJS } from "immutable"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"

import * as actions from "../../../actions/priority"
import Legend from "./Legend"
import { FeaturePropType } from "../../../CustomPropTypes"

import { TILE_HOST } from "../../../config"
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
    includedPoint
} from "./styles"
import { LAYER_CONFIG } from "./config"
import Map from "../../map/index"

// Construct colors for mapbox GL layers in advance
// const priorityColors = PRIORITY_TIER_COLORS.reduce((out, color, i) => out.concat([i, color]), [])

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
            mode: prevMode,
            filters: prevFilters
        } = prevProps
        const { scenario, summaryUnits, layer, selectedFeature, mode, filters } = this.props

        if (selectedFeature !== prevSelectedFeature) {
            this.updateBarrierHighlight()
        }

        if (summaryUnits !== prevSummaryUnits) {
            if (layer !== null) {
                this.updateUnitHighlight()
            }
        }

        if (layer !== prevLayer) {
            if (prevLayer !== null) {
                this.removeUnitLayers()
            }

            if (layer !== null) {
                this.addUnitLayers()
            }
        }

        if (mode !== prevMode) {
            // modes other than filter or prioritize will have null layers, and be covered above
            // this.setLayerVisibility(mode === "select" && layer !== null)

            if (mode === "select") {
                this.setLayerVisibility(true)
                map.setLayoutProperty("point-no-network", "visibility", "none")
            } else {
                this.setLayerVisibility(false)
            }

            if (prevMode === "filter") {
                this.removeBarrierFilterLayers()
            }

            if (mode === "filter") {
                this.addBarrierFilterLayers()
                map.setLayoutProperty("point-no-network", "visibility", "visible")
            }
        }

        if (filters !== prevFilters && mode === "filter") {
            this.updateBarrierFilters()
        }
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
        const { selectedFeature } = this.props
        const filterExpr = selectedFeature !== null ? ["==", "id", selectedFeature.get("id")] : ["==", "id", Infinity]
        this.map.setFilter("point-highlight", filterExpr)
    }

    setLayerVisibility = visible => {
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
            filterExpr = ["all", ["==", "hasnetwork", true], [inExpr, layer, ...unitIds], ...filterValues]
        } else {
            filterExpr = ["all", ["==", "hasnetwork", true], ["any", [inExpr, layer, ...unitIds], ...filterValues]]
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

        // add highlight layer last so it is on top
        map.addLayer(
            fromJS(pointHighlight)
                .merge(config)
                .toJS()
        )
    }

    updateBarrierFilters = () => {
        const { map } = this
        map.setFilter("point-excluded", this.getBarrierFilter(false))
        map.setFilter("point-included", this.getBarrierFilter(true))
    }

    removeBarrierFilterLayers = () => {
        const { map } = this

        map.removeLayer("point-excluded")
        map.removeLayer("point-included")
        map.removeLayer("point-highlight")
    }

    handleCreateMap = map => {
        this.map = map

        const { type } = this.props

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

            // Add the background (no network) points up front, but not visible
            // these don't change style based on any props
            map.addLayer(
                fromJS(backgroundPoint)
                    .merge(
                        fromJS({
                            source: type,
                            "source-layer": type
                        })
                    )
                    .toJS()
            )
        })

        map.on("zoom", () => this.setState({ zoom: this.map.getZoom() }))
        map.on("click", e => {
            const { layer, selectFeature, selectUnit, mode } = this.props

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
                    const points = map.queryRenderedFeatures(e.point, {
                        layers: ["point-no-network", "point-excluded", "point-included"]
                    })
                    if (points.length > 0) {
                        const point = points[0]
                        console.log(point)
                        selectFeature(fromJS(point.properties))
                        // selectFeature(fromJS(point.properties).merge({ layerId: point.sourceLayer, type }))
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

    renderLegend() {
        const { zoom } = this.state
        const { mode, type } = this.props

        if (mode === "filter") {
            // TODO: based on zoom
            if (zoom <= 5) {
                return <Legend title={`Zoom in further to see selected ${type}`} />
            }

            const entries = [
                {
                    label: `Selected ${type}`,
                    color: includedPoint.paint["circle-color"],
                    size: 16
                }
            ]
            if (zoom >= 7) {
                entries.push({
                    label: `Not selected ${type}`,
                    color: excludedPoint.paint["circle-color"],
                    borderColor: excludedPoint.paint["circle-stroke-color"],
                    size: 12
                })
            }
            if (zoom >= 10) {
                entries.push({
                    label: `Off-network ${type}`,
                    color: backgroundPoint.paint["circle-color"],
                    size: 10
                })
            }

            return <Legend entries={entries} />
        }

        return null
    }

    render() {
        const { scenario, setScenario, bounds } = this.props

        return (
            <React.Fragment>
                <Map baseStyle="streets-v9" bounds={bounds} onCreateMap={this.handleCreateMap} />
                {this.renderLegend()}
            </React.Fragment>
        )
    }
}

PriorityMap.propTypes = {
    type: PropTypes.string.isRequired,
    scenario: PropTypes.string,
    bounds: ImmutablePropTypes.listOf(PropTypes.number), // example: [-180, -86, 180, 86]
    selectedFeature: FeaturePropType,
    filters: ImmutablePropTypes.mapOf(
        ImmutablePropTypes.setOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number]))
    ).isRequired,
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
        type: state.get("type"),
        bounds: state.get("bounds"),
        selectedFeature: state.get("selectedFeature"),
        scenario: state.get("scenario"),
        summaryUnits: state.get("summaryUnits"),
        filters: state.get("filters"),
        layer: state.get("layer"),
        mode: state.get("mode")
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
