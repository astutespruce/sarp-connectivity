import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"
import ImmutablePropTypes from "react-immutable-proptypes"
import geoViewport from "@mapbox/geo-viewport"
import mapboxgl from "mapbox-gl"
import "mapbox-gl/dist/mapbox-gl.css"

import { LocationPropType } from "../../CustomPropTypes"

import LatLong from "./LatLong"

mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_ACCESS_TOKEN || "" // REQUIRED: this must be present in .env file

class Map extends React.Component {
    constructor(props) {
        super(props)

        this.map = null
        this.mapNode = null
        this.locationMarker = null
    }

    componentDidMount() {
        const { baseStyle, bounds, onCreateMap } = this.props

        const { mapNode } = this
        let center = [0, 0]
        let zoom = 0

        // If bounds are available, use these to establish center and zoom when map first
        if (bounds && bounds.size === 4) {
            const { offsetWidth: width, offsetHeight: height } = mapNode
            const viewport = geoViewport.viewport(bounds.toJS(), [width, height], undefined, undefined, undefined, true)
            // Zoom out slightly to pad around bounds
            zoom = Math.max(viewport.zoom - 1, 0) * 0.9
            /* eslint-disable prefer-destructuring */
            center = viewport.center
        }

        const map = new mapboxgl.Map({
            container: mapNode,
            style: `mapbox://styles/mapbox/${baseStyle}`,
            center,
            zoom
        })

        this.map = map
        window.map = map

        map.addControl(new mapboxgl.NavigationControl(), "top-right")

        map.on("load", () => {
            this.map.resize() // force map to realign center
        })

        onCreateMap(map)
    }

    componentDidUpdate(prevProps) {
        const { bounds: prevBounds, location: prevLocation } = prevProps
        const { bounds, location } = this.props
        const { map } = this

        if (!bounds.equals(prevBounds)) {
            map.fitBounds(bounds.toJS(), { padding: 10 })
        }

        if (!location.equals(prevLocation)) {
            const { latitude = null, longitude = null } = location.toJS()

            if (latitude !== null && longitude !== null) {
                map.flyTo({ center: [longitude, latitude], zoom: 9 })

                if (!this.locationMarker) {
                    this.locationMarker = new mapboxgl.Marker().setLngLat([longitude, latitude]).addTo(this.map)
                } else {
                    this.locationMarker.setLngLat([longitude, latitude])
                }
            } else {
                this.locationMarker.remove()
                this.locationMarker = null
            }
        }
    }

    renderMapNode() {
        return (
            <div
                ref={el => {
                    this.mapNode = el
                }}
                style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0
                }}
            >
                <LatLong />
            </div>
        )
    }

    render() {
        return this.renderMapNode()
    }
}

Map.propTypes = {
    location: ImmutablePropTypes.mapContains({
        latitude: PropTypes.number,
        longitude: PropTypes.number
    }),
    baseStyle: PropTypes.string,
    bounds: ImmutablePropTypes.listOf(PropTypes.number), // example: [-180, -86, 180, 86]
    onCreateMap: PropTypes.func // called with map object when created
}

Map.defaultProps = {
    location: null,
    baseStyle: "light-v9",
    bounds: null,
    onCreateMap: () => {}
}

const mapStateToProps = globalState => {
    const state = globalState.get("map")

    return {
        location: state.get("location")
    }
}

export default connect(mapStateToProps)(Map)

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
