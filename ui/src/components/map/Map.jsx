/* eslint-disable max-len, no-underscore-dangle */
import React, { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

import styled from 'style'
import { hasWindow } from 'util/dom'
import { getCenterAndZoom } from './util'
// import StyleSelector from './StyleSelector'
import GoToLocation from './GoToLocation'
import { FeaturePropType, SearchFeaturePropType } from './proptypes'

import { siteMetadata } from '../../../gatsby-config'
import { config, sources } from './config'

// This wrapper must be positioned relative for the map to be able to lay itself out properly
const Wrapper = styled.div`
  position: relative;
  flex: 1 0 auto;
  height: 100%;
  z-index: 1;
`

const { mapboxToken } = siteMetadata
if (!mapboxToken) {
  console.error(
    'ERROR: Mapbox token is required in gatsby-config.js siteMetadata'
  )
}

const { bounds, baseStyle, minZoom, maxZoom } = config

const Map = ({searchFeature, selectedFeature}) => {
  // if there is no window, we cannot render this component
  if (!hasWindow) {
    return null
  }

  const mapNode = useRef(null)
  const mapRef = useRef(null)
  const markerRef = useRef(null)

  // construct the map within an effect that has no dependencies
  // this allows us to construct it only once at the time the
  // component is constructed.
  useEffect(() => {
    const { center, zoom } = getCenterAndZoom(mapNode.current, bounds, 0.1)

    // Token must be set before constructing map
    mapboxgl.accessToken = mapboxToken

    const map = new mapboxgl.Map({
      container: mapNode.current,
      style: `mapbox://styles/mapbox/${baseStyle}`,
      center,
      zoom: zoom || 0,
      minZoom,
      maxZoom,
    })
    mapRef.current = map
    window.map = map // for easier debugging and querying via console

    map.addControl(new mapboxgl.NavigationControl(), 'top-right')

    // if (styles.length > 1) {
    //   map.addControl(
    //     new StyleSelector({
    //       styles,
    //       token: mapboxToken,
    //     }),
    //     'bottom-left'
    //   )
    // }

    map.on('load', () => {
      // add sources
      Object.entries(sources).forEach(([id, source]) => {
        map.addSource(id, source)
      })

      // // add layers
      // layers.forEach(layer => {
      //   map.addLayer(layer)
      // })
    })

    // hook up map events here, such as click, mouseenter, mouseleave
    // e.g., map.on('click', (e) => {})

    // when this component is destroyed, remove the map
    return () => {
      map.remove()
    }
  }, [])

  const handleSetLocation = ({ latitude, longitude }) => {
    const { current: map } = mapRef
    const { current: marker } = markerRef

    if (latitude === null || longitude === null) {
      if (marker) {
        marker.remove()
      }

      markerRef.current = null
    } else {
      map.flyTo({ center: [longitude, latitude], zoom: 9 })
      if (!marker) {
        markerRef.current = new mapboxgl.Marker()
          .setLngLat([longitude, latitude])
          .addTo(map)
      } else {
        markerRef.current.setLngLat([longitude, latitude])
      }
    }
  }

  return (
    <Wrapper>
      <div ref={mapNode} style={{ width: '100%', height: '100%' }} />
      <GoToLocation setLocation={handleSetLocation} />
      {/* <StyleSelector map={mapRef.current} styles={styles} token={mapboxToken} /> */}
    </Wrapper>
  )
}

Map.propTypes = {
  layers: PropTypes.arrayOf(PropTypes.object),
  // location: LocationPropType,
  selectedFeature: FeaturePropType,
  searchFeature: SearchFeaturePropType,
}

Map.defaultProps = {
  layers: [],
  location: null,
  selectedFeature: null,
  searchFeature: null,
}

export default Map
