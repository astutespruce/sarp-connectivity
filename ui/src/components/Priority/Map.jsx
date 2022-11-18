import React, { memo, useEffect, useRef, useCallback, useState } from 'react'
import PropTypes from 'prop-types'
import { useDebouncedCallback } from 'use-debounce'

// exclude Mapbox GL from babel transpilation per https://docs.mapbox.com/mapbox-gl-js/guides/migrate-to-v2/
/* eslint-disable-next-line */
import mapboxgl from '!mapbox-gl'

import { useCrossfilter } from 'components/Crossfilter'
import { useBarrierType } from 'components/Data'
import {
  Map,
  DropDownLayerChooser,
  Legend,
  SearchFeaturePropType,
  networkLayers,
  highlightNetwork,
  setBarrierHighlight,
} from 'components/Map'
import { barrierTypeLabels } from 'config'
import { isEqual } from 'util/data'
import { capitalize } from 'util/format'
import { isEmptyString } from 'util/string'

import { unitLayerConfig } from './config'
import {
  maskFill,
  maskOutline,
  unitLayers,
  unitHighlightLayers,
  parentOutline,
  offnetworkPoint,
  excludedPoint,
  includedPoint,
  pointLegends,
  rankedPoint,
  damsSecondaryLayer,
  waterfallsLayer,
  priorityWatersheds,
  priorityWatershedLegends,
  getTierPointColor,
  getTierPointSize,
} from './layers'

