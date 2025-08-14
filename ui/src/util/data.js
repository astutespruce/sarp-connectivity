import { dequal } from 'dequal'

import { toCamelCase } from 'util/format'

/**
 * Calculate the sum of an array of numbers
 * @param {Array} values - array of numbers
 */
export const sum = (values) => values.reduce((prev, value) => prev + value, 0)

export const groupBy = (records, groupField) =>
  records.reduce(
    (prev, record) => Object.assign(prev, { [record[groupField]]: record }),
    {}
  )

/**
 * Count records within each group.
 * Returns object where keys are each unique value of groupField.
 * NOTE: if the sum is 0, the key is absent from the resulting Map.
 *
 * @param {Array} records - Array of objects
 * @param {String} groupField - field to group by
 */
export const countBy = (records, groupField) =>
  records.reduce((prev, record) => {
    const group = record[groupField]
    /* eslint-disable-next-line no-param-reassign */
    prev[group] = (prev[group] || 0) + 1
    return prev
  }, {})

/**
 * Creates a reducer function to pass on to a .reduce() operation.
 * If valueGetter is present, it will be executed on each object
 * in the array this is being called against (except key field).  Otherwise,
 * it returns a new object with just the remaining non-key fields and values.
 *
 * @param {name of field to set as key} keyField
 * @param {*} valueGetter - OPTIONAL: function to extract value from remaining
 * (non-key) values in each object in array
 */
export const reduceToObject = (keyField, valueGetter) => [
  (prev, { [keyField]: key, ...rest }) =>
    Object.assign(prev, { [key]: valueGetter ? valueGetter(rest) : rest }),
  {},
]

/**
 * Convert snake_case fields to camelCase fields
 * @param {Object} obj
 * @returns object
 */
export const toCamelCaseFields = (obj) =>
  Object.entries(obj).reduce(
    (prev, [key, value]) => Object.assign(prev, { [toCamelCase(key)]: value }),
    {}
  )

/**
 * Split an array into elements that meet the condition and elements that don't.
 * @param {Array} arr - input array
 * @param {Function} conditionFunc - if true, elements are added to first array
 * otherwise they are added to second array
 */
export const splitArray = (arr, conditionFunc) => {
  const out = [[], []]
  arr.forEach((elem) => {
    if (conditionFunc(elem)) {
      out[0].push(elem)
    } else {
      out[1].push(elem)
    }
  })

  return out
}

/**
 * Unpack a previously bit-packed value.
 *
 * Offset is added back to value.
 *
 * @param {Number} packed - bit-packed value
 * @param {Object} fieldBits - array of {field: <field>, bits: <num bits>, offset: <offset>} per field
 * @returns Object of {field: value, ...}
 */
export const unpackBits = (packed, fieldBits) => {
  const out = {}

  let sumBits = 0
  fieldBits.forEach(({ field, bits, value_shift = 0 }) => {
    /* eslint-disable no-bitwise */
    out[field] = ((packed >> sumBits) & (2 ** bits - 1)) + value_shift
    sumBits += bits
  })

  return out
}

/**
 * Tests if the left and right objects have the same values for props
 *
 * @param {Object} left
 * @param {Object} right
 * @param {Array} props - list of prop names to test for equality
 */
export const isEqual = (left, right, props) =>
  props.filter((p) => left && right && dequal(left[p], right[p])).length ===
  props.length

/** Serialize a key, which may be a nested object, so that it can
 * be used as a query key for tanstack/react-query
 *
 * @param {Object | String} key - query key
 * @returns String - serialized query key
 */
export const serializeQueryKey = (key) =>
  JSON.stringify(key, (_, value) => (value instanceof Set ? [...value] : value))
