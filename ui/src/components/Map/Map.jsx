/* eslint-disable max-len, no-underscore-dangle */
import React, { useLayoutEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

// exclude Mapbox GL from babel transpilation per https://docs.mapbox.com/mapbox-gl-js/guides/migrate-to-v2/
/* eslint-disable-next-line */
import mapboxgl from '!mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

import { getCenterAndZoom } from './util'
import BasemapSelector from './BasemapSelector'
import GoToLocation from './GoToLocation'
import { mapConfig, sources, basemapLayers } from './config'
import Coords from './Coords'

import { siteMetadata } from '../../../gatsby-config'

const { mapboxToken } = siteMetadata
if (!mapboxToken) {
  console.error(
    'ERROR: Mapbox token is required in gatsby-config.js siteMetadata'
  )
}

const {
  bounds: configBounds,
  styleID,
  minZoom,
  maxZoom,
  projection,
} = mapConfig

// IMPORTANT: this component can only be rendered client-side after re-hydration
const Map = ({ bounds, children, onCreateMap }) => {
  const mapNode = useRef(null)
  const [map, setMap] = useState(null)

  // construct the map within an effect that has no dependencies
  // this allows us to construct it only once at the time the
  // component is constructed.
  useLayoutEffect(
    () => {
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
        projection,
      })
      window.map = mapObj // for easier debugging and querying via console

      mapObj.addControl(new mapboxgl.NavigationControl(), 'top-right')

      mapObj.on('load', () => {
        // add sources
        Object.entries(sources).forEach(([id, source]) => {
          mapObj.addSource(id, source)
        })

        // add basemap sources and layers (must be done before adding other layers)
        Object.values(basemapLayers).forEach((layers) => {
          layers.forEach(({ id, source, ...rest }) => {
            mapObj.addSource(id, source)
            mapObj.addLayer({
              ...rest,
              id,
              source: id,
            })
          })
        })

        // rerender to pass map into child components
        setMap(mapObj)
        onCreateMap(mapObj)
      })

      // when this component is destroyed, remove the map
      return () => {
        mapObj.remove()
      }
    },
    // intentionally omitting onCreateMap from deps list
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  return (
    <Box
      sx={{
        // This wrapper must be positioned relative for the map to be able to lay itself out properly
        position: 'relative',
        flex: '1 0 auto',
        height: '100%',
        zIndex: 1,
      }}
    >
      <Box ref={mapNode} sx={{ width: '100%', height: '100%' }} />

      {map && (
        <>
          <Coords map={map} />
          <GoToLocation map={map} />
          <BasemapSelector map={map} basemaps={basemapLayers} />
          {children}
        </>
      )}
    </Box>
  )
}

Map.propTypes = {
  bounds: PropTypes.arrayOf(PropTypes.number),
  children: PropTypes.oneOfType([PropTypes.node, PropTypes.element]),
  onCreateMap: PropTypes.func.isRequired,
}

Map.defaultProps = {
  bounds: configBounds,
  children: null,
}

export default Map
