/* eslint-disable no-await-in-loop */
// awaits in loops below are intentional

import { tableFromIPC } from '@uwdata/flechette'
import { fromArrow } from 'arquero'

import { unpackBits, toCamelCaseFields } from 'util/data'
import { captureException } from 'util/log'
import { siteMetadata, TIER_FIELDS, TIER_PACK_INFO } from 'config'
import { extractYearRemovedStats } from 'components/Restoration/util'

const { apiHost } = siteMetadata

const pollInterval = 1000 // milliseconds; 1 second
const jobTimeout = 600000 // milliseconds; 10 minutes
const failedFetchLimit = 5

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
    query += '&custom_rank=1'
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

    // WARNING: flechette (1.1.0) tableFromIPC will break if called with an IPC
    // that batches with no rows; make sure that all responses from API use
    // .combine_chunks() to aggregate data before encoding to Feather if using
    // a selection of existing data
    const bytes = new Uint8Array(await response.arrayBuffer())
    const data = await tableFromIPC(bytes)

    return {
      data: asTable ? fromArrow(data) : data.toArray(),
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

  // Unpack bit-packed tier scenarios
  const { data: packedTiers, bounds } = await fetchFeather(url, undefined)
  const data = packedTiers.map(({ id, full, perennial, mainstem }) => ({
    id,
    // ...unpackBits(tiers, TIER_PACK_BITS),
    ...unpackBits(
      full,
      TIER_FIELDS.map((field) => ({ field, ...TIER_PACK_INFO }))
    ),
    ...unpackBits(
      perennial,
      TIER_FIELDS.map((field) => ({ field: `p${field}`, ...TIER_PACK_INFO }))
    ),
    ...unpackBits(
      mainstem,
      TIER_FIELDS.map((field) => ({ field: `m${field}`, ...TIER_PACK_INFO }))
    ),
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

export const fetchUnitDetails = async (layer, id) => {
  const url = `${apiHost}/api/v1/internal/units/${layer}/details/${id}`

  try {
    const response = await fetch(url)
    if (response.status !== 200) {
      throw new Error(`Failed request to ${url}: ${response.statusText}`)
    }

    const rawData = await response.json()

    const { removedDamsByYear, removedSmallBarriersByYear, bbox, ...data } =
      toCamelCaseFields(rawData)

    const removedBarriersByYear = extractYearRemovedStats(
      removedDamsByYear,
      removedSmallBarriersByYear
    )

    return {
      ...data,
      bbox: bbox ? bbox.split(',').map(parseFloat) : null,
      removedBarriersByYear,
    }
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

    const bytes = new Uint8Array(await response.arrayBuffer())
    const data = await tableFromIPC(bytes)

    return {
      results: data.toArray().map((row) => toCamelCaseFields(row)),
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

    const bytes = new Uint8Array(await response.arrayBuffer())
    const data = await tableFromIPC(bytes)

    return data.toArray().map((row) => toCamelCaseFields(row))
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

    const bytes = new Uint8Array(await response.arrayBuffer())
    const data = await tableFromIPC(bytes)

    return {
      results: data.toArray(),
      remaining: parseInt(data.schema.metadata.get('count'), 10) - data.numRows,
    }
  } catch (err) {
    captureException(err)

    throw err
  }
}

const pollJob = async (jobId, onProgress = null) => {
  let time = 0
  let failedRequests = 0

  let response = null

  while (time < jobTimeout && failedRequests < failedFetchLimit) {
    try {
      response = await fetch(
        `${apiHost}/api/v1/internal/downloads/status/${jobId}`,
        {
          cache: 'no-cache',
        }
      )
    } catch (ex) {
      failedRequests += 1

      // sleep and try again
      await new Promise((r) => {
        setTimeout(r, pollInterval)
      })
      time += pollInterval
      /* eslint-disable-next-line no-continue */
      continue
    }

    if (response.status === 500) {
      const error = await response.text()
      console.error('server error for download job', error)
      captureException('server error for download job', error)
      return {
        error: 'server error',
      }
    }

    const json = await response.json()
    const {
      status = null,
      progress = null,
      queue_position: queuePosition = null,
      elapsed_time: elapsedTime = null,
      message = null,
      detail: error = null, // error message
      path = null,
    } = json

    if (response.status !== 200 || status === 'failed') {
      captureException('Download job failed', json)
      if (error) {
        return { error }
      }

      throw Error(response.statusText)
    }

    if (status === 'success') {
      return { url: `${apiHost}${path}` }
    }

    if (
      onProgress &&
      (status === 'queued' || status === 'in_progress' || progress !== null)
    ) {
      onProgress({
        status,
        inProgress: true,
        progress: progress || 0,
        queuePosition: queuePosition || 0,
        elapsedTime: elapsedTime || null,
        message,
      })
    }

    // sleep
    await new Promise((r) => {
      setTimeout(r, pollInterval)
    })
    time += pollInterval
  }

  // if we got here, it meant that we hit a timeout error or a fetch error
  if (failedRequests) {
    captureException(`Download job encountered ${failedRequests} fetch errors`)

    return {
      error:
        'network errors were encountered while creating your download.  The server may be too busy or your network connection may be having problems.  Please try again in a few minutes.',
    }
  }

  if (time >= jobTimeout) {
    captureException('Download job timed out')
    return {
      error:
        'timeout while creating your download.  Try selecting a smaller area or number of records to download.',
    }
  }

  captureException('Download job had an unexpected error')
  return {
    error:
      'unexpected errors prevented your download job from completing successfully.  Please try again.',
  }
}

export const getDownloadURL = async (
  {
    barrierType,
    summaryUnits,
    filters,
    includeUnranked = null,
    sort = null,
    customRank = false,
  },
  onProgress = null
) => {
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

  if (onProgress) {
    onProgress({
      status: 'queued',
      inProgress: true,
      progress: 0,
    })
  }

  const response = await fetch(
    `${apiHost}/api/v1/internal/${barrierType}/csv?${apiQueryParams(params)}`,
    {
      method: 'POST',
    }
  )

  if (response.status !== 200) {
    let error = await response.text()
    try {
      const { detail } = JSON.parse(error)
      error = detail
    } catch (ex) {
      // don't do anything here
    }

    error = error || 'unhandled error'

    if (response.status === 500) {
      // this happens if redis is offline on the server
      console.error('server error for download request', error)
      captureException('server error for download request', error)
    } else {
      console.error('unhandled download request error', error)
      captureException('unhandled download request error', error)
    }
    return {
      error,
    }
  }

  const { status, job, path } = await response.json()

  // created download immediately, no need to poll job
  if (status === 'success' && path) {
    if (onProgress) {
      onProgress({
        status,
        inProgress: false,
        progress: 100,
      })
    }

    return { url: `${apiHost}${path}` }
  }

  const result = await pollJob(job, onProgress)
  return result
}
