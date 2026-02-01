import { v4 as uuid } from 'uuid'

import { MAPBOX_TOKEN } from '$lib/env'
import { getFromStorage, saveToStorage } from '$lib/util/dom'

import { mapConfig as config } from '../config'

type MapboxPlace = {
	mapbox_id: string
	name: string
	name_preferred?: string
	address?: string
	full_address?: string
	place_formatted?: string
}

const apiURL = 'https://api.mapbox.com/search/searchbox/v1'

// mapbox limits requests to world domain, clip to -180
const bounds = [...config.bounds]
bounds[0] = Math.max(bounds[0], -180)

const types = ['region', 'place', 'poi', 'address']
const numResults = 5

let sessionToken = getFromStorage('mapbox.search.session_token')
if (!sessionToken) {
	sessionToken = uuid()
	saveToStorage('mapbox.search.session_token', sessionToken)
}

export const searchPlaces = (query: string) => {
	const controller = new AbortController()

	const url = `${apiURL}/suggest?language=en&bbox=${bounds.toString()}&types=${types.toString()}&limit=${numResults}&access_token=${MAPBOX_TOKEN}&session_token=${sessionToken}&q=${encodeURI(
		query
	)}`

	const promise = fetch(url, {
		method: 'GET',
		mode: 'cors',
		signal: controller.signal
	})
		.then((response) => {
			if (!response.ok) {
				return Promise.reject(new Error(response.statusText))
			}

			return response
				.json()
				.catch((error) => Promise.reject(new Error('Invalid JSON: ', error.message)))
		})
		.then(({ suggestions = [] }) =>
			suggestions.map(
				({
					mapbox_id: id,
					name,
					name_preferred: altName,
					address: rawAddress,
					full_address: fullAddress,
					place_formatted: placeFormatted
				}: MapboxPlace) => {
					let address = fullAddress || placeFormatted
					if (placeFormatted && rawAddress && rawAddress === fullAddress) {
						address = `${fullAddress}, ${placeFormatted}`
					}
					return {
						id,
						name: altName || name,
						address
					}
				}
			)
		)

		.catch((error) => Promise.reject(new Error(error.message)))

	promise.cancel = () => {
		controller.abort()

		// make sure to resolve promise or it raises an error on cancel
		return Promise.resolve()
	}

	return promise
}

export const getPlace = async (id: string) => {
	const url = `${apiURL}/retrieve/${id}?access_token=${MAPBOX_TOKEN}&session_token=${sessionToken}`

	const response = await fetch(url, {
		method: 'GET',
		mode: 'cors'
	})

	if (!response.ok) {
		throw new Error(`Could not fetch Mapbox place: ${id}`)
	}

	const { features = [] } = await response.json()
	if (features.length === 0) {
		return {}
	}
	const [
		{
			geometry: {
				coordinates: [longitude, latitude]
			}
		}
	] = features

	return { latitude, longitude }
}
