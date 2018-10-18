import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"
// import { fromJS, is } from 'immutable'
import geoViewport from "@mapbox/geo-viewport"
import mapboxgl from "mapbox-gl"
import "mapbox-gl/dist/mapbox-gl.css"

import * as actions from "../../actions"
import Legend from "./Legend"
import { mapColorsToRange } from "../../utils/colors"
import { equalIntervals } from "../../utils/stats"
import { getParentId } from "../../utils/features"
// import { LabelPointPropType } from "../../CustomPropTypes"
import { labelsToGeoJSON } from "../../utils/geojson"

import summaryStats from "../../data/summary_stats.json"

// TODO: change to one for this account
mapboxgl.accessToken = "pk.eyJ1IjoiYmN3YXJkIiwiYSI6InJ5NzUxQzAifQ.CVyzbyOpnStfYUQ_6r8AgQ"

const TILE_HOST = process.env.NODE_ENV === "production" ? "http://34.237.24.48:8000" : "http://localhost:8000"
// from lowest to highest count, just setup a linear interpolation in that range and find 3 interior breaks
// const COUNT_COLORS = ["#fef0d9", "#fdcc8a", "#fc8d59", "#e34a33", "#b30000"]
const COUNT_COLORS = ["#fff7ec", "#fee8c8", "#fdd49e", "#fdbb84", "#fc8d59", "#ef6548", "#d7301f", "#b30000", "#7f0000"]

const FEATURE_ID_FIELD = {
    HUC2: "HUC2",
    HUC4: "HUC4",
    HUC8: "HUC8",
    ecoregion1: "NA_L1CODE",
    ecoregion2: "NA_L2CODE",
    ecoregion3: "NA_L3CODE",
    ecoregion4: "US_L4CODE"
}

const ZOOM_LEVELS = {
    HUC2: [0, 4.5],
    HUC4: [4.5, 6],
    HUC8: [6, 21],
    // ecoregion1: [0, 4],
    // ecoregion2: [4, 5],
    ecoregion3: [0, 7],
    ecoregion4: [7, 21]
}

const SYSTEM_LEVELS = {
    HUC: ["HUC2", "HUC4", "HUC8"],
    ecoregion: ["ecoregion3", "ecoregion4"]
}

const LEVEL_LABELS = {
    HUC2: "Hydrologic region",
    HUC4: "Hydrologic subregion",
    HUC8: "Hydrologic subbasin",
    ecoregion3: "Level 3 Ecoregion",
    ecoregion4: "Level 4 Ecoregion"
}

// Precalculate colors
const LEVEL_LEGEND = {}
Object.keys(SYSTEM_LEVELS).forEach(s => {
    SYSTEM_LEVELS[s].forEach(l => {
        LEVEL_LEGEND[l] = {
            bins: equalIntervals(summaryStats[l].dams, COUNT_COLORS.length),
            colors: COUNT_COLORS
        }
    })
})

