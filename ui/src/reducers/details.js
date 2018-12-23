import { Map } from "immutable"

import { DETAILS_SET_TAB, DETAILS_SET_UNIT } from "../actions/details"

const initialState = Map({
    tab: "details",
    unit: "custom" // custom, state, se
})

// TODO: when prioritization is changed, change the summaryUnit to custom
export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case DETAILS_SET_TAB: {
            return state.set("tab", payload.tab)
        }
        case DETAILS_SET_UNIT: {
            return state.set("unit", payload.unit)
        }
        default: {
            return state
        }
    }
}

export default reducer
