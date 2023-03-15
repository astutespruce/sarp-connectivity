/* eslint-disable no-underscore-dangle */

import { op } from 'arquero'

import { reduceToObject } from 'util/data'

/**
 * Return an arquero table as an object of {<key>: <value>, ...}
 * @param {Object} table - arquero table
 * @param {String} keyCol - name of key column
 * @param {String} valueCol - name of value column
 * @returns Object
 */
export const columnsToObject = (table, keyCol, valueCol) =>
  table
    .array(valueCol)
    .reduce(
      (prev, value, i) =>
        Object.assign(prev, { [table.get(keyCol, i)]: value }),
      {}
    )

/**
 * Calculate the count for each value present in values for dimension;
 * ignores count for any value that is not in values.
 */
export const getDimensionCount = (table, dimension) => {
  const { field, isArray, values } = dimension

  // FIXME: this is not working for multi-value fields
  let grouped = table.groupby(field).rollup({ _count: (d) => op.sum(d._count) })

  // drop any values in data not in values list
  if (!isArray && values.length < grouped.numRows()) {
    grouped = grouped
      .params({ field, values })
      .filter((d, $) => op.includes($.values, d[$.field]))
  }

  return columnsToObject(grouped, field, '_count')
}

/**
 * Calculates the count by value for each dimension based on the current filters
 * @param {Object} table - arquero table
 * @param {Object} dimensions - object of dimensions
 */

export const countByDimension = (table, dimensions) =>
  Object.values(dimensions)
    .map((dimension) => ({
      field: dimension.field,
      total: getDimensionCount(table, dimension),
    }))
    .reduce(...reduceToObject('field', (d) => d.total))
