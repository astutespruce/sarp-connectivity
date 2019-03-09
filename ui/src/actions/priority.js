import { csv } from "d3-fetch"

import { clear, load } from "./crossfilter"
import { DAM_FILTERS, BARRIER_FILTERS } from "../filters"
import { apiQueryParams } from "../utils/api"
import { logException } from "../utils/errors"
import { API_HOST } from "../config"

export const PRIORITY_SET_MODE = "PRIORITY_SET_MODE"
export const setMode = mode => ({
    type: PRIORITY_SET_MODE,
    payload: { mode }
})

export const PRIORITY_SET_TYPE = "PRIORITY_SET_TYPE"
export const setType = type => ({
    type: PRIORITY_SET_TYPE,
    payload: { type }
})

export const PRIORITY_SET_LAYER = "PRIORITY_SET_LAYER"
export const setLayer = id => ({
    type: PRIORITY_SET_LAYER,
    payload: { id }
})

export const PRIORITY_ADD_SUMMARY_UNIT = "PRIORITY_ADD_SUMMARY_UNIT"
export const selectUnit = unit => ({
    type: PRIORITY_ADD_SUMMARY_UNIT,
    payload: { unit }
})

export const PRIORITY_SELECT_FEATURE = "PRIORITY_SELECT_FEATURE"
export const selectFeature = selectedFeature => ({
    type: PRIORITY_SELECT_FEATURE,
    payload: { selectedFeature }
})

export const PRIORITY_FETCH_START = "PRIORITY_FETCH_START"
export const fetchStart = () => ({
    type: PRIORITY_FETCH_START,
    payload: {}
})

export const PRIORITY_FETCH_SUCCESS = "PRIORITY_FETCH_SUCCESS"
export const fetchSuccess = data => ({
    type: PRIORITY_FETCH_SUCCESS,
    payload: {
        data
    }
})

export const PRIORITY_FETCH_ERROR = "PRIORITY_FETCH_ERROR"
export const fetchError = error => ({
    type: PRIORITY_FETCH_ERROR,
    payload: { error }
})

export function fetchRanks(type, layer, units, filters) {
    return dispatch => {
        const url = `${API_HOST}/api/v1/${type}/rank/${layer}?${apiQueryParams(units, filters)}`

        csv(url, row => {
            // Convert fields to floating point or int as needed
            Object.keys(row).forEach(f => {
                if (f === "lat" || f === "lon") {
                    row[f] = parseFloat(row[f])
                } else {
                    row[f] = parseInt(row[f], 10)
                }
            })
            return row
        })
            .then(data => {
                window.rankData = data
                dispatch(fetchSuccess(data))
            })
            .catch(error => {
                logException(error, `request: ${url}`)
                dispatch(fetchError(error))
            })
        return dispatch(fetchStart())
    }
}

export const FETCH_QUERY_START = "FETCH_QUERY_START"
export const fetchQueryStart = () => ({
    type: FETCH_QUERY_START,
    payload: {}
})

export const FETCH_QUERY_SUCCESS = "FETCH_QUERY_SUCCESS"
export const fetchQuerySuccess = (data, filters) => ({
    type: FETCH_QUERY_SUCCESS,
    payload: {
        data,
        filters
    }
})

export const FETCH_QUERY_ERROR = "FETCH_QUERY_ERROR"
export const fetchQueryError = error => ({
    type: FETCH_QUERY_ERROR,
    payload: {
        error
    }
})

export const fetchQuery = (type, layer, units) => dispatch => {
    const url = `${API_HOST}/api/v1/${type}/query/${layer}?${apiQueryParams(units)}`

    const filters = type === "dams" ? DAM_FILTERS : BARRIER_FILTERS
    dispatch(clear())

    csv(url, row => {
        // convert everything to integer
        Object.keys(row).forEach(f => {
            row[f] = parseInt(row[f], 10)
        })
        return row
    })
        .then(data => {
            window.data = data
            dispatch(load(data, filters))
            dispatch(fetchQuerySuccess(data, filters))
        })
        .catch(error => {
            logException(error, `request: ${url}`)
            dispatch(fetchQueryError(error))
        })
    return dispatch(fetchQueryStart())
}

export const TOGGLE_FILTER_CLOSED = "TOGGLE_FILTER_CLOSED"
export function toggleFilterClosed(filter, isClosed) {
    return {
        type: TOGGLE_FILTER_CLOSED,
        payload: {
            filter,
            isClosed
        }
    }
}

export const SET_TIER_THRESHOLD = "SET_TIER_THRESHOLD"
export const setTierThreshold = threshold => ({
    type: SET_TIER_THRESHOLD,
    payload: {
        threshold
    }
})

export const PRIORITY_SET_SCENARIO = "PRIORITY_SET_SCENARIO"
export const setScenario = scenario => ({
    type: PRIORITY_SET_SCENARIO,
    payload: { scenario }
})

// Just for logging purposes
export const PRIORITY_DOWNLOAD = "PRIORITY_DOWNLOAD"
export const logDownload = () => ({
    type: PRIORITY_DOWNLOAD,
    payload: {}
})

export const ON_MAP_LOAD = "ON_MAP_LOAD"
export const onMapLoad = () => ({
    type: ON_MAP_LOAD,
    payload: {}
})

export const PRIORITY_SET_SEARCH_FEATURE = "PRIORITY_SET_SEARCH_FEATURE"
export const setSearchFeature = (searchFeature, maxZoom = null) => ({
    type: PRIORITY_SET_SEARCH_FEATURE,
    payload: {
        searchFeature,
        maxZoom
    }
})
