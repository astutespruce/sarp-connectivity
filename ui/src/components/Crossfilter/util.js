import { Map, Set } from 'immutable'

import { sum } from 'util/data'

// Custom reducer to get stats for all filtered records EXCEPT
// filter by timestep

/**
 * Create a triad of add, remove, init reducers to use with the
 * `.groupAll().reduce(...<thisResult>)` function on a dimension.
 * The result of using this is an ImmutableJS Map Object where
 * the key is the id value of each record, and the value is the non-zero
 * total of all values of valueField for those records that meet all
 * OTHER filters than the current dimension.
 *
 * Note: all zero values are removed.
 * IMPORTANT: since this is applied to a dimension, the filters against
 * that dimension ARE NOT USED.
 * Also note: this DOES NOT work where valueField === 'id'
 *
 * @param {String} valueField - name of value field
 */
const valueByIDReducer = valueField => [
  (prev, d) => {
    return prev.update(
      d.get('id'),
      0,
      prevCount => prevCount + d.get(valueField)
    )
  },
  (prev, d) => {
    const id = d.get('id')
    const total = prev.get(id, 0) - d.get(valueField)
    if (total > 0) {
      return prev.set(id, total)
    }
    // remove zero entries
    return prev.remove(id)
  },
  () => Map(),
]

/**
 * reducer functions to group by unique ID.  Returns a set of IDS.
 * call this as `.reduce(...idReducer)` and then unpack the results.
 *
 * For total:
 * `crossfilter.groupAll().reduce(...idReducer).value().size`
 *
 * By dimension:
 * `dimensions.timestep.group().reduce(...idReducer).all().map(d => [d.key, d.value.size])`
 */

const idReducer = [
  // add
  (prev, d) => {
    return prev.update(d.get('id'), 0, prevCount => prevCount + 1)
  },
  // remove
  (prev, d) => {
    const id = d.get('id')
    const prevCount = prev.get(id, 0)
    if (prevCount > 1) {
      return prev.set(id, prevCount - 1)
    }
    // remove due to insufficient count
    return prev.remove(id)
  },
  // init
  () => Map(),
]

/**
 * Calculates the total COUNT (if valueField is absent) or total SUM (if valueField provided)
 * of ALL records.
 * Note: id is a special case, this returns count of unique id
 *
 * @param {Object} crossfilter - Crossfilter object
 * @param {String} valueField - name of the value field within record.
 */
export const getRawTotal = (crossfilter, valueField) => {
  if (!valueField) {
    return crossfilter.size()
  }
  const values = crossfilter.all().map(d => d.get(valueField))
  if (valueField === 'id') {
    return Set(values).size
  }
  return sum(values)
}

/**
 * Calculates the total COUNT (if valueField is absent) or total SUM (if valueField provided)
 * for all records that meet the current filters.
 * Note: id is a special case, this returns count of unique id
 *
 * @param {Object} crossfilter - Crossfilter object
 * @param {String} valueField - name of value field within record.
 */
export const getFilteredTotal = ({ groupAll }, valueField) => {
  if (!valueField) {
    return groupAll().value()
  }
  // id is a special case, return count of unique IDs
  if (valueField === 'id') {
    return groupAll()
      .reduce(...idReducer)
      .value().size
  }
  return groupAll()
    .reduceSum(d => d.get(valueField))
    .value()
}

/**
 * COUNT(valueField) by dimension.
 * Excludes any dimension for which `aggregate` property is `false`.
 * Note: records in crossfilter are ImmutableJS Map objects.
 *
 * @param {Object} dimensions - object containing crossfilter dimensions.
 *
 */
export const countByDimension = dimensions => {
  return Map(
    Object.values(dimensions)
      .filter(({ config: { aggregate = true } }) => aggregate)
      .map(({ group, config: { field } }) => {
        // Convert the array of key:count returned by crossfilter to a Map
        const counts = Map(
          group()
            .all()
            .map(d => Object.values(d))
        )
        return [field, counts]
      })
  )
}

/**
 * SUM(valueField) by dimension
 * Excludes any dimension for which `aggregate` property is `false`.
 * Note: records in crossfilter are ImmutableJS Map objects.
 *
 * @param {Object} dimensions - object containing crossfilter dimensions.
 * @param {String} valueField - name of value field within record.
 *
 */
export const sumByDimension = (dimensions, valueField) => {
  return Map(
    Object.values(dimensions)
      .filter(({ config: { aggregate = true } }) => aggregate)
      .map(({ group, config: { field } }) => {
        const sums = Map(
          group()
            .reduceSum(d => d.get(valueField))
            .all()
            .map(d => Object.values(d))
        )
        return [field, sums]
      })
  )
}

/**
 * Aggregate values within each dimension.
 * If valueField is provided, aggregate will return the SUM, otherwise COUNT.
 * Excludes any dimension for which `internal` property is `true`.
 * Note: records in crossfilter are ImmutableJS Map objects.
 *
 * @param {Object} dimensions - object containing crossfilter dimensions.
 * @param {String} valueField - name of value field within record.
 *
 */
export const aggregateByDimension = (dimensions, valueField) => {
  return Map(
    Object.values(dimensions)
      // .filter(({ config: { aggregate = true } }) => aggregate)
      .filter(({ config: { internal } }) => !internal)
      .map(({ group, config: { field } }) => {
        let sums = null

        if (!valueField) {
          sums = group()
            .all()
            .map(d => Object.values(d))
        } else if (valueField === 'id') {
          sums = group()
            .reduce(...idReducer)
            .all()
            .map(d => [d.key, d.value.size])
        } else {
          sums = group()
            .reduceSum(d => d.get(valueField))
            .all()
            .map(d => Object.values(d))
        }
        return [field, Map(sums)]
      })
  )
}


/**
 * Aggregate values by id field within each dimension.
 * Aggregate will return the SUM by valueField.
 * Excludes any dimension for which `aggregateById` property is `false`.
 * Note: records in crossfilter are ImmutableJS Map objects.
 *
 * @param {Object} dimensions - object containing crossfilter dimensions.
 * @param {String} valueField - name of value field within record. 
 *
 */
export const aggregateDimensionById = (dimensions, valueField) => {
  return Map(
    Object.values(dimensions)
      .filter(({ config: { aggregateById } }) => aggregateById)
      .map(({ groupAll, config: { field } }) => {
        return [
          field,
          groupAll()
            .reduce(...valueByIDReducer(valueField))
            .value(),
        ]
      })
  )
}
