/* eslint-disable max-len, no-underscore-dangle */
import React, { useEffect, useRef, useState } from 'react'
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
import Coords from './Coords'

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

const Map = ({ searchFeature, selectedFeature }) => {
  console.log('map render')
  // if there is no window, we cannot render this component
  if (!hasWindow) {
    return null
  }

  const mapNode = useRef(null)
  const mapRef = useRef(null)
  const markerRef = useRef(null)
  const [mapObj, setMap] = useState(null)

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
    setMap(map)

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

  useEffect(() => {
    const { current: map } = mapRef

    if (!(map && searchFeature)) {
      return
    }

    const { id = null, layer, bbox, maxZoom: fitBoundsMaxZoom } = searchFeature
    // if feature is already visible, select it
    // otherwise, zoom and attempt to select it

    // TODO: re-enable
    // let feature = this.selectFeatureByID(id, layer)
    // if (!feature) {
    //     map.once("moveend", () => {
    //         feature = this.selectFeatureByID(id, layer)
    //         // source may still be loading, try again in 1 second
    //         if (!feature) {
    //             setTimeout(() => {this.selectFeatureByID(id, layer)}, 1000)
    //         }
    //     })
    // }

    map.fitBounds(bbox, { padding: 20, fitBoundsMaxZoom, duration: 500 })
  }, [searchFeature])

  return (
    <Wrapper>
      <div ref={mapNode} style={{ width: '100%', height: '100%' }} />

      {/* <StyleSelector map={mapRef.current} styles={styles} token={mapboxToken} /> */}

      {mapObj && (
        <>
          <Coords map={mapObj} />
          <GoToLocation map={mapObj} />
        </>
      )}
    </Wrapper>
  )
}

Map.propTypes = {
  layers: PropTypes.arrayOf(PropTypes.object),
  selectedFeature: FeaturePropType,
  searchFeature: SearchFeaturePropType,
}

Map.defaultProps = {
  layers: [],
  selectedFeature: null,
  searchFeature: null,
}

export default Map
