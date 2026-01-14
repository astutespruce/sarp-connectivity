import camelcaseKeys from 'camelcase-keys'
import { tableFromIPC } from '@uwdata/flechette'

import { API_HOST } from '$lib/env'
import { captureException } from '$lib/util/log'
import { extractYearRemovedStats } from '$lib/util/stats'

export const fetchUnitDetails = async (layer: string, id: string | number) => {
	const url = `${API_HOST}/api/v1/internal/units/${layer}/details/${id}`

	try {
		const response = await fetch(url)
		if (response.status !== 200) {
			throw new Error(`Failed request to ${url}: ${response.statusText}`)
		}

		const rawData = await response.json()

		const { removedDamsByYear, removedSmallBarriersByYear, bbox, ...data } = camelcaseKeys(rawData)

		const removedBarriersByYear = extractYearRemovedStats(
			removedDamsByYear,
			removedSmallBarriersByYear
		)

		return {
			...data,
			bbox: bbox ? bbox.split(',').map(parseFloat) : null,
			removedBarriersByYear
		}
	} catch (err) {
		captureException(err)

		throw err
	}
}

export const searchUnits = async (layers: string[], query: string) => {
	const url = `${API_HOST}/api/v1/internal/units/search?layer=${layers.join(',')}&query=${query}`

	try {
		const response = await fetch(url)
		if (response.status !== 200) {
			throw new Error(`Failed request to ${url}: ${response.statusText}`)
		}

		const bytes = new Uint8Array(await response.arrayBuffer())
		const data = await tableFromIPC(bytes)

		return {
			results: data.toArray().map((row) => camelcaseKeys(row)),
			remaining: parseInt(data.schema?.metadata?.get('count') || '0', 10) - data.numRows
		}
	} catch (err) {
		captureException(err)

		throw err
	}
}

export const fetchUnitList = async (layer, ids) => {
	const url = `${API_HOST}/api/v1/internal/units/${layer}/list?id=${ids.join(',')}`

	try {
		const response = await fetch(url)
		if (response.status !== 200) {
			throw new Error(`Failed request to ${url}: ${response.statusText}`)
		}

		const bytes = new Uint8Array(await response.arrayBuffer())
		const data = await tableFromIPC(bytes)

		return data.toArray().map((row) => toCamelCaseFields(row))
	} catch (err) {
		captureException(err)

		throw err
	}
}
