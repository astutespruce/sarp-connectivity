import geoViewport from '@mapbox/geo-viewport'

import { barrierTypeLabelSingular, barrierNameWhenUnknown } from 'config'
import { isEmptyString } from 'util/string'

/**
 * Calculate the appropriate center and zoom to fit the bounds, given padding.
 * @param {Element} - map DOM node used to calculate height and width in screen pixels of map
 * @param {Array(number)} bounds - [xmin, ymin, xmax, ymax]
 * @param {float} padding - proportion of calculated zoom level to zoom out by, to pad the bounds
 */
export const getCenterAndZoom = (mapNode, bounds, padding = 0) => {
  const { offsetWidth: width, offsetHeight: height } = mapNode
  const viewport = geoViewport.viewport(
    bounds,
    [width, height],
    undefined,
    undefined,
    undefined,
    true
  )

  // Zoom out slightly to pad around bounds

  const zoom = Math.max(viewport.zoom - 1, 0) * (1 - padding)

  return { center: viewport.center, zoom }
}

/**
 * Calculate outer bounds that contains bounds1 and bounds2
 * @param {Array} bounds1 - [xmin, ymin, xmax, ymax] or null
 * @param {Array} bounds2 - [xmin, ymin, xmax, ymax] or null
 * @returns
 */
export const unionBounds = (bounds1, bounds2) => {
  if (!(bounds1 && bounds2)) {
    return bounds1 || bounds2
  }
  return [
    Math.min(bounds1[0], bounds2[0]),
    Math.min(bounds1[1], bounds2[1]),
    Math.max(bounds1[2], bounds2[2]),
    Math.max(bounds1[3], bounds2[3]),
  ]
}

/**
 * Interleaves a and b arrays into a single flat array:
 * a=[1,2], b=[3,4]
 * returns [1,3,2,4]
 *
 * @param {Array} a
 * @param {Array} b
 */
const flatzip = (a, b) => {
  if (a.length !== b.length) {
    throw new Error('arrays must be equal to use zip')
  }

  return a.reduce((prev, v, i) => prev.concat([v, b[i]]), [])
}

export const interpolateExpr = (fieldExpr, domain, range) => [
  'interpolate',
  ['linear'],
  fieldExpr,
  ...flatzip(domain, range),
]

export const toGeoJSONPoint = (record, x = 'lon', y = 'lat') => {
  const properties = {}
  Object.keys(record)
    .filter((f) => f !== x && f !== y)
    .forEach((f) => {
      properties[f] = record[f]
    })

  const feature = {
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [record[x], record[y]],
    },
    properties,
  }

  const { id } = record
  if (id !== undefined && id !== null) {
    feature.id = id
  }

  return feature
}

export const toGeoJSONPoints = (records) => ({
  type: 'FeatureCollection',
  features: records.map((r) => toGeoJSONPoint(r)),
})

/**
 * Returns an async function that can be used to get a blob from the map's canvas
 * @param {Object} map - Mapbox GL object
 * @returns
 */
export const mapToBlob = async (map) =>
  new Promise((resolve) => {
    map.once('idle', () => {
      map.getCanvas().toBlob(resolve)
    })
    // force redraw if needed
    map.triggerRepaint()
  })

export const mapToDataURL = async (map) =>
  new Promise((resolve) => {
    map.once('idle', () => {
      resolve(map.getCanvas().toDataURL('image/png'))
    })
    // force redraw if needed
    map.triggerRepaint()
  })

/**
 * Create an expression to toggle style based on highlight state of point
 * @param {Array or String} defaultExpr - expression used when point is not highlighted
 * @param {Array or String} highlightExpr - expression used when point is highlighted
 * @returns
 */
export const getHighlightExpr = (defaultExpr, highlightExpr) => [
  'case',
  ['boolean', ['feature-state', 'highlight'], false],
  highlightExpr,
  defaultExpr,
]

/**
 * Create an expression to toggle between two expressions based on a given
 * network scenario and tier threshold
 * @param {String} scenario
 * @param {Number} tierThreshold
 * @param {Array or String} belowExpr - expression used when tier of point is <= tierThreshold
 * @param {Array or String} aboveExpr  - expression used when tier of point is > tierThreshold
 * @returns
 */
export const getTierExpr = (scenario, tierThreshold, belowExpr, aboveExpr) => [
  'case',
  // make sure that tier field exists in feature state, otherwise emits null warnings
  // for following condition
  ['!=', ['feature-state', scenario], null],
  [
    'case',
    ['<=', ['feature-state', scenario], tierThreshold],
    belowExpr,
    aboveExpr,
  ],
  aboveExpr,
]

