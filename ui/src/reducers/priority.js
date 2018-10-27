import { List, Map } from "immutable"

import { PRIORITY_SET_SYSTEM, PRIORITY_SET_SCENARIO, PRIORITY_SELECT_FEATURE } from "../actions/priority"
import { SARP_BOUNDS } from "../components/map/config"

const initialState = Map({
    bounds: SARP_BOUNDS, // SARP bounds
    prevBounds: List(), // push previous bounds here
    scenario: "NCWC" // NC, WC, NCWC, or *_NC, *_WC, *_NCWC
})

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
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
        default: {
            return state
        }
    }
}

export default reducer
