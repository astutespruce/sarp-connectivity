import { addFunction, op } from 'arquero'

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
      // .params({ field })
      // .derive({ [field]: (d, $) => op.split(d[$.field], ',') })
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

export const applyFilter = (data, dimension, filterValues) => {
  const { field, isArray } = dimension
  let filteredData = data

  if (isArray) {
    filteredData = data
      .params({ field, values: [...filterValues] })
      .filter((d, $) => op.hasAny($.values, d[$.field]))
  } else {
    filteredData = data
      .params({ field, values: filterValues })
      .filter((d, $) => op.has($.values, d[$.field]))
  }

  return filteredData
}
