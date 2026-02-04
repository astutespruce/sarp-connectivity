import { browser } from '$app/environment'

export const hasGeolocation = browser && navigator && 'geolocation' in navigator

/**
 * URI encode object key:value pairs
 *
 * @param {Object} data
 */
export const encodeParams = (obj: object) =>
	Object.keys(obj)
		.map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(obj[key as keyof typeof obj])}`)
		.join('&')

export const saveToStorage = (key: string, data: unknown) => {
	if (!browser) return

	window.localStorage.setItem(key, JSON.stringify(data))
}

export const getFromStorage = (key: string) => {
	if (browser && typeof localStorage !== 'undefined') {
		const rawValue = localStorage.getItem(key)
		if (rawValue) {
			return JSON.parse(rawValue)
		}
	}
	return null
}
