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

import { TILE_HOST, COUNT_COLORS } from "./config"
import MapBase from "./MapBase"

const FEATURE_ID_FIELD = {
    HUC2: "HUC2",
    HUC4: "HUC4",
    HUC8: "HUC8",
    ecoregion3: "NA_L3CODE",
    ecoregion4: "US_L4CODE"
}

const ZOOM_LEVELS = {
    HUC2: [0, 4.5],
    HUC4: [4.5, 6],
    HUC8: [6, 21],
    ecoregion3: [0, 6],
    ecoregion4: [6, 21]
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
console.log("level legend", LEVEL_LEGEND)

class SummaryMap extends Component {
    constructor() {
        super()

        this.map = null
    }

    componentDidMount() {
        // const { map } = this

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

            this.addUnitLayers(SYSTEM_LEVELS.HUC, true)
            this.addUnitLayers(SYSTEM_LEVELS.ecoregion, false)
            // this.addLabelLayer(labels.toJS())

            // Hack: Update to make it fit its viewport
            // this is here to give the styles time to load on the page and set the dimensions for
            // the map container
            map.resize()
        })

        // map.on("click", e => {
        //     const { system: curSystem, level: curLevel, childLevel: curChildLevel, setLevel } = this.props
        //     if (curSystem === null) return

        //     const layerID = `${curLevel}-fill`
        //     const childLayerID = `${curChildLevel}-fill`
        //     const layers = [layerID]
        //     if (curChildLevel) {
        //         layers.push(childLayerID)
        //     }

        //     // TODO: capture and emit all intersected IDs, let consumer figure out which to process?
        //     let features = map.queryRenderedFeatures(e.point, { layers })
        //     if (features.length === 0) return
        //     console.log("click features", features)

        //     const childFeatures = features.filter(d => d.layer.id === childLayerID)
        //     features = features.filter(d => d.layer.id === layerID)

        //     // TODO: the prop with the ID and the level are NOT always the same, need a LUT

        //     if (childFeatures.length > 0) {
        //         // set feature in current level, and move to next level
        //         // setLevel(curChildLevel)
        //         setUnit(childFeatures[0].properties[FEATURE_ID_FIELD[curChildLevel]], curChildLevel)
        //     } else {
        //         // select feature in current level
        //         setUnit(features[0].properties[FEATURE_ID_FIELD[curLevel]])
        //     }
        // })
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
                filter: [">", "dams", 0],
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
                filter: [">", "dams", 0],
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
        const curUnit = null
        const colors = null
        const labels = null
        const showLegend = false
        // const showLegend = system !== null && view === "summary"
        // if (system) {
        //     curUnit = SYSTEM_LEVELS[system].filter(u => {
        //         const [minzoom, maxzoom] = ZOOM_LEVELS[u]
        //         return zoom >= minzoom && zoom < maxzoom
        //     })
        //     console.log("curUnit", curUnit)
        //     const legendInfo = LEVEL_LEGEND[curUnit]
        //     colors = legendInfo.colors.slice()
        //     const { bins } = legendInfo
        //     labels = bins.map(([min, max], i) => {
        //         if (i === 0) {
        //             return `< ${Math.round(max).toLocaleString()} dams`
        //         }
        //         if (i === bins.length - 1) {
        //             return `≥ ${Math.round(min).toLocaleString()} dams`
        //         }
        //         // Use midpoint value
        //         return Math.round((max - min) / 2 + min).toLocaleString()
        //     })
        // }

        return (
            <React.Fragment>
                <Map bounds={bounds} />

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

SummaryMap.propTypes = {
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

SummaryMap.defaultProps = {
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
)(SummaryMap)
