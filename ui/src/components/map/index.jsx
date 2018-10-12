import React from "react"
import PropTypes from "prop-types"
// import { fromJS, is } from 'immutable'
import geoViewport from "@mapbox/geo-viewport"
import mapboxgl from "mapbox-gl"
import "mapbox-gl/dist/mapbox-gl.css"

// TODO: change to one for this account
mapboxgl.accessToken = "pk.eyJ1IjoiYmN3YXJkIiwiYSI6InJ5NzUxQzAifQ.CVyzbyOpnStfYUQ_6r8AgQ"

const TILE_HOST = "http://localhost:8000"
// from lowest to highest count, just setup a linear interpolation in that range and find 3 interior breaks
// const COUNT_COLORS = ['#fef0d9','#fdcc8a','#fc8d59','#e34a33','#b30000']

class Map extends React.Component {
    // static getDerivedStateFromProps(nextProps) {
    //     const {
    //         location, drawingGeometry, footprint, zoi
    //     } = nextProps
    //     return {
    //         location: fromJS(location),
    //     }
    // }

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
            bounds,
            // layers,
            location
        } = this.props

        const { mapContainer } = this
        // let center = [0, 0]
        // let zoom = 1
        let center = [-87.69692774001089, 31.845649246524772]
        let zoom = 4

        // If bounds are available, use these to establish center and zoom when map first
        // boots, then fit the bounds more specifically later
        if (bounds && bounds.length) {
            const { offsetWidth: width, offsetHeight: height } = mapContainer
            const viewport = geoViewport.viewport(bounds, [width, height], undefined, undefined, undefined, true)
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
        // map.setLayerVisibility = this.setLayerVisibility

        map.on("load", () => {
            // Add boundary layers
            map.addSource("boundaries", {
                type: "vector",
                tiles: [`${TILE_HOST}/services/sarp_boundaries/tiles/{z}/{x}/{y}.pbf`],
                maxzoom: 8
            })

            map.addLayer({
                id: "states-outline",
                source: "boundaries",
                "source-layer": "sarp_states_wgs84",
                type: "line",
                layout: {}, // TODO: set as not visible by default
                paint: {
                    "line-color": "#AAAAAA",
                    "line-opacity": 0.8,
                    "line-width": 2
                }
            })

            // colors are inline pairs of value and color, followed by default color
            const colors = ["Texas", "#FF0000", "North Carolina", "#00FF00", "#FFF"]

            map.addLayer({
                id: "states-fill",
                source: "boundaries",
                "source-layer": "sarp_states_wgs84",
                type: "fill",
                layout: {}, // TODO: set as not visible by default
                paint: {
                    "fill-opacity": 0.6,
                    "fill-color": [
                        "match",
                        ["get", "NAME"],
                        ...colors
                        // "Texas",
                        // "#FF0000",

                        // // all others
                        // "#FFF"
                    ]
                }
            })

            if (location) {
                this.setLocationMarker()
            }

            // Hack: Update to make it fit its viewport
            // this is here to give the styles time to load on the page and set the dimensions for
            // the map container
            map.resize()
        })
    }

    // componentDidUpdate(prevProps, prevState) {
    //     // console.log('componentDidUpdate', prevState, this.state)
    //     // Use this function to update the state of the map object to the current state
    //     // of this component

    //     const {
    //         location, drawingGeometry, footprint, zoi
    //     } = this.state
    //     const {
    //         location: prevLocation,
    //         drawingGeometry: prevDrawingGeometry,
    //         footprint: prevFootprint,
    //         zoi: prevZOI
    //     } = prevState

    //     // Update the location marker if needed or remove it
    //     if (!is(location, prevLocation)) {
    //         this.setLocationMarker()
    //     }

    //     // Update drawing geometry
    //     if (!is(drawingGeometry, prevDrawingGeometry)) {
    //         this.setDrawingGeometry()
    //     }

    // }

    setLayerVisibility = (datasetId, isHidden) => {
        const source = `layer-${datasetId}`
        const layers = this.map.getStyle().layers.filter(layer => layer.source === source)
        layers.forEach(({ id }) => {
            this.map.setLayoutProperty(id, "visibility", isHidden ? "none" : "visible")
        })
    }

    // setLocationMarker = () => {
    //     const { location } = this.state

    //     if (location !== null) {
    //         const { latitude, longitude } = location.toObject()
    //         this.map.flyTo({ center: [longitude, latitude], zoom: 10 })

    //         if (!this.locationMarker) {
    //             this.locationMarker = new mapboxgl.Marker().setLngLat([longitude, latitude]).addTo(this.map)
    //         } else {
    //             this.locationMarker.setLngLat([longitude, latitude])
    //         }
    //     } else {
    //         this.locationMarker.remove()
    //         this.locationMarker = null
    //     }
    // }

    // addLayerToMap = (layer) => {
    //     // TODO: caller is responsible for setting next available color from palette if no
    //     // color is defined for dataset (requires state management in container)
    //     const { overlayStyle, minZoom, maxZoom } = layer
    //     const source = `layer-${layer.datasetId}`
    //     const options = {
    //         type: 'vector',
    //         tiles: [`${window.location.protocol}//${TILESERVER_HOST}/services/${layer.datasetId}/tiles/{z}/{x}/{y}.pbf`]
    //     }
    //     if (minZoom) {
    //         options.minzoom = minZoom
    //     }
    //     if (maxZoom) {
    //         options.maxzoom = maxZoom
    //     }
    //     this.map.addSource(source, options)

    //     console.log('adding layer', layer, `/services/${layer.datasetId}/tiles/{z}/{x}/{y}.pbf`)

    //     overlayStyle.forEach((style, i) => {
    //         this.map.addLayer(
    //             Object.assign(
    //                 {
    //                     id: `${source}-${i}`,
    //                     source,
    //                     'source-layer': 'data', // 'data' is hard-coded into vector tile creation pipeline
    //                     layout: {
    //                         visibility: !layer.hidden ? 'visible' : 'none'
    //                     }
    //                 },
    //                 style
    //             )
    //         )
    //     })
    // }

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
    bounds: PropTypes.arrayOf(PropTypes.number), // example: [-180, -86, 180, 86]
    // layers: PropTypes.arrayOf(DatasetPropType),
    location: PropTypes.shape({
        latitude: PropTypes.number.isRequired,
        longitude: PropTypes.number.isRequired
    }) // location to highlight on the map, such as a placename search result
}

