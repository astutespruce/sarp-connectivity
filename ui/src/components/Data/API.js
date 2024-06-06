import { tableFromIPC } from '@apache-arrow/es2015-esm'
import { fromArrow } from 'arquero'

import { unpackBits, toCamelCaseFields } from 'util/data'
import { captureException } from 'util/log'
import { siteMetadata, TIER_PACK_BITS } from 'config'
import { extractYearRemovedStats } from 'components/Restoration/util'

const { apiHost } = siteMetadata

/**
 * Converts units and filters into query parameters for API requests
 */
const apiQueryParams = ({
  summaryUnits = {},
  filters = {},
  includeUnranked = false,
  sort = null,
  customRank = false,
}) => {
  let query = Object.entries(summaryUnits)
    .map(([key, values]) => `${key}=${values.join(',')}`)
    .join('&')

  const filterValues = Object.entries(filters).filter(([, v]) => v.size > 0)
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

const fetchFeather = async (url, options, asTable = false) => {
  try {
    const response = await fetch(url, options)

    if (response.status !== 200) {
      throw new Error(`Failed request to ${url}: ${response.statusText}`)
    }

    const data = await tableFromIPC(response.arrayBuffer())

    return {
      data: asTable
        ? fromArrow(data)
        : data.toArray().map((row) => row.toJSON()),
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
export const fetchBarrierInfo = async (barrierType, summaryUnits) => {
  const url = `${apiHost}/api/v1/internal/${barrierType}/query?${apiQueryParams(
    {
      summaryUnits,
    }
  )}`

  return fetchFeather(url, undefined, true)
}

/**
 * Fetch and parse Feather data from API for dams or small barriers
 */
export const fetchBarrierRanks = async (barrierType, summaryUnits, filters) => {
  const url = `${apiHost}/api/v1/internal/${barrierType}/rank?${apiQueryParams({
    summaryUnits,
    filters,
  })}`

  // Unpack bit-packed tiers
  const { data: packedTiers, bounds } = await fetchFeather(url, undefined)
  const data = packedTiers.map(({ id, tiers }) => ({
    id,
    ...unpackBits(tiers, TIER_PACK_BITS),
  }))

  return {
    bounds,
    data,
  }
}

export const fetchBarrierDetails = async (networkType, sarpid) => {
  const url = `${apiHost}/api/v1/internal/${networkType}/details/${sarpid}`

  const response = await fetch(url)
  if (response.status === 404) {
    return null // not found
  }

  const data = await response.json()
  return data
}

export const getDownloadURL = ({
  barrierType,
  summaryUnits,
  filters,
  includeUnranked = null,
  sort = null,
  customRank = false,
}) => {
  const params = {
    summaryUnits,
    filters,
  }

  if (includeUnranked !== null) {
    params.includeUnranked = includeUnranked
  }

  if (sort !== null) {
    params.sort = sort
  }
  if (customRank) {
    params.customRank = customRank
  }

  return `${apiHost}/api/v1/internal/${barrierType}/csv?${apiQueryParams(
    params
  )}`
}

export const fetchUnitDetails = async (layer, id) => {
  const url = `${apiHost}/api/v1/internal/units/${layer}/details/${id}`

  try {
    const response = await fetch(url)
    if (response.status !== 200) {
      throw new Error(`Failed request to ${url}: ${response.statusText}`)
    }

    const rawData = await response.json()

    const { removedDamsByYear, removedSmallBarriersByYear, ...data } =
      toCamelCaseFields(rawData)

    const removedBarriersByYear = extractYearRemovedStats(
      removedDamsByYear,
      removedSmallBarriersByYear
    )

    return { ...data, removedBarriersByYear }
  } catch (err) {
    captureException(err)

    throw err
  }
}

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

    return {
      results: data.toArray().map((row) => toCamelCaseFields(row.toJSON())),
      remaining: parseInt(data.schema.metadata.get('count'), 10) - data.numRows,
    }
  } catch (err) {
    captureException(err)

    throw err
  }
}

export const fetchUnitList = async (layer, ids) => {
  const url = `${apiHost}/api/v1/internal/units/${layer}/list?id=${ids.join(',')}`

  try {
    const response = await fetch(url)
    if (response.status !== 200) {
      throw new Error(`Failed request to ${url}: ${response.statusText}`)
    }

    const data = await tableFromIPC(response.arrayBuffer())

    return data.toArray().map((row) => toCamelCaseFields(row.toJSON()))
  } catch (err) {
    captureException(err)

    throw err
  }
}

export const searchBarriers = async (query) => {
  const url = `${apiHost}/api/v1/internal/barriers/search?query=${query}`

  try {
    const response = await fetch(url)
    if (response.status !== 200) {
      throw new Error(`Failed request to ${url}: ${response.statusText}`)
    }

    const data = await tableFromIPC(response.arrayBuffer())

    return {
      results: data.toArray().map((row) => row.toJSON()),
      remaining: parseInt(data.schema.metadata.get('count'), 10) - data.numRows,
    }
  } catch (err) {
    captureException(err)

    throw err
  }
}
