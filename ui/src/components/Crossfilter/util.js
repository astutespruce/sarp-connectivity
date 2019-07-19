import { reduceToObject } from 'util/data'

/**
 * Calculates the total COUNT
 * for all records that meet the current filters.
 *
 * @param {Object} crossfilter - Crossfilter object
 */
export const getFilteredCount = crossfilter =>
  crossfilter
    .groupAll()
    .reduceCount()
    .value()

/**
 * Calculates the count by value for each dimension based on the current filters
 * @param {Object} dimensions
 */
export const countByDimension = dimensions =>
  Object.values(dimensions)
    .filter(({ config: { internal } }) => !internal)
    .map(({ group, config: { field } }) => {
      // reduce [{key:..., value:...},...] for each entry into {key: value, ...}
      return {
        field,
        total: group()
          .all()
          .reduce(...reduceToObject('key', d => d.value)),
      }
    })
    .reduce(...reduceToObject('field', d => d.total))

//         case 'id': {
//           sums = group()
//             .reduce(...groupReducer(valueField))
//             .all()
//             // only keep values > 0, and retain count of entries instead of values
//             .map(({ key, value }) => ({
//               key,
//               value: Object.values(value).filter(v => v > 0).length,
//             }))
//           break
//         }

/**
 * Aggregate values within each dimension.
 * If valueField is provided, aggregate will return the SUM, otherwise COUNT.
 * Excludes any dimension for which `internal` property is `true`.
 *
 * @param {Object} dimensions - object containing crossfilter dimensions.
 * @param {String} valueField - name of value field within record.
 *
 */

// export const aggregateByDimension = (dimensions, valueField = null) =>
//   Object.values(dimensions)
//     .filter(({ config: { internal } }) => !internal)
//     .map(({ group, config: { field } }) => {
//       let sums = null

//       switch (valueField) {
//         case null: {
//           sums = group().all()
//           break
//         }
//         case 'id': {
//           sums = group()
//             .reduce(...groupReducer(valueField))
//             .all()
//             // only keep values > 0, and retain count of entries instead of values
//             .map(({ key, value }) => ({
//               key,
//               value: Object.values(value).filter(v => v > 0).length,
//             }))
//           break
//         }
//         case 'species': {
//           sums = group()
//             // only retain entries for species that have nonzero detectionNights
//             .reduce(
//               ...filteredGroupReducer(valueField, d => d.detectionNights > 0)
//             )
//             .all()
//             // only keep values > 0, and retain count of entries instead of values
//             .map(({ key, value }) => ({
//               key,
//               value: Object.values(value).filter(v => v > 0).length,
//             }))
//           break
//         }
//         default: {
//           sums = group()
//             .reduceSum(d => d[valueField])
//             .all()
//           break
//         }
//       }

//       // reduce [{key:..., value:...},...] for each entry into {key: value, ...}
//       return {
//         field,
//         total: sums.reduce(...reduceToObject('key', d => d.value)),
//       }
//     })
//     .reduce(...reduceToObject('field', d => d.total))
