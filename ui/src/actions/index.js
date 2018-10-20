export const SET_SYSTEM = "SET_SYSTEM"
export const setSystem = system => ({
    type: SET_SYSTEM,
    payload: { system }
})

export const SELECT_FEATURE = "SELECT_FEATURE"
export const selectFeature = selectedFeature => ({
    type: SELECT_FEATURE,
    payload: { selectedFeature }
})

export const GO_BACK = "GO_BACK"
export const goBack = () => ({
    type: GO_BACK
})
