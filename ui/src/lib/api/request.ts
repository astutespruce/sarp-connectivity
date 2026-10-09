import { tableFromIPC } from '@uwdata/flechette'
import { fromArrow } from 'arquero'

import { encodeParams } from '#lib/util/dom.js'
import { captureException } from '#lib/util/log.js'

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
			// @ts-expect-error callbackName is valid
			window[callbackName] = undefined
			document.querySelector('head')?.removeChild(script)
			clearTimeout(timeout)
		}

		const timeout = setTimeout(() => {
			removeCallback()

			return reject(new Error('JSONP request timed out'))
		}, requestTimeout)

		// @ts-expect-error callbackName is valid, return is any
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
			// @ts-expect-error tableFromIPC returns valid input for fromArrow
			data: asTable ? fromArrow(data) : data.toArray(),
			bounds: data.schema?.metadata?.get('bounds')
		}
	} catch (err) {
		captureException(err as Error | string)

		return {
			error: err,
			data: null
		}
	}
}
