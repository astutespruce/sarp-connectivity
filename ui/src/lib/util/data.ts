import { dequal } from 'dequal'

/**
 * Calculate the sum of an array of numbers
 * @param {Array} values - array of numbers
 */
export const sum = (values: number[]) => values.reduce((prev, value) => prev + value, 0)

/**
 * Count records within each group.
 * Returns object where keys are each unique value of groupField.
 * NOTE: if the sum is 0, the key is absent from the resulting Map.
 *
 * @param {Array} records - Array of objects
 * @param {String} groupField - field to group by
 */
export const countBy = (records: object[], groupField: string) =>
	records.reduce((prev: Record<string, number>, record) => {
		const group = record[groupField as keyof typeof record]
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
export const reduceToObject = (
	keyField: string,
	valueGetter: (params: object) => number | string
) => [
	(prev: object, { [keyField]: key, ...rest }) =>
		Object.assign(prev, { [key]: valueGetter ? valueGetter(rest) : rest }),
	{}
]

/**
 * Split an array into elements that meet the condition and elements that don't.
 * @param {Array} arr - input array
 * @param {Function} conditionFunc - if true, elements are added to first array
 * otherwise they are added to second array
 */
export const splitArray = (arr: unknown[], conditionFunc: (params: unknown) => boolean) => {
	const out: unknown[][] = [[], []]
	arr.forEach((elem) => {
		if (conditionFunc(elem)) {
			out[0].push(elem)
		} else {
			out[1].push(elem)
		}
	})

	return out
}

type FieldBitsSpec = {
	field: string
	bits: number
	value_shift?: number
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
export const unpackBits = (packed: number, fieldBits: FieldBitsSpec[]) => {
	const out: Record<string, number> = {}

	let sumBits = 0
	fieldBits.forEach(({ field, bits, value_shift = 0 }: FieldBitsSpec) => {
		out[field] = ((packed >> sumBits) & (2 ** bits - 1)) + value_shift
		sumBits += bits
	})

	return out
}

/**
 * Tests if the left and right objects have the same values for props, without
 * doing a deep comparison of the full object
 *
 * @param {Object} left
 * @param {Object} right
 * @param {Array} props - list of prop names to test for equality
 */
export const isEqual = (left: object | null, right: object | null, props: string[]) =>
	props.filter(
		(p) => left && right && dequal(left[p as keyof typeof left], right[p as keyof typeof right])
	).length === props.length
