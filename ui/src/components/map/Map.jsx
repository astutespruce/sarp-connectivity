/* eslint-disable max-len, no-underscore-dangle */
import React, { useEffect, useLayoutEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

import styled from 'style'
import { hasWindow } from 'util/dom'
import { getCenterAndZoom } from './util'
import BasemapSelector from './BasemapSelector'
import GoToLocation from './GoToLocation'
import { FeaturePropType, SearchFeaturePropType } from './proptypes'

import { siteMetadata } from '../../../gatsby-config'
import { config, sources, basemapLayers } from './config'
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

const { bounds, styleID, minZoom, maxZoom } = config

const Map = ({ searchFeature, selectedFeature }) => {
  // if there is no window, we cannot render this component
  if (!hasWindow) {
    return null
  }

  const mapNode = useRef(null)
  const [map, setMap] = useState(null)

  // construct the map within an effect that has no dependencies
  // this allows us to construct it only once at the time the
  // component is constructed.
  useLayoutEffect(() => {
    const { center, zoom } = getCenterAndZoom(mapNode.current, bounds, 0.1)

    // Token must be set before constructing map
    mapboxgl.accessToken = mapboxToken

    const mapObj = new mapboxgl.Map({
      container: mapNode.current,
      style: `mapbox://styles/mapbox/${styleID}`,
      center,
      zoom: zoom || 0,
      minZoom,
      maxZoom,
    })
    window.map = mapObj // for easier debugging and querying via console


    mapObj.addControl(new mapboxgl.NavigationControl(), 'top-right')

    mapObj.on('load', () => {

    // rerender to pass map into child components
    setMap(mapObj)

      // add sources
      Object.entries(sources).forEach(([id, source]) => {
        mapObj.addSource(id, source)
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
      mapObj.remove()
    }
  }, [])

  useEffect(() => {
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

      {map && (
        <>
          <Coords map={map} />
          <GoToLocation map={map} />
          <BasemapSelector
            map={map}
            defaultStyle={styleID}
            basemaps={basemapLayers}
          />
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
