import { tableFromIPC } from '@apache-arrow/es2015-esm'

import { captureException } from 'util/log'
import { siteMetadata } from 'constants'

const { apiHost } = siteMetadata

/**
 * Converts units and filters into query parameters for API requests
 */
const apiQueryParams = ({
  summaryUnits = [],
  filters = {},
  includeUnranked = false,
  sort = null,
  customRank = false,
}) => {
  const ids = summaryUnits.map(({ id }) => id)
  const filterValues = Object.entries(filters).filter(([, v]) => v.size > 0)

  if (!(ids.length || filterValues.length)) return ''

  let query = `id=${ids.join(',')}`

  if (filterValues.length > 0) {
    query += `&${filterValues
      .map(([k, v]) => `${k}=${Array.from(v).join(',')}`)
      .join('&')}`
  }

  if (includeUnranked) {
    query += '&include_unranked=1'
  }
  if (customRank) {
    query += '&custom=1'
  }
  if (sort) {
    query += `&sort=${sort}`
  }

  return query
}

const fetchFeather = async (url, options) => {
  try {
    const response = await fetch(url, options)

    if (response.status !== 200) {
      throw new Error(`Failed request to ${url}: ${response.statusText}`)
    }

    const data = await tableFromIPC(response.arrayBuffer())
    const [...table] = data

    return {
      data: table.map((row) => row.toJSON()),
      bounds: data.schema.metadata.get('bounds'),
    }
  } catch (err) {
    captureException(err)

    return {
      error: err,
      data: null,
    }
  }
}

/**
 * Fetch and parse Feather data from API for dams or small barriers
 */
export const fetchBarrierInfo = async (barrierType, layer, summaryUnits) => {
  const url = `${apiHost}/api/v1/internal/${barrierType}/query/${layer}?${apiQueryParams(
    {
      summaryUnits,
    }
  )}`

  return fetchFeather(url, undefined)
}

/**
 * Fetch and parse Feather data from API for dams or small barriers
 */
export const fetchBarrierRanks = async (
  barrierType,
  layer,
  summaryUnits,
  filters
) => {
  const url = `${apiHost}/api/v1/internal/${barrierType}/rank/${layer}?${apiQueryParams(
    {
      summaryUnits,
      filters,
    }
  )}`

  return fetchFeather(url, undefined)
}

export const fetchBarrierDetails = async (barrierType, sarpid) => {
  const url = `${apiHost}/api/v1/internal/${barrierType}/details/${sarpid}`

  const request = await fetch(url)
  const response = await request.json()
  if (response.detail) {
    return null // not found
  }
  return response
}

export const getDownloadURL = ({
  barrierType,
  layer,
  summaryUnits,
  filters,
  includeUnranked,
  sort,
  customRank = false,
}) =>
  `${apiHost}/api/v1/internal/${barrierType}/csv/${layer}?${apiQueryParams({
    summaryUnits,
    filters,
    includeUnranked,
    sort,
    customRank,
  })}`

export const searchUnits = async (layers, query) => {
  const url = `${apiHost}/api/v1/internal/units/search?layer=${layers.join(
    ','
  )}&query=${query}`

  try {
    const response = await fetch(url)
    if (response.status !== 200) {
      throw new Error(`Failed request to ${url}: ${response.statusText}`)
    }

    const data = await tableFromIPC(response.arrayBuffer())
    const [...table] = data

    return {
      results: table.map((row) => row.toJSON()),
      remaining: parseInt(data.schema.metadata.get('count'), 10) - data.numRows,
    }
  } catch (err) {
    captureException(err)

    throw err
  }
}
