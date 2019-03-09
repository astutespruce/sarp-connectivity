import { fromJS, Map } from "immutable"

import {
    SUMMARY_SET_SYSTEM,
    SUMMARY_SELECT_FEATURE,
    SUMMARY_SET_TYPE,
    SUMMARY_SET_SEARCH_FEATURE
} from "../actions/summary"

const initialState = Map({
    system: "HUC", // HUC, ECO, ADMIN. null means SARP region
    type: "dams", // dams, barriers
    searchFeature: Map(), // {id, layer, bbox, maxZoom=null}
    selectedFeature: Map() // selected unit properties {id: <>, ...}
})

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case "@@router/LOCATION_CHANGE": {
            return initialState
        }
        case SUMMARY_SET_SYSTEM: {
            return state.merge({
                system: payload.system,
                searchFeature: Map(),
                selectedFeature: Map()
            })
        }
        case SUMMARY_SET_TYPE: {
            return state.merge({
                type: payload.type,
                selectedFeature: Map()
            })
        }
        case SUMMARY_SET_SEARCH_FEATURE: {
            return state.set("searchFeature", fromJS(payload.searchFeature).set("maxZoom", payload.maxZoom))
        }
        case SUMMARY_SELECT_FEATURE: {
            return state.merge({
                selectedFeature: payload.selectedFeature,
                searchFeature: Map()
            })
        }
        default: {
            return state
        }
    }
}

export default reducer