Map.defaultProps = {
    bounds: [],
    // layers: [],
    location: null
}

export default Map

// TODO: enable this if we want animated markers
// const addAnimatedLocationToMap = (map, { latitude, longitude }) => {
//     map.addSource('location', {
//         type: 'geojson',
//         data: {
//             type: 'Point',
//             coordinates: [longitude, latitude]
//         }
//     })
//     locationStyle.forEach(style => map.addLayer(style))

//     // setup animation
//     const framesPerSecond = 15
//     const { 'circle-opacity': initialOpacity, 'circle-radius': initialRadius } = locationStyle[0].paint
//     const maxRadius = 15

//     let radius = initialRadius
//     let opacity = initialOpacity
//     let counter = 0
//     // derived from: https://bl.ocks.org/danswick/2f72bc392b65e77f6a9c
//     const animateMarker = () => {
//         // TODO: store this timeout someplace so we can kill it later
//         setTimeout(() => {
//             requestAnimationFrame(animateMarker)
//             counter++

//             radius += (maxRadius - radius) / framesPerSecond
//             opacity -= 0.9 / framesPerSecond
//             opacity = Math.max(opacity, 0)

//             map.setPaintProperty('location-point1', 'circle-radius', radius)
//             map.setPaintProperty('location-point1', 'circle-opacity', opacity)

//             // if (opacity <= 0) {
//             if (counter >= framesPerSecond) {
//                 counter = 0
//                 radius = initialRadius
//                 opacity = initialOpacity
//             }
//         }, 1000 / framesPerSecond)
//     }
//     animateMarker()
// }
