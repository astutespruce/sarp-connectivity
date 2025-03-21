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
  setBarrierHighlight,
  getInArrayExpr,
  getInStringExpr,
  getInMapUnitsExpr,
  getBarrierTooltip,
  getBitFromBitsetExpr,
} from 'components/Map'
import { barrierTypeLabels, pointLegends, pointColors } from 'config'
import { isEqual, groupBy } from 'util/data'

import {
  sources,
  priorityAreasLegend,
  unitLayerConfig,
} from 'components/Workflow/config'
import {
  maskFill,
  maskOutline,
  unitLayers,
  unitHighlightLayers,
  parentOutline,
  priorityAreaLayers,
} from 'components/Workflow/layers'
import {
  excludedPointLayer,
  includedPointLayer,
  waterfallsLayer,
} from './layers'

const SurveyMap = ({
  allowUnitSelect,
  activeLayer,
  selectedUnit,
  selectedBarrier,
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
  const hoverPriorityAreaRef = useRef(null)
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
        waterfallsLayer.id,
        excludedPointLayer.id,
        includedPointLayer.id,
        // NOTE: other barrier types not added because they are already
        // present in road crossings tiles
      ]

      const clickLayers = pointLayers.concat(
        Object.keys(unitLayerConfig).map((id) => `${id}-unit-fill`)
      )

      // add extra sources
      Object.entries(sources).forEach(([id, source]) => {
        map.addSource(id, source)
      })

      // Add the priority areas under everything else
      priorityAreaLayers.forEach((lyr) => {
        map.addLayer(lyr)
      })

      map.on(
        'mousemove',
        priorityAreaLayers[0].id,
        ({ features: [feature], lngLat }) => {
          if (map.getZoom() > 10) {
            if (hoverPriorityAreaRef.current !== null) {
              map.removeFeatureState({
                id: hoverPriorityAreaRef.current,
                source: priorityAreaLayers[1].source,
                sourceLayer: priorityAreaLayers[1]['source-layer'],
              })
              hoverPriorityAreaRef.current = null
            }
            return
          }

          const {
            id: featureId,
            properties: { type, name },
          } = feature

          if (hoverPriorityAreaRef.current !== featureId) {
            map.removeFeatureState({
              id: hoverPriorityAreaRef.current,
              source: priorityAreaLayers[1].source,
              sourceLayer: priorityAreaLayers[1]['source-layer'],
            })
          }

          const { label: priorityLabel, showName } =
            priorityAreasLegend.entries.filter(({ id }) => id === type)[0]

          const prefix = `${priorityLabel}`
          const suffix = showName ? `: ${name}` : ''

          /* eslint-disable-next-line no-param-reassign */
          map.getCanvas().style.cursor = 'pointer'
          tooltip
            .setLngLat(lngLat)
            .setHTML(`<b>${prefix}${suffix}</b>`)
            .addTo(map)

          map.setFeatureState(
            {
              id: featureId,
              source: priorityAreaLayers[1].source,
              sourceLayer: priorityAreaLayers[1]['source-layer'],
            },
            { highlight: true }
          )

          hoverPriorityAreaRef.current = featureId
        }
      )
      map.on('mouseleave', priorityAreaLayers[0].id, () => {
        /* eslint-disable-next-line no-param-reassign */
        map.getCanvas().style.cursor = ''
        tooltip.remove()

        map.removeFeatureState({
          id: hoverPriorityAreaRef.current,
          source: priorityAreaLayers[1].source,
          sourceLayer: priorityAreaLayers[1]['source-layer'],
        })

        hoverPriorityAreaRef.current = null
      })

      // Initially the mask and boundary are visible
      map.addLayer(maskFill)
      map.addLayer(maskOutline)

      // Add flowlines
      networkLayers
        .filter(({ id }) => !id.endsWith('-highlight'))
        .forEach((layer) => {
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
          // show grey fill when the map unit cannot be ranked
          const bitPos = 5
          const fillExpr = [
            'case',
            ['==', getBitFromBitsetExpr('has_data', bitPos), 0],
            0.25,
            0,
          ]

          unitLayers.forEach(({ id, ...rest }) => {
            const unitLayer = { ...config, ...rest, id: `${layer}-${id}` }

            if (id === 'unit-fill') {
              unitLayer.paint['fill-opacity'] = fillExpr
            }

            map.addLayer(unitLayer)
          })

          // Each layer has 2 highlight layers: highlight fill, highlight outline
          unitHighlightLayers.forEach(({ id, ...rest }) => {
            map.addLayer({ ...config, ...rest, id: `${layer}-${id}` })
          })
        }
      )

      map.addLayer(waterfallsLayer)

      // all points are initially excluded from analysis until their
      // units are selected
      map.addLayer(excludedPointLayer)
      map.addLayer(includedPointLayer)

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
            properties,
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
                properties.sarpidname && properties.sarpidname.startsWith('sm')
                  ? 'small_barriers'
                  : feature.source,
                properties
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

        if (source === 'map_units') {
          onSelectUnit({ layer: sourceLayer, id: properties.id })
          return
        }

        if (map.getZoom() < 8) {
          // don't allow selection of points below zoom 8
          const [unitLayerFeature] = features.filter(
            ({ source: lyrSource }) => lyrSource === 'map_units'
          )
          if (unitLayerFeature) {
            onSelectUnit({
              layer: unitLayerFeature.sourceLayer,
              id: unitLayerFeature.properties.id,
            })
          }
          return
        }

        const removed = sourceLayer.startsWith('removed_')

        const thisBarrierType =
          properties.sarpidname && properties.sarpidname.startsWith('sm')
            ? 'small_barriers'
            : source

        const networkType =
          barrierType === 'small_barriers' || barrierType === 'road_crossings'
            ? 'combined_barriers'
            : barrierType

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
    [barrierType, onMapLoad, onSelectBarrier, onSelectUnit]
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

    if (selectedBarrier === null) {
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
        ? getInMapUnitsExpr(activeLayer, ids)
        : false

      const outsideActiveUnitsExpr = hasActiveUnits
        ? ['!', insideActiveUnitsExpr]
        : true

      const includedByFilters = filterEntries.map(([field, values]) =>
        filterConfigIndex[field].isArray
          ? getInStringExpr(field, values)
          : getInArrayExpr(field, values)
      )

      const excludedByFilters = includedByFilters.map((f) => ['!', f])

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
    if (bounds == null) return
    const { current: map } = mapRef
    if (!map) return

    map.fitBounds(bounds, { padding: 20, maxZoom: 14, duration: 500 })
  }, [bounds])

  const handlePriorityLayerChange = useCallback((typeStatus) => {
    const { current: map } = mapRef
    if (!map) return

    const visibleTypes = Object.entries(typeStatus)
      /* eslint-disable-next-line no-unused-vars */
      .filter(([id, isVisible]) => isVisible)
      /* eslint-disable-next-line no-unused-vars */
      .map(([id, _]) => id)

    priorityAreaLayers.forEach(({ id }) => {
      map.setLayoutProperty(
        id,
        'visibility',
        visibleTypes.length > 0 ? 'visible' : 'none'
      )
      map.setFilter(id, ['in', ['get', 'type'], ['literal', visibleTypes]])
    })

    setPriorityLayerState(visibleTypes)
  }, [])

  const getLegend = () => {
    const {
      included: includedLegend,
      excluded: excludedLegend,
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

    if (allowUnitSelect) {
      patches.push({
        id: 'summaryAreas',
        entries: [
          {
            color: 'rgba(0,0,0,0.15)',
            label: `area with no mapped ${barrierTypeLabel}`,
          },
        ],
      })
    }

    const footnote = zoom < 10 ? `zoom in to see ${barrierTypeLabel}` : null

    if (priorityLayerState.length > 0) {
      priorityAreasLegend.entries
        .filter(({ id }) => priorityLayerState.indexOf(id) !== -1)
        .forEach(({ id, label }) => {
          patches.push({
            id,
            entries: [{ id, label, color: priorityAreasLegend.color }],
          })
        })
    }

    if (zoom >= 10) {
      // if no layer is selected for choosing summary areas
      if (activeLayer === null) {
        circles.push({
          ...includedLegend.getSymbol(barrierType),
          label: `${barrierTypeLabel}`,
        })
      }
      // either in select units or filter step
      else {
        circles.push(
          ...[
            {
              ...includedLegend.getSymbol(barrierType),
              label: includedLegend
                .getLabel(barrierTypeLabel)
                .replace('included in prioritization', 'selected for download'),
            },
            {
              ...excludedLegend.getSymbol(barrierType),
              label: excludedLegend
                .getLabel(barrierTypeLabel)
                .replace(
                  'not included in prioritization',
                  'not selected for download'
                ),
            },
            {
              id: 'majorBarrier',
              label: 'major or worse barrier based on field assessment',
              radius: 6,
              color: `${pointColors.majorBarrier.color}`,
              borderColor: `${pointColors.majorBarrier.strokeColor}`,
              borderWidth: 1,
            },
          ]
        )

        unrankedBarriers.forEach(({ id, getSymbol, getLabel }) => {
          circles.push({
            ...getSymbol('small_barriers'),
            label: getLabel(
              `${id === 'default' ? 'off-network surveyed ' : ''}${barrierTypeLabels.small_barriers}`
            ).replace('not available for prioritization', ''),
          })
        })

        other
          .filter(({ id }) => id !== 'dams-secondary')
          .forEach(({ getSymbol, getLabel }) => {
            circles.push({
              ...getSymbol('small_barriers'),
              label: getLabel(barrierTypeLabels.small_barriers),
            })
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
    <Map onCreateMap={handleCreateMap} bounds={bounds} {...props}>
      <DropDownLayerChooser
        label="Priority Areas"
        options={priorityAreasLegend.entries}
        onChange={handlePriorityLayerChange}
      />
      <Legend {...getLegend()} />
      {children}
    </Map>
  )
}

SurveyMap.propTypes = {
  allowUnitSelect: PropTypes.bool,
  activeLayer: PropTypes.string,
  selectedUnit: PropTypes.object,
  selectedBarrier: PropTypes.object,
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

SurveyMap.defaultProps = {
  allowUnitSelect: false,
  activeLayer: null,
  selectedUnit: null,
  selectedBarrier: null,
  summaryUnits: [],
  bounds: null,
  children: null,
}

export default memo(SurveyMap)
