import { List, Map, fromJS } from "immutable"

import { GO_BACK, SET_SYSTEM, SET_UNIT } from "../actions"

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

const SYSTEM_LEVELS = {
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
    prevBounds: List(), // push previous bounds here
    index,
    system: null, // HUC, ecoregion, state. null means SARP bounds
    level: null, // HUC: 2,4,8; Ecoregion1-4
    levelIndex: null, // index of level within system
    unit: null, // selected unit ID
    parentUnit: null, // larger unit in system that contains current unit
    labels: List([SARPLabelPoint])
})

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case SET_SYSTEM: {
            const { system } = payload
            const levelIndex = 0
            const level = `${system}${SYSTEM_LEVELS[system][levelIndex]}`

            const units = index.get(level)
            const labels = Array.from(units.values(), d => ({
                point: d.get("center").toJS(),
                label: d.get("dams")
            }))

            return state.merge({
                system,
                level,
                levelIndex,
                labels
            })
        }
        case SET_UNIT: {
            const prevBounds = state.get("prevBounds")

            if (payload.unit === null) {
                // setting unit to null means reset, so go to previous bounds or full bounds?
                return state.merge({
                    unit: null,
                    bounds: prevBounds.last(SARPBounds),
                    prevBounds: prevBounds.pop(),
                    labels: List([SARPLabelPoint])
                })
            }

            return state.merge({
                unit: payload.unit,
                bounds: index
                    .get(state.get("level"))
                    .get(payload.unit)
                    .get("bbox"),
                prevBounds: prevBounds.push(state.get("bounds"))
            })
        }
        case GO_BACK: {
            const system = state.get("system")
            const levelIndex = state.get("levelIndex")
            const prevBounds = state.get("prevBounds")

            if (system === null) return state

            // if we are already on the top most level of system, reset
            if (levelIndex === 0) {
                return state.merge({
                    system: null,
                    level: null,
                    levelIndex: null,
                    bounds: SARPBounds,
                    prevBounds: List(),
                    labels: List([SARPLabelPoint])
                })
            }

            // TODO: get labels for prev level

            return state.merge({
                level: SYSTEM_LEVELS[levelIndex - 1],
                levelIndex: levelIndex - 1,
                bounds: prevBounds.last(SARPBounds),
                prevBounds: prevBounds.pop()
            })
        }
        default: {
            return state
        }
    }
}

export default reducer
