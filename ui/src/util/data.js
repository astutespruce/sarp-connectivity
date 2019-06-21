export const groupBy = (records, groupField) =>
  records.reduce(
    (prev, record) => Object.assign(prev, { [record[groupField]]: record }),
    {}
  )
