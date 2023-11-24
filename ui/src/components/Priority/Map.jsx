// @refresh reset
import React, {
  memo,
  useEffect,
  useRef,
  useCallback,
  useState,
  useMemo,
} from 'react'
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
  networkLayers,
  highlightNetwork,
  setBarrierHighlight,
  getInArrayExpr,
  getNotInArrayExpr,
  getInStringExpr,
  getNotInStringExpr,
  getBarrierTooltip,
} from 'components/Map'
import { barrierTypeLabels, pointLegends } from 'config'
import { isEqual, groupBy } from 'util/data'

import { unitLayerConfig } from './config'
import {
  maskFill,
  maskOutline,
  unitLayers,
  unitHighlightLayers,
  parentOutline,
  prioritizedPointLayer,
  unrankedPointLayer,
  removedBarrierPointLayer,
  otherBarrierPointLayer,
  excludedPointLayer,
  includedPointLayer,
  roadCrossingsLayer,
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
  summaryUnits,
  bounds,
  onSelectUnit,
  onSelectBarrier,
  onMapLoad,
  children,
  ...props
}) => {
  const barrierType = useBarrierType()
  const barrierTypeLabel = barrierTypeLabels[barrierType]

  const {
    state: { filters },
    filterConfig,
  } = useCrossfilter()
  const mapRef = useRef(null)
  const hoverFeatureRef = useRef(null)
  const selectedFeatureRef = useRef(null)
  const rankedBarriersRef = useRef(null)
  const rankedBarriersIndexRef = useRef({})
  const [priorityLayerState, setPriorityLayerState] = useState({})

  const filterConfigIndex = useMemo(
    () => {
      const allFilters = filterConfig.reduce(
        (prev, { filters: groupFilters }) => {
          prev.push(...groupFilters)
          return prev
        },
        []
      )

      return groupBy(allFilters, 'field')
    },
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  // first layer of system is default on init
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
        roadCrossingsLayer.id,
        damsSecondaryLayer.id,
        waterfallsLayer.id,
        removedBarrierPointLayer.id,
        otherBarrierPointLayer.id,
        unrankedPointLayer.id,
        excludedPointLayer.id,
        includedPointLayer.id,
        prioritizedPointLayer.id,
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
          // by default, show anything with 0 ranked barriers as grey
          let fillExpr = ['match', ['get', `ranked_${barrierType}`], 0, 0.25, 0]

          if (barrierType === 'small_barriers') {
            fillExpr = [
              'case',
              [
                'any',
                ['==', ['get', 'ranked_small_barriers'], 0],
                ['<', ['get', 'total_small_barriers'], 10],
              ],
              0.25,
              0,
            ]
          } else if (
            barrierType === 'combined_barriers' ||
            barrierType === 'largefish_barriers' ||
            barrierType === 'smallfish_barriers'
          ) {
            let damField = 'ranked_dams'
            if (barrierType === 'largefish_barriers') {
              damField = 'largefish_barriers_ranked_dams'
            } else if (barrierType === 'smallfish_barriers') {
              damField = 'smallfish_barriers_ranked_dams'
            }

            // show grey if there are 0 of both types, or < 10 total barriers
            // (Ok if all are not actual barriers and / or no dams)
            // always use total small barriers even if count for scenario is 0
            fillExpr = [
              'case',
              [
                'any',
                ['<', ['get', 'total_small_barriers'], 10],
                [
                  'all',
                  ['==', ['get', damField], 0],
                  ['==', ['get', 'total_small_barriers'], 0],
                ],
              ],
              0.25,
              0,
            ]
          }

          unitLayers.forEach(({ id, ...rest }) => {
            const layerId = `${layer}-${id}`
            const unitLayer = { ...config, ...rest, id: layerId }

            if (id === 'unit-fill') {
              unitLayer.paint['fill-opacity'] = fillExpr
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

      // add waterfalls
      map.addLayer(waterfallsLayer)

      // add road crossings layer
      map.addLayer({
        ...roadCrossingsLayer,
        layout: {
          visibility: barrierType !== 'dams' ? 'visible' : 'none',
        },
      })

      // add secondary dams layer (only applicable for small barriers)
      map.addLayer({
        ...damsSecondaryLayer,
        layout: {
          visibility: barrierType === 'small_barriers' ? 'visible' : 'none',
        },
      })

      map.addLayer({
        source: barrierType,
        'source-layer': `other_${barrierType}`,
        ...otherBarrierPointLayer,
      })

      map.addLayer({
        source: barrierType,
        'source-layer': `removed_${barrierType}`,
        ...removedBarrierPointLayer,
      })

      map.addLayer({
        source: barrierType,
        'source-layer': `unranked_${barrierType}`,
        ...unrankedPointLayer,
      })

      // add primary barrier-type point layers
      const pointConfig = {
        source: barrierType,
        'source-layer': `ranked_${barrierType}`,
      }

      // all points are initially excluded from analysis until their
      // units are selected
      map.addLayer({ ...pointConfig, ...excludedPointLayer })
      map.addLayer({
        ...pointConfig,
        ...includedPointLayer,
      })

      map.addLayer({
        ...pointConfig,
        ...prioritizedPointLayer,
        paint: {
          ...prioritizedPointLayer.paintLayer,
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
                feature.source === 'combined_barriers' ||
                  feature.source === 'largefish_barriers' ||
                  feature.source === 'smallfish_barriers'
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

        const removed = sourceLayer.startsWith('removed_')

        const thisBarrierType =
          source === 'combined_barriers' ||
          source === 'largefish_barriers' ||
          source === 'smallfish_barriers'
            ? properties.barriertype
            : source

        const networkType =
          barrierType === 'small_barriers' ? 'combined_barriers' : barrierType

        // promote network fields if clicking on a waterfall
        let networkIDField = 'upnetid'
        if (removed) {
          networkIDField = 'id'
        } else if (thisBarrierType === 'waterfalls') {
          networkIDField = `${networkType}_upnetid`
        }

        setBarrierHighlight(map, feature, true)
        selectedFeatureRef.current = feature

        onSelectBarrier({
          upnetid: properties[networkIDField] || Infinity,
          ...properties,
          tiers: rankedBarriersIndexRef.current[properties.id] || null,
          barrierType: thisBarrierType,
          networkType,
          lat,
          lon,
          // note: ranked layers are those that can be ranked, not necessarily those that have custom ranks
          ranked: sourceLayer.startsWith('ranked_'),
          removed,
          layer: {
            source,
            sourceLayer,
          },
        })
      })

      // let consumers of map know that it is now fully loaded
      map.once('idle', () => onMapLoad(map))
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

  // Debounce updates to the filter to prevent frequent redraws
  // which have bad performance with high numbers of dams
  const debouncedSetRankFilter = useDebouncedCallback(
    (currentScenario, threshold) => {
      const { current: map } = mapRef

      map.setPaintProperty(
        prioritizedPointLayer.id,
        'circle-color',
        getTierPointColor(currentScenario, threshold)
      )
      map.setPaintProperty(
        prioritizedPointLayer.id,
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
    const removed = selectedBarrier && selectedBarrier.removed
    if (selectedBarrier) {
      const networkIDField = removed ? 'id' : 'upnetid'
      const { [networkIDField]: upnetid = Infinity } = selectedBarrier

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
      barrierType === 'small_barriers' ? 'combined_barriers' : barrierType,
      networkID,
      removed
    )
  }, [barrierType, selectedBarrier])

  // if map allows filter, show selected vs unselected points, and make those without networks
  // background points
  useEffect(
    () => {
      const { current: map } = mapRef

      if (!map) return

      const ids = summaryUnits.map(({ id }) => id)

      if (!(activeLayer || ids.length > 0)) {
        // if no summary units are selected, reset filters on barriers
        map.setFilter(includedPointLayer.id, ['==', 'id', Infinity])
        map.setFilter(excludedPointLayer.id, null)
        return
      }

      // Construct filter expressions for each active filter
      const filterEntries = Object.entries(filters || {}).filter(
        ([, v]) => v && v.size > 0
      )

      const hasActiveUnits = ids && ids.length > 0
      const insideActiveUnitsExpr = hasActiveUnits
        ? getInArrayExpr(activeLayer, ids)
        : false

      const outsideActiveUnitsExpr = hasActiveUnits
        ? getNotInArrayExpr(activeLayer, ids)
        : true

      const includedByFilters = filterEntries.map(([field, values]) =>
        filterConfigIndex[field].isArray
          ? getInStringExpr(field, values)
          : getInArrayExpr(field, values)
      )
      const excludedByFilters = filterEntries.map(([field, values]) =>
        filterConfigIndex[field].isArray
          ? getNotInStringExpr(field, values)
          : getNotInArrayExpr(field, values)
      )

      // update barrier layers to select those that are in selected units
      map.setFilter(includedPointLayer.id, [
        'all',
        insideActiveUnitsExpr,
        ...includedByFilters,
      ])
      map.setFilter(excludedPointLayer.id, [
        'any', // should this be any?
        outsideActiveUnitsExpr,
        ...excludedByFilters,
      ])
    },
    // filterConfigIndex intentionally excluded
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [activeLayer, summaryUnits, filters]
  )

  useEffect(() => {
    const { current: map } = mapRef
    if (!map) return

    const showRanks = rankedBarriers.length > 0
    map.setLayoutProperty(
      includedPointLayer.id,
      'visibility',
      showRanks ? 'none' : 'visible'
    )
    map.setLayoutProperty(
      prioritizedPointLayer.id,
      'visibility',
      showRanks ? 'visible' : 'none'
    )

    const { source, sourceLayer } = map.getLayer(prioritizedPointLayer.id)
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
      map.setFilter(
        prioritizedPointLayer.id,
        map.getFilter(includedPointLayer.id)
      )
      rankedBarriers.forEach(({ id, ...rest }) => {
        map.setFeatureState({ source, sourceLayer, id }, rest)
      })
      rankedBarriersIndexRef.current = groupBy(rankedBarriers, 'id')
    } else {
      rankedBarriersIndexRef.current = {}
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
      includedPointLayer,
      excludedPointLayer,
      otherBarrierPointLayer,
      prioritizedPointLayer,
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
      topRank: topRankLegend,
      lowerRank: lowerRankLegend,
      unrankedBarriers,
      other,
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
      if (!isWithinZoom[excludedPointLayer.id]) {
        footnote = `zoom in to see ${barrierTypeLabel} available for prioritization`
      } else {
        circles.push({
          ...includedLegend.getSymbol(barrierType),
          label: `${barrierTypeLabel} available for prioritization`,
        })
      }
    }

    // may need to be mutually exclusive of above
    else if (rankedBarriers.length > 0) {
      const tierLabel =
        tierThreshold === 1 ? 'tier 1' : `tiers 1 - ${tierThreshold}`
      circles.push({
        ...topRankLegend.getSymbol(barrierType),
        label: topRankLegend.getLabel(barrierTypeLabel, tierLabel),
      })

      circles.push({
        ...lowerRankLegend.getSymbol(barrierType),
        label: lowerRankLegend.getLabel(barrierTypeLabel, tierLabel),
      })

      if (isWithinZoom[excludedPointLayer.id]) {
        circles.push({
          ...excludedLegend.getSymbol(barrierType),
          label: excludedLegend.getLabel(barrierTypeLabel),
        })
      }
    } else {
      // either in select units or filter step
      if (isWithinZoom[includedPointLayer.id]) {
        circles.push({
          ...includedLegend.getSymbol(barrierType),
          label: includedLegend.getLabel(barrierTypeLabel),
        })
      } else {
        footnote = `zoom in to see ${barrierTypeLabel} included in prioritization`
      }

      if (isWithinZoom[excludedPointLayer.id]) {
        circles.push({
          ...excludedLegend.getSymbol(barrierType),
          label: excludedLegend.getLabel(barrierTypeLabel),
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

    if (isWithinZoom[otherBarrierPointLayer.id]) {
      unrankedBarriers
        .filter(
          ({ id }) =>
            // don't show minor barriers legend entry for dams view
            id !== 'minorBarrier' || barrierType !== 'dams'
        )
        .forEach(({ getSymbol, getLabel }) => {
          circles.push({
            ...getSymbol(barrierType),
            label: getLabel(barrierTypeLabel),
          })
        })

      other.forEach(({ id, getSymbol, getLabel }) => {
        if (id === 'dams-secondary' && barrierType !== 'small_barriers') {
          return
        }

        circles.push({
          ...getSymbol(barrierType),
          label: getLabel(barrierTypeLabel),
        })
      })
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
      {children}
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
  bounds: PropTypes.arrayOf(PropTypes.number),
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]),
  onSelectUnit: PropTypes.func.isRequired,
  onSelectBarrier: PropTypes.func.isRequired,
  onMapLoad: PropTypes.func.isRequired,
}

PriorityMap.defaultProps = {
  allowUnitSelect: false,
  activeLayer: null,
  selectedUnit: null,
  selectedBarrier: null,
  summaryUnits: [],
  rankedBarriers: [],
  bounds: null,
  children: null,
}

export default memo(PriorityMap)
