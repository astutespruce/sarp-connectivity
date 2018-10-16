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
    sarp: [0],
    states: [0],
    HUC: [2, 4, 8],
    ecoregion: [1, 2, 3, 4]
}

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
    system: null, // HUC, ecoregion, state. null means SARP bounds
    levelIndex: null, // index of level within system
    level: null, // HUC: 2,4,8; Ecoregion1-4, states, sarp
    childLevel: null,
    unit: null, // selected unit ID
    parentUnit: null, // larger unit in system that contains current unit
    labels: SARPLabelPoint
})

export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case SET_SYSTEM: {
            const { system } = payload
            const levels = SYSTEM_LEVELS[system]
            const levelIndex = 0
            const level = `${system}${levels[levelIndex]}`
            const labels = Array.from(index.get(level).values(), getLabels)

            return state.merge({
                system,
                level,
                levelIndex,
                childLevel: levelIndex < levels.length - 1 ? `${system}${levels[levelIndex + 1]}` : null,
                labels
            })
        }
        case SET_UNIT: {
            const prevBounds = state.get("prevBounds")

            if (payload.unit === null) {
                // setting unit to null means reset, so go to previous bounds or full bounds?
                // stay at same level
                return state.merge({
                    unit: null,
                    bounds: prevBounds.last(SARPBounds),
                    prevBounds: prevBounds.pop()
                })
            }

            // We are at the same level, but a different unit; we only want to store
            // bounds for the last selected unit at this level
            if (state.get("unit") !== null) {
                prevBounds.pop()
            }

            return state.merge({
                unit: payload.unit,
                bounds: index
                    .get(state.get("level"))
                    .get(payload.unit)
                    .get("bbox"),
                prevBounds: prevBounds.push(state.get("bounds"))
            })

            // const system = state.get("system")
            // let levelIndex = state.get("levelIndex")
            // console.log(
            //     "cur level",
            //     `${system}${SYSTEM_LEVELS[system][levelIndex]}`,
            //     levelIndex,
            //     SYSTEM_LEVELS[system].length
            // )

            // // move up to the next level
            // if (levelIndex < SYSTEM_LEVELS[system].length - 1) {
            //     levelIndex += 1
            //     const level = `${system}${SYSTEM_LEVELS[system][levelIndex]}`

            //     newState = newState.merge({
            //         levelIndex,
            //         level
            //         // labels: Array.from(index.get(level).values(), getLabels)
            //     })
            // }

            // return newState
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
                    childLevel: null,
                    unit: null,
                    bounds: SARPBounds,
                    prevBounds: List(),
                    labels: SARPLabelPoint
                })
            }

            return state.merge({
                unit: null,
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
