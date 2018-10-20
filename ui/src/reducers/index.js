import { List, Map, fromJS } from "immutable"

import { SET_SYSTEM, SET_LEVEL, SELECT_FEATURE } from "../actions"

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
const SARPBounds = List([-106.645646, 17.623468, -64.512674, 40.61364])
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
    bounds: SARPBounds, // SARP bounds
    prevBounds: List(), // push previous bounds here
    index,
    system: "HUC", // HUC, ECO, state. null means SARP b
    selectedFeature: null, // selected unit properties {id: <>, ...}
    labels: SARPLabelPoint
})

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case SET_SYSTEM: {
            return state.set("system", payload.system)
        }
        case SELECT_FEATURE: {
            return state.set("selectedFeature", payload.selectedFeature)

            // let prevBounds = state.get("prevBounds")
            // if (unit === null) {
            //     // setting unit to null means reset, so go to previous bounds or full bounds?
            //     // stay at same level
            //     return state.merge({
            //         unit,
            //         bounds: prevBounds.last(SARPBounds),
            //         prevBounds: prevBounds.pop()
            //     })
            // }

            // // We are at the same level, but a different unit; we only want to store
            // // bounds for the last selected unit at this level
            // // TODO: this isn't working properly
            // if (state.get("unit") !== null) {
            //     prevBounds = prevBounds.pop()
            // }

            // return state.merge({
            //     unit,
            //     bounds: index
            //         .get(level)
            //         .get(unit)
            //         .get("bbox"),
            //     prevBounds: prevBounds.push(state.get("bounds"))
            // })
        }
        // case GO_BACK: {
        //     const system = state.get("system")
        //     const levelIndex = state.get("levelIndex")
        //     const prevBounds = state.get("prevBounds")

        //     if (system === null) return state

        //     // if we are already on the top most level of system, reset
        //     if (levelIndex === 0) {
        //         return state.merge({
        //             system: null,
        //             level: null,
        //             levelIndex: null,
        //             childLevel: null,
        //             unit: null,
        //             bounds: SARPBounds,
        //             prevBounds: List(),
        //             labels: SARPLabelPoint
        //         })
        //     }

        //     return state.merge({
        //         unit: null,
        //         level: SYSTEM_LEVELS[levelIndex - 1],
        //         levelIndex: levelIndex - 1,
        //         bounds: prevBounds.last(SARPBounds),
        //         prevBounds: prevBounds.pop()
        //     })
        // }
        default: {
            return state
        }
    }
}

export default reducer
