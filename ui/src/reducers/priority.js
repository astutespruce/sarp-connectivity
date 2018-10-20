import { List, Map } from "immutable"

import { PRIORITY_SET_SYSTEM, PRIORITY_SELECT_FEATURE } from "../actions/priority"
import { SARP_BOUNDS } from "../components/Map/config"

const initialState = Map({
    bounds: SARP_BOUNDS, // SARP bounds
    prevBounds: List() // push previous bounds here
})

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case PRIORITY_SET_SYSTEM: {
            return state.merge({
                system: payload.system,
                selectedFeature: null
            })
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
