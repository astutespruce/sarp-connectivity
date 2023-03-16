import { addFunction, op, escape } from 'arquero'

import { reduceToObject } from 'util/data'

/**
 * Create object with dimensions
 * @param {Object} filterConfig - nested object of filter groups and filters
 * @returns Object
 */
export const createDimensions = (filterConfig) => {
  const dimensions = {}
  filterConfig.forEach(({ filters }) => {
    filters.forEach((filter) => {
      dimensions[filter.field] = filter
    })
  })

  return dimensions
}

/**
 * Calculate the count for each value present in values for dimension;
 * ignores count for any value that is not in values.
 */
export const getDimensionCount = (data, dimension) => {
  const { field, isArray, values: rawValues } = dimension
  const values = new Set(rawValues)

  let grouped = data.groupby(field).rollup({ _count: (d) => op.sum(d._count) })

  if (isArray) {
    // split by commas into separate rows, then regroup
    grouped = grouped
      .unroll(field)
      .groupby(field)
      .rollup({ _count: (d) => op.sum(d._count) })
  }

  return (
    grouped
      .derive({ row: op.row_object() })
      .array('row')
      // drop any values in data not in values list
      .filter(({ [field]: v }) => values.has(v))
      .reduce(...reduceToObject(field, (d) => d._count))
  )
}

/**
 * Calculates the count by value for each dimension based on the current filters
 * @param {Object} data - arquero table
 * @param {Object} dimensions - object of dimensions
 */

export const countByDimension = (data, dimensions) =>
  Object.values(dimensions)
    .map((dimension) => ({
      field: dimension.field,
      total: getDimensionCount(data, dimension),
    }))
    .reduce(...reduceToObject('field', (d) => d.total))

/**
 * Determine if record values contain any of the filterValues
 * @param {Array} filterValues - values in filter that are being searched
 * @param {Array} values - values on record
 * @returns bool
 */
const hasAny = (filterValues, values) => {
  for (let i = 0; i < filterValues.length; i += 1) {
    if (op.indexof(values, filterValues[i]) !== -1) {
      return true
    }
  }
  return false
}

// define hasAny filter for use in arquero
// NOTE: overwrite is used to redefine this on window reload
addFunction('hasAny', hasAny, { override: true })

export const applyFilters = (rawData, dimensions, rawFilters) => {
  let data = rawData
  const dimensionCounts = {}

  // do a first pass and apply all filters into derived columns
  const filters = Object.entries(rawFilters)
    /* eslint-disable-next-line no-unused-vars */
    .filter(([field, values]) => values && values.size > 0)
    .map(([field, values]) => {
      if (dimensions[field].isArray) {
        data = data.params({ field, values: [...values] }).derive({
          [`${field}_filter`]: (d, $) => op.hasAny($.values, d[$.field]),
        })
      } else {
        data = data.params({ field, values }).derive({
          [`${field}_filter`]: (d, $) => op.has($.values, d[$.field]),
        })
      }

      return field
    })

  // loop over filter in filters, apply all other filters except self and get count
  filters.forEach((field) => {
    const otherFilterFields = filters
      .filter((otherField) => otherField !== field)
      .map((otherField) => `${otherField}_filter`)

    const filtered = data
      .params({ fields: otherFilterFields })
      .filter(
        escape(
          (d, $) => $.fields.filter((f) => d[f]).length === $.fields.length
        )
      )

    dimensionCounts[field] = getDimensionCount(filtered, dimensions[field])
  })

  // apply all filters and update dimension counts for every dimension that
  // doesn't have a filter
  const allFilterFields = filters.map((field) => `${field}_filter`)
  data = data
    .params({ fields: allFilterFields })
    .filter(
      escape((d, $) => $.fields.filter((f) => d[f]).length === $.fields.length)
    )

  Object.values(dimensions)
    .filter(({ field }) => !(rawFilters[field] && rawFilters[field].size > 0))
    .forEach((dimension) => {
      dimensionCounts[dimension.field] = getDimensionCount(data, dimension)
    })

  return {
    data,
    dimensionCounts,
  }
}
