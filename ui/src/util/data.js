export const groupBy = (records, groupField) =>
  records.reduce(
    (prev, record) => Object.assign(prev, { [record[groupField]]: record }),
    {}
  )

/**
 * Filter an object to only those entries that meet the predicate function.
 * Returns a new object.
 *
 * From: https://stackoverflow.com/a/37616104
 * @param {Object} obj
 * @param {function} predicate - function that determines if entry should be kept
 */
export const filterObject = (obj, predicate) => {
  const selected = Object.keys(obj)
    .filter(key => predicate(obj[key]))
    .map(key => ({ [key]: obj[key] }))

  return selected.length > 0 ? Object.assign(...selected) : {}
}

/**
 * Sum values in array.
 * @param {Array} values
 */
export const sum = values => values.reduce((prev, value) => prev + value, 0)

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
