/* eslint-disable max-len, no-underscore-dangle */
import React, { useLayoutEffect, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Box } from 'theme-ui'

import { config } from './config'

import { siteMetadata } from '../../../gatsby-config'

const { mapboxToken } = siteMetadata
if (!mapboxToken) {
  console.error(
    'ERROR: Mapbox token is required in gatsby-config.js siteMetadata'
  )
}

const { styleID: defaultStyleID, minZoom, maxZoom } = config

// hide the logo
const mapCSS = {
  '.mapboxgl-ctrl-logo': {
    display: 'none',
  },
}

// NOTE: bounds prop is for the associated bounds; we draw a rectangle for those here
const LocatorMap = ({
  width,
  height,
  center,
  zoom,
  bounds,
  styleID,
  onCreateMap,
}) => {
  const mapNode = useRef(null)
  const mapRef = useRef(null)
  //   const markerRef = useRef(null)

  // construct the map within an effect that has no dependencies
  // this allows us to construct it only once at the time the
  // component is constructed.
  useLayoutEffect(() => {
    // Token must be set before constructing map
    mapboxgl.accessToken = mapboxToken

    const mapObj = new mapboxgl.Map({
      container: mapNode.current,
      style: `mapbox://styles/mapbox/${styleID}`,
      center,
      zoom: zoom || 0,
      minZoom,
      maxZoom,
      preserveDrawingBuffer: true,
      interactive: false,
      attributionControl: false,
    })
    window.locatorMap = mapObj // for easier debugging and querying via console

    mapObj.on('load', () => {
      const [xmin, ymin, xmax, ymax] = bounds

      mapObj.addLayer({
        id: 'marker',
        source: {
          type: 'geojson',
          data: {
            type: 'Point',
            coordinates: [(xmin + xmax) / 2, (ymin + ymax) / 2],
          },
        },
        type: 'circle',
        paint: {
          'circle-color': '#fd8d3c',
          'circle-radius': 8,
          'circle-stroke-width': 2,
          'circle-stroke-color': '#f03b20',
        },
      })

      mapRef.current = mapObj
      onCreateMap(mapObj)
    })

    // when this component is destroyed, remove the map
    return () => {
      mapObj.remove()
    }
  }, []) // intentionally omitting onCreateMap from deps list
  // TODO: this should probably be via useCallback, so should be stable

  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    map.jumpTo({
      center,
      zoom,
    })

    const [xmin, ymin, xmax, ymax] = bounds
    map.getSource('marker').setData({
      type: 'Point',
      coordinates: [(xmin + xmax) / 2, (ymin + ymax) / 2],
    })
  }, [center, zoom, bounds])

  return (
    <Box
      sx={{
        // This wrapper must be positioned relative for the map to be able to lay itself out properly
        position: 'relative',
        width,
        height,
        zIndex: 1,
        border: '1px solid #AAA',
      }}
    >
      <Box ref={mapNode} sx={{ ...mapCSS, width: '100%', height: '100%' }} />
    </Box>
  )
}

LocatorMap.propTypes = {
  width: PropTypes.string,
  height: PropTypes.string,
  center: PropTypes.arrayOf(PropTypes.number).isRequired,
  zoom: PropTypes.number.isRequired,
  bounds: PropTypes.arrayOf(PropTypes.number).isRequired,
  styleID: PropTypes.string,
  onCreateMap: PropTypes.func.isRequired,
}

LocatorMap.defaultProps = {
  width: '200px',
  height: '200px',
  styleID: defaultStyleID,
}

export default LocatorMap
