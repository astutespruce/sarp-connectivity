import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"
// import { fromJS, is } from 'immutable'
import geoViewport from "@mapbox/geo-viewport"
import mapboxgl from "mapbox-gl"
import "mapbox-gl/dist/mapbox-gl.css"

import * as actions from "../../actions"
import { mapColorsToRange } from "../../utils/colors"
import { LabelPointPropType } from "../../CustomPropTypes"
import { labelsToGeoJSON } from "../../utils/geojson"

import summaryStats from "../../data/summary_stats.json"

// TODO: change to one for this account
mapboxgl.accessToken = "pk.eyJ1IjoiYmN3YXJkIiwiYSI6InJ5NzUxQzAifQ.CVyzbyOpnStfYUQ_6r8AgQ"

const TILE_HOST = process.env.NODE_ENV === "production" ? "http://34.237.24.48:8000" : "http://localhost:8000"
// from lowest to highest count, just setup a linear interpolation in that range and find 3 interior breaks
const COUNT_COLORS = ["#fef0d9", "#fdcc8a", "#fc8d59", "#e34a33", "#b30000"]

class Map extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            // location: fromJS(location)
        }

        this.map = null
        this.locationMarker = null
    }

    componentDidMount() {
        const {
            view,
            bounds,
            labels,
            // layers,
            location,
            setUnit
        } = this.props

        const { mapContainer } = this
        let center = [-87.69692774001089, 31.845649246524772] // approx center of SARP
        let zoom = 4

        // If bounds are available, use these to establish center and zoom when map first
        // boots, then fit the bounds more specifically later
        if (bounds && bounds) {
            const { offsetWidth: width, offsetHeight: height } = mapContainer
            const viewport = geoViewport.viewport(bounds.toJS(), [width, height], undefined, undefined, undefined, true)
            // Zoom out slightly to pad around bounds
            zoom = Math.max(viewport.zoom - 1, 0) * 0.99
            /* eslint-disable prefer-destructuring */
            center = viewport.center
        }

        const map = new mapboxgl.Map({
            container: mapContainer,
            style: "mapbox://styles/mapbox/light-v9",
            center,
            zoom
        })

        this.map = map
        window.map = map

        map.addControl(new mapboxgl.NavigationControl(), "top-right")

        map.on("load", () => {
            map.addSource("sarp", {
                type: "vector",
                maxzoom: 8,
                tiles: [`${TILE_HOST}/services/sarp_summary/tiles/{z}/{x}/{y}.pbf`]
            })

            // Initially the mask and boundary are visible
            map.addLayer({
                id: "mask",
                source: "sarp",
                "source-layer": "mask",
                type: "fill",
                layout: {},
                paint: {
                    "fill-opacity": 0.6,
                    "fill-color": "#FFFFFF"
                }
            })
            map.addLayer({
                id: "boundary",
                source: "sarp",
                "source-layer": "boundary",
                type: "line",
                layout: {
                    // visibility: view === "priority" ? "visible" : "none"
                },
                paint: {
                    "line-opacity": 0.8,
                    "line-width": 2,
                    "line-color": "#AAA"
                }
            })

            if (view === "summary") {
                this.addUnitLayers()
                this.addLabelLayer(labels.toJS())
                // this.addSummaryLayers("HUC2", "dams")
                // this.addSummaryLayers("HUC4", "dams", { HUC2: "03" })
            }

            if (location) {
                this.setLocationMarker()
            }

            // Hack: Update to make it fit its viewport
            // this is here to give the styles time to load on the page and set the dimensions for
            // the map container
            map.resize()
        })

        map.on("click", e => {
            if (this.props.system === null) return

            const unit = `${this.props.system}${this.props.level}`
            const layerID = `${unit}-fill`
            // must query against a fill feature; poly outline doesn't work
            const features = map.queryRenderedFeatures(e.point, { layers: [layerID] })
            console.log("click features", features)

            if (features.length > 0) {
                setUnit(features[0].properties[unit])
            }
        })
    }

    componentDidUpdate(prevProps) {
        console.log("component did update", this.props, prevProps)
        // const { bounds, labels } = this.props
        // const { prevBounds, prevLabels } = prevProps

        const { map } = this
        const { bounds: prevBounds, system: prevSystem, level: prevLevel } = prevProps
        const { bounds, system, level, labels } = this.props

        // TODO: immutable comparison
        console.log("new bounds", bounds.toJS(), prevBounds.toJS())
        if (!bounds.equals(prevBounds)) {
            map.fitBounds(bounds.toJS(), { padding: 50 })
        }

        // TODO: update displayed units]

        if (level !== prevLevel) {
            // toogle layer visibility to show these units
            if (prevSystem !== null) {
                map.setLayoutProperty(`${prevLevel}-fill`, "visibility", "none")
                map.setLayoutProperty(`${prevLevel}-outline`, "visibility", "none")
            }

            if (system !== null) {
                map.setLayoutProperty(`${level}-fill`, "visibility", "visible")
                map.setLayoutProperty(`${level}-outline`, "visibility", "visible")
            }

            // update labels
            console.log("labels", labels, labels.toJS())
            map.getSource("unit-labels").setData(labelsToGeoJSON(labels.toJS()))
        }
    }

    addLabelLayer = labels => {
        console.log("labels", labels)

        const { map } = this
        const data = labelsToGeoJSON(labels)

        map.addSource("unit-labels", {
            type: "geojson",
            data
        })

        map.addLayer({
            id: "unit-labels-circle",
            source: "unit-labels",
            type: "circle",
            layout: {},
            paint: {
                "circle-opacity": 0.4,
                "circle-color": "#FFF",
                "circle-stroke-color": "#AAA",
                "circle-stroke-width": 2,
                "circle-radius": 30
            }
        })

        map.addLayer({
            id: "unit-labels-text",
            type: "symbol",
            source: "unit-labels",
            layout: {
                "text-field": ["get", "label"]
            },
            paint: {
                "text-color": "#333",
                "text-halo-color": "#FFF",
                "text-halo-width": 2
            }
        })
    }

    addUnitLayers = () => {
        // add all unit layers, but make them hidden initially
        const units = ["states", "HUC2", "HUC4", "HUC8", "ecoregion1", "ecoregion2", "ecoregion3", "ecoregion4"]

        const { map } = this
        units.forEach(unit => {
            map.addLayer({
                id: `${unit}-fill`,
                source: "sarp",
                "source-layer": unit,
                type: "fill",
                layout: {
                    visibility: "none"
                },
                paint: {
                    "fill-opacity": 0.6,
                    "fill-color": "#FFF"
                }
            })
            map.addLayer({
                id: `${unit}-outline`,
                source: "sarp",
                "source-layer": unit,
                type: "line",
                layout: {
                    visibility: "none"
                },
                paint: {
                    "line-opacity": 0.6,
                    "line-width": 2,
                    "line-color": "#AAA"
                }
            })
        })
    }

    addSummaryLayers = (unit, metric, filters = null) => {
        // unit: states, HUC2, HUC4, etc
        // metric: dams, connectedmiles
        // filters: null or object of key: value pairs.
        const { map } = this

        let filter = [">", metric, 0]
        if (filters) {
            const expressions = Object.entries(filters).map(([k, v]) => ["==", k, v])
            // filter = ["all", filter, ...expressions]
            filter = ["all", filter, ...expressions]
        }

        const colors = mapColorsToRange(COUNT_COLORS, summaryStats[unit][metric])
        map.addLayer({
            id: `${unit}-${metric}-fill`,
            source: "sarp",
            "source-layer": unit,
            type: "fill",
            layout: {},
            paint: {
                "fill-opacity": 0.6,
                "fill-color": ["interpolate", ["linear"], ["get", metric], ...colors]
            },
            filter
        })

        map.addLayer({
            id: `${unit}-outline`,
            source: "sarp",
            "source-layer": unit,
            type: "line",
            layout: {},
            paint: {
                "line-opacity": 0.8,
                "line-color": "#AAAAAA"
            },
            filter
        })

        // map.addLayer({
        //     id: `${unit}-${metric}-centroid`,
        //     source: "sarp",
        //     "source-layer": `${unit}_centroids`,
        //     type: "circle",
        //     layout: {},
        //     paint: {
        //         "circle-opacity": 0.3,
        //         "circle-color": "#FFF",
        //         // "circle-color": ["interpolate", ["linear"], ["get", metric], ...colors]
        //         "circle-stroke-color": "#AAA",
        //         "circle-stroke-width": 2,
        //         "circle-radius": 30
        //     },
        //     filter
        // })

        map.addLayer({
            id: `${unit}-${metric}-label`,
            source: "sarp",
            "source-layer": `${unit}_centroids`,
            type: "symbol",
            layout: {
                "text-field": ["get", metric]
            },
            paint: {
                "text-color": "#333",
                "text-halo-color": "#FFF",
                "text-halo-width": 2
            },
            filter
        })
    }

    setLayerVisibility = (datasetId, isHidden) => {
        const source = `layer-${datasetId}`
        const layers = this.map.getStyle().layers.filter(layer => layer.source === source)
        layers.forEach(({ id }) => {
            this.map.setLayoutProperty(id, "visibility", isHidden ? "none" : "visible")
        })
    }

    render() {
        return (
            <div
                ref={el => {
                    this.mapContainer = el
                }}
                style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0
                }}
            />
        )
    }
}

Map.propTypes = {
    view: PropTypes.string.isRequired, // summary, priority
    system: PropTypes.string,
    level: PropTypes.string,
    labels: ImmutablePropTypes.listOf(LabelPointPropType),
    setUnit: PropTypes.func.isRequired,

    bounds: ImmutablePropTypes.listOf(PropTypes.number), // example: [-180, -86, 180, 86]
    // layers: PropTypes.arrayOf(DatasetPropType),
    location: PropTypes.shape({
        latitude: PropTypes.number.isRequired,
        longitude: PropTypes.number.isRequired
    }) // location to highlight on the map, such as a placename search result
}

Map.defaultProps = {
    bounds: null,
    system: null,
    level: null,
    labels: [],
    // layers: [],
    location: null
}

const mapStateToProps = state => ({
    bounds: state.get("bounds"),
    system: state.get("system"),
    level: state.get("level"),
    unit: state.get("unit"),
    labels: state.get("labels")
})

export default connect(
    mapStateToProps,
    actions
)(Map)
