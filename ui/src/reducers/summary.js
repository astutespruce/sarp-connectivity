import { List, Map } from "immutable"

import { SUMMARY_SET_SYSTEM, SUMMARY_SELECT_FEATURE, SUMMARY_SET_TYPE } from "../actions/summary"
import { SARP_BOUNDS } from "../components/map/config"

const initialState = Map({
    bounds: SARP_BOUNDS, // SARP bounds
    prevBounds: List(), // push previous bounds here
    system: "HUC", // HUC, ECO, ADMIN. null means SARP region
    type: "dams", // dams, barriers
    selectedFeature: null // selected unit properties {id: <>, ...}
})

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case "@@router/LOCATION_CHANGE": {
            return initialState
        }
        case SUMMARY_SET_SYSTEM: {
            return state.merge({
                system: payload.system,
                selectedFeature: null
            })
        }
        case SUMMARY_SET_TYPE: {
            return state.set("type", payload.type)
        }
        case SUMMARY_SELECT_FEATURE: {
            return state.set("selectedFeature", payload.selectedFeature)
        }
        default: {
            return state
        }
    }
}

export default reducer
