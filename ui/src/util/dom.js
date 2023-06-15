export const hasWindow = typeof window !== 'undefined' && window

export const isUnsupported =
  hasWindow &&
  navigator !== undefined &&
  (/MSIE 9/i.test(navigator.userAgent) ||
    /MSIE 10/i.test(navigator.userAgent) ||
    /Trident/i.test(navigator.userAgent))

export const isDebug = hasWindow && process.env.NODE_ENV === 'development'

export const hasGeolocation =
  hasWindow && navigator && 'geolocation' in navigator

/**
 * URI encode object key:value pairs
 *
 * @param {Object} data
 */
export const encodeParams = (obj) =>
  Object.keys(obj)
    .map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(obj[key])}`)
    .join('&')

export const saveToStorage = (key, data) => {
  if (!hasWindow) return

  window.localStorage.setItem(key, JSON.stringify(data))
}

export const getFromStorage = (key) => {
  if (!hasWindow) return

  JSON.parse(window.localStorage.getItem(key))
}

/**
 * Extract query params into a key / value object
 * @param {Object} location - location object from Gatsby
 * @returns Object
 */
export const getQueryParams = (location) => {
  if (!(location && hasWindow)) return []

  return [...new window.URLSearchParams(location.search).entries()].reduce(
    (prev, [key, value]) => Object.assign(prev, { [key]: value }),
    {}
  )
}
