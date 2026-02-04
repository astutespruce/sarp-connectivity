export const isEmptyString = (value: string | null | undefined) =>
	value === null || value === undefined || value === '' || value === '"' || value === 'null'

export default { isEmptyString }
