const getIntKeys = (obj) =>
  Object.keys(obj)
    .map((k) => parseInt(k, 10))
    .sort()

/**
 * Get sorted integer keys and labels for each entry in a keyed object
 * @param {Object} obj
 */
export const getEntries = (obj, filter = null) => {
  let values = getIntKeys(obj).sort((l, r) => (l < r ? -1 : 1))

  if (filter) {
    values = values.filter(filter)
  }

  return {
    values,
    labels: values.map((key) => obj[key]),
  }
}

// Only show diadromous filters if within 500 miles of coast
export const hasDiadromousData = (records) =>
  records &&
  records.filter(
    ({ downstreamoceanmilesclass }) =>
      downstreamoceanmilesclass > 0 && downstreamoceanmilesclass < 8
  ).length > 0
