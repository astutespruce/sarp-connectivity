// @refresh reset

import React, {
  memo,
  useEffect,
  useRef,
  useCallback,
  useState,
  useMemo,
  useLayoutEffect,
} from 'react'
import PropTypes from 'prop-types'

// exclude Mapbox GL from babel transpilation per https://docs.mapbox.com/mapbox-gl-js/guides/migrate-to-v2/
/* eslint-disable-next-line */
import mapboxgl from '!mapbox-gl'

import { useRegionBounds } from 'components/Data'
import {
  Map,
  Legend,
  interpolateExpr,
  networkLayers,
  highlightNetwork,
  setBarrierHighlight,
  getBarrierTooltip,
} from 'components/Map'
import { barrierTypeLabels, pointLegends, SUMMARY_UNIT_COLORS } from 'config'
import { isEqual } from 'util/data'
import { layers, removedPointLayer, regionLayers } from './layers'

const barrierTypes = ['dams', 'small_barriers', 'combined_barriers']

const RestorationMap = ({
  region,
  bounds,
  system,
  focalBarrierType,
  summaryUnits,
  selectedBarrier,
  onSelectUnit,
  onSelectBarrier,
  onCreateMap,
  children,
  ...props
}) => {
  const barrierTypeLabel = barrierTypeLabels[focalBarrierType]
  const regionBounds = useRegionBounds()
  const mapRef = useRef(null)
  const hoverFeatureRef = useRef(null)
  const selectedFeatureRef = useRef(null)
  const focalBarrierTypeRef = useRef(focalBarrierType)

  const [zoom, setZoom] = useState(0)

  const clearNetworkHighlight = () => {
    const { current: map } = mapRef

    if (map) {
      map.setFilter('network-highlight', ['==', 'dams', Infinity])
      map.setFilter('network-intermittent-highlight', ['==', 'dams', Infinity])
      map.setFilter('removed-network-highlight', ['==', 'barrier_id', Infinity])
      map.setFilter('removed-network-intermittent-highlight', [
        '==',
        'barrier_id',
        Infinity,
      ])
    }
  }

  const handleCreateMap = useCallback(
    (map) => {
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
          bins: { [focalBarrierType]: bins },
        }) => {
          const colors = SUMMARY_UNIT_COLORS.Greens[bins.length]
          const visibility = lyrSystem === system ? 'visible' : 'none'

          // base config for each layer
          const config = {
            source: 'summary',
            'source-layer': id,
            minzoom,
            maxzoom,
          }

          // add fill layer
          const fieldExpr =
            focalBarrierType === 'combined_barriers'
              ? [
                  '+',
                  ['get', 'removed_dams'],
                  ['get', 'removed_small_barriers'],
                ]
              : ['get', `removed_${focalBarrierType}`]

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
                fieldExpr,
                0,
                SUMMARY_UNIT_COLORS.empty,
                // NOTE: using simpler get expr here because barrierType is
                // dams at init time
                interpolateExpr(fieldExpr, bins, colors),
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
              'line-color': SUMMARY_UNIT_COLORS.Greens[7][3],
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

      // Add mask / boundary layers
      regionLayers.forEach((l) => {
        const layer = {
          ...l,
          filter: ['==', 'id', region],
        }
        map.addLayer(layer)
      })

      // Add network layers
      networkLayers.forEach((layer) => {
        map.addLayer(layer)
      })

      // Add barrier point layers
      barrierTypes.forEach((t) => {
        // on-network ranked barriers
        map.addLayer({
          id: `removed_${t}`,
          source: t,
          'source-layer': `removed_${t}`,
          ...removedPointLayer,
          layout: {
            visibility: focalBarrierType === t ? 'visible' : 'none',
          },
        })
      })

      const pointLayers = barrierTypes.map((t) => `removed_${t}`)
      const clickLayers = pointLayers.concat(
        layers.map(({ id }) => `${id}-fill`)
      )

      // add hover and tooltip to point layers
      const tooltip = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false,
        anchor: 'left',
        offset: 20,
      })
      pointLayers.forEach((id) => {
        map.on('mousemove', id, ({ features: [feature] }) => {
          if (map.getZoom() < 9) {
            return
          }

          const {
            geometry: { coordinates },
          } = feature

          setBarrierHighlight(map, hoverFeatureRef.current, false)
          hoverFeatureRef.current = feature
          setBarrierHighlight(map, feature, true)

          /* eslint-disable-next-line no-param-reassign */
          map.getCanvas().style.cursor = 'pointer'

          tooltip
            .setLngLat(coordinates)
            .setHTML(
              getBarrierTooltip(
                feature.source === 'combined_barriers'
                  ? feature.properties.barriertype
                  : feature.source,
                feature.properties
              )
            )
            .addTo(map)
        })
        map.on('mouseleave', id, () => {
          // only unhighlight if not the same as currently selected feature
          const prevFeature = hoverFeatureRef.current
          const selectedFeature = selectedFeatureRef.current

          if (prevFeature) {
            if (
              !selectedFeature ||
              prevFeature.id !== selectedFeature.id ||
              prevFeature.layer.id !== selectedFeature.layer.id
            ) {
              setBarrierHighlight(map, prevFeature, false)
            }
          }

          hoverFeatureRef.current = null

          /* eslint-disable-next-line no-param-reassign */
          map.getCanvas().style.cursor = ''
          tooltip.remove()
        })
      })

      map.on('click', ({ point }) => {
        const [feature] = map.queryRenderedFeatures(point, {
          layers: clickLayers,
        })

        // always clear out prior feature
        const prevFeature = selectedFeatureRef.current
        if (prevFeature) {
          setBarrierHighlight(map, prevFeature, false)

          selectedFeatureRef.current = null

          if (isEqual(prevFeature, hoverFeatureRef.current, ['id', 'layer'])) {
            setBarrierHighlight(map, hoverFeatureRef.current, false)
            hoverFeatureRef.current = null
          }
        }

        if (!feature) {
          return
        }

        const { source, sourceLayer, properties } = feature

        if (source === 'summary') {
          // summary unit layer
          const { id } = properties
          onSelectUnit({ layer: sourceLayer, id })
        } else {
          const {
            geometry: {
              coordinates: [lon, lat],
            },
          } = feature

          setBarrierHighlight(map, feature, true)
          selectedFeatureRef.current = feature

          const removed = sourceLayer.startsWith('removed_')

          const thisBarrierType =
            source === 'combined_barriers' ? properties.barriertype : source

          // promote network fields if clicking on a waterfall
          let networkIDField = 'upnetid'
          if (removed) {
            networkIDField = 'id'
          } else if (thisBarrierType === 'waterfalls') {
            networkIDField = `${focalBarrierTypeRef}_upnetid`
          }

          // dam, barrier, waterfall
          onSelectBarrier({
            ...properties,
            upnetid: properties[networkIDField] || Infinity,
            barrierType: thisBarrierType,
            // use combined barrier networks unless we are looking at only
            // dams
            networkType:
              focalBarrierTypeRef.current === 'dams'
                ? 'dams'
                : 'combined_barriers',
            lat,
            lon,
            ranked: sourceLayer.startsWith('ranked_'),
            removed,
            layer: {
              source,
              sourceLayer,
            },
          })
        }
      })

      onCreateMap()
    },
    // hook deps are intentionally omitted here
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

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
    focalBarrierTypeRef.current = focalBarrierType

    const { current: map } = mapRef

    if (!map) return

    // update renderer and filter on all layers
    const fieldExpr =
      focalBarrierType === 'combined_barriers'
        ? ['+', ['get', 'removed_dams'], ['get', 'removed_small_barriers']]
        : ['get', `removed_${focalBarrierType}`]
    layers.forEach(({ id, bins: { [focalBarrierType]: bins } }) => {
      const colors = SUMMARY_UNIT_COLORS.Greens[bins.length]
      map.setPaintProperty(`${id}-fill`, 'fill-color', [
        'match',
        fieldExpr,
        0,
        SUMMARY_UNIT_COLORS.empty,
        interpolateExpr(fieldExpr, bins, colors),
      ])
    })

    // toggle barriers layer
    barrierTypes.forEach((t) => {
      const visibility = focalBarrierType === t ? 'visible' : 'none'
      map.setLayoutProperty(`removed_${t}`, 'visibility', visibility)
    })

    clearNetworkHighlight()
  }, [focalBarrierType])

  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    clearNetworkHighlight()

    if (selectedBarrier) {
      const networkIDField = selectedBarrier.removed ? 'id' : 'upnetid'
      const { [networkIDField]: networkID = Infinity } = selectedBarrier

      // highlight upstream network
      highlightNetwork(
        map,
        focalBarrierType === 'dams' ? 'dams' : 'combined_barriers',
        networkID,
        selectedBarrier.removed
      )
    } else {
      const prevFeature = selectedFeatureRef.current
      if (prevFeature) {
        setBarrierHighlight(map, prevFeature, false)
        hoverFeatureRef.current = null

        if (isEqual(prevFeature, hoverFeatureRef.current, ['id', 'layer'])) {
          setBarrierHighlight(map, hoverFeatureRef.current, false)
          hoverFeatureRef.current = null
        }
      }
    }
  }, [selectedBarrier, focalBarrierType])

  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    const ids = summaryUnits.map(({ id }) => id)

    layers.forEach(({ id: lyrId, system: lyrSystem }) => {
      map.setFilter(
        `${lyrId}-highlight`,
        lyrSystem === system && ids.length > 0
          ? ['in', 'id', ...ids]
          : ['==', 'id', Infinity]
      )
    })
  }, [system, summaryUnits])

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
      bins: { [focalBarrierType]: bins },
    } = layer
    // flip the order of colors and bins since we are displaying from top to bottom
    // add opacity to color
    const colors = SUMMARY_UNIT_COLORS.Greens[bins.length]
      .map((c) => `${c}4d`)
      .reverse()

    const labels = bins
      .map((bin, i) => {
        if (i === 0) {
          return `≤ ${Math.round(bin).toLocaleString()}`
        }
        if (i === bins.length - 1) {
          return `≥ ${Math.round(bin).toLocaleString()}`
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
      label: `no inventoried ${barrierTypeLabel}`,
    })

    const circles = []
    if (map && map.getZoom() >= 8) {
      const { unrankedBarriers } = pointLegends
      const removedLegend = unrankedBarriers.filter(
        ({ id }) => id === 'removed'
      )[0]
      circles.push({
        ...removedLegend.getSymbol(focalBarrierType),
        label: removedLegend.getLabel(barrierTypeLabel),
      })
    }

    let lines = null
    if (zoom >= 11) {
      lines = [
        {
          id: 'normal',
          label: 'stream reach',
          color: '#1891ac',
          lineWidth: '2px',
        },
        {
          id: 'altered',
          label: 'altered stream reach (canal / ditch / reservoir)',
          color: '#9370db',
          lineWidth: '2px',
        },
        {
          id: 'intermittent',
          label: 'intermittent / ephemeral stream reach',
          color: '#1891ac',
          lineStyle: 'dashed',
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
  }, [system, focalBarrierType, zoom])

  useLayoutEffect(
    () => {
      const { current: map } = mapRef

      if (!map) return

      regionLayers.forEach(({ id }) => {
        map.setFilter(id, ['==', 'id', region])
      })

      map.fitBounds(regionBounds[region], {
        padding: 100,
      })
    },
    // regionBounds deliberately omitted
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [region]
  )

  return (
    <>
      <Map
        onCreateMap={handleCreateMap}
        {...props}
        bounds={bounds || regionBounds[region]}
      >
        <Legend
          title={layerTitle}
          subtitle={`number of ${barrierTypeLabel}`}
          {...legendEntries}
          maxWidth="12rem"
        />
        {children}
      </Map>
    </>
  )
}

RestorationMap.propTypes = {
  region: PropTypes.string,
  bounds: PropTypes.arrayOf(PropTypes.number),
  system: PropTypes.string.isRequired,
  focalBarrierType: PropTypes.string.isRequired,
  summaryUnits: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
    })
  ),
  selectedBarrier: PropTypes.object,
  onSelectUnit: PropTypes.func.isRequired,
  onSelectBarrier: PropTypes.func.isRequired,
  onCreateMap: PropTypes.func.isRequired,
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]),
}

RestorationMap.defaultProps = {
  region: 'total',
  bounds: null,
  summaryUnits: [],
  selectedBarrier: null,
  children: null,
}

// construct only once
export default memo(RestorationMap)
