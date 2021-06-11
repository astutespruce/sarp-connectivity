import { csvParse, autoType } from 'd3-dsv'

import { captureException } from 'util/log'
import { siteMetadata } from '../../../gatsby-config'

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
    query += '&unranked=1'
  }
  if (customRank) {
    query += '&custom=1'
  }
  if (sort) {
    query += `&sort=${sort}`
  }

  return query
}

const fetchCSV = async (url, options, rowParser) => {
  try {
    const request = await fetch(url, options)
    if (request.status !== 200) {
      throw new Error(`Failed request to ${url}: ${request.statusText}`)
    }

    const rawContent = await request.text()

    return {
      error: null,
      csv: csvParse(rawContent, rowParser),
    }
  } catch (err) {
    captureException(err)

    return {
      error: err,
      csv: null,
    }
  }
}

/**
 * Fetch and parse CSV data from API for dams or small barriers
 */
export const fetchBarrierInfo = async (barrierType, layer, summaryUnits) => {
  const url = `${apiHost}/api/v1/internal/${barrierType}/query/${layer}?${apiQueryParams(
    {
      summaryUnits,
    }
  )}`

  return fetchCSV(url, undefined, autoType)
}

/**
 * Fetch and parse CSV data from API for dams or small barriers
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

  return fetchCSV(url, undefined, autoType)
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
