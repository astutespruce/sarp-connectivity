/* eslint-disable no-underscore-dangle */

import { reduceToObject } from 'util/data'

/**
 * Calculates the total COUNT
 * for all records that meet the current filters.
 *
 * @param {Object} crossfilter - Crossfilter object
 */
export const getFilteredCount = (crossfilter) =>
  // aggregate all counts
  crossfilter
    .groupAll()
    .reduceSum((d) => d._count)
    .value()

/**
 * Calculates the count by value for each dimension based on the current filters
 * @param {Object} dimensions
 */
export const countByDimension = (dimensions) =>
  Object.values(dimensions)
    .filter(({ config: { internal } }) => !internal)
    .map(({ group, config: { field } }) =>
      // reduce [{key:..., value:...},...] for each entry into {key: value, ...}
      ({
        field,
        total: group()
          .reduceSum((d) => d._count)
          .all()
          .reduce(...reduceToObject('key', (d) => d.value)),
      })
    )
    .reduce(...reduceToObject('field', (d) => d.total))
