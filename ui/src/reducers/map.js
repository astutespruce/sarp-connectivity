import { Map } from "immutable"

import { SET_LOCATION } from "../actions/map"
// import { SARP_BOUNDS } from "../components/map/config"

const initialState = Map({
    // bounds: SARP_BOUNDS, // SARP bounds
    location: Map() // {latitude, longitude, timestamp}
})

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case SET_LOCATION: {
            return state.set("location", Map(payload.location))
        }
        default: {
            return state
        }
    }
}

export default reducer
