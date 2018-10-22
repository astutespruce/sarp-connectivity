import { List, Map, fromJS } from "immutable"

import { SUMMARY_SET_SYSTEM, SUMMARY_SELECT_FEATURE } from "../actions/summary"
import { SARP_BOUNDS } from "../components/map/config"

// TODO: load this at run time instead of build time
import data from "../data/units.json"

// Index data on ID, and create as Immutable
// TODO: tune this
let index = {}
Object.entries(data).forEach(([key, records]) => {
    index[key] = {}
    records.forEach(r => {
        index[key][r.id] = r
    })
})
index = fromJS(index)
window.index = index

// TODO: migrate this into units.json instead

const SARPLabelPoint = fromJS([
    {
        point: [-87.69692774001089, 31.845649246524772],
        label: data.states.reduce((out, record) => out + record.dams, 0)
    }
])

const getLabels = d => ({
    point: d.get("center").toJS(),
    label: d.get("dams")
})

const initialState = Map({
    bounds: SARP_BOUNDS, // SARP bounds
    prevBounds: List(), // push previous bounds here
    index,
    system: "HUC", // HUC, ECO, state. null means SARP b
    selectedFeature: null, // selected unit properties {id: <>, ...}
    labels: SARPLabelPoint
})

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case SUMMARY_SET_SYSTEM: {
            return state.merge({
                system: payload.system,
                selectedFeature: null
            })
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
