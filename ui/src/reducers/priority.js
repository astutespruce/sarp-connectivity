import { List, Map, Set, fromJS } from "immutable"

import {
    PRIORITY_SET_SYSTEM,
    PRIORITY_SET_SCENARIO,
    PRIORITY_SELECT_FEATURE,
    PRIORITY_SET_LAYER,
    PRIORITY_ADD_SUMMARY_UNIT,
    PRIORITY_SET_MODE,
    PRIORITY_SET_TYPE,
    SET_FILTER,
    FETCH_QUERY_START,
    FETCH_QUERY_SUCCESS,
    FETCH_QUERY_ERROR,
    TOGGLE_FILTER_CLOSED,
    RESET_FILTERS,
    PRIORITY_FETCH_START,
    PRIORITY_FETCH_SUCCESS,
    PRIORITY_FETCH_ERROR,
    SET_TIER_THRESHOLD
} from "../actions/priority"
import { SARP_BOUNDS } from "../components/map/config"

import { allFilters, getDimensionCounts, getTotalFilteredCount } from "../filters"

allFilters.reduce((out, item) => out.set(item, Set()), Map())

const initialState = Map({
    mode: "select", // mode or step in selection process: "default" (initial), "select", "filter", "results"
    bounds: SARP_BOUNDS, // SARP bounds
    // bounds: List([-85.03324716546452, 32.63585392698306, -84.15434091546213, 32.96541554455193]),
    prevBounds: List(), // push previous bounds here
    scenario: "ncwc", // nc, wc, ncwc
    layer: "HUC8", // HUC*, ECO*, State
    summaryUnits: Set([{ id: "03130007" }]), // set of specific IDs from the summary unit layer
    type: "dams", // null, // dams or barriers; not set until chosen by user
    rankData: List(),
    tierThreshold: 1, // 1-20, which tiers to include in top-ranked dams on map

    // filter state
    filtersLoaded: false,
    filters: allFilters.reduce((out, item) => out.set(item, Set()), Map()),
    dimensionCounts: Map(), // Map of Map of ints
    totalCount: 0,
    closedFilters: allFilters.reduce((out, item, i) => out.set(item, i >= 0), Map()),

    isLoading: false,
    isError: false
})

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case "@@router/LOCATION_CHANGE": {
            return initialState
        }
        case PRIORITY_SET_SYSTEM: {
            return state.merge({
                system: payload.system,
                selectedFeature: null
            })
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
            return state.set("summaryUnits", updated)
        }
        case PRIORITY_SET_MODE: {
            const { mode } = payload
            // TODO: clear out units depending on mode
            // TODO: clear out crossfilter and associated stuff if going from filter to previous?
            return state.set("mode", mode)
        }
        case PRIORITY_SET_TYPE: {
            return state.merge({
                type: payload.type,
                mode: "select"
            })
        }
        case SET_FILTER: {
            const { filter, filterValues } = payload

            const dimension = window.dims[filter]
            if (filterValues.size > 0) {
                dimension.filterFunction(d => filterValues.has(d))
            } else {
                dimension.filterAll()
            }

            return state.merge({
                dimensionCounts: fromJS(getDimensionCounts()),
                totalCount: getTotalFilteredCount(),
                filters: state.get("filters").set(filter, filterValues)
            })
        }
        case RESET_FILTERS: {
            allFilters.forEach(d => {
                window.dims[d].filterAll()
            })
            return state.merge({
                filters: allFilters.reduce((out, item) => out.set(item, Set()), Map()),
                dimensionCounts: fromJS(getDimensionCounts()),
                totalCount: getTotalFilteredCount()
            })
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
            return state.merge({
                filtersLoaded: true,
                filters: allFilters.reduce((out, item) => out.set(item, Set()), Map()),
                dimensionCounts: fromJS(getDimensionCounts()),
                totalCount: getTotalFilteredCount(),
                mode: "filter",
                isLoading: false,
                isError: false
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
