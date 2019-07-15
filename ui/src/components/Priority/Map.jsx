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
import { unitLayerConfig } from './config'
import {
  maskFill,
  maskOutline,
  unitLayers,
  parentOutline,
  pointHighlight,
  backgroundPoint,
  excludedPoint,
  includedPoint,
  topRank,
  lowerRank,
} from './layers'
import { selectUnit } from '../../../../ui-bk/src/actions/priority'

const PriorityMap = ({
  activeLayer,
  barrierType,
  selectedUnit,
  selectedBarrier,
  searchFeature,
  summaryUnits,
  onSelectUnit,
  onSelectBarrier,
  ...props
}) => {
  const mapRef = useRef(null)

  // first layer of system is default on init
  // const [visibleLayer, setVisibleLayer] = useState(layers.filter(({system: lyrSystem}) => lyrSystem === system)[0])
  const [zoom, setZoom] = useState(0)

  const handleCreateMap = useCallback(map => {
    mapRef.current = map

    map.on('zoomend', () => {
      setZoom(map.getZoom())
    })

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

        // Each layer has 4 display layers: outline, fill, highlight fill, highlight outline
        unitLayers.forEach(({ id, ...rest }) => {
          const layerId = `${layer}-${id}`
          map.addLayer({ ...config, ...rest, id: layerId })

          if (id === 'unit-fill') {
            handleLayerClick(layerId, onSelectUnit)
          }
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
  }, [])

  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    // toggle visibility of layers so that we only show those layers for the activeLayer
    Object.keys(unitLayerConfig).forEach(layer => {
      const visibility = layer === activeLayer ? 'visible' : 'none'
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
    })
  }, [activeLayer])

  useEffect(() => {
    const { current: map } = mapRef

    if (!(map && activeLayer)) return

    const ids = summaryUnits.map(({ id }) => id)
    const filterExpr =
      ids.length > 0 ? ['in', 'id', ...ids] : ['==', 'id', Infinity]

    // last 2 layers are for highlight
    unitLayers.slice(2).forEach(({ id }) => {
      map.setFilter(`${activeLayer}-${id}`, filterExpr)
    })
  }, [activeLayer, summaryUnits])

  useEffect(() => {
    const { current: map } = mapRef

    if (!map) return

    const { id } = pointHighlight

    // setting to null effectively hides this layer
    let data = null

    if (selectedBarrier) {
      const { lat, lon } = selectedBarrier
      data = {
        type: 'Point',
        coordinates: [lon, lat],
      }
    }

    map.getSource(id).setData(data)
  }, [selectedBarrier])

  // useEffect(() => {
  //   const { current: map } = mapRef

  //   if (!map) return

  //   const subLayers = ['fill', 'outline', 'highlight']

  //   // show or hide layers as necessary
  //   layers.forEach(({ id, system: lyrSystem }) => {
  //     const visibility = lyrSystem === system ? 'visible' : 'none'
  //     subLayers.forEach(suffix => {
  //       map.setLayoutProperty(`${id}-${suffix}`, 'visibility', visibility)
  //     })
  //   })

  //   // setVisibleLayer(getVisibleLayer(map, system))
  //   // TODO: update legend
  // }, [system])

  // useEffect(() => {
  //   const { current: map } = mapRef

  //   if (!map) return

  //   // update renderer and filter on all layers
  //   layers.forEach(({ id, bins: { [barrierType]: bins } }) => {
  //     const colors = COLORS.count[bins.length]
  //     map.setPaintProperty(
  //       `${id}-fill`,
  //       'fill-color',
  //       interpolateExpr(barrierType, bins, colors)
  //     )
  //     map.setFilter(`${id}-fill`, ['>', barrierType, 0])
  //     map.setFilter(`${id}-outline`, ['>', barrierType, 0])
  //   })

  //   // TODO: update legend
  // }, [barrierType])

  // useEffect(() => {
  //   const { current: map } = mapRef

  //   if (!map) return

  //   // clear out filter on non-visible layers and set for visible layers
  //   // also clear it out if it is undefined
  //   const { id = Infinity } = selectedUnit || {}
  //   layers.forEach(({ id: lyrId, system: lyrSystem }) => {
  //     map.setFilter(`${lyrId}-highlight`, [
  //       '==',
  //       'id',
  //       lyrSystem === system ? id : Infinity,
  //     ])
  //   })
  // }, [system, selectedUnit])

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

  // const { layerTitle, legendEntries } = useMemo(() => {
  //   const layer = layers.filter(
  //     ({ system: lyrSystem, minzoom, maxzoom }) =>
  //       lyrSystem === system && zoom >= minzoom && zoom < maxzoom
  //   )[0]

  //   const {
  //     title,
  //     bins: { [barrierType]: bins },
  //   } = layer
  //   // flip the order of colors and bins since we are displaying from top to bottom
  //   // add opacity to color
  //   const colors = COLORS.count[bins.length].map(c => `${c}4d`).reverse()

  //   const labels = bins
  //     .map((bin, i) => {
  //       if (i === 0) {
  //         return `≤ ${Math.round(bin).toLocaleString()} ${barrierType}`
  //       }
  //       if (i === bins.length - 1) {
  //         return `≥ ${Math.round(bin).toLocaleString()} ${barrierType}`
  //       }
  //       // Use midpoint value
  //       return Math.round(bin).toLocaleString()
  //     })
  //     .reverse()

  //   return {
  //     layerTitle: title,
  //     legendEntries: colors.map((color, i) => ({
  //       color,
  //       label: labels[i],
  //     })),
  //   }
  // }, [system, barrierType, zoom])

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

  return (
    <>
      <Map onCreateMap={handleCreateMap} {...props} />
      {/* <Legend
        title={layerTitle}
        entries={legendEntries}
        footnote={`areas with no ${barrierType} are not shown`}
      /> */}
    </>
  )
}

PriorityMap.propTypes = {
  activeLayer: PropTypes.string,
  barrierType: PropTypes.string.isRequired,
  selectedUnit: PropTypes.object,
  summaryUnits: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
    })
  ),
  searchFeature: SearchFeaturePropType,
  onSelectUnit: PropTypes.func.isRequired,
  onSelectBarrier: PropTypes.func.isRequired,
}

PriorityMap.defaultProps = {
  activeLayer: null,
  selectedUnit: null,
  selectedBarrier: null,
  searchFeature: null,
  summaryUnits: [],
}

export default memo(PriorityMap)
