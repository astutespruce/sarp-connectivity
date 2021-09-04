import React, { memo, useEffect, useRef, useCallback, useState } from 'react'
import PropTypes from 'prop-types'
import { useDebouncedCallback } from 'use-debounce'
import mapboxgl from 'mapbox-gl'

import { useCrossfilter } from 'components/Crossfilter'
import { useBarrierType } from 'components/Data'
import {
  Map,
  DropDownLayerChooser,
  Legend,
  SearchFeaturePropType,
  toGeoJSONPoints,
} from 'components/Map'
import { capitalize } from 'util/format'
import { isEmptyString } from 'util/string'

import { unitLayerConfig } from './config'
import {
  maskFill,
  maskOutline,
  unitLayers,
  unitHighlightLayers,
  networkLayers,
  parentOutline,
  pointHighlight,
  pointHover,
  backgroundPoint,
  excludedPoint,
  includedPoint,
  pointLegends,
  topRank,
  lowerRank,
  damsSecondaryLayer,
  waterfallsLayer,
  priorityWatersheds,
  priorityWatershedLegends,
} from './layers'

import { barrierTypeLabels } from '../../../config/constants'

const emptyFeatureCollection = {
  type: 'FeatureCollection',
  features: [],
}

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

      // Hookup map on click handler to call onClick with the properties
      // of the feature selected
      const handleLayerClick = (layerId, onClick) => {
        map.on('click', layerId, ({ point }) => {
          const [feature] = map.queryRenderedFeatures(point, {
            layers: [layerId],
          })
          // only call handler if there was a feature
          if (feature) {
            onClick(feature)
          }
        })
      }

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

              handleLayerClick(layerId, ({ properties }) =>
                onSelectUnit(properties)
              )
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
        ...backgroundPoint,
        source: barrierType,
      })
      handleLayerClick(backgroundPoint.id, (feature) => {
        const {
          properties,
          geometry: {
            coordinates: [lon, lat],
          },
        } = feature

        onSelectBarrier({
          ...properties,
          barrierType,
          HUC8Name: getHUCName('HUC8', properties.HUC8),
          HUC12Name: getHUCName('HUC12', properties.HUC12),
          lat,
          lon,
          hasnetwork: properties.hasnetwork || false,
          ranked: properties.ranked || false,
        })
      })

      // add waterfalls
      map.addLayer(waterfallsLayer)
      handleLayerClick(waterfallsLayer.id, (feature) => {
        const {
          properties,
          geometry: {
            coordinates: [lon, lat],
          },
        } = feature

        // promote network fields
        const networkFields = {}
        Object.keys(properties)
          .filter((k) => k.endsWith(barrierType))
          .forEach((field) => {
            networkFields[field.split('_')[0]] = properties[field]
          })

        onSelectBarrier({
          ...properties,
          ...networkFields,
          barrierType: 'waterfalls',
          HUC8Name: getHUCName('HUC8', properties.HUC8),
          HUC12Name: getHUCName('HUC12', properties.HUC12),
          lat,
          lon,
          hasnetwork: properties.hasnetwork,
          ranked: false,
        })
      })

      // add secondary dams layer
      map.addLayer({
        ...damsSecondaryLayer,
        layout: {
          visibility: barrierType === 'small_barriers' ? 'visible' : 'none',
        },
      })
      handleLayerClick(damsSecondaryLayer.id, (feature) => {
        const {
          properties,
          geometry: {
            coordinates: [lon, lat],
          },
        } = feature

        onSelectBarrier({
          ...properties,
          barrierType: 'dams',
          HUC8Name: getHUCName('HUC8', properties.HUC8),
          HUC12Name: getHUCName('HUC12', properties.HUC12),
          lat,
          lon,
          hasnetwork: true, // this only shows on-network dams
          networkType: 'dams', // only show against dams network
        })
      })

      // add filter point layers
      const pointConfig = {
        source: barrierType,
        'source-layer': barrierType,
      }

      // all points are initially excluded from analysis until their
      // units are selected
      map.addLayer({ ...pointConfig, ...excludedPoint })
      handleLayerClick(excludedPoint.id, (feature) => {
        const {
          properties,
          geometry: {
            coordinates: [lon, lat],
          },
        } = feature
        onSelectBarrier({
          ...properties,
          barrierType,
          HUC8Name: getHUCName('HUC8', properties.HUC8),
          HUC12Name: getHUCName('HUC12', properties.HUC12),
          lat,
          lon,
          hasnetwork: true,
          ranked: true,
        })
      })

      map.addLayer({
        ...pointConfig,
        ...includedPoint,
      })
      handleLayerClick(includedPoint.id, (feature) => {
        const {
          properties,
          geometry: {
            coordinates: [lon, lat],
          },
        } = feature
        onSelectBarrier({
          ...properties,
          barrierType,
          HUC8Name: getHUCName('HUC8', properties.HUC8),
          HUC12Name: getHUCName('HUC12', properties.HUC12),
          lat,
          lon,
          hasnetwork: true,
          ranked: true,
        })
      })

      // Add layers for ranks
      map.addSource('ranked', {
        type: 'geojson',
        data: emptyFeatureCollection,
      })

      map.addLayer({
        source: 'ranked',
        ...lowerRank,
        filter: ['>', `${scenario}_tier`, tierThreshold],
      })
      map.addLayer({
        source: 'ranked',
        ...topRank,
        filter: ['<=', `${scenario}_tier`, tierThreshold],
      })

      // Add layer for highlight
      map.addLayer(pointHover)

      // add hover and tooltip to point layers
      const tooltip = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false,
        anchor: 'left',
        offset: 20,
      })
      const pointLayers = [
        backgroundPoint.id,
        damsSecondaryLayer.id,
        excludedPoint.id,
        includedPoint.id,
        lowerRank.id,
        topRank.id,
        'waterfalls',
      ]

      pointLayers.forEach((id) => {
        map.on('mouseenter', id, ({ features: [feature] }) => {
          if (map.getZoom() <= 7) {
            return
          }

          const {
            properties: { id: barrierId },
            geometry: { coordinates },
          } = feature

          let barrierName = ''
          if (id.startsWith('rank-')) {
            // get barrier details from tiles
            const barrier = getBarrierById(barrierId)
            if (!barrier) {
              return
            }
            barrierName = barrier.properties.name
          } else {
            barrierName = feature.properties.name
          }

          map.getSource(pointHover.id).setData({
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
          map.getSource(pointHover.id).setData(emptyFeatureCollection)

          /* eslint-disable-next-line no-param-reassign */
          map.getCanvas().style.cursor = ''
          tooltip.remove()
        })
      })

      // select barrier from tile data using ID
      // this is only called from rankedBarriers click handler, which means that
      // we are reasonably sure these data are available for querying
      // NOTE: these data are not available at the same zoom levels as
      // the ranked data
      const getBarrierById = (id) => {
        const [feature] = map.querySourceFeatures(barrierType, {
          sourceLayer: barrierType,
          filter: ['==', 'id', id],
        })

        return feature
      }

      const handleRankLayerClick = (feature) => {
        const {
          properties,
          geometry: {
            coordinates: [lon, lat],
          },
        } = feature

        const barrier = getBarrierById(properties.id)

        if (barrier) {
          onSelectBarrier({
            ...barrier.properties,
            barrierType,
            HUC8Name: getHUCName('HUC8', barrier.properties.HUC8),
            HUC12Name: getHUCName('HUC12', barrier.properties.HUC12),
            lat,
            lon,
            ...properties,
            hasnetwork: true,
            ranked: true,
          })
        }
      }

      handleLayerClick(lowerRank.id, handleRankLayerClick)
      handleLayerClick(topRank.id, handleRankLayerClick)

      // Add barrier highlight layer.
      map.addLayer(pointHighlight)

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

  const getHUCName = (layer, id) => {
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
  const debouncedSetRankFilter = useDebouncedCallback((field, threshold) => {
    const { current: map } = mapRef
    map.setFilter(topRank.id, ['<=', field, threshold])
    map.setFilter(lowerRank.id, ['>', field, threshold])
  }, 200)

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

    const { id } = pointHighlight

    // setting to empty feature collection effectively hides this layer
    let data = emptyFeatureCollection
    let networkID = Infinity
    let networkType = barrierType

    if (selectedBarrier) {
      console.log('selected', selectedBarrier)
      const {
        lat,
        lon,
        upnetid = Infinity,
        networkType: barrierNetworkType = barrierType,
      } = selectedBarrier
      data = {
        type: 'Point',
        coordinates: [lon, lat],
      }

      networkID = upnetid
      networkType = barrierNetworkType
    }

    // highlight upstream network if set otherwise clear it
    map.setFilter('network-highlight', [
      'all',
      ['==', ['get', 'intermittent'], false],
      ['==', ['get', networkType], networkID],
    ])
    map.setFilter('network-intermittent-highlight', [
      'all',
      ['==', ['get', 'intermittent'], true],
      ['==', ['get', networkType], networkID],
    ])

    map.getSource(id).setData(data)
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

    const { id = null, layer, bbox, maxZoom: fitBoundsMaxZoom } = searchFeature
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

    map.fitBounds(bbox, { padding: 20, fitBoundsMaxZoom, duration: 500 })
  }, [searchFeature, selectUnitById])

  useEffect(() => {
    const { current: map } = mapRef
    if (!map) return

    // if rankedBarriers is an empty array, layers attached to this source are effectively
    // hidden on the map
    map.getSource('ranked').setData(toGeoJSONPoints(rankedBarriers))

    // rankedBarriers are only present for results step, so if this is non-empty
    // we need to hide the includedPoints layer; otherwise show it
    map.setLayoutProperty(
      includedPoint.id,
      'visibility',
      rankedBarriers.length > 0 ? 'none' : 'visible'
    )
  }, [rankedBarriers])

  useEffect(() => {
    const { current: map } = mapRef
    if (!map) return

    debouncedSetRankFilter(`${scenario}_tier`, tierThreshold)
  }, [tierThreshold, scenario, debouncedSetRankFilter])

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
      backgroundPoint,
      topRank,
      lowerRank,
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
      background: backgroundLegend,
      topRank: topRankLegend,
      lowerRank: lowerRankLegend,
      damsSecondary,
      waterfalls,
    } = pointLegends

    const circles = []
    const patches = []
    const lines = [
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
    let footnote = null

    if (Math.max(...Object.values(priorityLayerState))) {
      Object.entries(priorityLayerState)
        .filter(([id, visible]) => visible)
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

      if (isWithinZoom[backgroundPoint.id]) {
        circles.push({
          ...backgroundLegend,
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
      if (!isWithinZoom[topRank.id]) {
        footnote = `Zoom in further to see top-ranked ${barrierTypeLabel}`
      } else {
        const tierLabel =
          tierThreshold === 1 ? 'tier 1' : `tiers 1 - ${tierThreshold}`
        circles.push({
          ...topRankLegend,
          label: `Top-ranked ${barrierTypeLabel} (${tierLabel})`,
        })
      }

      if (isWithinZoom[lowerRank.id]) {
        circles.push({
          ...lowerRankLegend,
          label: `lower-ranked ${barrierTypeLabel}`,
        })
      }

      if (isWithinZoom[excludedPoint.id]) {
        circles.push({
          ...excludedLegend,
          label: `not selected ${barrierTypeLabel}`,
        })
      }

      if (isWithinZoom[backgroundPoint.id]) {
        circles.push({
          ...backgroundLegend,
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

      if (isWithinZoom[backgroundPoint.id]) {
        circles.push({
          ...backgroundLegend,
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
    <>
      <Map onCreateMap={handleCreateMap} {...props}>
        <DropDownLayerChooser
          label="Priority Watersheds"
          options={[
            { id: 'usfs', label: 'USFS priority watersheds' },
            { id: 'coa', label: 'SARP conservation opportunity areas' },
            {
              id: 'sgcn',
              label:
                'Watersheds with most Species of Greatest Conservation Need per state',
            },
          ]}
          onChange={handlePriorityLayerChange}
        />
        <Legend {...getLegend()} />
      </Map>
    </>
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
}

export default memo(PriorityMap)