/**
 * Highlight an upstream functional network for a given networkID
 * @param {Object} map - Mapbox GL map instance
 * @param {String} networkType - dams or small_barriers
 * @param {Number} networkID - network to highlight or Infinity to clear highlight
 * @param {bool} removed - true if network is for a removed barrier
 */
export const highlightNetwork = (
  map,
  networkType,
  networkID,
  removed = false
) => {
  const prefix = removed ? 'removed-' : ''
  const filterExpr = removed
    ? [
        ['==', 'network_type', networkType],
        ['==', 'barrier_id', networkID],
      ]
    : [['==', networkType, networkID]]

  map.setFilter(`${prefix}network-highlight`, [
    'all',
    ['any', ['==', 'mapcode', 0], ['==', 'mapcode', 2]],
    ...filterExpr,
  ])
  map.setFilter(`${prefix}network-intermittent-highlight`, [
    'all',
    ['any', ['==', 'mapcode', 1], ['==', 'mapcode', 3]],
    ...filterExpr,
  ])
}

export const highlightRemovedNetwork = (map, networkType, barrierID) => {
  map.setFilter('removed-network-highlight', [
    'all',
    ['any', ['==', 'mapcode', 0], ['==', 'mapcode', 2]],
    ['==', 'network_type', networkType],
    ['==', 'barrier_id', barrierID],
  ])
  map.setFilter('removed-network-intermittent-highlight', [
    'all',
    ['any', ['==', 'mapcode', 1], ['==', 'mapcode', 3]],
    ['==', 'network_type', networkType],
    ['==', 'barrier_id', barrierID],
  ])
}

export const setBarrierHighlight = (map, feature, highlight) => {
  if (!feature) {
    return
  }

  const {
    id,
    layer: { source, 'source-layer': sourceLayer },
  } = feature

  map.setFeatureState(
    {
      id,
      source,
      sourceLayer,
    },
    {
      highlight,
    }
  )
}

/**
 * Construct Mapbox GL filter expression where field value must be in list of values
 * @param {String} field
 * @param {Iterable} values - list of values where field value must be present
 * @returns
 */
export const getInArrayExpr = (field, values) => [
  'in',
  ['get', field],
  ['literal', Array.from(values)],
]

/**
 * Construct Mapbox GL filter expression where field value must not be in list of values
 * @param {String} field
 * @param {Iterable} values - list of values where field value must be present
 * @returns
 */
export const getNotInArrayExpr = (field, values) => [
  '!',
  ['in', ['get', field], ['literal', Array.from(values)]],
]

/**
 * Construct Mapbox GL filter expression where at least one of the strings in
 * values must be a substring of the string in the field value
 * @param {String} field
 * @param {Iterable} values
 * @returns
 */
export const getInStringExpr = (field, values) => [
  'any',
  ...Array.from(values).map((v) => ['!=', ['index-of', v, ['get', field]], -1]),
]

/**
 * Construct Mapbox GL filter expression where none of the values must be a
 * substring of the string in the field value
 * @param {String} field
 * @param {Iterable} values
 * @returns
 */
export const getNotInStringExpr = (field, values) => [
  'all',
  ...Array.from(values).map((v) => ['==', ['index-of', v, ['get', field]], -1]),
]

export const getBarrierTooltip = (barrierType, { sarpidname = '|' }) => {
  const rawName = sarpidname.split('|')[1]

  // const typeLabel = capitalize(barrierTypeLabelSingular[barrierType])
  const typeLabel = barrierTypeLabelSingular[barrierType]
  let name = ''
  if (!isEmptyString(rawName)) {
    switch (barrierType) {
      case 'dams': {
        if (
          !(
            rawName.toLowerCase().startsWith('estimated') ||
            rawName.toLowerCase().startsWith('water diversion') ||
            rawName.toLowerCase().indexOf('dam') !== -1
          )
        ) {
          name = `${rawName} (${typeLabel})`
        } else {
          name = rawName
        }
        break
      }
      case 'waterfalls': {
        if (!(rawName.toLowerCase().indexOf('fall') !== -1)) {
          // name = `${typeLabel}: ${rawName}`
          name = `${rawName} (${typeLabel})`
        } else {
          name = rawName
        }

        break
      }
      default: {
        // name = `${typeLabel}: ${rawName}`
        name = `${rawName} (${typeLabel})`
      }
    }
  } else {
    name = barrierNameWhenUnknown[barrierType] || 'Unknown name'
  }

  return `<b>${name}</b>`
}
