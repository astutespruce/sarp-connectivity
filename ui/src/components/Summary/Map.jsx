import React, { memo, useEffect, useRef, useCallback } from 'react'
import PropTypes from 'prop-types'

import { Map, interpolateExpr } from 'components/Map'
import { COLORS, LAYER_CONFIG as layers } from './config'

const SummaryMap = ({
  system,
  barrierType,
  selectedUnit,
  onSelectUnit,
  ...props
}) => {
  const mapRef = useRef(null)

  const handleCreateMap = useCallback(map => {
    mapRef.current = map

    layers.forEach(
      ({
        id,
        system: lyrSystem,
        minzoom = 0,
        maxzoom = 24,
        fill,
        outline,
        bins: { [barrierType]: bins },
      }) => {
        const colors = COLORS.count[bins.length]
        const visibility = lyrSystem === system ? 'visible' : 'none'

        // base config for each layer
        const config = {
          source: 'sarp',
          'source-layer': id,
          minzoom,
          maxzoom,
          filter: ['>', barrierType, 0],
        }

        // add fill layer
        const fillID = `${id}-fill`
        map.addLayer({
          ...config,
          ...fill,
          id: fillID,
          type: 'fill',
          layout: {
            visibility,
          },
          paint: {
            'fill-opacity': fill.paint['fill-opacity'],
            'fill-color': interpolateExpr(barrierType, bins, colors),
          },
        })

        map.on('click', fillID, ({ point }) => {
          const [feature] = map.queryRenderedFeatures(point, {
            layers: [fillID],
          })

          if (feature) {
            const { sourceLayer, properties } = feature
            onSelectUnit({
              ...properties,
              layerId: sourceLayer,
            })
          }
        })

        // add outline layer
        map.addLayer({
          ...config,
          ...outline,
          id: `${id}-outline`,
          type: 'line',
          maxzoom: 24,
          layout: {
            visibility,
            'line-cap': 'round',
            'line-join': 'round',
          },
          paint: {
            'line-opacity': 1,
            'line-width': outline.paint['line-width'],
            'line-color': '#CC99A8', // last color of COUNT_COLORS, then lightened several shades
          },
        })

        // add highlight layer
        map.addLayer({
          ...config,
          id: `${id}-highlight`,
          type: 'line',
          minzoom: 0,
          maxzoom: 21,
          layout: {
            visibility,
            'line-cap': 'round',
            'line-join': 'round',
          },
          paint: {
            'line-opacity': 1,
            'line-width': 4,
            'line-color': '#333',
          },
          filter: ['==', 'id', Infinity],
        })
      }
    )
  }, [])

  useEffect(() => {
    console.log('update system')
    const { current: map } = mapRef

    if (!map) return

    const subLayers = ['fill', 'outline', 'highlight']

    // show or hide layers as necessary
    layers.forEach(({ id, system: lyrSystem }) => {
      const visibility = lyrSystem === system ? 'visible' : 'none'
      subLayers.forEach(suffix => {
        map.setLayoutProperty(`${id}-${suffix}`, 'visibility', visibility)
      })
    })
  }, [system])

  useEffect(() => {
    console.log('update type')
    const { current: map } = mapRef

    if (!map) return

    // update renderer and filter on all layers
    layers.forEach(({ id, bins: { [barrierType]: bins } }) => {
      const colors = COLORS.count[bins.length]
      map.setPaintProperty(
        `${id}-fill`,
        'fill-color',
        interpolateExpr(barrierType, bins, colors)
      )
      map.setFilter(`${id}-fill`, ['>', barrierType, 0])
      map.setFilter(`${id}-outline`, ['>', barrierType, 0])
    })
  }, [barrierType])

  useEffect(() => {
    console.log('update selectedUnit')
    const { current: map } = mapRef

    if (!map) return

    // clear out filter on non-visible layers and set for visible layers
    // also clear it out if it is undefined
    const { id = Infinity } = selectedUnit || {}
    layers.forEach(({ id: lyrId, system: lyrSystem }) => {
      map.setFilter(`${lyrId}-highlight`, [
        '==',
        'id',
        lyrSystem === system ? id : Infinity,
      ])
    })
  }, [system, selectedUnit])

  return (
    <>
      <Map onCreateMap={handleCreateMap} {...props} />
    </>
  )
}

SummaryMap.propTypes = {
  system: PropTypes.string,
  barrierType: PropTypes.string,
  selectedUnit: PropTypes.object,
  onSelectUnit: PropTypes.func.isRequired,
}

SummaryMap.defaultProps = {
  system: 'HUC',
  barrierType: 'dams',
  selectedUnit: null,
}

export default memo(SummaryMap)
