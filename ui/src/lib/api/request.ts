import { fromArrow } from 'arquero'
import camelcaseKeys from 'camelcase-keys'
import { tableFromIPC } from '@uwdata/flechette'

import { API_HOST } from '$lib/env'
import { encodeParams } from '$lib/util/dom'
import { captureException } from '$lib/util/log'

export const fetchJSON = async (path: string) => {
	try {
		const response = await fetch(`${API_HOST}/${path}`, {
			method: 'GET',
			credentials: 'include'
		})

		if (response.status === 200) {
			return await camelcaseKeys(response.json())
		}

		try {
			const { detail = null, ...rest } = await response.json()

			return {
				error: detail,
				status: response.status,
				...rest
			}
		} catch (ex) {
			console.error('unhandled error parsing JSON from API', ex)
		}

		return {
			error: 'SERVER_ERROR',
			status: response.status
		}
	} catch (ex) {
		console.error('UNHANDLED_ERROR', ex)
		return {
			error: 'UNHANDLED_ERROR',
			status: 500
		}
	}
}

let jsonpCounter = 1

export const fetchJSONP = async (
	rootURL: string,
	params: object,
	jsonpCallback = 'jsonpCallback',
	requestTimeout = 60000
) => {
	const callbackName = `jsonpCallback${jsonpCounter}`
	jsonpCounter += 1
	const url = `${rootURL}?${encodeParams({ ...params, [jsonpCallback]: callbackName })}`

	return new Promise((resolve, reject) => {
		const script = document.createElement('script')
		script.src = url
		script.async = true
		script.addEventListener('error', (error) => {
			console.log('caught JSONP error')
			removeCallback()

			return reject(error)
		})

		const removeCallback = () => {
			window[callbackName] = undefined
			document.querySelector('head')?.removeChild(script)
			clearTimeout(timeout)
		}

		const timeout = setTimeout(() => {
			removeCallback()

			return reject(new Error('JSONP request timed out'))
		}, requestTimeout)

		window[callbackName] = (responseData) => {
			removeCallback()

			return resolve(responseData)
		}

		document.querySelector('head')?.appendChild(script)
	})
}

export const fetchFeather = async (url: string, options?: RequestInit, asTable = false) => {
	try {
		const response = await fetch(url, options)

		if (response.status !== 200) {
			throw new Error(`Failed request to ${url}: ${response.statusText}`)
		}

		// WARNING: flechette (1.1.0) tableFromIPC will break if called with an IPC
		// that batches with no rows; make sure that all responses from API use
		// .combine_chunks() to aggregate data before encoding to Feather if using
		// a selection of existing data
		const bytes = new Uint8Array(await response.arrayBuffer())
		const data = await tableFromIPC(bytes)

		return {
			data: asTable ? fromArrow(data) : data.toArray(),
			bounds: data.schema?.metadata?.get('bounds')
		}
	} catch (err) {
		captureException(err)

		return {
			error: err,
			data: null
		}
	}
}

export const postJSON = async (path: string, data: object) => {
	try {
		const response = await fetch(`${API_HOST}/${path}`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(data),
			credentials: 'include'
		})

		if (response.status === 200) {
			return await camelcaseKeys(response.json())
		}

		try {
			const { detail = null, ...rest } = await response.json()

			if (response.status === 422) {
				// indicates implementation error; passed invalid parameters to API
				console.error('IMPLEMENTATION ERROR: submitted incorrect data to API', detail)
			}

			return {
				error: detail,
				status: response.status,
				...rest
			}
		} catch (ex) {
			console.error('unhandled error from API', ex)
		}

		return {
			error: 'SERVER_ERROR',
			status: response.status
		}
	} catch (ex) {
		console.error('UNHANDLED_ERROR', ex)
		return {
			error: 'UNHANDLED_ERROR',
			status: 500
		}
	}
}
