import { List, Map, Set, fromJS } from "immutable"

import { ON_LOAD as ON_CROSSFILTER_LOAD } from "../actions/crossfilter"

import {
    ON_MAP_LOAD,
    PRIORITY_SET_SCENARIO,
    PRIORITY_SELECT_FEATURE,
    PRIORITY_SET_LAYER,
    PRIORITY_ADD_SUMMARY_UNIT,
    PRIORITY_SET_MODE,
    PRIORITY_SET_TYPE,
    FETCH_QUERY_START,
    FETCH_QUERY_SUCCESS,
    FETCH_QUERY_ERROR,
    TOGGLE_FILTER_CLOSED,
    PRIORITY_FETCH_START,
    PRIORITY_FETCH_SUCCESS,
    PRIORITY_FETCH_ERROR,
    PRIORITY_SET_SEARCH_FEATURE,
    SET_TIER_THRESHOLD
} from "../actions/priority"

const initialState = Map({
    mode: "start", // mode or step in selection process: "select", "filter", "results"
    scenario: "ncwc", // nc, wc, ncwc
    layer: null, // HUC*, ECO*, State
    summaryUnits: Set(), // set of specific IDs from the summary unit layer
    selectedFeature: Map(),
    searchFeature: Map(),
    type: null, // dams or barriers; not set until chosen by user
    rankData: List(),
    tierThreshold: 1, // 1-20, which tiers to include in top-ranked dams on map

    closedFilters: Map(), //  allFilters.reduce((out, item, i) => out.set(item, i >= 0), Map()),

    // loading data, crossfilter, and map all happen in very separate steps, so for convenience completion of each can update this value
    isLoading: true, // assume we are at start, and nothing has loaded yet
    isError: false
})

// FIXME: dev only
// if (process.env.NODE_ENV !== "production") {
//     initialState = initialState.merge({
//         mode: "select",
//         type: "dams",
//         layer: "HUC12",
//         summaryUnits: Set([{ id: "030101030502" }])
//     })
// }

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case "@@router/LOCATION_CHANGE": {
            return initialState
        }
        case ON_CROSSFILTER_LOAD: {
            return state.set("isLoading", false)
        }
        case ON_MAP_LOAD: {
            return state.set("isLoading", false)
        }
        case PRIORITY_SET_SCENARIO: {
            return state.set("scenario", payload.scenario)
        }
        case PRIORITY_SELECT_FEATURE: {
            return state.set("selectedFeature", payload.selectedFeature)
        }
        case PRIORITY_SET_LAYER: {
            return state.merge({
                layer: payload.id,
                summaryUnits: Set()
            })
        }
        case PRIORITY_ADD_SUMMARY_UNIT: {
            const unit = fromJS(payload.unit)
            const summaryUnits = state.get("summaryUnits")
            const updated = summaryUnits.has(unit) ? summaryUnits.delete(unit) : summaryUnits.add(unit)
            return state.merge({
                summaryUnits: updated,
                searchFeature: Map()
            })
        }
        case PRIORITY_SET_MODE: {
            const { mode } = payload
            return state.merge({
                mode,
                isLoading: mode === "start" ? true : state.get("isLoading")
            })
        }
        case PRIORITY_SET_TYPE: {
            return state.merge({
                type: payload.type,
                mode: "select"
            })
        }
        case PRIORITY_SET_SEARCH_FEATURE: {
            return state.set("searchFeature", fromJS(payload.searchFeature))
        }
        case FETCH_QUERY_START: {
            return state.set("isLoading", true)
        }
        case FETCH_QUERY_ERROR: {
            return state.merge({
                isLoading: false,
                isError: true
            })
        }
        case FETCH_QUERY_SUCCESS: {
            const { filters } = payload

            return state.merge({
                mode: "filter",
                isError: false,
                closedFilters: filters.reduce((out, item, i) => out.set(item.field, i >= 0), Map())
            })
        }
        case TOGGLE_FILTER_CLOSED: {
            const { filter, isClosed } = payload
            const closed = state.get("closedFilters")
            return state.set("closedFilters", closed.set(filter, isClosed))
        }
        case PRIORITY_FETCH_START: {
            return state.set("isLoading", true)
        }
        case PRIORITY_FETCH_ERROR: {
            return state.merge({
                isLoading: false,
                isError: true
            })
        }
        case PRIORITY_FETCH_SUCCESS: {
            const { data } = payload
            return state.merge({
                mode: "results",
                rankData: fromJS(data),
                isLoading: false,
                isError: false
            })
        }
        case SET_TIER_THRESHOLD: {
            return state.set("tierThreshold", payload.threshold)
        }
        default: {
            return state
        }
    }
}

export default reducer
