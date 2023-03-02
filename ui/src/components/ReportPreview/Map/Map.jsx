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
  damsSecondaryLayer,
  roadCrossingsLayer,
  waterfallsLayer,
  offnetworkPointLayer,
  unrankedPointLayer,
  removedBarrierPointLayer,
} from 'components/Summary/layers'

import {
  BasemapSelector,
  getCenterAndZoom,
  networkLayers,
  mapConfig,
  sources,
  basemapLayers,
} from 'components/Map'

import { siteMetadata } from 'config'

import { pointHighlightLayer } from './layers'

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
  networkType,
  barrierID,
  networkID,
  onCreateMap,
  onUpdateBasemap,
  onVisibleLayerUpdate,
}) => {
  const mapNode = useRef(null)
  const mapRef = useRef(null)
  const [map, setMap] = useState(null)

  // TODO: hook this up to map zoom / pan
  const handleVisibleLayerUpdate = () => {
    const { current: mapObj } = mapRef

    if (!mapObj) {
      return
    }

    const flowlineLayers = networkLayers
      .filter(({ id }) => !id.endsWith('-highlight'))
      .map(({ id }) => id)

    const flowlines = mapObj.queryRenderedFeatures(undefined, {
      layers: flowlineLayers,
    })

    const flowlineTypes = flowlines
      .map(({ properties: { mapcode } }) =>
        mapcode === 2 || mapcode === 3 ? 'alteredFlowline' : 'flowline'
      )
      .concat(
        flowlines.map(({ properties: { mapcode } }) =>
          mapcode === 1 || mapcode === 3 ? 'intermittentFlowline' : 'flowline'
        )
      )

    const barrierLayers = [waterfallsLayer.id]
    if (networkType === 'small_barriers') {
      barrierLayers.push(damsSecondaryLayer.id)
      barrierLayers.push(roadCrossingsLayer.id)
    }
    const barriers = mapObj.queryRenderedFeatures(undefined, {
      layers: barrierLayers,
    })

    const visible = new Set(
      flowlineTypes.concat(barriers.map(({ layer: { id } }) => id))
    )
    onVisibleLayerUpdate(visible)
  }

  // construct the map within an effect that has no dependencies
  // this allows us to construct it only once at the time the
  // component is constructed.
  useLayoutEffect(
    () => {
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
      mapRef.current = mapObj
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
              filter: [
                '==',
                networkType === 'dams' ? 'dams' : 'small_barriers',
                networkID,
              ],
            })
          } else {
            mapObj.addLayer(layer)
          }
        })

        // Add barrier point layers
        mapObj.addLayer(waterfallsLayer)

        if (networkType === 'small_barriers') {
          mapObj.addLayer({
            ...damsSecondaryLayer,
            layout: { visibility: 'visible' },
          })
        }
        if (
          networkType === 'small_barriers' ||
          networkType === 'combined_barriers'
        ) {
          mapObj.addLayer({
            ...roadCrossingsLayer,
            layout: { visibility: 'visible' },
          })
        }

        mapObj.addLayer({
          id: networkType,
          source: networkType,
          'source-layer': `ranked_${networkType}`,
          ...pointLayer,
        })

        mapObj.addLayer({
          id: `unranked_${networkType}`,
          source: networkType,
          'source-layer': `unranked_${networkType}`,
          ...unrankedPointLayer,
        })

        mapObj.addLayer({
          id: `offnetwork_${networkType}`,
          source: networkType,
          'source-layer': `offnetwork_${networkType}`,
          ...offnetworkPointLayer,
        })

        mapObj.addLayer({
          id: `removed_${networkType}`,
          source: networkType,
          'source-layer': `removed_${networkType}`,
          ...removedBarrierPointLayer,
        })

        // Add barrier highlight layer for on and off-network barriers.
        mapObj.addLayer({
          ...pointHighlightLayer,
          source: networkType,
          'source-layer': `ranked_${networkType}`,
          minzoom: 6,
          filter: ['==', ['get', 'id'], barrierID],
        })

        mapObj.addLayer({
          ...pointHighlightLayer,
          id: 'unranked-point-highlight',
          source: networkType,
          'source-layer': `unranked_${networkType}`,
          minzoom: 9,
          filter: ['==', ['get', 'id'], barrierID],
        })

        mapObj.addLayer({
          ...pointHighlightLayer,
          id: 'offnetwork-point-highlight',
          source: networkType,
          'source-layer': `offnetwork_${networkType}`,
          minzoom: 9,
          filter: ['==', ['get', 'id'], barrierID],
        })

        mapObj.addLayer({
          ...pointHighlightLayer,
          id: 'removed-point-highlight',
          source: networkType,
          'source-layer': `removed_${networkType}`,
          minzoom: 9,
          filter: ['==', ['get', 'id'], barrierID],
        })

        mapObj.once('idle', handleVisibleLayerUpdate)
        mapObj.on('zoomend', handleVisibleLayerUpdate)
        mapObj.on('moveend', handleVisibleLayerUpdate)

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
  networkType: PropTypes.string.isRequired,
  barrierID: PropTypes.number.isRequired,
  networkID: PropTypes.number,
  onCreateMap: PropTypes.func.isRequired,
  onUpdateBasemap: PropTypes.func.isRequired,
  onVisibleLayerUpdate: PropTypes.func.isRequired,
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
