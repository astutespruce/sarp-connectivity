// derived from: https://scotch.io/tutorials/create-a-custom-usefetch-react-hook

// import { useEffect, useState } from 'react'
import { csvParse } from 'd3-dsv'

// import { useBarrierType } from 'components/Data'
import { siteMetadata } from '../../../gatsby-config'

const { apiHost } = siteMetadata

// const infoURL =
// const rankURL = `${API_HOST}/api/v1/${type}/rank/${layer}` // plus query params

/**
 * Converts units and filters into query parameters for API requests
 * @param {Array} units - array of objects with id property
 * @param {Map} filters - map of filter values, where filter name is key
 */
const apiQueryParams = (units = [], filters = {}) => {
  const ids = units.map(({ id }) => id)
  const filterValues = Object.entries(filters).filter(([, v]) => v.length > 0)

  if (!(ids.length || filterValues.length)) return ''

  let query = `id=${ids.join(',')}`
  if (filterValues.length > 0) {
    query += `&${filterValues.map(([k, v]) => `${k}=${v.join(',')}`).join('&')}`
  }

  return query
}

/** Row parser for use with d3-dsv */
const rowToInts = row => {
  // convert everything to integer
  Object.keys(row).forEach(f => {
    row[f] = parseInt(row[f], 10)
  })
  return row
}

const fetchCSV = async (url, options, rowParser) => {
  try {
    const request = await fetch(url, options)
    const rawContent = await request.text()

    return {
      error: null,
      csv: csvParse(rawContent, rowParser),
    }
  } catch (err) {
    console.error(err)

    return {
      error: err,
      csv: null,
    }
  }
}

/**
 * Use fetch API and d3-dsv to get API response and parse CSV into JSON.
 * Returns {error, csv}.  If both are null, request is loading
 *
 *
 * @param {string} url - URL to fetch from
 * @param {Object} options - fetch API options
 */
// const useFetchCSV = (url, options, rowParser) => {
//   const [{ error, csv }, setState] = useState({
//     error: null,
//     csv: null,
//   })

//   useEffect(() => {

//     fetchCSV()
//   }, [])
//   return { csv, error }
// }

/**
 * Fetch and parse CSV data from API for dams or small barriers
 */
// export const useBarrierInfo = ({ layer, summaryUnits }) => {
//   const barrierType = useBarrierType()
//   const url = `${apiHost}/api/v1/${barrierType}/query/${layer}?${apiQueryParams(
//     summaryUnits
//   )}`

//   return useFetchCSV(url, undefined, rowToInts)
// }

// export const useRanks = () => {
//   // TODO
// }

export const fetchBarrierInfo = async (barrierType, layer, summaryUnits) => {
  const url = `${apiHost}/api/v1/${barrierType}/query/${layer}?${apiQueryParams(
    summaryUnits
  )}`

  return fetchCSV(url, undefined, rowToInts)
}
