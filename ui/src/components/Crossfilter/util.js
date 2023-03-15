import { op } from 'arquero'

import { reduceToObject } from 'util/data'

/**
 * Calculate the count for each value present in values for dimension;
 * ignores count for any value that is not in values.
 */
export const getDimensionCount = (table, dimension) => {
  const { field, isArray, values } = dimension

  // FIXME: this is not working for multi-value fields
  let grouped = table.groupby(field).rollup({ _count: (d) => op.sum(d._count) })

  if (isArray) {
    // split by commas into separate rows, then regroup
    grouped = grouped
      .params({ field })
      .derive({ [field]: (d, $) => op.split(d[$.field], ',') })
      .unroll(field)
      .groupby(field)
      .rollup({ _count: (d) => op.sum(d._count) })
  }

  // TODO: drop any values in data not in values list
  // if (!isArray && values.length < grouped.numRows()) {
  // grouped = grouped
  //   .params({ field, values })
  //   .filter((d, $) => op.includes($.values, d[$.field]))
  // }

  return grouped
    .derive({ row: op.row_object() })
    .array('row')
    .reduce(...reduceToObject(field, (d) => d._count))
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
