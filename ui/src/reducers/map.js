import { Map, List, fromJS } from "immutable"

import { SET_BOUNDS, SET_CENTER, SET_LOCATION } from "../actions/map"
import { SARP_BOUNDS } from "../constants"

const initialState = Map({
    bounds: List(SARP_BOUNDS),
    center: Map(), // { latitude, longitude, zoom }
    location: Map(), // {latitude, longitude, timestamp}
    searchFeature: Map() // {id, layer, bbox, maxZoom=null}
})

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case SET_BOUNDS: {
            return state.set("bounds", List(payload.bounds))
        }
        case SET_CENTER: {
            return state.set("center", Map(payload.center))
        }
        case SET_LOCATION: {
            return state.set("location", Map(payload.location))
        }
        default: {
            return state
        }
    }
}

export default reducer
