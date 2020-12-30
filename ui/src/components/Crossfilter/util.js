import { reduceToObject } from 'util/data'

/**
 * Calculates the total COUNT
 * for all records that meet the current filters.
 *
 * @param {Object} crossfilter - Crossfilter object
 */
export const getFilteredCount = (crossfilter) =>
  crossfilter.groupAll().reduceCount().value()

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
          .all()
          .reduce(...reduceToObject('key', (d) => d.value)),
      })
    )
    .reduce(...reduceToObject('field', (d) => d.total))
