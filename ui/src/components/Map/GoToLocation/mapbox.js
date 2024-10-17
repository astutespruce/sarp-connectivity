import { v4 as uuid } from 'uuid'
import { useQuery } from '@tanstack/react-query'

import { getFromStorage, saveToStorage } from 'util/dom'

import { siteMetadata } from '../../../../gatsby-config'
import { mapConfig as config } from '../config'

const { mapboxToken } = siteMetadata

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

export const searchPlaces = (query) => {
  const controller = new AbortController()

  const url = `${apiURL}/suggest?language=en&bbox=${bounds.toString()}&types=${types.toString()}&limit=${numResults}&access_token=${mapboxToken}&session_token=${sessionToken}&q=${encodeURI(
    query
  )}`

  const promise = fetch(url, {
    method: 'GET',
    mode: 'cors',
    signal: controller.signal,
  })
    .then((response) => {
      if (!response.ok) {
        return Promise.reject(new Error(response.statusText))
      }

      return response
        .json()
        .catch((error) =>
          Promise.reject(new Error('Invalid JSON: ', error.message))
        )
    })
    .then(({ suggestions = [] }) =>
      suggestions.map(
        ({
          mapbox_id: id,
          name,
          name_preferred: altName,
          address: rawAddress,
          full_address: fullAddress,
          place_formatted: placeFormatted,
        }) => {
          let address = fullAddress || placeFormatted
          if (placeFormatted && rawAddress && rawAddress === fullAddress) {
            address = `${fullAddress}, ${placeFormatted}`
          }
          return {
            id,
            name: altName || name,
            address,
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

export const getPlace = (id) => {
  const controller = new AbortController()

  const url = `${apiURL}/retrieve/${id}?access_token=${mapboxToken}&session_token=${sessionToken}`

  const promise = fetch(url, {
    method: 'GET',
    mode: 'cors',
    signal: controller.signal,
  })
    .then((response) => {
      if (!response.ok) {
        return Promise.reject(new Error(response.statusText))
      }

      return response
        .json()
        .catch((error) =>
          Promise.reject(new Error('Invalid JSON: ', error.message))
        )
    })
    .then(({ features = [] }) => {
      if (features.length === 0) {
        return null
      }

      const [
        {
          geometry: {
            coordinates: [longitude, latitude],
          },
        },
      ] = features

      return {
        longitude,
        latitude,
      }
    })

    .catch((error) => Promise.reject(new Error(error.message)))

  promise.cancel = () => {
    controller.abort()

    // make sure to resolve promise or it raises an error on cancel
    return Promise.resolve()
  }

  return promise
}

const useSearchSuggestions = (query) => {
  const {
    isLoading,
    error,
    data: results = [],
  } = useQuery({
    queryKey: ['searchMapbox', query],
    queryFn: () => {
      if (!query) {
        return null
      }

      return searchPlaces(query)
    },

    enabled: !!query && query.length >= 3,
    staleTime: 60 * 60 * 1000, // 60 minutes
    // staleTime: 1, // use then reload to force refresh of underlying data during dev
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  // Just log the error, there isn't much we can show the user here
  if (error) {
    // eslint-disable-next-line no-console
    console.error('ERROR loading search API results', error)
  }

  return { isLoading, error, results }
}

const useRetriveItemDetails = (selectedId) => {
  const {
    isLoading,
    error,
    data: location = null,
  } = useQuery({
    queryKey: ['retrieve', selectedId],
    queryFn: () => {
      if (!selectedId) {
        return null
      }

      return getPlace(selectedId)
    },

    enabled: !!selectedId,
    staleTime: 60 * 60 * 1000, // 60 minutes
    // staleTime: 1, // use then reload to force refresh of underlying data during dev
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  // Just log the error, there isn't much we can show the user here
  if (error) {
    // eslint-disable-next-line no-console
    console.error('ERROR retrieving result from search API ', error)
  }

  return {
    isLoading,
    error,
    location,
  }
}

export const useMapboxSearch = (query, selectedId) => {
  // only really updated when query is updated
  const {
    isLoading: suggestionLoading,
    error: suggestionError,
    results,
  } = useSearchSuggestions(query)

  // called when selectedId is set
  const {
    location,
    isLoading: retriveLoading,
    error: retrieveError,
  } = useRetriveItemDetails(selectedId)

  // Just log the errors, there isn't much we can show the user here
  if (suggestionError) {
    // eslint-disable-next-line no-console
    console.error('ERROR loading search API results', suggestionError)
  }

  if (retrieveError) {
    // eslint-disable-next-line no-console
    console.error('ERROR retrieving result from search API ', retrieveError)
  }

  return {
    results,
    location,
    isLoading: suggestionLoading || retriveLoading,
    error: suggestionError || retrieveError,
  }
}
