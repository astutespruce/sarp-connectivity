// import axios from "axios"
import { csv } from "d3-fetch"

import { initCrossfilter } from "../filters"
import { API_HOST } from "../config"

export const PRIORITY_SET_SYSTEM = "PRIORITY_SET_SYSTEM"
export const setSystem = system => ({
    type: PRIORITY_SET_SYSTEM,
    payload: { system }
})

export const PRIORITY_SET_SCENARIO = "PRIORITY_SET_SCENARIO"
export const setScenario = scenario => ({
    type: PRIORITY_SET_SCENARIO,
    payload: { scenario }
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

export const PRIORITY_FETCH_START = "PRIORITY_FETCH_START"
export const fetchStart = (layer, ids) => ({
    type: PRIORITY_FETCH_START,
    payload: {
        layer,
        ids
    }
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

export function fetchRanks(layer, units, filters) {
    return dispatch => {
        const ids = units.map(({ id }) => id)
        const filterValues = Object.entries(filters).filter(([, v]) => v.length > 0) // .map(([, v]) => v.join(','))

        let url = `${API_HOST}/api/v1/dams/rank/${layer}?id=${ids.join(",")}`
        if (filterValues) {
            url += filterValues.map(([k, v]) => `&${k}=${v.join(",")}`)
            // url += `&filter=${filterValues}`
        }

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
                console.log(data)
                dispatch(fetchSuccess(data))
            })
            .catch(error => {
                console.error(error)
                dispatch(fetchError(error))
            })
        return dispatch(fetchStart(layer, ids))
    }
}

export const FETCH_QUERY_START = "FETCH_QUERY_START"
export const fetchQueryStart = (layer, ids) => ({
    type: FETCH_QUERY_START,
    payload: {
        layer,
        ids
    }
})

export const FETCH_QUERY_SUCCESS = "FETCH_QUERY_SUCCESS"
export const fetchQuerySuccess = data => ({
    type: FETCH_QUERY_SUCCESS,
    payload: {
        data
    }
})

export const FETCH_QUERY_ERROR = "FETCH_QUERY_ERROR"
export const fetchQueryError = error => ({
    type: FETCH_QUERY_ERROR,
    payload: {
        error
    }
})

export const fetchQuery = (layer, units) => dispatch => {
    const ids = units.map(({ id }) => id)
    csv(`${API_HOST}/api/v1/dams/query/${layer}?id=${ids.join(",")}`, row => {
        // convert everything to integer
        Object.keys(row).forEach(f => {
            row[f] = parseInt(row[f], 10)
        })
        return row
    })
        .then(data => {
            window.data = data
            initCrossfilter(data)
            dispatch(fetchQuerySuccess(data))
        })
        .catch(error => {
            console.error(error)
            dispatch(fetchQueryError(error))
        })
    return dispatch(fetchQueryStart(layer, ids))
}

export const SET_FILTER = "SET_FILTER"
export const setFilter = (filter, filterValues) => ({
    type: SET_FILTER,
    payload: {
        filter,
        filterValues
    }
})

// TODO: not hooked up yet
export const RESET_FILTERS = "RESET_FILTERS"
export const resetFilters = () => ({
    type: RESET_FILTERS
})

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
