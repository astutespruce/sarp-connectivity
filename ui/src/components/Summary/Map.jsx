import React, {
  memo,
  useEffect,
  useRef,
  useCallback,
  useState,
  useMemo,
} from 'react'
import PropTypes from 'prop-types'
import mapboxgl from 'mapbox-gl'

import {
  Map,
  Legend,
  interpolateExpr,
  SearchFeaturePropType,
} from 'components/Map'
import { capitalize } from 'util/format'
import { isEmptyString } from 'util/string'
import { COLORS } from './config'
import {
  layers,
  networkLayers,
  waterfallsLayer,
  damsSecondaryLayer,
  pointLayer,
  backgroundPointLayer,
  pointHighlightLayer,
  pointHoverLayer,
  pointLegends,
} from './layers'

import { barrierTypeLabels } from '../../../config/constants'

const barrierTypes = ['dams', 'small_barriers']

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

  const selectFeatureByID = useCallback((id, layer) => {
    const { current: map } = mapRef

    if (!map) return null

    const [feature] = map.querySourceFeatures('summary', {
      sourceLayer: layer,
      filter: ['==', 'id', id],
    })

    if (feature !== undefined) {
      onSelectUnit({ ...feature.properties, layerId: layer })
    }
    return feature
  }, []) // onSelectUnit intentionally omitted here

  const handleCreateMap = useCallback((map) => {
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
          source: 'summary',
          'source-layer': id,
          minzoom,
          maxzoom,
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

    // Add network layers
    networkLayers.forEach((layer) => {
      map.addLayer(layer)
    })

    // Add barrier point layers
    map.addLayer(waterfallsLayer)
    map.addLayer(damsSecondaryLayer)

    barrierTypes.forEach((t) => {
      map.addLayer({
        id: `${t}-background`,
        source: t,
        ...backgroundPointLayer,
        layout: {
          visibility: barrierType === t ? 'visible' : 'none',
        },
      })

      map.addLayer({
        id: t,
        source: t,
        'source-layer': t,
        ...pointLayer,
        layout: {
          visibility: barrierType === t ? 'visible' : 'none',
        },
      })
    })

    // Add barrier highlight layers
    map.addLayer(pointHoverLayer)
    map.addLayer(pointHighlightLayer)

    const pointLayers = barrierTypes
      .map((t) => t)
      .concat(barrierTypes.map((t) => `${t}-background`))
      .concat(['dams-secondary', 'waterfalls'])

    const clickLayers = pointLayers.concat(layers.map(({ id }) => `${id}-fill`))

    // add hover and tooltip to point layers
    const tooltip = new mapboxgl.Popup({
      closeButton: false,
      closeOnClick: false,
      anchor: 'left',
      offset: 20,
    })
    pointLayers.forEach((id) => {
      map.on('mouseenter', id, ({ features: [feature] }) => {
        if (map.getZoom() <= 7) {
          return
        }

        const {
          geometry: { coordinates },
        } = feature
        map.getSource(pointHoverLayer.id).setData({
          type: 'Point',
          coordinates,
        })

        /* eslint-disable-next-line no-param-reassign */
        map.getCanvas().style.cursor = 'pointer'
        const prefix = barrierTypeLabels[feature.source]
          ? `${capitalize(barrierTypeLabels[feature.source]).slice(
              0,
              barrierTypeLabels[feature.source].length - 1
            )}: `
          : ''
        const { name } = feature.properties
        tooltip
          .setLngLat(coordinates)
          .setHTML(
            `<b>${prefix}${!isEmptyString(name) ? name : 'Unknown name'}</b>`
          )
          .addTo(map)
      })
      map.on('mouseleave', id, () => {
        map.getSource(pointHoverLayer.id).setData(emptyFeatureCollection)

        /* eslint-disable-next-line no-param-reassign */
        map.getCanvas().style.cursor = ''
        tooltip.remove()
      })
    })

    map.on('click', ({ point }) => {
      const [feature] = map.queryRenderedFeatures(point, {
        layers: clickLayers,
      })
      if (!feature) {
        return
      }

      const { source, sourceLayer, properties } = feature

      if (source === 'summary') {
        // summary unit layer
        onSelectUnit({
          ...properties,
          layerId: sourceLayer,
        })
      } else {
        // query HUC8 and HUC12 names to show with barrier details
        let HUC8Name = null
        let HUC12Name = null

        if (properties.HUC8 && properties.HUC12) {
          const [HUC8] = map.querySourceFeatures('summary', {
            sourceLayer: 'HUC8',
            filter: ['==', 'id', properties.HUC8],
          })
          if (HUC8) {
            HUC8Name = HUC8.properties.name
          }

          const [HUC12] = map.querySourceFeatures('summary', {
            sourceLayer: 'HUC12',
            filter: ['==', 'id', properties.HUC12],
          })
          if (HUC12) {
            HUC12Name = HUC12.properties.name
          }
        }

        const {
          geometry: {
            coordinates: [lon, lat],
          },
        } = feature

        const {
          hasnetwork = sourceLayer !== 'background',
          ranked = sourceLayer !== 'background' && source !== 'waterfalls',
        } = properties

        // dam, barrier, waterfall
        onSelectBarrier({
          ...properties,
          HUC8Name,
          HUC12Name,
          barrierType: source,
          lat,
          lon,
          hasnetwork,
          ranked,
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
      subLayers.forEach((suffix) => {
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
    barrierTypes.forEach((t) => {
      const visibility = barrierType === t ? 'visible' : 'none'
      map.setLayoutProperty(t, 'visibility', visibility)
      map.setLayoutProperty(`${t}-background`, 'visibility', visibility)
    })

    // clear highlighted networks
    map.setFilter('network-highlight', ['==', 'dams', Infinity])
    map.setFilter('network-intermittent-highlight', ['==', 'dams', Infinity])

    map.setLayoutProperty(
      'dams-secondary',
      'visibility',
      barrierType === 'small_barriers' ? 'visible' : 'none'
    )
  }, [barrierType])

  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    const { id } = pointHighlightLayer

    // setting to empty feature collection effectively hides this layer
    let data = emptyFeatureCollection
    let networkID = Infinity

    if (selectedBarrier) {
      const { lat, lon, upnetid = Infinity } = selectedBarrier
      data = {
        type: 'Point',
        coordinates: [lon, lat],
      }

      // highlight upstream network
      networkID = upnetid
    }

    map.setFilter('network-highlight', [
      'all',
      ['==', ['get', 'intermittent'], false],
      ['==', ['get', barrierType], networkID],
    ])
    map.setFilter('network-intermittent-highlight', [
      'all',
      ['==', ['get', 'intermittent'], true],
      ['==', ['get', barrierType], networkID],
    ])

    map.getSource(id).setData(data)
  }, [selectedBarrier, barrierType])

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
  }, [searchFeature, selectFeatureByID])

  const { layerTitle, legendEntries } = useMemo(() => {
    const { current: map } = mapRef

    const [layer] = layers.filter(
      ({ system: lyrSystem, fill: { minzoom, maxzoom } }) =>
        lyrSystem === system && zoom >= minzoom && zoom <= maxzoom
    )

    if (layer === undefined) {
      return {
        layerTitle: '',
        legendEntries: [],
      }
    }

    const {
      title,
      bins: { [barrierType]: bins },
    } = layer
    // flip the order of colors and bins since we are displaying from top to bottom
    // add opacity to color
    const colors = COLORS.count[bins.length].map((c) => `${c}4d`).reverse()

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
      const { primary, background, damsSecondary, waterfalls } = pointLegends
      circles.push({
        ...primary,
        label: `${barrierType} analyzed for impacts to aquatic connectivity`,
      })

      circles.push({
        ...background,
        label: `${barrierType} not analyzed`,
      })

      if (barrierType === 'small_barriers') {
        circles.push({
          ...damsSecondary,
          label: 'dams analyzed for impacts to aquatic connectivity',
        })
      }

      circles.push({
        ...waterfalls,
        label: 'waterfalls',
      })
    }

    let lines = null
    if (zoom >= 11) {
      lines = [
        {
          id: 'intermittent',
          label: 'intermittent / ephemeral stream reach',
          color: '#1891ac',
          lineStyle: 'dashed',
          lineWidth: '2px',
        },
        {
          id: 'altered',
          label: 'altered stream reach (canal / ditch)',
          color: 'red',
          lineWidth: '2px',
        },
      ]
    }

    return {
      layerTitle: title,
      legendEntries: {
        patches: [{ id: 'summaryAreas', entries: patchEntries }],
        circles,
        lines,
      },
    }
  }, [system, barrierType, zoom])

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

// construct only once
export default memo(SummaryMap)
