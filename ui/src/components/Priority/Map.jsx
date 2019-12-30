import React, { memo, useEffect, useRef, useCallback, useState } from 'react'
import PropTypes from 'prop-types'
import { useDebouncedCallback } from 'use-debounce'

import { useCrossfilter } from 'components/Crossfilter'
import { useBarrierType } from 'components/Data'
import {
  Map,
  DropDownLayerChooser,
  Legend,
  SearchFeaturePropType,
  toGeoJSONPoints,
} from 'components/Map'

import { unitLayerConfig } from './config'
import {
  maskFill,
  maskOutline,
  unitLayers,
  unitHighlightLayers,
  flowlinesLayer,
  networkHighlightLayer,
  parentOutline,
  pointHighlight,
  backgroundPoint,
  excludedPoint,
  includedPoint,
  pointLegends,
  topRank,
  lowerRank,
  priorityWatersheds,
  priorityWatershedLegends,
} from './layers'

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
  const {
    state: { filters },
  } = useCrossfilter()
  const mapRef = useRef(null)
  const [priorityLayerState, setPriorityLayerState] = useState({})

  // first layer of system is default on init
  // const [visibleLayer, setVisibleLayer] = useState(layers.filter(({system: lyrSystem}) => lyrSystem === system)[0])
  const [zoom, setZoom] = useState(0)

  const handleCreateMap = useCallback(
    map => {
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
      priorityWatersheds.forEach(lyr => {
        map.addLayer(lyr)
      })

      // Initially the mask and boundary are visible
      map.addLayer(maskFill)
      map.addLayer(maskOutline)

      // Add flowlines and network highlight layers
      map.addLayer(flowlinesLayer)
      map.addLayer({
        ...networkHighlightLayer,
        source: `${barrierType}_network`,
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
      handleLayerClick(backgroundPoint.id, feature => {
        const {
          properties,
          geometry: {
            coordinates: [lon, lat],
          },
        } = feature
        onSelectBarrier({
          ...properties,
          lat,
          lon,
          hasnetwork: false,
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
      handleLayerClick(excludedPoint.id, feature => {
        const {
          properties,
          geometry: {
            coordinates: [lon, lat],
          },
        } = feature
        onSelectBarrier({
          ...properties,
          lat,
          lon,
          hasnetwork: true,
        })
      })

      map.addLayer({
        ...pointConfig,
        ...includedPoint,
      })
      handleLayerClick(includedPoint.id, feature => {
        const {
          properties,
          geometry: {
            coordinates: [lon, lat],
          },
        } = feature
        onSelectBarrier({
          ...properties,
          lat,
          lon,
          hasnetwork: true,
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

      // select barrier from tile data using ID
      // this is only called from rankedBarriers click handler, which means that
      // we are reasonably sure these data are available for querying
      // NOTE: these data are not available at the same zoom levels as
      // the ranked data
      const getBarrierById = id => {
        const [feature] = map.querySourceFeatures(barrierType, {
          sourceLayer: barrierType,
          filter: ['==', 'id', id],
        })

        return feature
      }

      const handleRankLayerClick = feature => {
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
            lat,
            lon,
            ...properties,
            hasnetwork: true,
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

  const selectUnitById = useCallback(
    (id, layer) => {
      const [feature] = mapRef.current.querySourceFeatures('sarp', {
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
  const [debouncedSetRankFilter] = useDebouncedCallback((field, threshold) => {
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
    Object.keys(unitLayerConfig).forEach(layer => {
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

    if (selectedBarrier) {
      const { lat, lon, upnetid = Infinity } = selectedBarrier
      data = {
        type: 'Point',
        coordinates: [lon, lat],
      }

      networkID = upnetid
    }

    // highlight upstream network if set otherwise clear it
    map.setFilter('networks', ['==', 'networkID', networkID])

    map.getSource(id).setData(data)
  }, [selectedBarrier])

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

  const handlePriorityLayerChange = useCallback(visiblePriorityLayers => {
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
    } = pointLegends

    const circles = []
    const patches = []
    let footnote = null

    if (Math.max(...Object.values(priorityLayerState))) {
      const priorityEntries = Object.entries(priorityLayerState)
        .filter(([id, visible]) => visible)
        .forEach(([id]) => {
          patches.push(priorityWatershedLegends[id])
        })
    }

    // if no layer is selected for choosing summary areas
    if (activeLayer === null) {
      if (!isWithinZoom[excludedPoint.id]) {
        // return {
        //   footnote: `zoom in to see ${barrierType} available for analysis`,
        // }
        footnote = `zoom in to see ${barrierType} available for analysis`
      } else {
        circles.push({
          ...excludedLegend,
          label: `${barrierType} available for analysis`,
        })
      }

      if (isWithinZoom[backgroundPoint.id]) {
        circles.push({
          ...backgroundLegend,
          label: `${barrierType} not available for analysis`,
        })
      }

      // return {
      //   circles,
      // }
    }

    // may need to be mutually exclusive of above
    else if (rankedBarriers.length > 0) {
      if (!isWithinZoom[topRank.id]) {
        // return {
        //   footnote: `Zoom in further to see top-ranked ${barrierType}`,
        // }
        footnote = `Zoom in further to see top-ranked ${barrierType}`
      } else {
        const tierLabel =
          tierThreshold === 1 ? 'tier 1' : `tiers 1 - ${tierThreshold}`
        circles.push({
          ...topRankLegend,
          label: `Top-ranked ${barrierType} (${tierLabel})`,
        })
      }

      if (isWithinZoom[lowerRank.id]) {
        circles.push({
          ...lowerRankLegend,
          label: `lower-ranked ${barrierType}`,
        })
      }

      if (isWithinZoom[excludedPoint.id]) {
        circles.push({
          ...excludedLegend,
          label: `not selected ${barrierType}`,
        })
      }

      if (isWithinZoom[backgroundPoint.id]) {
        circles.push({
          ...backgroundLegend,
          label: `${barrierType} not included in analysis`,
        })
      }

      // return {
      //   circles,
      // }
    } else {
      // either in select units or filter step
      if (isWithinZoom[includedPoint.id]) {
        circles.push({
          ...includedLegend,
          label: `selected ${barrierType}`,
        })
      } else {
        footnote = `zoom in to see selected ${barrierType}`
        // return {
        //   patches,
        //   footnote: `zoom in to see selected ${barrierType}`,
        // }
      }

      if (isWithinZoom[excludedPoint.id]) {
        circles.push({
          ...excludedLegend,
          label: `not selected ${barrierType}`,
        })
      }

      if (isWithinZoom[backgroundPoint.id]) {
        circles.push({
          ...backgroundLegend,
          label: `${barrierType} not available for analysis`,
        })
      }

      if (allowUnitSelect) {
        patches.push({
          id: 'summaryAreas',
          entries: [
            {
              color: 'rgba(0,0,0,0.15)',
              label: `area with no inventoried ${barrierType}`,
            },
          ],
        })
      }
    }

    return {
      patches,
      circles,
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
            // {
            //   id: 'sebio',
            //   label: 'Southeast aquatic biodiversity hotspots',
            // },
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
