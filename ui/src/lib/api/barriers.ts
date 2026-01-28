import { error as handleError } from '@sveltejs/kit'
import { tableFromIPC } from '@uwdata/flechette'

import { API_HOST } from '$lib/env'
import { SPECIES_HABITAT_FIELDS, barrierNameWhenUnknown } from '$lib/config/constants'
import { captureException } from '$lib/util/log'
import type { SummaryUnits, Filters } from '$lib/config/types'
import { isEmptyString } from '$lib/util/string'

import { pollJob } from './job'
import type { ProgressCallback } from './job'
import { fetchFeather } from './request'

type APIQueryParams = {
	summaryUnits: SummaryUnits
	filters: Filters
	includeUnranked?: boolean | null
	sort?: string | null
	customRank?: boolean
}

/**
 * Extract habitat fields into a data structure per species
 */
const extractHabitat = (data: object) =>
	Object.entries(SPECIES_HABITAT_FIELDS)
		.map(([id, { label, source, limit }]) => ({
			id,
			label,
			source,
			limit,
			upstreammiles: data[`${id}upstreammiles` as keyof typeof data] || 0,
			downstreammiles: data[`free${id}downstreammiles` as keyof typeof data] || 0
		}))
		.filter(({ upstreammiles, downstreammiles }) => upstreammiles + downstreammiles > 0)

/**
 * Converts units and filters into query parameters for API requests
 */
const apiQueryParams = ({
	summaryUnits = {},
	filters = {},
	includeUnranked,
	sort,
	customRank
}: APIQueryParams) => {
	let query = Object.entries(summaryUnits)
		.map(([key, values]) => `${key}=${values.join(',')}`)
		.join('&')

	const filterValues = Object.entries(filters).filter(([, v]) => v.size > 0)
	if (filterValues.length > 0) {
		query += `&${filterValues.map(([k, v]) => `${k}=${Array.from(v).join(',')}`).join('&')}`
	}

	if (includeUnranked) {
		query += '&include_unranked=1'
	}
	if (customRank) {
		query += '&custom_rank=1'
	}
	if (sort) {
		query += `&sort=${sort}`
	}

	return query
}

/**
 * Fetch and parse Feather data from API for dams or small barriers
 */
export const fetchBarrierInfo = async (barrierType: string, summaryUnits) => {
	const url = `${API_HOST}/api/v1/internal/${barrierType}/query?${apiQueryParams({
		summaryUnits
	})}`

	return fetchFeather(url, undefined, true)
}

/**
 * Fetch and parse Feather data from API for dams or small barriers
 */
export const fetchBarrierRanks = async (barrierType, summaryUnits, filters) => {
	const url = `${API_HOST}/api/v1/internal/${barrierType}/rank?${apiQueryParams({
		summaryUnits,
		filters
	})}`

	// Unpack bit-packed tier scenarios
	const { data: packedTiers, bounds, error } = await fetchFeather(url, undefined)
	if (error) {
		// data needs to be non-null or map breaks
		return { error, bounds: null, data: [] }
	}

	const data = packedTiers.map(({ id, full, perennial, mainstem }) => ({
		id,
		// ...unpackBits(tiers, TIER_PACK_BITS),
		...unpackBits(
			full,
			TIER_FIELDS.map((field) => ({ field, ...TIER_PACK_INFO }))
		),
		...unpackBits(
			perennial,
			TIER_FIELDS.map((field) => ({ field: `p${field}`, ...TIER_PACK_INFO }))
		),
		...unpackBits(
			mainstem,
			TIER_FIELDS.map((field) => ({ field: `m${field}`, ...TIER_PACK_INFO }))
		)
	}))

	return {
		bounds,
		data
	}
}

export const fetchBarrierDetails = async (networkType: string, sarpid: string) => {
	const url = `${API_HOST}/api/v1/internal/${networkType}/details/${sarpid}`

	const response = await fetch(url)
	if (response.status === 404) {
		return null // not found
	}

	const data = await response.json()

	// backfill empty name
	if (isEmptyString(data.name)) {
		data.name =
			barrierNameWhenUnknown[data.barriertype as keyof typeof barrierNameWhenUnknown] ||
			'Unknown name'
	}

	if (data.hasnetwork) {
		data.habitat = extractHabitat(data)
	}

	return data
}

export const searchBarriers = async (query: string) => {
	const url = `${API_HOST}/api/v1/internal/barriers/search?query=${query}`

	try {
		const response = await fetch(url)
		if (response.status !== 200) {
			throw new Error(`Failed request to ${url}: ${response.statusText}`)
		}

		const bytes = new Uint8Array(await response.arrayBuffer())
		const data = await tableFromIPC(bytes)

		return {
			results: data.toArray(),
			remaining: parseInt(data.schema!.metadata!.get('count')!, 10) - data.numRows
		}
	} catch (err) {
		captureException(err as Error | string)

		throw err
	}
}

type GetDownloadURLParams = APIQueryParams & {
	barrierType: string
}

type GetDownloadURL = (
	params: GetDownloadURLParams,
	onProgress: ProgressCallback | null
) => Promise<{
	error?: string | null
	url?: string | null
}>

export const getDownloadURL: GetDownloadURL = async (
	{
		barrierType,
		summaryUnits,
		filters,
		includeUnranked = null,
		sort = null,
		customRank = false
	}: GetDownloadURLParams,
	onProgress = null
) => {
	const params = {
		summaryUnits,
		filters,
		includeUnranked: includeUnranked !== null ? includeUnranked : undefined,
		sort: sort !== null ? sort : undefined,
		customRank: customRank || undefined
	}

	if (onProgress) {
		onProgress({
			status: 'queued',
			inProgress: true,
			progress: 0
		})
	}

	const response = await fetch(
		`${API_HOST}/api/v1/internal/${barrierType}/csv?${apiQueryParams(params)}`,
		{
			method: 'POST'
		}
	)

	if (response.status !== 200) {
		let error = await response.text()
		try {
			const { detail } = JSON.parse(error)
			error = detail
		} catch {
			// don't do anything here
		}

		error = error || 'unhandled error'

		if (response.status === 500) {
			// this happens if redis is offline on the server
			captureException(`server error for download request: ${error}`)
		} else {
			captureException(`unhandled download request error: ${error}`)
		}
		return {
			error
		}
	}

	const { status, job, path } = await response.json()

	// created download immediately, no need to poll job
	if (status === 'success' && path) {
		if (onProgress) {
			onProgress({
				status,
				inProgress: false,
				progress: 100
			})
		}

		return { url: `${API_HOST}${path}` }
	}

	const result = await pollJob(job, onProgress)

	return result
}
