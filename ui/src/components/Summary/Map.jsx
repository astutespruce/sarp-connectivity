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
import { COLORS } from './config'
import {
  layers,
  pointLayer,
  backgroundPointLayer,
  pointHighlightLayer,
  pointLegends,
} from './layers'

const barrierTypes = ['dams', 'barriers']

const emptyFeatureCollection = {
  type: 'FeatureCollection',
  features: [],
}

const SummaryMap = ({
  system,
  barrierType,
  selectedUnit,
  searchFeature,
  selectedBarrier,
  onSelectUnit,
  onSelectBarrier,
  ...props
}) => {
  const mapRef = useRef(null)

  const [zoom, setZoom] = useState(0)

  const handleCreateMap = useCallback(map => {
    mapRef.current = map

    map.on('zoomend', () => {
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
          // filter: ['>', barrierType, 0],
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
            'fill-color': [
              'match',
              ['get', barrierType],
              0,
              COLORS.empty,
              interpolateExpr(barrierType, bins, colors),
            ],
          },
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

    // Add point layers
    barrierTypes.forEach(t => {
      map.addLayer({
        id: t,
        source: t,
        'source-layer': t,
        ...pointLayer,
        layout: {
          visibility: barrierType === t ? 'visible' : 'none',
        },
      })

      map.addLayer({
        id: `${t}-background`,
        source: t,
        ...backgroundPointLayer,
        layout: {
          visibility: barrierType === t ? 'visible' : 'none',
        },
      })
    })

    // Add barrier highlight layer.
    map.addLayer(pointHighlightLayer)

    const clickLayers = barrierTypes
      .map(t => t)
      .concat(barrierTypes.map(t => `${t}-background`))
      .concat(layers.map(({ id }) => `${id}-fill`))

    map.on('click', ({ point }) => {
      const [feature] = map.queryRenderedFeatures(point, {
        layers: clickLayers,
      })
      if (!feature) {
        return
      }

      const { source, sourceLayer, properties } = feature

      if (source === 'sarp') {
        // summary unit layer
        onSelectUnit({
          ...properties,
          layerId: sourceLayer,
        })
      } else {
        // dam or barrier
        onSelectBarrier({
          ...properties,
          hasnetwork: sourceLayer !== 'background',
        })
      }
    })
    // hook deps are intentionally omitted here
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
  }, [system])

  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    // update renderer and filter on all layers
    layers.forEach(({ id, bins: { [barrierType]: bins } }) => {
      const colors = COLORS.count[bins.length]
      map.setPaintProperty(`${id}-fill`, 'fill-color', [
        'match',
        ['get', barrierType],
        0,
        COLORS.empty,
        interpolateExpr(barrierType, bins, colors),
      ])
    })

    // toggle barriers layer
    barrierTypes.forEach(t => {
      const visibility = barrierType === t ? 'visible' : 'none'
      map.setLayoutProperty(t, 'visibility', visibility)
      map.setLayoutProperty(`${t}-background`, 'visibility', visibility)
    })
  }, [barrierType])

  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    const { id } = pointHighlightLayer

    // setting to empty feature collection effectively hides this layer
    let data = emptyFeatureCollection

    if (selectedBarrier) {
      const { lat, lon } = selectedBarrier
      data = {
        type: 'Point',
        coordinates: [lon, lat],
      }
    }

    map.getSource(id).setData(data)
  }, [selectedBarrier])

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
    const { current: map } = mapRef

    const layer = layers.filter(
      ({ system: lyrSystem, fill: { minzoom, maxzoom } }) =>
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

    const patchEntries = colors.map((color, i) => ({
      color,
      label: labels[i],
    }))

    patchEntries.push({
      color: 'rgba(0,0,0,0.15)',
      label: `no inventoried ${barrierType}`,
    })

    const circles = []
    if (map && map.getZoom() >= 12) {
      const { primary, background } = pointLegends
      circles.push({
        ...primary,
        label: `${barrierType} analyzed for impacts to aquatic connectivity`,
      })

      circles.push({
        ...background,
        label: `${barrierType} not analyzed`,
      })
    }

    return {
      layerTitle: title,
      legendEntries: {
        patches: [{ id: 'summaryAreas', entries: patchEntries }],
        circles,
      },
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
      <Legend title={layerTitle} {...legendEntries} />
    </>
  )
}

SummaryMap.propTypes = {
  system: PropTypes.string.isRequired,
  barrierType: PropTypes.string.isRequired,
  selectedUnit: PropTypes.object,
  searchFeature: SearchFeaturePropType,
  selectedBarrier: PropTypes.object,
  onSelectUnit: PropTypes.func.isRequired,
  onSelectBarrier: PropTypes.func.isRequired,
}

SummaryMap.defaultProps = {
  selectedUnit: null,
  searchFeature: null,
  selectedBarrier: null,
}

export default memo(SummaryMap)
