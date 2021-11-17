/* eslint-disable max-len, no-underscore-dangle */
import React, { useLayoutEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

// exclude Mapbox GL from babel transpilation per https://docs.mapbox.com/mapbox-gl-js/guides/migrate-to-v2/
/* eslint-disable-next-line */
import mapboxgl from '!mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

import {
  pointLayer,
  pointHighlightLayer,
  damsSecondaryLayer,
  waterfallsLayer,
  backgroundPointLayer,
} from 'components/Summary/layers'

import {
  BasemapSelector,
  getCenterAndZoom,
  networkLayers,
  mapConfig,
  sources,
  basemapLayers,
} from 'components/Map'

import { siteMetadata } from '../../../../gatsby-config'

const { mapboxToken } = siteMetadata
if (!mapboxToken) {
  console.error(
    'ERROR: Mapbox token is required in gatsby-config.js siteMetadata'
  )
}

const { styleID: defaultStyleID } = mapConfig

/**
 * A map component that supports export to image.
 * Override of browser's devicePixelRatio adapted from: https://github.com/mpetroff/print-maps/blob/master/js/script.js
 */

const Map = ({
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
  onUpdateBasemap,
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

    // Token must be set before constructing map
    mapboxgl.accessToken = mapboxToken

    const mapObj = new mapboxgl.Map({
      container: mapNode.current,
      style: `mapbox://styles/mapbox/${styleID}`,
      center,
      zoom: zoom || 0,
      minZoom: 7,
      maxZoom: 18,
      preserveDrawingBuffer: true,
    })
    window.previewMap = mapObj // for easier debugging and querying via console

    mapObj.addControl(new mapboxgl.NavigationControl(), 'top-right')
    mapObj.addControl(
      new mapboxgl.ScaleControl({ unit: 'imperial' }),
      'bottom-right'
    )

    mapObj.on('load', () => {
      // add sources
      Object.entries(sources).forEach(([id, source]) => {
        mapObj.addSource(id, source)
      })

      // add basemap sources and layers
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

      // Add network layers
      networkLayers.forEach((layer) => {
        if (layer.id.endsWith('-highlight')) {
          mapObj.addLayer({
            ...layer,
            minzoom: 6,
            filter: ['==', barrierType, networkID],
          })
        } else {
          mapObj.addLayer(layer)
        }
      })

      // Add barrier point layers
      mapObj.addLayer(waterfallsLayer)

      if (barrierType === 'small_barriers') {
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

      // Add barrier highlight layer for both on and off-network barriers.
      mapObj.addLayer({
        ...pointHighlightLayer,
        source: barrierType,
        'source-layer': barrierType,
        minzoom: 6,
        filter: ['==', ['get', 'id'], barrierID],
      })
      mapObj.addLayer({
        ...pointHighlightLayer,
        id: 'point-background-highlight',
        source: barrierType,
        'source-layer': 'background',
        minzoom: 9,
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
      <Box
        ref={mapNode}
        sx={{
          width: '100%',
          height: '100%',
          '.mapboxgl-ctrl-logo': {
            display: 'none',
          },
          '.mapboxgl-ctrl-attrib': {
            display: 'none',
          },
        }}
      />

      {map && (
        <>
          <BasemapSelector
            map={map}
            basemaps={basemapLayers}
            onUpdate={onUpdateBasemap}
            size="40px"
            bottom="10px"
          />
        </>
      )}
    </Box>
  )
}

Map.propTypes = {
  width: PropTypes.string,
  height: PropTypes.string,
  center: PropTypes.arrayOf(PropTypes.number),
  zoom: PropTypes.number,
  bounds: PropTypes.arrayOf(PropTypes.number),
  padding: PropTypes.number,
  styleID: PropTypes.string,
  barrierType: PropTypes.string.isRequired,
  barrierID: PropTypes.number.isRequired,
  networkID: PropTypes.number,
  onCreateMap: PropTypes.func.isRequired,
  onUpdateBasemap: PropTypes.func.isRequired,
}

Map.defaultProps = {
  width: '538pt', // 7.5in once border is added
  height: '396pt', // 5.5
  center: null,
  zoom: null,
  bounds: null,
  padding: 0.1,
  styleID: defaultStyleID,
  networkID: null,
}

export default Map
