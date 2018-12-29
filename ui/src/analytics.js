import ReactGA from "react-ga"

import {
    PRIORITY_SET_LAYER,
    PRIORITY_SET_TYPE,
    PRIORITY_ADD_SUMMARY_UNIT,
    PRIORITY_SELECT_FEATURE,
    FETCH_QUERY_SUCCESS,
    PRIORITY_FETCH_SUCCESS,
    PRIORITY_DOWNLOAD,
    PRIORITY_SET_SCENARIO
} from "./actions/priority"

import { SUMMARY_SET_TYPE, SUMMARY_SET_SYSTEM, SUMMARY_SELECT_FEATURE } from "./actions/summary"

import { SET_FILTER } from "./actions/crossfilter"

const events = {
    [PRIORITY_SET_TYPE]: {
        category: "Priority",
        action: "Select Type",
        data: "priority.type"
    },
    [PRIORITY_SET_LAYER]: {
        category: "Priority",
        action: "Select Layer",
        data: "priority.layer"
    },
    [PRIORITY_ADD_SUMMARY_UNIT]: {
        category: "Priority",
        action: "Select Unit",
        data: "priority.summaryUnits",
        func: summaryUnits => {
            summaryUnits
                .map(f => f.id)
                .sort()
                .join(",")
        }
    },
    [PRIORITY_SELECT_FEATURE]: {
        category: "Priority",
        action: "Select Unit"
    },
    [PRIORITY_SET_SCENARIO]: {
        category: "Priority",
        action: "Select scenario in map",
        data: "priority.scenario"
    },
    [FETCH_QUERY_SUCCESS]: {
        category: "Priority",
        action: "Loaded data for filter"
    },
    [SET_FILTER]: {
        category: "Priority",
        action: "Set filter",
        data: "crossfilter.filters",
        func: filters =>
            Object.entries(filters)
                .filter(([k, v]) => v.length > 0)
                .map(([k, v]) => `${k}:${v.join(",")}`)
                .join("|")
    },
    [PRIORITY_FETCH_SUCCESS]: {
        category: "Priority",
        action: "Ranked data"
    },
    [PRIORITY_DOWNLOAD]: {
        category: "Priority",
        action: "Download data"
    },
    [SUMMARY_SET_SYSTEM]: {
        category: "Summary",
        action: "Select Layer",
        data: "summary.system"
    },
    [SUMMARY_SELECT_FEATURE]: {
        category: "Summary",
        action: "Select Unit",
        data: "summary.selectedFeature",
        func: ({ id, layerId }) => `${layerId}:${id}`
    },
    [SUMMARY_SET_TYPE]: {
        category: "Summary",
        action: "Select Type",
        data: "summary.type"
    }
}

/**
 *
 * @param {string} path - path to value, using dot notation.  First entry is name of reducer.
 * @param {ImmutableObject} state - state from the store
 * @param {function} func - function that takes as input the fetched data and returns a string
 */
const resolveData = (path, state, func) => {
    if (!path) return null

    try {
        const [reducer, prop, ...props] = path.split(".")
        let data = state.get(reducer).get(prop)
        props.forEach(p => {
            if (data) {
                data = data.get ? data.get(p) : data[p]
            }
        })

        data = data.toJS ? data.toJS() : data

        if (data && func) {
            data = func(data)
        }

        return data.toString()
    } catch {
        console.error("Error fetching data for path", path)
        return null
    }
}

const trackEvent = ({ category, action, data, func }, state) => {
    ReactGA.event({ category, action, label: resolveData(data, state, func) || null })
}

export const trackingMiddleware = store => next => action => {
    const { type, payload } = action
    if (type === "@@router/LOCATION_CHANGE") {
        const { pathname, search } = payload.location
        const page = `${pathname}${search}`
        ReactGA.set({ page })
        ReactGA.pageview(page)
    }

    // Apply the action so that we can get the resulting state
    const result = next(action)

    if (events[type]) {
        trackEvent(events[type], store.getState())
    }

    return result
}

export default trackingMiddleware
