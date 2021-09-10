import { toCamelCase } from 'util/format'

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