const PriorityMap = ({
  allowUnitSelect,
  activeLayer,
  selectedUnit,
  selectedBarrier,
  rankedBarriers,
  tierThreshold,
  scenario,
  searchFeature,
  summaryUnits,
  bounds,
  onSelectUnit,
  onSelectBarrier,
  onMapLoad,
  ...props
}) => {
  const barrierType = useBarrierType()
  const barrierTypeLabel = barrierTypeLabels[barrierType]

  const {
    state: { filters },
  } = useCrossfilter()
  const mapRef = useRef(null)
  const hoverFeatureRef = useRef(null)
  const selectedFeatureRef = useRef(null)
  const rankedBarriersRef = useRef(null)
  const [priorityLayerState, setPriorityLayerState] = useState({})

  // first layer of system is default on init
  // const [visibleLayer, setVisibleLayer] = useState(layers.filter(({system: lyrSystem}) => lyrSystem === system)[0])
  const [zoom, setZoom] = useState(0)

  const handleCreateMap = useCallback(
    (map) => {
      mapRef.current = map

      map.on('zoomend', () => {
        setZoom(map.getZoom())
      })

      // set for initial load too
      setZoom(map.getZoom())

      const pointLayers = [
        offnetworkPoint.id,
        damsSecondaryLayer.id,
        excludedPoint.id,
        includedPoint.id,
        rankedPoint.id,
        'waterfalls',
      ]

      const clickLayers = pointLayers.concat(
        Object.keys(unitLayerConfig).map((id) => `${id}-unit-fill`)
      )

      // Add the priority watersheds under everything else
      priorityWatersheds.forEach((lyr) => {
        map.addLayer(lyr)
      })

      // Initially the mask and boundary are visible
      map.addLayer(maskFill)
      map.addLayer(maskOutline)

      // Add flowlines and network highlight layers
      networkLayers.forEach((layer) => {
        map.addLayer(layer)
      })

      // Add summary unit layers
      Object.entries(unitLayerConfig).forEach(
        ([layer, { minzoom = 0, maxzoom = 24, parent }]) => {
          const config = {
            'source-layer': layer,
            minzoom,
            maxzoom,
          }

          if (parent) {
            map.addLayer({
              'source-layer': parent.id,
              minzoom: parent.minzoom || minzoom,
              maxzoom: parent.maxzoom || maxzoom,
              ...parentOutline,
              id: `${layer}-${parentOutline.id}`,
            })
          }

          // Each layer has 2 display layers: outline, fill
          unitLayers.forEach(({ id, ...rest }) => {
            const layerId = `${layer}-${id}`
            const unitLayer = { ...config, ...rest, id: layerId }

            if (id === 'unit-fill') {
              unitLayer.paint['fill-opacity'] = [
                'match',
                ['get', barrierType],
                0,
                0.25,
                0,
              ]
            }

            map.addLayer(unitLayer)
          })

          // Each layer has 2 highlight layers: highlight fill, highlight outline
          unitHighlightLayers.forEach(({ id, ...rest }) => {
            const layerId = `${layer}-${id}`
            map.addLayer({ ...config, ...rest, id: layerId })
          })
        }
      )

      // add background point layer before the others, so that it is below them in the map
      map.addLayer({
        ...offnetworkPoint,
        source: barrierType,
        'source-layer': `offnetwork_${barrierType}`,
      })

      // add waterfalls
      map.addLayer(waterfallsLayer)

      // add secondary dams layer
      map.addLayer({
        ...damsSecondaryLayer,
        layout: {
          visibility: barrierType === 'small_barriers' ? 'visible' : 'none',
        },
      })

      // add filter point layers
      const pointConfig = {
        source: barrierType,
        'source-layer': `ranked_${barrierType}`,
      }

      // all points are initially excluded from analysis until their
      // units are selected
      map.addLayer({ ...pointConfig, ...excludedPoint })
      map.addLayer({
        ...pointConfig,
        ...includedPoint,
      })

      map.addLayer({
        ...pointConfig,
        ...rankedPoint,
        paint: {
          ...rankedPoint.paint,
          'circle-color': getTierPointColor(scenario, tierThreshold),
          'circle-radius': getTierPointSize(scenario, tierThreshold),
        },
      })

      // add hover and tooltip to point layers
      const tooltip = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false,
        anchor: 'left',
        offset: 20,
      })

      pointLayers.forEach((id) => {
        map.on('mousemove', id, ({ features: [feature] }) => {
          if (map.getZoom() < 8) {
            return
          }

          const {
            properties: { sarpidname = '|' },
            geometry: { coordinates },
          } = feature

          const barrierName = sarpidname.split('|')[1]

          setBarrierHighlight(map, hoverFeatureRef.current, false)

          hoverFeatureRef.current = feature
          setBarrierHighlight(map, feature, true)

          /* eslint-disable-next-line no-param-reassign */
          map.getCanvas().style.cursor = 'pointer'

          const prefix = barrierTypeLabels[feature.source]
            ? `${capitalize(barrierTypeLabels[feature.source]).slice(
                0,
                barrierTypeLabels[feature.source].length - 1
              )}: `
            : ''

          tooltip
            .setLngLat(coordinates)
            .setHTML(
              `<b>${prefix}${
                !isEmptyString(barrierName) ? barrierName : 'Unknown name'
              }</b>`
            )
            .addTo(map)
        })
        map.on('mouseleave', id, () => {
          // only unhighlight if not the same as currently selected feature
          const prevFeature = hoverFeatureRef.current
          if (
            prevFeature &&
            !isEqual(prevFeature, selectedFeatureRef.current, ['id', 'layer'])
          ) {
            setBarrierHighlight(map, prevFeature, false)
          }

          hoverFeatureRef.current = null

          /* eslint-disable-next-line no-param-reassign */
          map.getCanvas().style.cursor = ''
          tooltip.remove()
        })
      })

      map.on('click', ({ point }) => {
        const features = map.queryRenderedFeatures(point, {
          layers: clickLayers,
        })

        const [feature] = features

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

        // only call handler if there was a feature
        if (!feature) {
          onSelectBarrier(null)
          return
        }

        const {
          source,
          sourceLayer,
          properties,
          geometry: {
            coordinates: [lon, lat],
          },
        } = feature

        if (source === 'summary') {
          onSelectUnit(properties)
          return
        }

        if (map.getZoom() < 8) {
          // don't allow selection of points below zoom 8
          const [unitLayerFeature] = features.filter(
            ({ source: lyrSource }) => lyrSource === 'summary'
          )
          if (unitLayerFeature) {
            onSelectUnit(unitLayerFeature.properties)
          }
          return
        }

        // promote network fields if clicking on a waterfall
        const networkFields = {}
        Object.keys(properties)
          .filter((k) => k.endsWith(barrierType))
          .forEach((field) => {
            networkFields[field.split('_')[0]] = properties[field]
          })

        setBarrierHighlight(map, feature, true)
        selectedFeatureRef.current = feature

        onSelectBarrier({
          ...properties,
          ...networkFields,
          barrierType,
          // FIXME: is this right?
          networkType: source === 'dams' ? 'dams' : undefined,
          HUC8Name: getSummaryUnitName('HUC8', properties.HUC8),
          HUC12Name: getSummaryUnitName('HUC12', properties.HUC12),
          CountyName: getSummaryUnitName('County', properties.County),
          lat,
          lon,
          ranked: sourceLayer.startsWith('ranked_'),
          layer: {
            source,
            sourceLayer,
          },
        })
      })

      // let consumers of map know that it is now fully loaded
      map.once('idle', onMapLoad)
    },
    [
      barrierType,
      onMapLoad,
      onSelectBarrier,
      onSelectUnit,
      scenario,
      tierThreshold,
    ]
  )

  const getSummaryUnitName = (layer, id) => {
    if (!id) return null

    const [result] = mapRef.current.querySourceFeatures('summary', {
      sourceLayer: layer,
      filter: ['==', 'id', id],
    })
    if (result) {
      return result.properties.name
    }
    return null
  }

  const selectUnitById = useCallback(
    (id, layer) => {
      const [feature] = mapRef.current.querySourceFeatures('summary', {
        sourceLayer: layer,
        filter: ['==', 'id', id],
      })

      if (feature !== undefined) {
        onSelectUnit({ ...feature.properties, layerId: layer })
      }
      return feature
    },
    [onSelectUnit]
  )

  // Debounce updates to the filter to prevent frequent redraws
  // which have bad performance with high numbers of dams
  const debouncedSetRankFilter = useDebouncedCallback(
    (currentScenario, threshold) => {
      const { current: map } = mapRef

      map.setPaintProperty(
        rankedPoint.id,
        'circle-color',
        getTierPointColor(currentScenario, threshold)
      )
      map.setPaintProperty(
        rankedPoint.id,
        'circle-radius',
        getTierPointSize(currentScenario, threshold)
      )
    },
    200
  )

  // If map allows unit selection, make layers visible for the activeLayer, so that user can select from them
  // otherwise just highlight those currently selected
  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    // toggle visibility of layers so that we only show those layers for the activeLayer
    Object.keys(unitLayerConfig).forEach((layer) => {
      // only show the unit fill and boundary if we allow selection
      const visibility =
        layer === activeLayer && allowUnitSelect ? 'visible' : 'none'
      unitLayers.forEach(({ id }) => {
        map.setLayoutProperty(`${layer}-${id}`, 'visibility', visibility)
      })

      const { parent } = unitLayerConfig[layer]
      if (parent) {
        map.setLayoutProperty(
          `${layer}-unit-parent-outline`,
          'visibility',
          visibility
        )
      }

      // only show highlight fill when selecting units
      map.setLayoutProperty(
        `${layer}-${unitHighlightLayers[0].id}`,
        'visibility',
        visibility
      )

      // show boundary highlight in all cases
      map.setLayoutProperty(
        `${layer}-${unitHighlightLayers[1].id}`,
        'visibility',
        layer === activeLayer ? 'visible' : 'none'
      )
    })
  }, [allowUnitSelect, activeLayer])

  // Highlight currently selected summaryUnits
  useEffect(() => {
    const { current: map } = mapRef

    if (!(map && activeLayer)) return

    const ids = summaryUnits.map(({ id }) => id)
    const filterExpr =
      ids.length > 0 ? ['in', 'id', ...ids] : ['==', 'id', Infinity]

    unitHighlightLayers.forEach(({ id }) => {
      map.setFilter(`${activeLayer}-${id}`, filterExpr)
    })
  }, [activeLayer, summaryUnits])

  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    let networkID = Infinity
    let networkType = barrierType

    if (selectedBarrier) {
      const {
        upnetid = Infinity,
        networkType: barrierNetworkType = barrierType,
      } = selectedBarrier

      networkID = upnetid
      networkType = barrierNetworkType
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

    highlightNetwork(map, networkType, networkID)
  }, [barrierType, selectedBarrier])

  // if map allows filter, show selected vs unselected points, and make those without networks
  // background points
  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    const ids = summaryUnits.map(({ id }) => id)

    if (!(activeLayer || ids.length > 0)) {
      // if no summary units are selected, reset filters on barriers
      map.setFilter(includedPoint.id, ['==', 'id', Infinity])
      map.setFilter(excludedPoint.id, null)
      return
    }

    // Construct filter expressions for each active filter
    const filterEntries = Object.entries(filters || {}).filter(
      ([, v]) => v && v.size > 0
    )

    const includedByFilters = filterEntries.map(([field, values]) => [
      'in',
      field,
      ...Array.from(values),
    ])
    const excludedByFilters = filterEntries.map(([field, values]) => [
      '!in',
      field,
      ...Array.from(values),
    ])

    // update barrier layers to select those that are in selected units
    map.setFilter(includedPoint.id, [
      'all',
      ['in', activeLayer, ...ids],
      ...includedByFilters,
    ])
    map.setFilter(excludedPoint.id, [
      'all',
      ['any', ['!in', activeLayer, ...ids], ...excludedByFilters],
    ])
  }, [activeLayer, summaryUnits, filters])

  useEffect(() => {
    const { current: map } = mapRef
    if (!(map && searchFeature)) {
      return
    }

    const { id = null, layer, bbox } = searchFeature
    // if feature is already visible, select it
    // otherwise, zoom and attempt to select it

    let feature = selectUnitById(id, layer)
    if (!feature) {
      map.once('moveend', () => {
        feature = selectUnitById(id, layer)
        // source may still be loading, try again in 1 second
        if (!feature) {
          setTimeout(() => {
            selectUnitById(id, layer)
          }, 1000)
        }
      })
    }

    // have to zoom to feature in order to fetch data for it
    map.fitBounds(bbox.split(',').map(parseFloat), {
      padding: 20,
      duration: 500,
    })
  }, [searchFeature, selectUnitById])

  useEffect(() => {
    const { current: map } = mapRef
    if (!map) return

    const showRanks = rankedBarriers.length > 0
    map.setLayoutProperty(
      includedPoint.id,
      'visibility',
      showRanks ? 'none' : 'visible'
    )
    map.setLayoutProperty(
      rankedPoint.id,
      'visibility',
      showRanks ? 'visible' : 'none'
    )

    const { source, sourceLayer } = map.getLayer(rankedPoint.id)
    const prevRankedBarriers = rankedBarriersRef.current

    // unset feature state for all ranked points
    if (prevRankedBarriers && prevRankedBarriers.length) {
      prevRankedBarriers.forEach(({ id }) => {
        // NOTE: this removes all feature state including selected and hover
        // but neither of those should be active on transition to showing
        // ranked barriers
        map.removeFeatureState({ source, sourceLayer, id })
      })
    }
    if (showRanks) {
      // copy filters to ranked layers
      map.setFilter(rankedPoint.id, map.getFilter(includedPoint.id))
      rankedBarriers.forEach(({ id, ...rest }) => {
        map.setFeatureState({ source, sourceLayer, id }, rest)
      })
    }
    rankedBarriersRef.current = rankedBarriers
  }, [rankedBarriers])

  useEffect(() => {
    const { current: map } = mapRef
    if (!map) return

    debouncedSetRankFilter(scenario, tierThreshold)
  }, [tierThreshold, scenario, debouncedSetRankFilter])

  useEffect(() => {
    if (bounds == null) return
    const { current: map } = mapRef
    if (!map) return

    map.fitBounds(bounds, { padding: 20, maxZoom: 14, duration: 500 })
  }, [bounds])

  const handlePriorityLayerChange = useCallback((visiblePriorityLayers) => {
    const { current: map } = mapRef
    if (!map) return

    // toggle layers on or off on the map
    Object.entries(visiblePriorityLayers).forEach(([id, visible]) => {
      const visibility = visible ? 'visible' : 'none'
      map.setLayoutProperty(`${id}-priority-fill`, 'visibility', visibility)
      map.setLayoutProperty(`${id}-priority-outline`, 'visibility', visibility)
    })

    setPriorityLayerState(visiblePriorityLayers)
  }, [])

  const getLegend = () => {
    const pointLayers = [
      includedPoint,
      excludedPoint,
      offnetworkPoint,
      rankedPoint,
      // topRank,
      // lowerRank,
    ]

    const isWithinZoom = pointLayers.reduce(
      (prev, { id, minzoom, maxzoom }) =>
        Object.assign(prev, {
          [id]: zoom >= minzoom && zoom <= maxzoom,
        }),
      {}
    )

    const {
      included: includedLegend,
      excluded: excludedLegend,
      offnetwork: offnetworkLegend,
      topRank: topRankLegend,
      lowerRank: lowerRankLegend,
      damsSecondary,
      waterfalls,
    } = pointLegends

    const circles = []
    const patches = []
    let lines = null

    if (zoom > 6) {
      lines = [
        {
          id: 'normal',
          label: 'stream reach',
          color: '#1891ac',
          lineWidth: '2px',
        },
        {
          id: 'altered',
          label: 'altered stream reach (canal / ditch)',
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

    let footnote = null

    if (Math.max(...Object.values(priorityLayerState))) {
      Object.entries(priorityLayerState)
        /* eslint-disable-next-line no-unused-vars */
        .filter(([_, visible]) => visible)
        .forEach(([id]) => {
          patches.push(priorityWatershedLegends[id])
        })
    }

    // if no layer is selected for choosing summary areas
    if (activeLayer === null) {
      if (!isWithinZoom[excludedPoint.id]) {
        footnote = `zoom in to see ${barrierTypeLabel} available for analysis`
      } else {
        circles.push({
          ...excludedLegend,
          label: `${barrierTypeLabel} available for analysis`,
        })
      }

      if (isWithinZoom[offnetworkPoint.id]) {
        circles.push({
          ...offnetworkLegend,
          label: `${barrierTypeLabel} not available for analysis`,
        })
        // only show secondary dams & waterfalls at same time as background points
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
    }

    // may need to be mutually exclusive of above
    else if (rankedBarriers.length > 0) {
      const tierLabel =
        tierThreshold === 1 ? 'tier 1' : `tiers 1 - ${tierThreshold}`
      circles.push({
        ...topRankLegend,
        label: `Top-ranked ${barrierTypeLabel} (${tierLabel})`,
      })

      circles.push({
        ...lowerRankLegend,
        label: `lower-ranked ${barrierTypeLabel}`,
      })

      if (isWithinZoom[excludedPoint.id]) {
        circles.push({
          ...excludedLegend,
          label: `not selected ${barrierTypeLabel}`,
        })
      }

      if (isWithinZoom[offnetworkPoint.id]) {
        circles.push({
          ...offnetworkLegend,
          label: `${barrierTypeLabel} not included in analysis`,
        })

        // only show secondary dams & waterfalls at same time as background points
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
    } else {
      // either in select units or filter step
      if (isWithinZoom[includedPoint.id]) {
        circles.push({
          ...includedLegend,
          label: `selected ${barrierTypeLabel}`,
        })
      } else {
        footnote = `zoom in to see selected ${barrierTypeLabel}`
      }

      if (isWithinZoom[excludedPoint.id]) {
        circles.push({
          ...excludedLegend,
          label: `not selected ${barrierTypeLabel}`,
        })
      }

      if (isWithinZoom[offnetworkPoint.id]) {
        circles.push({
          ...offnetworkLegend,
          label: `${barrierTypeLabel} not available for analysis`,
        })

        // only show secondary dams & waterfalls at same time as background points
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

      if (allowUnitSelect) {
        patches.push({
          id: 'summaryAreas',
          entries: [
            {
              color: 'rgba(0,0,0,0.15)',
              label: `area with no inventoried ${barrierTypeLabel}`,
            },
          ],
        })
      }
    }

    return {
      patches,
      circles,
      lines,
      footnote,
    }
  }

  return (
    <Map onCreateMap={handleCreateMap} {...props}>
      <DropDownLayerChooser
        label="Priority Watersheds"
        options={[{ id: 'coa', label: 'SARP conservation opportunity areas' }]}
        onChange={handlePriorityLayerChange}
      />
      <Legend {...getLegend()} />
    </Map>
  )
}

PriorityMap.propTypes = {
  allowUnitSelect: PropTypes.bool,
  activeLayer: PropTypes.string,
  selectedUnit: PropTypes.object,
  selectedBarrier: PropTypes.object,
  rankedBarriers: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
    })
  ),
  tierThreshold: PropTypes.number.isRequired,
  scenario: PropTypes.string.isRequired,
  summaryUnits: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
    })
  ),
  searchFeature: SearchFeaturePropType,
  bounds: PropTypes.arrayOf(PropTypes.number),
  onSelectUnit: PropTypes.func.isRequired,
  onSelectBarrier: PropTypes.func.isRequired,
  onMapLoad: PropTypes.func.isRequired,
}

PriorityMap.defaultProps = {
  allowUnitSelect: false,
  activeLayer: null,
  selectedUnit: null,
  selectedBarrier: null,
  searchFeature: null,
  summaryUnits: [],
  rankedBarriers: [],
  bounds: null,
}

export default memo(PriorityMap)
