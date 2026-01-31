import type { Table } from 'arquero'

const getIntKeys = (obj: object) =>
	Object.keys(obj)
		.map((k) => parseInt(k, 10))
		.sort()

/**
 * Get sorted integer keys and labels for each entry in a keyed object
 * @param {Object} obj
 */
export const getEntries = (obj: object, filter = null) => {
	let values = getIntKeys(obj).sort((l, r) => (l < r ? -1 : 1))

	if (filter) {
		values = values.filter(filter)
	}

	return {
		values,
		labels: values.map((key) => obj[key as keyof typeof obj])
	}
}

// Only show diadromous filters if within 500 miles of coast
export const hasDiadromousData = (data: Table) =>
	data &&
	data.numRows() > 0 &&
	data
		.filter(
			(d) =>
				(d.downstreamoceanmilesclass > 0 && d.downstreamoceanmilesclass < 8) ||
				d.diadromoushabitat === 1
		)
		.numRows() > 0
