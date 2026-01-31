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

export const saveToStorage = (key: string, data: any) => {
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

/**
 * Extract URL query params into a key / value object
 * @returns Object
 */
export const getQueryParams = () => {
	if (!browser) return []

	return [...new window.URLSearchParams(location.search).entries()].reduce(
		(prev, [key, value]) => Object.assign(prev, { [key]: value }),
		{}
	)
}

/**
 * Dynamically load an image using require()
 * @param {String} filename
 * @returns resolved image
 */
// FIXME: deprecated
// export const dynamicallyLoadImage = (filename:string) => {
// 	try {
//     alert('DEPRECATED: remove dynamicallyLoadImage')
// 		return require(`images/${filename}`).default
// 	} catch (err) {
// 		console.error(err)
// 	}
// 	return null
// }
