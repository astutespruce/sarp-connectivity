export const PRIORITY_SET_SYSTEM = "PRIORITY_SET_SYSTEM"
export const setSystem = system => ({
    type: PRIORITY_SET_SYSTEM,
    payload: { system }
})

export const PRIORITY_SET_SCENARIO = "PRIORITY_SET_SCENARIO"
export const setScenario = scenario => ({
    type: PRIORITY_SET_SCENARIO,
    payload: { scenario }
})

export const PRIORITY_SET_LAYER = "PRIORITY_SET_LAYER"
export const setLayer = id => ({
    type: PRIORITY_SET_LAYER,
    payload: { id }
})

export const PRIORITY_ADD_SUMMARY_UNIT = "PRIORITY_ADD_SUMMARY_UNIT"
export const selectUnit = id => ({
    type: PRIORITY_ADD_SUMMARY_UNIT,
    payload: { id }
})

export const PRIORITY_SELECT_FEATURE = "PRIORITY_SELECT_FEATURE"
export const selectFeature = selectedFeature => ({
    type: PRIORITY_SELECT_FEATURE,
    payload: { selectedFeature }
})

export const PRIORITY_SET_MODE = "PRIORITY_SET_MODE"
export const setMode = mode => ({
    type: PRIORITY_SET_MODE,
    payload: { mode }
})
