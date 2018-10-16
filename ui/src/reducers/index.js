import { List, Map } from "immutable"

import { SET_SYSTEM, SET_UNIT } from "../actions"

// TODO: load this at run time instead of build time
import data from "../data/units.json"

// Index data on ID, and create as Immutable
// TODO: tune this
let index = {}
Object.entries(data).forEach(([key, records]) => {
    index[key] = {}
    records.forEach(r => {
        r.bbox = List(r.bbox)
        index[key][r.id] = Map(r)
    })
    index[key] = Map(index[key])
})
index = Map(index)

const systemLevels = {
    states: [0],
    HUC: [2, 4, 8],
    ecoregion: [1, 2, 3, 4]
}

// TODO: migrate this into units.json instead
const SARPBounds = List([-106.645646, 17.623468, -64.512674, 40.61364])
const SARPLabelPoint = {
    point: [-87.69692774001089, 31.845649246524772],
    label: data.states.reduce((out, record) => out + record.dams, 0)
}

const initialState = Map({
    bounds: SARPBounds, // SARP bounds
    index,
    system: null, // HUC, ecoregion, state
    level: null, // HUC: 2,4,8; Ecoregion1-4
    unit: null, // selected unit ID
    parentUnit: null, // larger unit in system that contains current unit
    labels: [SARPLabelPoint]
})

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case SET_SYSTEM: {
            return state.merge({
                system: payload.system,
                level: systemLevels[payload.system][0]
                // TODO: labels
            })

            // switch (payload.system) {
            //     case "HUC": {
            //         return newState.set("level", 2)
            //     }
            //     case "ecoregion": {
            //         return newState.set("level", 1)
            //     }
            //     default: {
            //         return newState
            //     }
            // }
        }
        case SET_UNIT: {
            // TODO: if index of level is < max, update bounds for that unit and set containing unit
            // console.log(index[`${state.get("system")}${state.get("level")}`][payload.unit].bbox)
            console.log(
                index
                    .get(`${state.get("system")}${state.get("level")}`)
                    .get(payload.unit)
                    .get("bbox")
            )
            return state.merge({
                unit: payload.unit,
                bounds:
                    payload.unit !== null
                        ? index
                            .get(`${state.get("system")}${state.get("level")}`)
                            .get(payload.unit)
                            .get("bbox")
                        : SARPBounds
            })
            // return state.set("unit", payload.unit)
        }
        default: {
            return state
        }
    }
}

export default reducer