class Map extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            // location: fromJS(location)
            zoom: 4
        }

        this.map = null
        this.locationMarker = null
    }

    componentDidMount() {
        const {
            view,
            bounds,
            // labels,
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

        map.on("zoom", () => {
            this.setState({ zoom: map.getZoom() })
        })

        map.on("load", () => {
            map.addSource("sarp", {
                type: "vector",
                maxzoom: 8,
                tiles: [`${TILE_HOST}/services/sarp_summary/tiles/{z}/{x}/{y}.pbf`]
            })

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
            map.addLayer({
                id: "sarp-fill",
                source: "sarp",
                "source-layer": "boundary",
                type: "fill",
                layout: {},
                paint: {
                    "fill-opacity": 0
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

            if (view === "summary") {
                this.addUnitLayers(SYSTEM_LEVELS.HUC, true)
                this.addUnitLayers(SYSTEM_LEVELS.ecoregion, false)
                // this.addLabelLayer(labels.toJS())
            }

            if (view === "priority") {
                map.addSource("dams", {
                    type: "vector",
                    tiles: [`${TILE_HOST}/services/sarp_dams/tiles/{z}/{x}/{y}.pbf`],
                    maxzoom: 14
                })
                map.addLayer({
                    id: "dams-heatmap",
                    source: "dams",
                    "source-layer": "sarp_dams",
                    type: "heatmap",
                    paint: {
                        "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 0, 1, 9, 3],
                        "heatmap-color": [
                            "interpolate",
                            ["linear"],
                            ["heatmap-density"],
                            0,
                            "rgba(255,215, 215,0)",
                            1,
                            "rgb(178,24,43)"
                        ],
                        "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 4, 2, 9, 8],
                        "heatmap-opacity": ["interpolate", ["linear"], ["zoom"], 7, 1, 9, 0]
                    }
                })
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
            const { system: curSystem, level: curLevel, childLevel: curChildLevel, setLevel } = this.props
            if (curSystem === null) return

            const layerID = `${curLevel}-fill`
            const childLayerID = `${curChildLevel}-fill`
            const layers = [layerID]
            if (curChildLevel) {
                layers.push(childLayerID)
            }

            // TODO: capture and emit all intersected IDs, let consumer figure out which to process?
            let features = map.queryRenderedFeatures(e.point, { layers })
            if (features.length === 0) return
            console.log("click features", features)

            const childFeatures = features.filter(d => d.layer.id === childLayerID)
            features = features.filter(d => d.layer.id === layerID)

            // TODO: the prop with the ID and the level are NOT always the same, need a LUT

            if (childFeatures.length > 0) {
                // set feature in current level, and move to next level
                // setLevel(curChildLevel)
                setUnit(childFeatures[0].properties[FEATURE_ID_FIELD[curChildLevel]], curChildLevel)
            } else {
                // select feature in current level
                setUnit(features[0].properties[FEATURE_ID_FIELD[curLevel]])
            }
        })
    }

    componentDidUpdate(prevProps) {
        console.log("component did update", this.props, "prev:", prevProps)
        // const { bounds, labels } = this.props
        // const { prevBounds, prevLabels } = prevProps

        const { map } = this
        const { bounds: prevBounds, system: prevSystem, level: prevLevel, unit: prevUnit } = prevProps
        const { bounds, system, level, childLevel, labels, levelIndex, unit, index } = this.props
        const unitIDField = FEATURE_ID_FIELD[level]

        if (!bounds.equals(prevBounds)) {
            map.fitBounds(bounds.toJS(), { padding: 10 })
        }

        const prevFillID = `${prevLevel}-fill`
        const prevOutlineID = `${prevLevel}-outline`
        const fillID = `${level}-fill`
        const outlineID = `${level}-outline`
        const highlightID = `${level}-outline-highlight`
        const childFillID = `${childLevel}-fill`
        const childOutlineID = `${childLevel}-outline`

        if (system !== prevSystem) {
            // TODO: overhaul this
            // reset filters and styles for previous things
            // hide previous layers
            // TODO: hide boundary
            if (prevSystem !== null) {
                // map.setLayoutProperty(prevFillID, "visibility", "none")
                // map.setLayoutProperty(prevOutlineID, "visibility", "none")

                SYSTEM_LEVELS[prevSystem].forEach(u => {
                    map.setLayoutProperty(`${u}-fill`, "visibility", "none")
                    map.setLayoutProperty(`${u}-outline`, "visibility", "none")
                })
            }

            if (system === null) {
                // show boundary
                map.setLayoutProperty("sarp-fill", "visibility", "visible")
                map.setLayoutProperty("sarp-outline", "visibility", "visible")
            } else {
                // map.setLayoutProperty(fillID, "visibility", "visible")
                // map.setLayoutProperty(outlineID, "visibility", "visible")

                // hide the boundary
                map.setLayoutProperty("sarp-fill", "visibility", "none")
                map.setLayoutProperty("sarp-outline", "visibility", "none")

                SYSTEM_LEVELS[system].forEach(u => {
                    map.setLayoutProperty(`${u}-fill`, "visibility", "visible")
                    map.setLayoutProperty(`${u}-outline`, "visibility", "visible")
                })
            }
        }

        // TODO: compare before updating
        // map.getSource("unit-labels").setData(labelsToGeoJSON(labels.toJS()))
    }

    addLabelLayer = labels => {
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

    addUnitLayers = (units, visible = false) => {
        units.reverse() // make sure that higher level units are stacked on lower level ones

        const { map } = this
        units.forEach(unit => {
            // const colors = mapColorsToRange(COUNT_COLORS, summaryStats[unit].dams)
            const { bins, colors } = LEVEL_LEGEND[unit]
            const [minzoom, maxzoom] = ZOOM_LEVELS[unit]

            const renderColors = []
            bins.forEach(([min, max], i) => {
                renderColors.push((max - min) / 2 + min) // interpolate from the midpoint
                renderColors.push(colors[i])
            })

            let outlineColor = "#AAA"
            if (unit.startsWith("HUC")) {
                outlineColor = "#3F6DD7"
            } else if (unit.startsWith("ecoregion")) {
                outlineColor = "#008040"
            }

            map.addLayer({
                id: `${unit}-fill`,
                source: "sarp",
                "source-layer": unit,
                type: "fill",
                minzoom,
                maxzoom,
                layout: {
                    visibility: visible ? "visible" : "none"
                },
                paint: {
                    "fill-opacity": 0.6,
                    "fill-color": ["interpolate", ["linear"], ["get", "dams"], ...renderColors]
                }
            })
            map.addLayer({
                id: `${unit}-outline`,
                source: "sarp",
                "source-layer": unit,
                type: "line",
                minzoom,
                maxzoom,
                layout: {
                    visibility: visible ? "visible" : "none"
                },
                paint: {
                    "line-opacity": 1,
                    "line-width": 0.5,
                    "line-color": outlineColor
                }
            })

            // Show this and set the filter to highlight selected features
            map.addLayer({
                id: `${unit}-outline-highlight`,
                source: "sarp",
                "source-layer": unit,
                type: "line",
                layout: {
                    visibility: "none",
                    "line-cap": "round",
                    "line-join": "round"
                },
                paint: {
                    "line-opacity": 1,
                    "line-width": 4,
                    "line-color": "#333"
                }
            })
        })
    }

    render() {
        const { zoom } = this.state
        const { system, view, setSystem } = this.props

        // TODO: optimize this
        let curUnit = null
        let colors = null
        let labels = null
        const showLegend = system !== null && view === "summary"
        if (system) {
            curUnit = SYSTEM_LEVELS[system].filter(u => {
                const [minzoom, maxzoom] = ZOOM_LEVELS[u]
                return zoom >= minzoom && zoom < maxzoom
            })
            const legendInfo = LEVEL_LEGEND[curUnit]
            colors = legendInfo.colors.slice()
            const { bins } = legendInfo
            labels = bins.map(([min, max], i) => {
                if (i === 0) {
                    return `< ${Math.round(max).toLocaleString()} dams`
                }
                if (i === bins.length - 1) {
                    return `≥ ${Math.round(min).toLocaleString()} dams`
                }
                // Use midpoint value
                return Math.round((max - min) / 2 + min).toLocaleString()
            })
        }

        return (
            <React.Fragment>
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

                {showLegend && <Legend title={LEVEL_LABELS[curUnit]} labels={labels} colors={colors} />}
            </React.Fragment>
        )
    }
}

Map.propTypes = {
    view: PropTypes.string.isRequired, // summary, priority
    index: ImmutablePropTypes.map.isRequired,
    system: PropTypes.string,
    level: PropTypes.string,
    childLevel: PropTypes.string,
    levelIndex: PropTypes.number,
    unit: PropTypes.string,
    labels: ImmutablePropTypes.listOf(ImmutablePropTypes.map),
    setUnit: PropTypes.func.isRequired,
    setSystem: PropTypes.func.isRequired,

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
    childLevel: null,
    levelIndex: null,
    unit: null,
    labels: [],
    // layers: [],
    location: null
}

const mapStateToProps = state => ({
    index: state.get("index"),
    bounds: state.get("bounds"),
    system: state.get("system"),
    level: state.get("level"),
    childLevel: state.get("childLevel"),
    unit: state.get("unit"),
    labels: state.get("labels")
})

export default connect(
    mapStateToProps,
    actions
)(Map)

// assign colors to current level

// TODO: if childLevel and unit !== null, apply to child level and filter by unit instead
// if (level !== null) {
//     let records = []
//     if (unit !== null && childLevel !== null) {
//         console.log("info", level, childLevel, unit)
//         records = Array.from(index.get(childLevel).values(), d => ({
//             id: d.get("id"),
//             parentId:
//                 level === "HUC4"
//                     ? getParentId(system, getParentId(system, d.get("id")))
//                     : getParentId(system, d.get("id")),
//             dams: d.get("dams")
//         }))
//         records = records.filter(d => d.parentId === unit)
//         // TODO: filter by ID of parent
//     } else {
//         records = Array.from(index.get(level).values(), d => ({
//             id: d.get("id"),
//             dams: d.get("dams")
//         }))
//     }

//     console.log("records", records)

//     const colorFunc = equalIntervals(records.map(d => d.dams), COUNT_COLORS)
//     const colorLUT = []
//     records.forEach(d => {
//         colorLUT.push(d.id)
//         colorLUT.push(colorFunc(d.dams))
//     })
//     console.log("colors", colorLUT)

//     if (unit !== null && childLevel !== null) {
//         map.setPaintProperty(childFillID, "fill-color", [
//             "match",
//             ["get", FEATURE_ID_FIELD[childLevel]],
//             ...colorLUT,
//             "#FFF"
//         ])
//         map.setPaintProperty(fillID, "fill-color", "#FFF")
//     } else {
//         map.setPaintProperty(fillID, "fill-color", ["match", ["get", unitIDField], ...colorLUT, "#FFF"])
//     }
// }

// if (level !== prevLevel) {
//     console.log("levels changed", level, "prev", prevLevel)
// }

// if (unit !== prevUnit) {
//     if (unit === null) {
//         map.setLayoutProperty(highlightID, "visibility", "none")
//         if (childLevel !== null) {
//             map.setFilter(fillID, null)
//             // map.setPaintProperty(outlineID, "line-opacity", 1)

//             map.setLayoutProperty(childFillID, "visibility", "none")
//             map.setFilter(childFillID, null)

//             map.setLayoutProperty(childOutlineID, "visibility", "none")
//             map.setFilter(childOutlineID, null)
//         }
//         // reset filters
//         console.log("unit is null, reset filters and styles", highlightID)
//     } else {
//         map.setLayoutProperty(highlightID, "visibility", "visible")
//         map.setFilter(highlightID, ["==", unitIDField, unit])

//         if (childLevel !== null) {
//             map.setFilter(fillID, ["!=", unitIDField, unit])
//             // map.setPaintProperty(outlineID, "line-opacity", 0.1)

//             map.setLayoutProperty(childFillID, "visibility", "visible")
//             map.setFilter(childFillID, ["==", unitIDField, unit])

//             map.setLayoutProperty(childOutlineID, "visibility", "visible")
//             map.setFilter(childOutlineID, ["==", unitIDField, unit])
//         }
//     }
// }
