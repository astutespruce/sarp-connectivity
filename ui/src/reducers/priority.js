import { List, Map, Set, fromJS } from "immutable"

import {
    PRIORITY_SET_SYSTEM,
    PRIORITY_SET_SCENARIO,
    PRIORITY_SELECT_FEATURE,
    PRIORITY_SET_LAYER,
    PRIORITY_ADD_SUMMARY_UNIT,
    PRIORITY_SET_MODE,
    PRIORITY_SET_TYPE
} from "../actions/priority"
import { SARP_BOUNDS } from "../components/map/config"

const initialState = Map({
    mode: "default", // mode or step in selection process: "default" (initial), "select", "prioritize"
    // bounds: SARP_BOUNDS, // SARP bounds
    bounds: List([-85.03324716546452, 32.63585392698306, -84.15434091546213, 32.96541554455193]),
    prevBounds: List(), // push previous bounds here
    scenario: "NCWC", // NC, WC, NCWC, or *_NC, *_WC, *_NCWC
    layer: null, // HUC*, ECO*, State
    summaryUnits: Set(), // set of specific IDs from the summary unit layer
    type: "dams" // dams or barriers
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
            return state.set("mode", mode)
        }
        case PRIORITY_SET_TYPE: {
            return state.set("type", payload.type)
        }
        default: {
            return state
        }
    }
}

export default reducer
