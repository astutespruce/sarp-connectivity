// import axios from "axios"
import { csv } from "d3-fetch"

// TODO: make env var
const API_URL = "http://localhost:5000/api/v1/dams/rank"

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
    type: setType,
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

export function fetchRanks(layer, units) {
    return dispatch => {
        const ids = units.map(({ id }) => id)
        csv(`${API_URL}/${layer}?id=${ids.join(",")}`, row => {
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
            .then(response => {
                console.log(response)
                dispatch(fetchSuccess(response.data))
            })
            .catch(error => {
                console.error(error)
                dispatch(fetchError(error))
            })
        return dispatch(fetchStart(layer, ids))
    }
}
