import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"
// import { fromJS, is } from 'immutable'
import geoViewport from "@mapbox/geo-viewport"
import mapboxgl from "mapbox-gl"
import "mapbox-gl/dist/mapbox-gl.css"

import * as actions from "../../actions"

// TODO: change to one for this account
mapboxgl.accessToken = "pk.eyJ1IjoiYmN3YXJkIiwiYSI6InJ5NzUxQzAifQ.CVyzbyOpnStfYUQ_6r8AgQ"

class Map extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            zoom: 4
        }

        this.map = null
    }

    componentDidMount() {
        const { bounds } = this.props

        let { zoom } = this.state

        const { mapContainer } = this
        let center = [-87.69692774001089, 31.845649246524772] // approx center of SARP

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
    }

    renderMapNode() {
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

    render() {
        return this.renderMapNode()
    }
}

Map.propTypes = {
    bounds: ImmutablePropTypes.listOf(PropTypes.number) // example: [-180, -86, 180, 86]\
}

Map.defaultProps = {
    bounds: null
}

const mapStateToProps = state => ({
    bounds: state.get("bounds")
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
