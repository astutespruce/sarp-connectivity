export const PRIORITY_SET_SYSTEM = "PRIORITY_SET_SYSTEM"
export const setSystem = system => ({
    type: PRIORITY_SET_SYSTEM,
    payload: { system }
})

export const PRIORITY_SELECT_FEATURE = "PRIORITY_SELECT_FEATURE"
export const selectFeature = selectedFeature => ({
    type: PRIORITY_SELECT_FEATURE,
    payload: { selectedFeature }
})
