import React, {
  memo,
  useEffect,
  useRef,
  useCallback,
  useState,
  useMemo,
} from 'react'
import PropTypes from 'prop-types'

import {
  Map,
  Legend,
  interpolateExpr,
  SearchFeaturePropType,
} from 'components/Map'
import { COLORS, LAYER_CONFIG as layers } from './config'

const SummaryMap = ({
  system,
  barrierType,
  selectedUnit,
  searchFeature,
  onSelectUnit,
  ...props
}) => {
  const mapRef = useRef(null)

  // first layer of system is default on init
  // const [visibleLayer, setVisibleLayer] = useState(layers.filter(({system: lyrSystem}) => lyrSystem === system)[0])
  const [zoom, setZoom] = useState(0)

  const handleCreateMap = useCallback(map => {
    mapRef.current = map

    map.on('zoomend', () => {
      // setVisibleLayer(getVisibleLayer(map, system))
      setZoom(map.getZoom())
    })

    setZoom(map.getZoom())

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

    // setVisibleLayer(getVisibleLayer(map, system))
    // TODO: update legend
  }, [system])

  useEffect(() => {
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

    // TODO: update legend
  }, [barrierType])

  useEffect(() => {
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

  useEffect(() => {
    const { current: map } = mapRef
    if (!(map && searchFeature)) {
      return
    }

    const { id = null, layer, bbox, maxZoom: fitBoundsMaxZoom } = searchFeature
    // if feature is already visible, select it
    // otherwise, zoom and attempt to select it

    let feature = selectFeatureByID(id, layer)
    if (!feature) {
      map.once('moveend', () => {
        feature = selectFeatureByID(id, layer)
        // source may still be loading, try again in 1 second
        if (!feature) {
          setTimeout(() => {
            selectFeatureByID(id, layer)
          }, 1000)
        }
      })
    }

    map.fitBounds(bbox, { padding: 20, fitBoundsMaxZoom, duration: 500 })
  }, [searchFeature])

  const { layerTitle, legendEntries } = useMemo(() => {
    const layer = layers.filter(
      ({ system: lyrSystem, minzoom, maxzoom }) =>
        lyrSystem === system && zoom >= minzoom && zoom < maxzoom
    )[0]

    const {
      title,
      bins: { [barrierType]: bins },
    } = layer
    // flip the order of colors and bins since we are displaying from top to bottom
    // add opacity to color
    const colors = COLORS.count[bins.length].map(c => `${c}4d`).reverse()

    const labels = bins
      .map((bin, i) => {
        if (i === 0) {
          return `≤ ${Math.round(bin).toLocaleString()} ${barrierType}`
        }
        if (i === bins.length - 1) {
          return `≥ ${Math.round(bin).toLocaleString()} ${barrierType}`
        }
        // Use midpoint value
        return Math.round(bin).toLocaleString()
      })
      .reverse()

    return {
      layerTitle: title,
      legendEntries: colors.map((color, i) => ({
        color,
        label: labels[i],
      })),
    }
  }, [system, barrierType, zoom])

  const selectFeatureByID = (id, layer) => {
    const [feature] = mapRef.current.querySourceFeatures('sarp', {
      sourceLayer: layer,
      filter: ['==', 'id', id],
    })

    if (feature !== undefined) {
      onSelectUnit({ ...feature.properties, layerId: layer })
    }
    return feature
  }

  return (
    <>
      <Map onCreateMap={handleCreateMap} {...props} />
      <Legend
        title={layerTitle}
        entries={legendEntries}
        footnote={`areas with no ${barrierType} are not shown`}
      />
    </>
  )
}

SummaryMap.propTypes = {
  system: PropTypes.string.isRequired,
  barrierType: PropTypes.string.isRequired,
  selectedUnit: PropTypes.object,
  searchFeature: SearchFeaturePropType,
  onSelectUnit: PropTypes.func.isRequired,
}

SummaryMap.defaultProps = {
  selectedUnit: null,
  searchFeature: null,
}

export default memo(SummaryMap)
