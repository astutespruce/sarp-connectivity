import { browser } from '$app/environment'

// FIXME: remove, deprecated

// export const hasWindow = typeof window !== 'undefined' && window

// export const isUnsupported =
//   hasWindow &&
//   navigator !== undefined &&
//   (/MSIE 9/i.test(navigator.userAgent) ||
//     /MSIE 10/i.test(navigator.userAgent) ||
//     /Trident/i.test(navigator.userAgent))

// export const isDebug = hasWindow && process.env.NODE_ENV === 'development'

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
		return JSON.parse(localStorage.getItem(key) || '')
	}
	return null
}

/**
 * Extract query params into a key / value object
 * @param {Object} location - location object from Gatsby
 * @returns Object
 */
export const getQueryParams = (location: Location) => {
	if (!(location && browser)) return []

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
