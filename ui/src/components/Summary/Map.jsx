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

import { useRegionBounds } from 'components/Data/RegionBounds'
import {
  Map,
  Legend,
  interpolateExpr,
  SearchFeaturePropType,
  networkLayers,
  highlightNetwork,
  setBarrierHighlight,
  getBarrierTooltip,
} from 'components/Map'
import { barrierTypeLabels, pointLegends } from 'config'
import { isEqual } from 'util/data'
import { COLORS } from './config'
import {
  layers,
  waterfallsLayer,
  damsSecondaryLayer,
  roadCrossingsLayer,
  rankedPointLayer,
  otherBarrierPointLayer,
  unrankedPointLayer,
  regionLayers,
} from './layers'

const barrierTypes = ['dams', 'small_barriers', 'combined_barriers']

const SummaryMap = ({
  region,
  system,
  focalBarrierType,
  selectedUnit,
  searchFeature,
  selectedBarrier,
  onSelectUnit,
  onSelectBarrier,
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

  const selectFeatureByID = useCallback(
    (id, layer) => {
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
    },

    // onSelectUnit intentionally omitted here
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

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
          const fieldExpr =
            focalBarrierType === 'combined_barriers'
              ? ['+', ['get', 'dams'], ['get', 'small_barriers']]
              : ['get', focalBarrierType]

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
                COLORS.empty,
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
      map.addLayer(waterfallsLayer)
      map.addLayer(damsSecondaryLayer)
      map.addLayer(roadCrossingsLayer)

      barrierTypes.forEach((t) => {
        // off network barriers
        map.addLayer({
          id: `other_${t}`,
          source: t,
          'source-layer': `other_${t}`,
          ...otherBarrierPointLayer,
          layout: {
            visibility: focalBarrierType === t ? 'visible' : 'none',
          },
        })

        // on-network but unranked barriers
        map.addLayer({
          id: `unranked_${t}`,
          source: t,
          'source-layer': `unranked_${t}`,
          ...unrankedPointLayer, // TODO: dedicated styling
          layout: {
            visibility: focalBarrierType === t ? 'visible' : 'none',
          },
        })

        // on-network ranked barriers
        map.addLayer({
          id: `ranked_${t}`,
          source: t,
          'source-layer': `ranked_${t}`,
          ...rankedPointLayer,
          layout: {
            visibility: focalBarrierType === t ? 'visible' : 'none',
          },
        })
      })

      const pointLayers = []
        .concat(
          ...barrierTypes.map((t) => [
            `ranked_${t}`,
            `unranked_${t}`,
            `other_${t}`,
          ])
        )
        .concat(['dams-secondary', 'road-crossings', 'waterfalls'])

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
          onSelectUnit({
            ...properties,
            layerId: sourceLayer,
          })
        } else {
          const {
            geometry: {
              coordinates: [lon, lat],
            },
          } = feature

          setBarrierHighlight(map, feature, true)
          selectedFeatureRef.current = feature

          // dam, barrier, waterfall
          onSelectBarrier({
            ...properties,
            barrierType:
              source === 'combined_barriers' ? properties.barriertype : source,
            // use combined barrier networks unless we are looking at only
            // dams
            networkType:
              focalBarrierTypeRef.current === 'dams'
                ? 'dams'
                : 'combined_barriers',
            lat,
            lon,
            ranked: sourceLayer.startsWith('ranked_'),
            layer: {
              source,
              sourceLayer,
            },
          })
        }
      })
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
        ? ['+', ['get', 'dams'], ['get', 'small_barriers']]
        : ['get', focalBarrierType]
    layers.forEach(({ id, bins: { [focalBarrierType]: bins } }) => {
      const colors = COLORS.count[bins.length]
      map.setPaintProperty(`${id}-fill`, 'fill-color', [
        'match',
        fieldExpr,
        0,
        COLORS.empty,
        interpolateExpr(fieldExpr, bins, colors),
      ])
    })

    // toggle barriers layer
    barrierTypes.forEach((t) => {
      const visibility = focalBarrierType === t ? 'visible' : 'none'
      map.setLayoutProperty(`ranked_${t}`, 'visibility', visibility)
      map.setLayoutProperty(`unranked_${t}`, 'visibility', visibility)
      map.setLayoutProperty(`other_${t}`, 'visibility', visibility)
    })

    // clear highlighted networks
    map.setFilter('network-highlight', ['==', 'dams', Infinity])
    map.setFilter('network-intermittent-highlight', ['==', 'dams', Infinity])

    // dams-secondary is only relevant for small barriers
    map.setLayoutProperty(
      'dams-secondary',
      'visibility',
      focalBarrierType === 'small_barriers' ? 'visible' : 'none'
    )
    map.setLayoutProperty(
      'road-crossings',
      'visibility',
      focalBarrierType !== 'dams' ? 'visible' : 'none'
    )
  }, [focalBarrierType])

  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    let networkID = Infinity

    if (selectedBarrier) {
      const { upnetid = Infinity } = selectedBarrier

      // highlight upstream network
      networkID = upnetid
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

    highlightNetwork(
      map,
      focalBarrierType === 'dams' ? 'dams' : 'combined_barriers',
      networkID
    )
  }, [selectedBarrier, focalBarrierType])

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

    map.fitBounds(bbox.split(',').map(parseFloat), {
      padding: 20,
      fitBoundsMaxZoom,
      duration: 500,
    })
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
      bins: { [focalBarrierType]: bins },
    } = layer
    // flip the order of colors and bins since we are displaying from top to bottom
    // add opacity to color
    const colors = COLORS.count[bins.length].map((c) => `${c}4d`).reverse()

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
    if (map && map.getZoom() >= 12) {
      const { included: primary, unrankedBarriers, other } = pointLegends
      circles.push({
        ...primary.getSymbol(focalBarrierType),
        label: primary.getLabel(barrierTypeLabel),
      })

      unrankedBarriers
        .filter(
          ({ id }) =>
            // don't show minor barriers for dams view
            id !== 'minorBarrier' || focalBarrierType !== 'dams'
        )
        .forEach(({ getSymbol, getLabel }) => {
          circles.push({
            ...getSymbol(focalBarrierType),
            label: getLabel(barrierTypeLabel),
          })
        })

      other.forEach(({ id, getSymbol, getLabel }) => {
        if (id === 'dams-secondary' && focalBarrierType !== 'small_barriers') {
          return
        }
        circles.push({
          ...getSymbol(focalBarrierType),
          label: getLabel(barrierTypeLabel),
        })
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

      map.fitBounds(regionBounds[region].bbox, { padding: 100 })
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
        bounds={regionBounds[region].bbox}
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

SummaryMap.propTypes = {
  region: PropTypes.string,
  system: PropTypes.string.isRequired,
  focalBarrierType: PropTypes.string.isRequired,
  selectedUnit: PropTypes.object,
  searchFeature: SearchFeaturePropType,
  selectedBarrier: PropTypes.object,
  onSelectUnit: PropTypes.func.isRequired,
  onSelectBarrier: PropTypes.func.isRequired,
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]),
}

SummaryMap.defaultProps = {
  region: 'total',
  selectedUnit: null,
  searchFeature: null,
  selectedBarrier: null,
  children: null,
}

// construct only once
export default memo(SummaryMap)
