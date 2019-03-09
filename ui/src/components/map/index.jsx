import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"
import ImmutablePropTypes from "react-immutable-proptypes"
import geoViewport from "@mapbox/geo-viewport"
import mapboxgl from "mapbox-gl"
import "mapbox-gl/dist/mapbox-gl.css"

import LatLong from "./LatLong"

mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_ACCESS_TOKEN || "" // REQUIRED: this must be present in .env file

class Map extends React.Component {
    constructor(props) {
        super(props)

        this.map = null
        this.mapNode = null
        this.coordsNode = null
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

        map.addControl(new mapboxgl.NavigationControl({ showCompass: false }), "top-right")

        map.on("load", () => {
            this.map.resize() // force map to realign center
        })

        map.on("mousemove", ({ lngLat: { lat, lng } }) => {
            this.coordsNode.innerHTML = `${Math.round(lat * 100000) / 100000}° N, ${Math.round(lng * 100000) /
                100000}° E`
        })

        onCreateMap(map)
    }

    componentDidUpdate(prevProps) {
        const { bounds: prevBounds, center: prevCenter, location: prevLocation } = prevProps
        const { bounds, center, location } = this.props
        const { map } = this

        if (!bounds.equals(prevBounds)) {
            map.fitBounds(bounds.toJS(), { padding: 10 })
        }

        if (!center.equals(prevCenter)) {
            const { latitude = null, longitude = null, zoom = map.getZoom() } = center.toJS()
            if (latitude !== null && longitude !== null) {
                map.flyTo({ center: [longitude, latitude], zoom })
            }
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
                <div
                    ref={el => {
                        this.coordsNode = el
                    }}
                    className="map-coordinates is-size-7"
                />
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
    }).isRequired,
    baseStyle: PropTypes.string,
    bounds: ImmutablePropTypes.listOf(PropTypes.number), // example: [-180, -86, 180, 86]
    center: ImmutablePropTypes.mapContains({
        latitude: PropTypes.number,
        longitude: PropTypes.number,
        zoom: PropTypes.number
    }),
    onCreateMap: PropTypes.func // called with map object when created
}

Map.defaultProps = {
    baseStyle: "light-v9",
    bounds: null,
    center: null,
    onCreateMap: () => {}
}

const mapStateToProps = globalState => {
    const state = globalState.get("map")

    return {
        location: state.get("location"),
        bounds: state.get("bounds"),
        center: state.get("center")
    }
}

export default connect(mapStateToProps)(Map)
