export const isEmptyString = (value) =>
  value === null ||
  value === undefined ||
  value === '' ||
  value === '"' ||
  value === 'null'

export default { isEmptyString }
