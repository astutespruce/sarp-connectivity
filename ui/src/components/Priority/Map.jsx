import React, { memo, useEffect, useRef, useCallback, useState } from 'react'
import PropTypes from 'prop-types'

import { useCrossfilter } from 'components/Crossfilter'
import { useBarrierType } from 'components/Data'
import {
  Map,
  Legend,
  interpolateExpr,
  SearchFeaturePropType,
} from 'components/Map'

import { unitLayerConfig } from './config'
import {
  maskFill,
  maskOutline,
  unitLayers,
  unitHighlightLayers,
  parentOutline,
  pointHighlight,
  backgroundPoint,
  excludedPoint,
  includedPoint,
  pointLegends,
  topRank,
  lowerRank,
} from './layers'

const PriorityMap = ({
  allowUnitSelect,
  allowFilter,
  activeLayer,
  selectedUnit,
  selectedBarrier,
  rankedBarriers,
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

  // first layer of system is default on init
  // const [visibleLayer, setVisibleLayer] = useState(layers.filter(({system: lyrSystem}) => lyrSystem === system)[0])
  const [zoom, setZoom] = useState(0)

  const handleCreateMap = useCallback(map => {
    mapRef.current = map

    map.on('zoomend', () => {
      setZoom(map.getZoom())
    })

    // set for initial load too
    setZoom(map.getZoom())

    // Initially the mask and boundary are visible
    map.addLayer(maskFill)
    map.addLayer(maskOutline)

    Object.entries(unitLayerConfig).forEach(
      ([layer, { minzoom = 0, maxzoom = 24, parent }]) => {
        const config = {
          'source-layer': layer,
          minzoom,
          maxzoom,
        }

        if (parent) {
          map.addLayer({
            'source-layer': parent,
            minzoom,
            maxzoom,
            ...parentOutline,
            id: `${layer}-${parentOutline.id}`,
          })
        }

        // Each layer has 2 display layers: outline, fill
        unitLayers.forEach(({ id, ...rest }) => {
          const layerId = `${layer}-${id}`
          map.addLayer({ ...config, ...rest, id: layerId })

          if (id === 'unit-fill') {
            handleLayerClick(layerId, onSelectUnit)
          }
        })

        // Each layer has 2 highlight layers: highlight fill, highlight outline
        unitHighlightLayers.forEach(({ id, ...rest }) => {
          const layerId = `${layer}-${id}`
          map.addLayer({ ...config, ...rest, id: layerId })
        })
      }
    )

    // add background point layer
    map.addLayer({
      ...backgroundPoint,
      source: barrierType,
    })
    handleLayerClick(backgroundPoint.id, feature => {
      onSelectBarrier({
        ...feature,
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
      onSelectBarrier({
        ...feature,
        hasnetwork: true,
      })
    })

    map.addLayer({
      ...pointConfig,
      ...includedPoint,
    })
    handleLayerClick(includedPoint.id, feature => {
      onSelectBarrier({
        ...feature,
        hasnetwork: true,
      })
    })

    // Add barrier highlight layer.
    map.addLayer(pointHighlight)

    // let consumers of map know that it is now fully loaded
    map.once('idle', onMapLoad)
  }, [])

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

    let data = {
      type: 'FeatureCollection',
      features: [],
    }

    if (selectedBarrier) {
      const { lat, lon } = selectedBarrier
      data = {
        type: 'Point',
        coordinates: [lon, lat],
      }
    }

    map.getSource(id).setData(data)
  }, [selectedBarrier])

  // if map allows filter, show selected vs unselected points, and make those without networks
  // background points
  // TODO: coordinate with legend
  // TODO: enable click on barriers or handle better
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
  }, [searchFeature])

  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    console.log('update ranked barriers')
  }, [rankedBarriers])

  // TODO: scenario chooser

  const selectUnitById = (id, layer) => {
    const [feature] = mapRef.current.querySourceFeatures('sarp', {
      sourceLayer: layer,
      filter: ['==', 'id', id],
    })

    if (feature !== undefined) {
      onSelectUnit({ ...feature.properties, layerId: layer })
    }
    return feature
  }

  // Hookup map on click handler to call onClick with the properties
  // of the feature selected
  const handleLayerClick = (layerId, onClick) => {
    const { current: map } = mapRef

    map.on('click', layerId, ({ point }) => {
      const [feature] = map.queryRenderedFeatures(point, { layers: [layerId] })
      if (feature) {
        onClick(feature.properties)
      }
    })
  }

  // TODO: memoize?
  // returns {entries, footnote}
  const getLegend = () => {
    const includedIsVisible =
      zoom >= includedPoint.minzoom && zoom <= includedPoint.maxzoom
    const excludedIsVisible =
      zoom >= excludedPoint.minzoom && zoom <= excludedPoint.maxzoom
    const backgroundIsVisible =
      zoom >= backgroundPoint.minzoom && zoom <= backgroundPoint.maxzoom

    const {
      included: includedLegend,
      excluded: excludedLegend,
      background: backgroundLegend,
    } = pointLegends

    if (activeLayer === null) {
      if (!excludedIsVisible) {
        return {
          footnote: `zoom in to see ${barrierType} available for analysis`,
        }
      }
      const circles = [
        {
          ...excludedLegend,
          label: `${barrierType} available for analysis`,
        },
      ]

      if (backgroundIsVisible) {
        circles.push({
          ...backgroundLegend,
          label: `${barrierType} not available for analysis`,
        })
      }

      return {
        circles,
      }
    }

    if (rankedBarriers !== null) {
      // TODO
      // background is "not included in analysis"

      return {
        footnote: 'TODO!',
      }
    }

    // either in select units or filter step

    if (!includedIsVisible) {
      return {
        footnote: `zoom in to see selected ${barrierType}`,
      }
    }

    const circles = [
      {
        ...includedLegend,
        label: `selected ${barrierType}`,
      },
    ]

    if (excludedIsVisible) {
      circles.push({
        ...excludedLegend,
        label: `not selected ${barrierType}`,
      })
    }

    if (backgroundIsVisible) {
      circles.push({
        ...backgroundLegend,
        label: `${barrierType} not available for analysis`,
      })
    }

    return {
      circles,
    }
  }

  return (
    <>
      <Map onCreateMap={handleCreateMap} {...props} />
      <Legend {...getLegend()} />
    </>
  )
}

PriorityMap.propTypes = {
  allowUnitSelect: PropTypes.bool,
  allowFilter: PropTypes.bool,
  activeLayer: PropTypes.string,
  selectedUnit: PropTypes.object,
  selectedBarrier: PropTypes.object,
  rankedBarriers: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
    })
  ),
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
  allowFilter: false,
  activeLayer: null,
  selectedUnit: null,
  selectedBarrier: null,
  searchFeature: null,
  summaryUnits: [],
  rankedBarriers: null,
}

export default memo(PriorityMap)
