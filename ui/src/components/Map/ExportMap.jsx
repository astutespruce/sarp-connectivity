/* eslint-disable max-len, no-underscore-dangle */
import React, { useLayoutEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Box } from 'theme-ui'

import {
  flowlinesLayer,
  pointLayer,
  damsSecondaryLayer,
  waterfallsLayer,
  backgroundPointLayer,
} from 'components/Summary/layers'

import { getCenterAndZoom } from './util'
import BasemapSelector from './BasemapSelector'
import { config, sources, basemapLayers } from './config'

import { siteMetadata } from '../../../gatsby-config'

const { mapboxToken } = siteMetadata
if (!mapboxToken) {
  console.error(
    'ERROR: Mapbox token is required in gatsby-config.js siteMetadata'
  )
}

const { styleID: defaultStyleID } = config

const networkHighlightLayer = {
  id: 'network-highlight',
  'source-layer': 'networks',
  minzoom: 10,
  type: 'line',
  filter: ['==', 'networkID', Infinity],
  paint: {
    'line-opacity': 0.75,
    'line-width': {
      base: 1,
      stops: [
        [12, 1],
        [14, 2],
        [15, 3],
        [16, 4],
      ],
    },
    'line-color': '#fd8d3c',
  },
}

export const pointHighlightLayer = {
  id: 'point-highlight',
  type: 'circle',
  minzoom: 10,
  maxzoom: 24,
  paint: {
    'circle-color': '#fd8d3c',
    'circle-radius': {
      base: 1,
      stops: [
        [10, 6],
        [14, 12],
        [16, 14],
      ],
    },
    'circle-stroke-width': 3,
    'circle-stroke-color': '#f03b20',
  },
}

/**
 * A map component that supports export to image.
 * Override of browser's devicePixelRatio adapted from: https://github.com/mpetroff/print-maps/blob/master/js/script.js
 */

// TODO: props: selectedID
const ExportMap = ({
  width,
  height,
  center: centerProp,
  zoom: zoomProp,
  bounds,
  padding,
  styleID,
  barrierType,
  barrierID,
  networkID,
  onCreateMap,
}) => {
  const mapNode = useRef(null)
  const [map, setMap] = useState(null)

  // construct the map within an effect that has no dependencies
  // this allows us to construct it only once at the time the
  // component is constructed.
  useLayoutEffect(() => {
    const { center, zoom } =
      bounds !== null
        ? getCenterAndZoom(mapNode.current, bounds, padding)
        : { center: centerProp, zoom: zoomProp }

    // TODO: set pixel ratio
    // const actualPixelRatio = window.devicePixelRatio;
    // Object.defineProperty(window, 'devicePixelRatio', {
    //     get: function() {return dpi / 96}
    // });

    // Token must be set before constructing map
    mapboxgl.accessToken = mapboxToken

    const mapObj = new mapboxgl.Map({
      container: mapNode.current,
      style: `mapbox://styles/mapbox/${styleID}`,
      center,
      zoom: zoom || 0,
      minZoom: 10,
      maxZoom: 18,
      preserveDrawingBuffer: true,
    })
    window.exportMap = mapObj // for easier debugging and querying via console

    mapObj.addControl(new mapboxgl.NavigationControl(), 'top-right')

    mapObj.on('load', () => {
      // add sources
      Object.entries(sources).forEach(([id, source]) => {
        mapObj.addSource(id, source)
      })

      // Add flowlines and network highlight layers
      mapObj.addLayer(flowlinesLayer)
      mapObj.addLayer({
        ...networkHighlightLayer,
        // id: `${barrierType}_network`,
        source: `${barrierType}_network`,
        filter: ['==', 'networkID', networkID],
      })

      // Add barrier point layers
      mapObj.addLayer(waterfallsLayer)

      if (barrierType === 'barriers') {
        mapObj.addLayer(damsSecondaryLayer)
      }

      mapObj.addLayer({
        id: barrierType,
        source: barrierType,
        'source-layer': barrierType,
        ...pointLayer,
      })

      mapObj.addLayer({
        id: `${barrierType}-background`,
        source: barrierType,
        ...backgroundPointLayer,
      })

      // Add barrier highlight layer.
      mapObj.addLayer({
        ...pointHighlightLayer,
        source: barrierType,
        'source-layer': barrierType,
        filter: ['==', ['get', 'id'], barrierID],
      })

      // rerender to pass map into child components
      setMap(mapObj)
      onCreateMap(mapObj)
    })

    // when this component is destroyed, remove the map
    return () => {
      mapObj.remove()
    }
  }, []) // intentionally omitting onCreateMap from deps list
  // TODO: this should probably be via useCallback, so should be stable

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
      <Box ref={mapNode} sx={{ width: '100%', height: '100%' }} />

      {map && (
        <>
          <BasemapSelector map={map} basemaps={basemapLayers} />
        </>
      )}
    </Box>
  )
}

ExportMap.propTypes = {
  width: PropTypes.string,
  height: PropTypes.string,
  center: PropTypes.arrayOf(PropTypes.number),
  zoom: PropTypes.number,
  bounds: PropTypes.arrayOf(PropTypes.number),
  padding: PropTypes.number,
  styleID: PropTypes.string,
  barrierType: PropTypes.string.isRequired,
  barrierID: PropTypes.number.isRequired,
  networkID: PropTypes.number.isRequired,
  onCreateMap: PropTypes.func.isRequired,
}

ExportMap.defaultProps = {
  width: '800px',
  height: '540px',
  center: null,
  zoom: null,
  bounds: null,
  padding: 0.1,
  styleID: defaultStyleID,
}

export default ExportMap
