export const groupBy = (records, groupField) =>
  records.reduce(
    (prev, record) => Object.assign(prev, { [record[groupField]]: record }),
    {}
  )

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
